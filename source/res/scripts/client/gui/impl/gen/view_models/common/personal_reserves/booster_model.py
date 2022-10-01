# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/personal_reserves/booster_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel

class ReserveType(Enum):
    PERSONAL = 'personal'
    CLAN = 'clan'
    EVENT = 'event'


class ReserveState(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    USED = 2


class BoosterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(BoosterModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return UserCompoundPriceModel

    def getBoosterID(self):
        return self._getNumber(1)

    def setBoosterID(self, value):
        self._setNumber(1, value)

    def getReserveType(self):
        return ReserveType(self._getString(2))

    def setReserveType(self, value):
        self._setString(2, value.value)

    def getInactivationTime(self):
        return self._getNumber(3)

    def setInactivationTime(self, value):
        self._setNumber(3, value)

    def getInDepot(self):
        return self._getNumber(4)

    def setInDepot(self, value):
        self._setNumber(4, value)

    def getMinBonus(self):
        return self._getNumber(5)

    def setMinBonus(self, value):
        self._setNumber(5, value)

    def getMaxBonus(self):
        return self._getNumber(6)

    def setMaxBonus(self, value):
        self._setNumber(6, value)

    def getTotalDuration(self):
        return self._getNumber(7)

    def setTotalDuration(self, value):
        self._setNumber(7, value)

    def getIsPremium(self):
        return self._getBool(8)

    def setIsPremium(self, value):
        self._setBool(8, value)

    def getState(self):
        return ReserveState(self._getNumber(9))

    def setState(self, value):
        self._setNumber(9, value.value)

    def getIconId(self):
        return self._getString(10)

    def setIconId(self, value):
        self._setString(10, value)

    def getExpiryTime(self):
        return self._getNumber(11)

    def setExpiryTime(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(BoosterModel, self)._initialize()
        self._addViewModelProperty('price', UserCompoundPriceModel())
        self._addNumberProperty('boosterID', -1)
        self._addStringProperty('reserveType')
        self._addNumberProperty('inactivationTime', -1)
        self._addNumberProperty('inDepot', -1)
        self._addNumberProperty('minBonus', -1)
        self._addNumberProperty('maxBonus', 0)
        self._addNumberProperty('totalDuration', 60)
        self._addBoolProperty('isPremium', False)
        self._addNumberProperty('state')
        self._addStringProperty('iconId', '')
        self._addNumberProperty('expiryTime', 0)
