# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/rewards_selection_view.py
from functools import partial
from AccountCommands import RES_SUCCESS
from frameworks.wulf import WindowFlags
from gui import SystemMessages
from gui.battle_pass.rewards_sort import getRewardTypesComparator, getRewardsComparator
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.rewards_selection_view_model import RewardsSelectionViewModel
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.pub.lobby_window import LobbyWindow
from gui.selectable_reward.common import BattlePassSelectableRewardManager
from gui.shared.notifications import NotificationPriorityLevel
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class RewardsSelectionView(SelectableRewardBase):
    __slots__ = ('__chapterID', '__level', '__onRewardsReceivedCallback', '__onCloseCallback')
    __battlePass = dependency.descriptor(IBattlePassController)
    _helper = BattlePassSelectableRewardManager

    def __init__(self, chapterID=0, level=0, onRewardsReceivedCallback=None, onCloseCallback=None):
        self.__chapterID = int(chapterID)
        self.__level = int(level)
        self.__onRewardsReceivedCallback = onRewardsReceivedCallback
        self.__onCloseCallback = onCloseCallback
        super(RewardsSelectionView, self).__init__(R.views.lobby.battle_pass.RewardsSelectionView(), self._helper.getAvailableSelectableBonuses(partial(_isValidReward, self.__chapterID, self.__level)), RewardsSelectionViewModel)

    def _getReceivedRewards(self, rewardName):
        pass

    @property
    def viewModel(self):
        return super(RewardsSelectionView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RewardsSelectionView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setChapterID(self.__chapterID)
            tx.setLevel(self.__level)
            tx.setIsExtra(self.__battlePass.isExtraChapter(self.__chapterID))
            tx.setIsHoliday(self.__battlePass.isHoliday())

    def _initialize(self, *args, **kwargs):
        super(RewardsSelectionView, self)._initialize(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        self.__safeCall(self.__onCloseCallback)
        switchHangarOverlaySoundFilter(on=False)
        super(RewardsSelectionView, self)._finalize()

    def _getTypesComparator(self):
        return getRewardTypesComparator()

    def _getItemsComparator(self, tabName):
        return getRewardsComparator(tabName)

    def _processReceivedRewards(self, result):
        if result.success and result.auxData:
            successRewards = result.auxData.get(RES_SUCCESS, {})
            if successRewards:
                rewardsGenerator = ({group: rewards} for group, rewards in successRewards.iteritems())
                self.__safeCall(self.__onRewardsReceivedCallback, rewardsGenerator)
        else:
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.battlePass.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.HIGH)
        self.destroyWindow()

    @staticmethod
    def __safeCall(callback, *args, **kwargs):
        if callable(callback):
            callback(*args, **kwargs)


class RewardsSelectionWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, chapterID=0, level=0, onRewardsReceivedCallback=None, onCloseCallback=None):
        super(RewardsSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RewardsSelectionView(chapterID, level, onRewardsReceivedCallback, onCloseCallback))


def _isValidReward(chapterID, level, tokenID):
    if not chapterID:
        return True
    tokenChapterID, tokenLevel = tokenID.split(':')[-2:]
    return int(tokenChapterID) == chapterID and (not level or int(tokenLevel) == level)
