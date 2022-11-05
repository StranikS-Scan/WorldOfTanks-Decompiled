# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/kpi_equip_level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.kpi_equip_level_data_model import KpiEquipLevelDataModel

class KpiEquipLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(KpiEquipLevelModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getArray(1)

    def setValue(self, value):
        self._setArray(1, value)

    @staticmethod
    def getValueType():
        return KpiEquipLevelDataModel

    def _initialize(self):
        super(KpiEquipLevelModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addArrayProperty('value', Array())
