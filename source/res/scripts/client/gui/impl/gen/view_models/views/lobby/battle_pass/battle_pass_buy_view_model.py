# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_rewards_view_model import BattlePassBuyRewardsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.buy_chapter_model import BuyChapterModel
from gui.impl.gen.view_models.views.lobby.battle_pass.buy_package_view_model import BuyPackageViewModel

class BattlePassBuyViewModel(ViewModel):
    __slots__ = ('onShopOfferClick', 'onCloseClick', 'onBuyClick', 'onShowRewardsClick', 'onChangePurchaseWithLevels')
    BUY_STATE = 'buyState'
    REWARDS_STATE = 'rewardsState'

    def __init__(self, properties=8, commands=5):
        super(BattlePassBuyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def package(self):
        return self._getViewModel(0)

    @staticmethod
    def getPackageType():
        return BuyPackageViewModel

    @property
    def rewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardsType():
        return BattlePassBuyRewardsViewModel

    def getState(self):
        return self._getString(2)

    def setState(self, value):
        self._setString(2, value)

    def getIsWalletAvailable(self):
        return self._getBool(3)

    def setIsWalletAvailable(self, value):
        self._setBool(3, value)

    def getIsShopOfferAvailable(self):
        return self._getBool(4)

    def setIsShopOfferAvailable(self, value):
        self._setBool(4, value)

    def getShopOfferDiscount(self):
        return self._getNumber(5)

    def setShopOfferDiscount(self, value):
        self._setNumber(5, value)

    def getIsLogoBg(self):
        return self._getBool(6)

    def setIsLogoBg(self, value):
        self._setBool(6, value)

    def getChapters(self):
        return self._getArray(7)

    def setChapters(self, value):
        self._setArray(7, value)

    @staticmethod
    def getChaptersType():
        return BuyChapterModel

    def _initialize(self):
        super(BattlePassBuyViewModel, self)._initialize()
        self._addViewModelProperty('package', BuyPackageViewModel())
        self._addViewModelProperty('rewards', BattlePassBuyRewardsViewModel())
        self._addStringProperty('state', 'buyState')
        self._addBoolProperty('isWalletAvailable', False)
        self._addBoolProperty('isShopOfferAvailable', False)
        self._addNumberProperty('shopOfferDiscount', 0)
        self._addBoolProperty('isLogoBg', False)
        self._addArrayProperty('chapters', Array())
        self.onShopOfferClick = self._addCommand('onShopOfferClick')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onShowRewardsClick = self._addCommand('onShowRewardsClick')
        self.onChangePurchaseWithLevels = self._addCommand('onChangePurchaseWithLevels')
