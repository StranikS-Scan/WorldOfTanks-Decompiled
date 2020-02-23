# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_rewards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattlePassBuyRewardsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(BattlePassBuyRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def nowRewards(self):
        return self._getViewModel(0)

    @property
    def futureRewards(self):
        return self._getViewModel(1)

    def getFromLevel(self):
        return self._getNumber(2)

    def setFromLevel(self, value):
        self._setNumber(2, value)

    def getToLevel(self):
        return self._getNumber(3)

    def setToLevel(self, value):
        self._setNumber(3, value)

    def getStatePackage(self):
        return self._getString(4)

    def setStatePackage(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(BattlePassBuyRewardsViewModel, self)._initialize()
        self._addViewModelProperty('nowRewards', UserListModel())
        self._addViewModelProperty('futureRewards', UserListModel())
        self._addNumberProperty('fromLevel', 0)
        self._addNumberProperty('toLevel', 0)
        self._addStringProperty('statePackage', 'buyState')
