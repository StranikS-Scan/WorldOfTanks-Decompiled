# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/player_subscriptions/subscription_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SubscriptionTypeEnum(Enum):
    WOTSUBSCRIPTION = 'WotSubscription'
    EXTERNALSUBSCRIPTION = 'ExternalSubscription'


class SubscriptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(SubscriptionModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getSubscriptionType(self):
        return SubscriptionTypeEnum(self._getString(3))

    def setSubscriptionType(self, value):
        self._setString(3, value.value)

    def getImageUriSmall(self):
        return self._getString(4)

    def setImageUriSmall(self, value):
        self._setString(4, value)

    def getImageUriMedium(self):
        return self._getString(5)

    def setImageUriMedium(self, value):
        self._setString(5, value)

    def getImageUriLarge(self):
        return self._getString(6)

    def setImageUriLarge(self, value):
        self._setString(6, value)

    def getRefreshTime(self):
        return self._getNumber(7)

    def setRefreshTime(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(SubscriptionModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('subscriptionType')
        self._addStringProperty('imageUriSmall', '')
        self._addStringProperty('imageUriMedium', '')
        self._addStringProperty('imageUriLarge', '')
        self._addNumberProperty('refreshTime', 0)
