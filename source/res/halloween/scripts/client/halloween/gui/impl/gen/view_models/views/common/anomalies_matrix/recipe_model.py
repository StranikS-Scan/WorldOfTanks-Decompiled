# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/common/anomalies_matrix/recipe_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyModel

class RecipeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RecipeModel, self).__init__(properties=properties, commands=commands)

    def getAnomaliesList(self):
        return self._getArray(0)

    def setAnomaliesList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getAnomaliesListType():
        return AnomalyModel

    def _initialize(self):
        super(RecipeModel, self)._initialize()
        self._addArrayProperty('anomaliesList', Array())
