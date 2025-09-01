# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/service_records_model.py
from frameworks.wulf import ViewModel

class ServiceRecordsModel(ViewModel):
    __slots__ = ()
    IRON = 'iron'
    BRONZE = 'bronze'
    SILVER = 'silver'
    GOLD = 'gold'
    ENAMEL = 'enamel'
    MAXIMUM = 'prestige'
    UNDEFINED = 'undefined'

    def __init__(self, properties=10, commands=0):
        super(ServiceRecordsModel, self).__init__(properties=properties, commands=commands)

    def getPrestigeLevel(self):
        return self._getNumber(0)

    def setPrestigeLevel(self, value):
        self._setNumber(0, value)

    def getPrestigeGrade(self):
        return self._getNumber(1)

    def setPrestigeGrade(self, value):
        self._setNumber(1, value)

    def getPrestigeType(self):
        return self._getString(2)

    def setPrestigeType(self, value):
        self._setString(2, value)

    def getPrestigeXp(self):
        return self._getNumber(3)

    def setPrestigeXp(self, value):
        self._setNumber(3, value)

    def getPrestigeXpNextLevel(self):
        return self._getNumber(4)

    def setPrestigeXpNextLevel(self, value):
        self._setNumber(4, value)

    def getMarksOnGun(self):
        return self._getNumber(5)

    def setMarksOnGun(self, value):
        self._setNumber(5, value)

    def getMarksOnGunPercentage(self):
        return self._getString(6)

    def setMarksOnGunPercentage(self, value):
        self._setString(6, value)

    def getMarksOfMastery(self):
        return self._getNumber(7)

    def setMarksOfMastery(self, value):
        self._setNumber(7, value)

    def getWinsCount(self):
        return self._getNumber(8)

    def setWinsCount(self, value):
        self._setNumber(8, value)

    def getBattlesCount(self):
        return self._getNumber(9)

    def setBattlesCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(ServiceRecordsModel, self)._initialize()
        self._addNumberProperty('prestigeLevel', -1)
        self._addNumberProperty('prestigeGrade', -1)
        self._addStringProperty('prestigeType', '')
        self._addNumberProperty('prestigeXp', 0)
        self._addNumberProperty('prestigeXpNextLevel', 0)
        self._addNumberProperty('marksOnGun', -1)
        self._addStringProperty('marksOnGunPercentage', '')
        self._addNumberProperty('marksOfMastery', 0)
        self._addNumberProperty('winsCount', 0)
        self._addNumberProperty('battlesCount', 0)
