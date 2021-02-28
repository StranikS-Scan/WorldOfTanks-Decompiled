# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_confirm_any_number_view_model import BattlePassBuyConfirmAnyNumberViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_confirm_view_model import BattlePassBuyConfirmViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_rewards_view_model import BattlePassBuyRewardsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageItem

class BattlePassBuyViewModel(ViewModel):
    __slots__ = ('onBackClick', 'choosePackage', 'showConfirm', 'showConfirmAny', 'showRewards', 'onShopOfferClick')
    BUY_STATE = 'buyState'
    CONFIRM_STATE = 'confirmState'
    CONFIRM_ANY_NUMBER_STATE = 'confirmAnyNumberState'
    REWARDS_STATE = 'rewardsState'

    def __init__(self, properties=8, commands=6):
        super(BattlePassBuyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def packages(self):
        return self._getViewModel(0)

    @property
    def confirm(self):
        return self._getViewModel(1)

    @property
    def confirmAnyNumber(self):
        return self._getViewModel(2)

    @property
    def rewards(self):
        return self._getViewModel(3)

    def getState(self):
        return self._getString(4)

    def setState(self, value):
        self._setString(4, value)

    def getIsWalletAvailable(self):
        return self._getBool(5)

    def setIsWalletAvailable(self, value):
        self._setBool(5, value)

    def getIsShopOfferAvailable(self):
        return self._getBool(6)

    def setIsShopOfferAvailable(self, value):
        self._setBool(6, value)

    def getShopOfferDiscount(self):
        return self._getNumber(7)

    def setShopOfferDiscount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(BattlePassBuyViewModel, self)._initialize()
        self._addViewModelProperty('packages', UserListModel())
        self._addViewModelProperty('confirm', BattlePassBuyConfirmViewModel())
        self._addViewModelProperty('confirmAnyNumber', BattlePassBuyConfirmAnyNumberViewModel())
        self._addViewModelProperty('rewards', BattlePassBuyRewardsViewModel())
        self._addStringProperty('state', 'buyState')
        self._addBoolProperty('isWalletAvailable', False)
        self._addBoolProperty('isShopOfferAvailable', False)
        self._addNumberProperty('shopOfferDiscount', 0)
        self.onBackClick = self._addCommand('onBackClick')
        self.choosePackage = self._addCommand('choosePackage')
        self.showConfirm = self._addCommand('showConfirm')
        self.showConfirmAny = self._addCommand('showConfirmAny')
        self.showRewards = self._addCommand('showRewards')
        self.onShopOfferClick = self._addCommand('onShopOfferClick')
