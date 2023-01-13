# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/post_progression_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_buy_rewards_view_model import BattlePassBuyRewardsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.package_item import PackageItem

class PostProgressionViewModel(ViewModel):
    __slots__ = ('showRewards', 'onTakeRewardsClick', 'showTankmen', 'onBackClick', 'onPreviewVehicle', 'showVehicle', 'showBuy', 'onClose')
    BUY_STATE = 'buyState'
    REWARDS_STATE = 'rewardsState'
    TANKMEN_STATE = 'tankmenState'
    SELECTABLE_REWARDS_STATE = 'selectableRewardsState'
    FINAL_STATE = 'finalState'

    def __init__(self, properties=5, commands=8):
        super(PostProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def packages(self):
        return self._getViewModel(0)

    @staticmethod
    def getPackagesType():
        return PackageItem

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

    def getNotChosenRewardCount(self):
        return self._getNumber(3)

    def setNotChosenRewardCount(self, value):
        self._setNumber(3, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(4)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(PostProgressionViewModel, self)._initialize()
        self._addViewModelProperty('packages', UserListModel())
        self._addViewModelProperty('rewards', BattlePassBuyRewardsViewModel())
        self._addStringProperty('state', 'buyState')
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addBoolProperty('isChooseRewardsEnabled', True)
        self.showRewards = self._addCommand('showRewards')
        self.onTakeRewardsClick = self._addCommand('onTakeRewardsClick')
        self.showTankmen = self._addCommand('showTankmen')
        self.onBackClick = self._addCommand('onBackClick')
        self.onPreviewVehicle = self._addCommand('onPreviewVehicle')
        self.showVehicle = self._addCommand('showVehicle')
        self.showBuy = self._addCommand('showBuy')
        self.onClose = self._addCommand('onClose')
