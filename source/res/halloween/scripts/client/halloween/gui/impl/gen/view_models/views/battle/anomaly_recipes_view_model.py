# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/battle/anomaly_recipes_view_model.py
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.common.anomalies_matrix.anomalies_matrix_model import AnomaliesMatrixModel

class AnomalyRecipesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(AnomalyRecipesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def matrix(self):
        return self._getViewModel(0)

    @staticmethod
    def getMatrixType():
        return AnomaliesMatrixModel

    def getIsVisible(self):
        return self._getBool(1)

    def setIsVisible(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(AnomalyRecipesViewModel, self)._initialize()
        self._addViewModelProperty('matrix', AnomaliesMatrixModel())
        self._addBoolProperty('isVisible', False)
