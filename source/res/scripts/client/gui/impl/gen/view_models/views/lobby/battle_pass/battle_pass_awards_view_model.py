# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_awards_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattlePassAwardsViewModel(CommonViewModel):
    __slots__ = ('onBuyClick',)
    BUY_BATTLE_PASS_REASON = 'buyBattlePassReason'
    BUY_BATTLE_PASS_LEVELS_REASON = 'buyBattlePassLevelsReason'
    DEFAULT_REASON = 'defaultReason'

    def __init__(self, properties=13, commands=2):
        super(BattlePassAwardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(7)

    @property
    def additionalRewards(self):
        return self._getViewModel(8)

    def getPreviousLevel(self):
        return self._getNumber(9)

    def setPreviousLevel(self, value):
        self._setNumber(9, value)

    def getReason(self):
        return self._getString(10)

    def setReason(self, value):
        self._setString(10, value)

    def getIsFinalReward(self):
        return self._getBool(11)

    def setIsFinalReward(self, value):
        self._setBool(11, value)

    def getBadgeTooltipId(self):
        return self._getString(12)

    def setBadgeTooltipId(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(BattlePassAwardsViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addNumberProperty('previousLevel', 0)
        self._addStringProperty('reason', 'defaultReason')
        self._addBoolProperty('isFinalReward', False)
        self._addStringProperty('badgeTooltipId', '')
        self.onBuyClick = self._addCommand('onBuyClick')
