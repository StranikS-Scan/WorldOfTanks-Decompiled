# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/package_item.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel

class ChapterStates(IntEnum):
    ACTIVE = 0
    PAUSED = 1
    COMPLETED = 2
    NOTSTARTED = 3


class PackageType(IntEnum):
    BATTLEPASS = 0
    ANYLEVELS = 1
    SHOPOFFER = 2


class PackageItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(PackageItem, self).__init__(properties=properties, commands=commands)

    @property
    def compoundPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getCompoundPriceType():
        return UserCompoundPriceModel

    def getPackageID(self):
        return self._getNumber(1)

    def setPackageID(self, value):
        self._setNumber(1, value)

    def getPrice(self):
        return self._getNumber(2)

    def setPrice(self, value):
        self._setNumber(2, value)

    def getIsLocked(self):
        return self._getBool(3)

    def setIsLocked(self, value):
        self._setBool(3, value)

    def getIsBought(self):
        return self._getBool(4)

    def setIsBought(self, value):
        self._setBool(4, value)

    def getType(self):
        return PackageType(self._getNumber(5))

    def setType(self, value):
        self._setNumber(5, value.value)

    def getChapterID(self):
        return self._getNumber(6)

    def setChapterID(self, value):
        self._setNumber(6, value)

    def getChapterState(self):
        return ChapterStates(self._getNumber(7))

    def setChapterState(self, value):
        self._setNumber(7, value.value)

    def getCurrentLevel(self):
        return self._getNumber(8)

    def setCurrentLevel(self, value):
        self._setNumber(8, value)

    def getIsExtra(self):
        return self._getBool(9)

    def setIsExtra(self, value):
        self._setBool(9, value)

    def getExpireTime(self):
        return self._getNumber(10)

    def setExpireTime(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(PackageItem, self)._initialize()
        self._addViewModelProperty('compoundPrice', UserCompoundPriceModel())
        self._addNumberProperty('packageID', 0)
        self._addNumberProperty('price', 0)
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('isBought', False)
        self._addNumberProperty('type')
        self._addNumberProperty('chapterID', 0)
        self._addNumberProperty('chapterState')
        self._addNumberProperty('currentLevel', 0)
        self._addBoolProperty('isExtra', False)
        self._addNumberProperty('expireTime', 0)
