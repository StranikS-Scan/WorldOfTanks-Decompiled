# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/vehicle_statistic_model.py
from frameworks.wulf import Array, ViewModel

class VehicleStatisticModel(ViewModel):
    __slots__ = ()
    IRON = 'iron'
    BRONZE = 'bronze'
    SILVER = 'silver'
    GOLD = 'gold'
    ENAMEL = 'enamel'
    MAXIMUM = 'prestige'
    UNDEFINED = 'undefined'

    def __init__(self, properties=21, commands=0):
        super(VehicleStatisticModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIntCD(self):
        return self._getNumber(1)

    def setIntCD(self, value):
        self._setNumber(1, value)

    def getInventoryId(self):
        return self._getNumber(2)

    def setInventoryId(self, value):
        self._setNumber(2, value)

    def getXp(self):
        return self._getNumber(3)

    def setXp(self, value):
        self._setNumber(3, value)

    def getStatus(self):
        return self._getString(4)

    def setStatus(self, value):
        self._setString(4, value)

    def getStateLevel(self):
        return self._getString(5)

    def setStateLevel(self, value):
        self._setString(5, value)

    def getElite(self):
        return self._getBool(6)

    def setElite(self, value):
        self._setBool(6, value)

    def getBonusMultiplier(self):
        return self._getNumber(7)

    def setBonusMultiplier(self, value):
        self._setNumber(7, value)

    def getMastery(self):
        return self._getNumber(8)

    def setMastery(self, value):
        self._setNumber(8, value)

    def getBattlesCount(self):
        return self._getNumber(9)

    def setBattlesCount(self, value):
        self._setNumber(9, value)

    def getWinsCount(self):
        return self._getNumber(10)

    def setWinsCount(self, value):
        self._setNumber(10, value)

    def getTooltipID(self):
        return self._getNumber(11)

    def setTooltipID(self, value):
        self._setNumber(11, value)

    def getPrestigeLevel(self):
        return self._getNumber(12)

    def setPrestigeLevel(self, value):
        self._setNumber(12, value)

    def getPrestigeGrade(self):
        return self._getNumber(13)

    def setPrestigeGrade(self, value):
        self._setNumber(13, value)

    def getPrestigeType(self):
        return self._getString(14)

    def setPrestigeType(self, value):
        self._setString(14, value)

    def getFromWotPlus(self):
        return self._getBool(15)

    def setFromWotPlus(self, value):
        self._setBool(15, value)

    def getBpSpecial(self):
        return self._getBool(16)

    def setBpSpecial(self, value):
        self._setBool(16, value)

    def getMaxBpScore(self):
        return self._getNumber(17)

    def setMaxBpScore(self, value):
        self._setNumber(17, value)

    def getBpProgress(self):
        return self._getNumber(18)

    def setBpProgress(self, value):
        self._setNumber(18, value)

    def getNumberOfCrystalEarned(self):
        return self._getArray(19)

    def setNumberOfCrystalEarned(self, value):
        self._setArray(19, value)

    @staticmethod
    def getNumberOfCrystalEarnedType():
        return int

    def getOwn3DStyle(self):
        return self._getBool(20)

    def setOwn3DStyle(self, value):
        self._setBool(20, value)

    def _initialize(self):
        super(VehicleStatisticModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('intCD', 0)
        self._addNumberProperty('inventoryId', 0)
        self._addNumberProperty('xp', 0)
        self._addStringProperty('status', 'none')
        self._addStringProperty('stateLevel', '')
        self._addBoolProperty('elite', False)
        self._addNumberProperty('bonusMultiplier', -1)
        self._addNumberProperty('mastery', 0)
        self._addNumberProperty('battlesCount', 0)
        self._addNumberProperty('winsCount', 0)
        self._addNumberProperty('tooltipID', -1)
        self._addNumberProperty('prestigeLevel', -1)
        self._addNumberProperty('prestigeGrade', -1)
        self._addStringProperty('prestigeType', '')
        self._addBoolProperty('fromWotPlus', False)
        self._addBoolProperty('bpSpecial', False)
        self._addNumberProperty('maxBpScore', -1)
        self._addNumberProperty('bpProgress', -1)
        self._addArrayProperty('numberOfCrystalEarned', Array())
        self._addBoolProperty('own3DStyle', False)
