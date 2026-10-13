# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/wot_plus_subscription_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_bonus_model import WotPlusSubscriptionBonusModel

class WotPlusTypeEnum(Enum):
    NONE = 'None'
    CORE = 'Core'
    PRO = 'Pro'


class WotPlusStateEnum(Enum):
    INACTIVE = 'Inactive'
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'


class WotPlusPeriodicityEnum(IntEnum):
    P6MONTHS = 6
    P12MONTHS = 12


class WotPlusSubscriptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(WotPlusSubscriptionModel, self).__init__(properties=properties, commands=commands)

    def getIsWotPlusEnabled(self):
        return self._getBool(0)

    def setIsWotPlusEnabled(self, value):
        self._setBool(0, value)

    def getIsCrossPlatformCore(self):
        return self._getBool(1)

    def setIsCrossPlatformCore(self, value):
        self._setBool(1, value)

    def getType(self):
        return WotPlusTypeEnum(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getState(self):
        return WotPlusStateEnum(self._getString(3))

    def setState(self, value):
        self._setString(3, value.value)

    def getPeriodicity(self):
        return WotPlusPeriodicityEnum(self._getNumber(4))

    def setPeriodicity(self, value):
        self._setNumber(4, value.value)

    def getExpiryTime(self):
        return self._getNumber(5)

    def setExpiryTime(self, value):
        self._setNumber(5, value)

    def getBenefits(self):
        return self._getArray(6)

    def setBenefits(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBenefitsType():
        return WotPlusSubscriptionBonusModel

    def getProBenefits(self):
        return self._getArray(7)

    def setProBenefits(self, value):
        self._setArray(7, value)

    @staticmethod
    def getProBenefitsType():
        return WotPlusSubscriptionBonusModel

    def _initialize(self):
        super(WotPlusSubscriptionModel, self)._initialize()
        self._addBoolProperty('isWotPlusEnabled', True)
        self._addBoolProperty('isCrossPlatformCore', False)
        self._addStringProperty('type')
        self._addStringProperty('state')
        self._addNumberProperty('periodicity')
        self._addNumberProperty('expiryTime', 0)
        self._addArrayProperty('benefits', Array())
        self._addArrayProperty('proBenefits', Array())
