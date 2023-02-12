# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_level_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_confirm_any_number_view_model import BattlePassBuyConfirmAnyNumberViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_rewards_view_model import BattlePassBuyRewardsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageItem

class BattlePassBuyLevelViewModel(ViewModel):
    __slots__ = ('onBackClick', 'showConfirm', 'showConfirmAny', 'showRewards')
    CONFIRM_ANY_NUMBER_STATE = 'confirmAnyNumberState'
    REWARDS_STATE = 'rewardsState'

    def __init__(self, properties=5, commands=4):
        super(BattlePassBuyLevelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def packages(self):
        return self._getViewModel(0)

    @staticmethod
    def getPackagesType():
        return PackageItem

    @property
    def confirmAnyNumber(self):
        return self._getViewModel(1)

    @staticmethod
    def getConfirmAnyNumberType():
        return BattlePassBuyConfirmAnyNumberViewModel

    @property
    def rewards(self):
        return self._getViewModel(2)

    @staticmethod
    def getRewardsType():
        return BattlePassBuyRewardsViewModel

    def getState(self):
        return self._getString(3)

    def setState(self, value):
        self._setString(3, value)

    def getIsWalletAvailable(self):
        return self._getBool(4)

    def setIsWalletAvailable(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BattlePassBuyLevelViewModel, self)._initialize()
        self._addViewModelProperty('packages', UserListModel())
        self._addViewModelProperty('confirmAnyNumber', BattlePassBuyConfirmAnyNumberViewModel())
        self._addViewModelProperty('rewards', BattlePassBuyRewardsViewModel())
        self._addStringProperty('state', 'confirmAnyNumberState')
        self._addBoolProperty('isWalletAvailable', False)
        self.onBackClick = self._addCommand('onBackClick')
        self.showConfirm = self._addCommand('showConfirm')
        self.showConfirmAny = self._addCommand('showConfirmAny')
        self.showRewards = self._addCommand('showRewards')
