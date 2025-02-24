# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_rewards_selection_view.py
from functools import partial
from AccountCommands import RES_SUCCESS
from frameworks.wulf import WindowFlags
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_rewards_selection_view_model import PersonalMissionsRewardsSelectionViewModel
from gui.impl.lobby.common.rewards_sort import getRewardsComparator, getRewardTypesComparator
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.pub.lobby_window import LobbyWindow
from gui.selectable_reward.common import PersonalMissionsSelectableRewardManager
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsRewardsView
from gui.server_events.pm3_constants import SOUNDS

class PersonalMissionsRewardsSelectionView(SelectableRewardBase):
    __slots__ = ('__questId', '__onRewardsReceivedCallback', '__onCloseCallback')
    __battlePassController = dependency.descriptor(IBattlePassController)
    _helper = PersonalMissionsSelectableRewardManager

    def __init__(self, questId=0, onRewardsReceivedCallback=None, onCloseCallback=None):
        self.__questId = int(questId)
        self.__onRewardsReceivedCallback = showPersonalMissionsRewardsView if not onRewardsReceivedCallback else onRewardsReceivedCallback
        self.__onCloseCallback = onCloseCallback
        super(PersonalMissionsRewardsSelectionView, self).__init__(R.views.lobby.personal_missions.PersonalMissionsRewardsSelectionView(), self._helper.getAvailableSelectableBonuses(partial(_isValidReward, self.__questId)), PersonalMissionsRewardsSelectionViewModel)

    def _getReceivedRewards(self, rewardName):
        pass

    @property
    def viewModel(self):
        return super(PersonalMissionsRewardsSelectionView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsRewardsSelectionView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setQuestId(self.__questId)
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_ON)

    def _finalize(self):
        self.__safeCall(self.__onCloseCallback)
        super(PersonalMissionsRewardsSelectionView, self)._finalize()

    def _getTypesComparator(self):
        return getRewardTypesComparator()

    def _getItemsComparator(self, tabName):
        return getRewardsComparator(tabName)

    def _processReceivedRewards(self, result):
        if result.success and result.auxData:
            successRewards = result.auxData.get(RES_SUCCESS, {})
            if successRewards:
                self.__safeCall(self.__onRewardsReceivedCallback, self.__questId, successRewards)
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.battlePass.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error)
        self.destroyWindow()

    @staticmethod
    def __safeCall(callback, *args, **kwargs):
        if callable(callback):
            callback(*args, **kwargs)

    def _onCloseClick(self):
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_OFF)
        super(PersonalMissionsRewardsSelectionView, self)._onCloseClick()


class PersonalMissionsRewardsSelectionWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, questId=0, onRewardsReceivedCallback=None, onCloseCallback=None):
        super(PersonalMissionsRewardsSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PersonalMissionsRewardsSelectionView(questId, onRewardsReceivedCallback, onCloseCallback))


def _isValidReward(questId, tokenID):
    if not questId:
        return True
    tokenQuestID = tokenID.split(':')[-1]
    return int(tokenQuestID) == questId
