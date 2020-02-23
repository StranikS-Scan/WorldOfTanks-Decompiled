# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/package_item.py
from frameworks.wulf import ViewModel

class PackageItem(ViewModel):
    __slots__ = ()
    BATTLE_PASS_TYPE = 'battlePassType'
    LIMITED_LEVELS_TYPE = 'limitedLevelsType'
    ANY_LEVELS_TYPE = 'anyLevelsType'

    def __init__(self, properties=7, commands=0):
        super(PackageItem, self).__init__(properties=properties, commands=commands)

    def getPackageID(self):
        return self._getNumber(0)

    def setPackageID(self, value):
        self._setNumber(0, value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getLevels(self):
        return self._getNumber(2)

    def setLevels(self, value):
        self._setNumber(2, value)

    def getTimeToUnlock(self):
        return self._getString(3)

    def setTimeToUnlock(self, value):
        self._setString(3, value)

    def getIsLocked(self):
        return self._getBool(4)

    def setIsLocked(self, value):
        self._setBool(4, value)

    def getIsBought(self):
        return self._getBool(5)

    def setIsBought(self, value):
        self._setBool(5, value)

    def getType(self):
        return self._getString(6)

    def setType(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(PackageItem, self)._initialize()
        self._addNumberProperty('packageID', 0)
        self._addNumberProperty('price', 0)
        self._addNumberProperty('levels', 0)
        self._addStringProperty('timeToUnlock', '')
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('isBought', False)
        self._addStringProperty('type', '')
