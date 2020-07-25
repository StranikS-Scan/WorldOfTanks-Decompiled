# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/trophy_device_confirm_bonus_model.py
from frameworks.wulf import ViewModel

class TrophyDeviceConfirmBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TrophyDeviceConfirmBonusModel, self).__init__(properties=properties, commands=commands)

    def getKpiName(self):
        return self._getString(0)

    def setKpiName(self, value):
        self._setString(0, value)

    def getBaseValue(self):
        return self._getString(1)

    def setBaseValue(self, value):
        self._setString(1, value)

    def getUpgradedValue(self):
        return self._getString(2)

    def setUpgradedValue(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(TrophyDeviceConfirmBonusModel, self)._initialize()
        self._addStringProperty('kpiName', '')
        self._addStringProperty('baseValue', '')
        self._addStringProperty('upgradedValue', '')
