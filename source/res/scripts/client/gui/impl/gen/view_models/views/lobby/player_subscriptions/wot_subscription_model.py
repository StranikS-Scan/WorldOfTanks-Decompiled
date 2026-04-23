# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/player_subscriptions/wot_subscription_model.py
from enum import Enum, IntEnum
from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_model import SubscriptionModel

class WotSubscriptionStateEnum(Enum):
    INACTIVE = 'Inactive'
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'


class WotTierEnum(Enum):
    NONE = 'None'
    CORE = 'Core'
    PRO = 'Pro'


class WotPlusPeriodicityEnum(IntEnum):
    P6MONTHS = 6
    P12MONTHS = 12


class WotSubscriptionModel(SubscriptionModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(WotSubscriptionModel, self).__init__(properties=properties, commands=commands)

    def getWotSubscriptionState(self):
        return WotSubscriptionStateEnum(self._getString(8))

    def setWotSubscriptionState(self, value):
        self._setString(8, value.value)

    def getWotTier(self):
        return WotTierEnum(self._getString(9))

    def setWotTier(self, value):
        self._setString(9, value.value)

    def getSubscriptionPeriodicity(self):
        return WotPlusPeriodicityEnum(self._getNumber(10))

    def setSubscriptionPeriodicity(self, value):
        self._setNumber(10, value.value)

    def getIsButtonHighlighted(self):
        return self._getBool(11)

    def setIsButtonHighlighted(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(WotSubscriptionModel, self)._initialize()
        self._addStringProperty('wotSubscriptionState')
        self._addStringProperty('wotTier')
        self._addNumberProperty('subscriptionPeriodicity')
        self._addBoolProperty('isButtonHighlighted', False)
