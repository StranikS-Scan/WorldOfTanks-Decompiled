# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_rewards_selection_view.py
from functools import partial
from AccountCommands import RES_SUCCESS
from frameworks.wulf import WindowFlags
from gui import SystemMessages
from gui.battle_pass.rewards_sort import getRewardTypesComparator, getRewardsComparator
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_rewards_selection_view_model import WtEventRewardsSelectionViewModel
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.pub.lobby_window import LobbyWindow
from gui.selectable_reward.common import WTProgressionSelectableRewardManager
from gui.shared.notifications import NotificationPriorityLevel
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from gui.shared.missions.packers.bonus import BonusUIPacker
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPackerMap
from skeletons.gui.game_control import IEventBattlesController
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_item_model import SelectableRewardItemModel
from skeletons.gui.shared import IItemsCache

class WtEventRewardsSelectionView(SelectableRewardBase):
    __slots__ = ('__level', '__onRewardsReceivedCallback', '__onCloseCallback')
    __battlePass = dependency.descriptor(IBattlePassController)
    __gameController = dependency.descriptor(IEventBattlesController)
    _helper = WTProgressionSelectableRewardManager
    _packer = BonusUIPacker(getWtEventBonusPackerMap())
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, level=0, onRewardsReceivedCallback=None, onCloseCallback=None):
        self.__level = int(level)
        self.__onRewardsReceivedCallback = onRewardsReceivedCallback
        self.__onCloseCallback = onCloseCallback
        super(WtEventRewardsSelectionView, self).__init__(R.views.lobby.wt_event.WTEventRewardsSelectionView(), self._helper.getAvailableSelectableBonuses(partial(_isValidReward, self.__level)), WtEventRewardsSelectionViewModel)

    def _getReceivedRewards(self, rewardName):
        pass

    @property
    def viewModel(self):
        return super(WtEventRewardsSelectionView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventRewardsSelectionView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setLevel(self.__level)

    def _initialize(self, *args, **kwargs):
        super(WtEventRewardsSelectionView, self)._initialize(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)

    def _finalize(self):
        self.__safeCall(self.__onCloseCallback)
        self.__gameController.onRewardsUpdated()
        switchHangarOverlaySoundFilter(on=False)
        super(WtEventRewardsSelectionView, self)._finalize()

    def _getTypesComparator(self):
        return getRewardTypesComparator()

    def _getItemsComparator(self, tabName):
        return getRewardsComparator(tabName)

    def _prepareRewardsData(self, tabName):
        tabs = self._getTabs()
        for rewardName, reward in tabs[tabName]['rewards'].iteritems():
            state = SelectableRewardItemModel.STATE_NORMAL
            yield (rewardName, reward, state)

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


class WtEventRewardsSelectionWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, level=0, onRewardsReceivedCallback=None, onCloseCallback=None):
        super(WtEventRewardsSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventRewardsSelectionView(level, onRewardsReceivedCallback, onCloseCallback))


def _isValidReward(level, tokenID):
    _, tokenLevel = tokenID.split(':')[-2:]
    return not level or int(tokenLevel) == level
