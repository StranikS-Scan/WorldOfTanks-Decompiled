# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_voting_result_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.final_reward_item_model import FinalRewardItemModel

class BattlePassVotingResultViewModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onVoteClick', 'onBackClick', 'showLocked', 'showNeedVoting', 'showResult')
    LOCKED_STATE = 'lockedState'
    NEED_VOTING_STATE = 'needVotingState'
    RESULT_STATE = 'resultState'

    def __init__(self, properties=7, commands=6):
        super(BattlePassVotingResultViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def finalRewards(self):
        return self._getViewModel(0)

    def getState(self):
        return self._getString(1)

    def setState(self, value):
        self._setString(1, value)

    def getBackBtnLabel(self):
        return self._getString(2)

    def setBackBtnLabel(self, value):
        self._setString(2, value)

    def getBackBtnDescr(self):
        return self._getString(3)

    def setBackBtnDescr(self, value):
        self._setString(3, value)

    def getFailService(self):
        return self._getBool(4)

    def setFailService(self, value):
        self._setBool(4, value)

    def getMaxEpisode(self):
        return self._getNumber(5)

    def setMaxEpisode(self, value):
        self._setNumber(5, value)

    def getIsBattlePassPurchased(self):
        return self._getBool(6)

    def setIsBattlePassPurchased(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(BattlePassVotingResultViewModel, self)._initialize()
        self._addViewModelProperty('finalRewards', UserListModel())
        self._addStringProperty('state', 'lockedState')
        self._addStringProperty('backBtnLabel', '')
        self._addStringProperty('backBtnDescr', '')
        self._addBoolProperty('failService', False)
        self._addNumberProperty('maxEpisode', 0)
        self._addBoolProperty('isBattlePassPurchased', False)
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onVoteClick = self._addCommand('onVoteClick')
        self.onBackClick = self._addCommand('onBackClick')
        self.showLocked = self._addCommand('showLocked')
        self.showNeedVoting = self._addCommand('showNeedVoting')
        self.showResult = self._addCommand('showResult')
