# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/subscriptions_model.py
from frameworks.wulf import ViewModel

class SubscriptionsModel(ViewModel):
    __slots__ = ('onOpenPremium', 'onOpenWotPlus')
    NONE = 0
    BASIC = 1
    PLUS = 2
    VIP = 3
    INACTIVE = 0
    ACTIVE = 1
    CANCELLED = 2

    def __init__(self, properties=6, commands=2):
        super(SubscriptionsModel, self).__init__(properties=properties, commands=commands)

    def getPremiumSubscriptionEnabled(self):
        return self._getBool(0)

    def setPremiumSubscriptionEnabled(self, value):
        self._setBool(0, value)

    def getActivePremiumType(self):
        return self._getNumber(1)

    def setActivePremiumType(self, value):
        self._setNumber(1, value)

    def getActivePremiumExpiryTime(self):
        return self._getNumber(2)

    def setActivePremiumExpiryTime(self, value):
        self._setNumber(2, value)

    def getWotPlusEnabled(self):
        return self._getBool(3)

    def setWotPlusEnabled(self, value):
        self._setBool(3, value)

    def getWotPlusState(self):
        return self._getNumber(4)

    def setWotPlusState(self, value):
        self._setNumber(4, value)

    def getWotPlusExpiryTime(self):
        return self._getNumber(5)

    def setWotPlusExpiryTime(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(SubscriptionsModel, self)._initialize()
        self._addBoolProperty('premiumSubscriptionEnabled', False)
        self._addNumberProperty('activePremiumType', 0)
        self._addNumberProperty('activePremiumExpiryTime', 0)
        self._addBoolProperty('wotPlusEnabled', False)
        self._addNumberProperty('wotPlusState', 0)
        self._addNumberProperty('wotPlusExpiryTime', 0)
        self.onOpenPremium = self._addCommand('onOpenPremium')
        self.onOpenWotPlus = self._addCommand('onOpenWotPlus')
