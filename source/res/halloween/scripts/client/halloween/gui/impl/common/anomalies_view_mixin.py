# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/common/anomalies_view_mixin.py
from __future__ import absolute_import
import typing
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyModel, AnomalyState, AnomalyType
from halloween.gui.impl.gen.view_models.views.common.anomalies_matrix.recipe_model import RecipeModel
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import Optional, Set
    from halloween.gui.impl.gen.view_models.views.common.anomalies_matrix.anomalies_matrix_model import AnomaliesMatrixModel
    from halloween.gui.game_control.halloween_anomalies_controller import RecipeData, AnomalyData

class AnomaliesViewMixin(object):
    hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)

    def getAnomalyState(self, anomalyData):
        raise NotImplementedError

    @property
    def knownAnomaliesIDs(self):
        raise NotImplementedError

    def isAnomalyKnown(self, anomalyData):
        return anomalyData.id in self.knownAnomaliesIDs

    def refreshMatrix(self):
        with self.viewModel.transaction() as tx:
            matrixModel = tx.matrix
            recipesList = matrixModel.getRecipesList()
            recipesList.clear()
            for recipe in self.hwAnomaliesCtrl.recipes.values():
                recipesList.addViewModel(self.__createRecipeModel(recipe))

            recipesList.invalidate()
            individualAnomaliesList = matrixModel.getIndividualAnomaliesList()
            individualAnomaliesList.clear()
            for lootAnomaly in self.hwAnomaliesCtrl.lootAnomalies:
                individualAnomaliesList.addViewModel(self.__createAnomalyModel(anomaly=lootAnomaly))

            individualAnomaliesList.invalidate()

    def _onLoading(self, *args, **kwargs):
        self.refreshMatrix()
        super(AnomaliesViewMixin, self)._onLoading(*args, **kwargs)

    def __createRecipeModel(self, recipeData):
        recipeVM = RecipeModel()
        anomaliesList = recipeVM.getAnomaliesList()
        anomaliesList.clear()
        for anomalyID in recipeData.ingredients:
            anomaliesList.addViewModel(self.__createAnomalyModel(anomalyID=anomalyID))

        anomaliesList.addViewModel(self.__createAnomalyModel(anomalyID=recipeData.id))
        return recipeVM

    def __createAnomalyModel(self, anomaly=None, anomalyID=None):
        anomalyData = anomaly if anomaly else self.hwAnomaliesCtrl.getAnomalyByID(anomalyID)
        anomalyVM = AnomalyModel()
        anomalyVM.setId(anomalyData.id)
        anomalyVM.setType(AnomalyType(anomalyData.type))
        anomalyVM.setState(self.getAnomalyState(anomalyData))
        return anomalyVM
