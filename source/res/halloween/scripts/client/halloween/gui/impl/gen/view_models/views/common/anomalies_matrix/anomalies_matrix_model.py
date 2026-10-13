# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/common/anomalies_matrix/anomalies_matrix_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.common.anomalies_matrix.recipe_model import RecipeModel
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyModel

class AnomaliesMatrixModel(ViewModel):
    __slots__ = ('onAnomalyAcknowledged', 'onAnomalyClick')

    def __init__(self, properties=2, commands=2):
        super(AnomaliesMatrixModel, self).__init__(properties=properties, commands=commands)

    def getRecipesList(self):
        return self._getArray(0)

    def setRecipesList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRecipesListType():
        return RecipeModel

    def getIndividualAnomaliesList(self):
        return self._getArray(1)

    def setIndividualAnomaliesList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getIndividualAnomaliesListType():
        return AnomalyModel

    def _initialize(self):
        super(AnomaliesMatrixModel, self)._initialize()
        self._addArrayProperty('recipesList', Array())
        self._addArrayProperty('individualAnomaliesList', Array())
        self.onAnomalyAcknowledged = self._addCommand('onAnomalyAcknowledged')
        self.onAnomalyClick = self._addCommand('onAnomalyClick')
