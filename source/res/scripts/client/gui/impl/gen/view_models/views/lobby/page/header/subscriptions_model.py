# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/subscriptions_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.page.header.premium_account_subscription_model import PremiumAccountSubscriptionModel
from gui.impl.gen.view_models.views.lobby.page.header.wot_plus_subscription_model import WotPlusSubscriptionModel

class SubscriptionsModel(ViewModel):
    __slots__ = ('onOpenPremium', 'onOpenWotPlus')

    def __init__(self, properties=4, commands=2):
        super(SubscriptionsModel, self).__init__(properties=properties, commands=commands)

    @property
    def wotPlus(self):
        return self._getViewModel(0)

    @staticmethod
    def getWotPlusType():
        return WotPlusSubscriptionModel

    @property
    def premiumAccount(self):
        return self._getViewModel(1)

    @staticmethod
    def getPremiumAccountType():
        return PremiumAccountSubscriptionModel

    def getIsSteamPlatform(self):
        return self._getBool(2)

    def setIsSteamPlatform(self, value):
        self._setBool(2, value)

    def getIsCnRealm(self):
        return self._getBool(3)

    def setIsCnRealm(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SubscriptionsModel, self)._initialize()
        self._addViewModelProperty('wotPlus', WotPlusSubscriptionModel())
        self._addViewModelProperty('premiumAccount', PremiumAccountSubscriptionModel())
        self._addBoolProperty('isSteamPlatform', False)
        self._addBoolProperty('isCnRealm', False)
        self.onOpenPremium = self._addCommand('onOpenPremium')
        self.onOpenWotPlus = self._addCommand('onOpenWotPlus')
