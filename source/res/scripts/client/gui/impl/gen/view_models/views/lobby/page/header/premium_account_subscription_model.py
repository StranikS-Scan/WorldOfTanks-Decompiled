# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/premium_account_subscription_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PremiumTypeEnum(Enum):
    NONE = 'None'
    BASIC = 'Basic'
    PLUS = 'Plus'
    VIP = 'VIP'


class PremiumStateEnum(Enum):
    INACTIVE = 'Inactive'
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'


class PremiumAccountSubscriptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PremiumAccountSubscriptionModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return PremiumTypeEnum(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getState(self):
        return PremiumStateEnum(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getExpiryTime(self):
        return self._getNumber(2)

    def setExpiryTime(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PremiumAccountSubscriptionModel, self)._initialize()
        self._addStringProperty('type')
        self._addStringProperty('state')
        self._addNumberProperty('expiryTime', 0)
