# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/tooltips/kpi_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.kpi_value_model import KpiValueModel

class KpiModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(KpiModel, self).__init__(properties=properties, commands=commands)

    def getKpiName(self):
        return self._getString(0)

    def setKpiName(self, value):
        self._setString(0, value)

    def getKpiValues(self):
        return self._getArray(1)

    def setKpiValues(self, value):
        self._setArray(1, value)

    @staticmethod
    def getKpiValuesType():
        return KpiValueModel

    def _initialize(self):
        super(KpiModel, self)._initialize()
        self._addStringProperty('kpiName', '')
        self._addArrayProperty('kpiValues', Array())
