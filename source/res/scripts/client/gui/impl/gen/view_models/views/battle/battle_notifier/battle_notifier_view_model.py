# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_notifier/battle_notifier_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class ResultEnum(IntEnum):
    DEFEAT = -1
    DRAW = 0
    VICTORY = 1


class BattleNotifierViewModel(ViewModel):
    __slots__ = ('onResultShown',)

    def __init__(self, properties=9, commands=1):
        super(BattleNotifierViewModel, self).__init__(properties=properties, commands=commands)

    def getBattleResult(self):
        return ResultEnum(self._getNumber(0))

    def setBattleResult(self, value):
        self._setNumber(0, value.value)

    def getBattleStartTime(self):
        return self._getNumber(1)

    def setBattleStartTime(self, value):
        self._setNumber(1, value)

    def getMapName(self):
        return self._getString(2)

    def setMapName(self, value):
        self._setString(2, value)

    def getVehicleName(self):
        return self._getString(3)

    def setVehicleName(self, value):
        self._setString(3, value)

    def getVehicleTier(self):
        return self._getNumber(4)

    def setVehicleTier(self, value):
        self._setNumber(4, value)

    def getVehicleClass(self):
        return self._getString(5)

    def setVehicleClass(self, value):
        self._setString(5, value)

    def getCreditsAmount(self):
        return self._getNumber(6)

    def setCreditsAmount(self, value):
        self._setNumber(6, value)

    def getExperienceAmount(self):
        return self._getNumber(7)

    def setExperienceAmount(self, value):
        self._setNumber(7, value)

    def getCrystalAmount(self):
        return self._getNumber(8)

    def setCrystalAmount(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(BattleNotifierViewModel, self)._initialize()
        self._addNumberProperty('battleResult')
        self._addNumberProperty('battleStartTime', 667004400)
        self._addStringProperty('mapName', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('vehicleTier', 0)
        self._addStringProperty('vehicleClass', '')
        self._addNumberProperty('creditsAmount', 0)
        self._addNumberProperty('experienceAmount', 0)
        self._addNumberProperty('crystalAmount', 0)
        self.onResultShown = self._addCommand('onResultShown')
