# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/frontline/rewards_selection_view.py
from AccountCommands import RES_SUCCESS
from frameworks.wulf import WindowFlags
from helpers import dependency
from gui import SystemMessages
from gui.battle_pass.rewards_sort import getRewardTypesComparator, getRewardsComparator
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.shared.event_dispatcher import showHangar
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.frontline.rewards_selection_view_model import RewardsSelectionViewModel
from gui.impl.lobby.common.selectable_reward_base import SelectableRewardBase
from gui.impl.pub.lobby_window import LobbyWindow
from gui.selectable_reward.common import EpicSelectableRewardManager
from gui.sounds.filters import switchHangarOverlaySoundFilter
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons
from uilogging.epic_battle.loggers import EpicBattleTooltipLogger
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

class RewardsSelectionView(SelectableRewardBase):
    __slots__ = ('__onRewardsReceivedCallback', '__onCloseCallback', '__onLoadedCallback', '__isViewLoaded', '__uiEpicBattleLogger', '__isAutoDestroyWindowsOnReceivedRewards')
    _helper = EpicSelectableRewardManager
    _epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, onRewardsReceivedCallback=None, onCloseCallback=None, onLoadedCallback=None, isAutoDestroyWindowsOnReceivedRewards=True):
        self.__onRewardsReceivedCallback = onRewardsReceivedCallback
        self.__onCloseCallback = onCloseCallback
        self.__onLoadedCallback = onLoadedCallback
        self.__isViewLoaded = False
        self.__isAutoDestroyWindowsOnReceivedRewards = isAutoDestroyWindowsOnReceivedRewards
        self.__uiEpicBattleLogger = EpicBattleTooltipLogger()
        super(RewardsSelectionView, self).__init__(R.views.lobby.frontline.RewardsSelectionView(), self._helper.getAvailableSelectableBonuses(), RewardsSelectionViewModel)

    def _getReceivedRewards(self, rewardName):
        pass

    @property
    def viewModel(self):
        return super(RewardsSelectionView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(RewardsSelectionView, self)._initialize(*args, **kwargs)
        self._epicController.onUpdated += self._onEpicUpdate
        switchHangarOverlaySoundFilter(on=True)
        self.__uiEpicBattleLogger.initialize(EpicBattleLogKeys.REWARDS_SELECTION_VIEW.value, skipAdditionalInfoTooltips=(TOOLTIPS_CONSTANTS.EPIC_BATTLE_INSTRUCTION_TOOLTIP,))

    def _onLoading(self, *args, **kwargs):
        super(RewardsSelectionView, self)._onLoading(*args, **kwargs)
        self.viewModel.onLoadedView += self.__onViewLoaded

    def _finalize(self):
        self.__safeCall(self.__onCloseCallback)
        switchHangarOverlaySoundFilter(on=False)
        self._epicController.onUpdated -= self._onEpicUpdate
        self.viewModel.onLoadedView -= self.__onViewLoaded
        self.__uiEpicBattleLogger.reset()
        super(RewardsSelectionView, self)._finalize()

    def _onOkClick(self):
        super(RewardsSelectionView, self)._onOkClick()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, EpicBattleLogButtons.REWARDS_SELECTION_CONFIRM.value, EpicBattleLogKeys.REWARDS_SELECTION_VIEW.value)
        self.destroyWindow()

    def _onCloseClick(self):
        super(RewardsSelectionView, self)._onCloseClick()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, EpicBattleLogButtons.REWARDS_SELECTION_CLOSE.value, EpicBattleLogKeys.REWARDS_SELECTION_VIEW.value)

    def _onEpicUpdate(self, diff, *args):
        if 'isEnabled' in diff and not diff['isEnabled']:
            self.destroyWindow()
            showHangar()

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
            SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.battlePass.rewardChoice.error()), type=SystemMessages.SM_TYPE.Error)
        if self.__isAutoDestroyWindowsOnReceivedRewards:
            self.destroyWindow()

    def __onViewLoaded(self):
        if not self.__isViewLoaded:
            self.__safeCall(self.__onLoadedCallback)
            self.__isViewLoaded = True

    @staticmethod
    def __safeCall(callback, *args, **kwargs):
        if callable(callback):
            callback(*args, **kwargs)


class RewardsSelectionWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, onRewardsReceivedCallback=None, onCloseCallback=None, onLoadedCallback=None, isAutoDestroyWindowsOnReceivedRewards=True):
        super(RewardsSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RewardsSelectionView(onRewardsReceivedCallback, onCloseCallback, onLoadedCallback, isAutoDestroyWindowsOnReceivedRewards))
