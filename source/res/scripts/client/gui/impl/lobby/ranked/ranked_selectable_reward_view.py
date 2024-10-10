# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_selectable_reward_view.py
from functools import partial
import typing
from AccountCommands import RES_SUCCESS
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_selectable_reward_view_model import RankedSelectableRewardViewModel
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.selectable_reward.common import RankedSelectableRewardManager
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.event_dispatcher import showRankedYearAwardWindow
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
if typing.TYPE_CHECKING:
    from gui.SystemMessages import ResultMsg

class RankedSelectableRewardView(SelectableRewardBase):
    __slots__ = ('__allRewards', '__points')
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __REWARDS_ORDER = ['deluxImprovedVentilation',
     'deluxAimingStabilizer',
     'deluxRammer',
     'deluxEnhancedAimDrives',
     'deluxCoatedOptics',
     'deluxImprovedConfiguration',
     'deluxeTurbocharger',
     'deluxeExtraHealthReserve']
    _helper = RankedSelectableRewardManager

    def __init__(self, rankID):
        super(RankedSelectableRewardView, self).__init__(R.views.lobby.ranked.RankedSelectableRewardView(), self._helper.getAvailableSelectableBonuses(partial(_isValidReward, rankID)), RankedSelectableRewardViewModel)
        self.__allRewards = {}
        self.__points = 0
        completedYearQuest = self.__rankedController.getCompletedYearQuest()
        if completedYearQuest is not None:
            self.__points = next(completedYearQuest.iterkeys(), 0)
        return

    @property
    def viewModel(self):
        return super(RankedSelectableRewardView, self).getViewModel()

    def _processReceivedRewards(self, result):
        receivedRewards = result.auxData[RES_SUCCESS]
        isFirstShow = bool(self.__allRewards)
        self.__allRewards = getMergedBonusesFromDicts([self.__allRewards, receivedRewards])
        self.__tryToShowRewardsWindow(not isFirstShow)
        self.destroyWindow()

    def _getItemsComparator(self, _):
        return self.__rewardsComparator

    def __tryToShowRewardsWindow(self, showRemainedSelection=False):
        if self.__allRewards:
            showRankedYearAwardWindow(self.__allRewards, self.__points, True, showRemainedSelection=showRemainedSelection)

    def __rewardsComparator(self, reward1, reward2):
        defaultKey = len(self.__REWARDS_ORDER)
        rewardsList = self.__REWARDS_ORDER
        key1 = rewardsList.index(reward1[0]) if reward1[0] in rewardsList else defaultKey
        key2 = rewardsList.index(reward2[0]) if reward2[0] in rewardsList else defaultKey
        return cmp(key1, key2)


class RankedSelectableRewardWindow(LobbyNotificationWindow):

    def __init__(self, rankID=None):
        super(RankedSelectableRewardWindow, self).__init__(content=RankedSelectableRewardView(rankID), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)


def _isValidReward(rankID, tokenID):
    tokenRank = tokenID.split(':')[-1]
    return not rankID or int(tokenRank) == rankID
