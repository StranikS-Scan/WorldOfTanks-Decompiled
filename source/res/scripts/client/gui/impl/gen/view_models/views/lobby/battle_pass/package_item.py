# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/package_item.py
from frameworks.wulf import ViewModel

class PackageItem(ViewModel):
    __slots__ = ()
    BATTLE_PASS_TYPE = 'battlePassType'
    ANY_LEVELS_TYPE = 'anyLevelsType'
    SHOP_OFFER_TYPE = 'shopOfferType'

    def __init__(self, properties=6, commands=0):
        super(PackageItem, self).__init__(properties=properties, commands=commands)

    def getPackageID(self):
        return self._getNumber(0)

    def setPackageID(self, value):
        self._setNumber(0, value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getIsLocked(self):
        return self._getBool(2)

    def setIsLocked(self, value):
        self._setBool(2, value)

    def getIsBought(self):
        return self._getBool(3)

    def setIsBought(self, value):
        self._setBool(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getChapter(self):
        return self._getNumber(5)

    def setChapter(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(PackageItem, self)._initialize()
        self._addNumberProperty('packageID', 0)
        self._addNumberProperty('price', 0)
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('isBought', False)
        self._addStringProperty('type', '')
        self._addNumberProperty('chapter', 0)
