# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/sub_views/rewards_view.py
from helpers import dependency
from battle_pass_common import BattlePassState
from frameworks.wulf import ViewFlags, ViewSettings
from frontline.gui.frontline_bonus_packers import packBonusModelAndTooltipData
from frontline.gui.frontline_helpers import geFrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.rewards_view_model import RewardsViewModel
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showEpicRewardsSelectionWindow, showFrontlineAwards
from skeletons.gui.game_control import IEpicBattleMetaGameController, IBattlePassController
from skeletons.gui.shared import IItemsCache
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons
from uilogging.epic_battle.loggers import EpicBattleLogger

class RewardsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ('__tooltipItems', '__frontlineLevel', '__uiEpicBattleLogger', '__rewardsSelectionWindow', '__rewardSelectionLogged', '__parentView')

    def __init__(self, layoutID=R.views.frontline.lobby.RewardsView(), parentView=None, **kwargs):
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, RewardsViewModel())
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__frontlineLevel, _ = self.__epicController.getPlayerLevelInfo()
        self.__uiEpicBattleLogger = EpicBattleLogger()
        self.__rewardsSelectionWindow = None
        self.__rewardSelectionLogged = False
        self.__parentView = parentView
        super(RewardsView, self).__init__(settings)
        return

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipItems.get(tooltipId) if tooltipId else None

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RewardsView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    @property
    def viewModel(self):
        return super(RewardsView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClaimRewards, self.__onClaimRewards), (self.__epicController.onUpdated, self.__onEpicUpdate))

    def _fillModel(self):
        mergedLvlData = self.__epicController.getMergedLevelRewards()
        with self.viewModel.transaction() as vm:
            state = self.__battlePassController.getState()
            self._updateFrontlineState(vm)
            vm.setIsBattlePassComplete(state == BattlePassState.COMPLETED)
            vm.setFrontlineLevel(self.__frontlineLevel)
            vm.setSelectableRewardsCount(self.__epicController.getNotChosenRewardCount())
            rewardList = vm.getRewards()
            rewardList.clear()
            for startLvl, endLvl, bonuses in mergedLvlData:
                lvlRangeModel = vm.getRewardsType()()
                lvlRangeModel.setLvlStart(startLvl)
                lvlRangeModel.setLvlEnd(endLvl)
                lvlRewardList = lvlRangeModel.getRewards()
                packBonusModelAndTooltipData(bonuses, lvlRewardList, self.__tooltipItems)
                rewardList.addViewModel(lvlRangeModel)

        rewardList.invalidate()

    def _updateFrontlineState(self, model):
        state, _, _ = geFrontlineState()
        model.setFrontlineState(state.value)

    def _onLoading(self, *args, **kwargs):
        super(RewardsView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def __onClaimRewards(self):
        rewards = []
        currentScreen = EpicBattleLogKeys.REWARDS_VIEW.value

        def _logRewardSelectionClosed():
            if not self.__rewardSelectionLogged:
                self.__rewardSelectionLogged = True
                self.__uiEpicBattleLogger.stopAction(EpicBattleLogActions.VIEW_WATCHED.value, EpicBattleLogKeys.REWARDS_SELECTION_VIEW.value, currentScreen)

        def _onAwardsAnimationEnded():
            if self.__rewardsSelectionWindow:
                self.__rewardsSelectionWindow.destroy()

        def _onAwardsClosed():
            self.__uiEpicBattleLogger.stopAction(EpicBattleLogActions.VIEW_WATCHED.value, EpicBattleLogKeys.AWARDS_VIEW.value, currentScreen)

        def _onRewardReceived(rs):
            rewards.extend(rs)
            self._fillModel()
            if rewards:
                _logRewardSelectionClosed()
                self.__uiEpicBattleLogger.startAction(EpicBattleLogActions.VIEW_WATCHED.value)
                showFrontlineAwards(rewards, _onAwardsClosed, _onAwardsAnimationEnded)
            if self.__parentView:
                self.__parentView.updateTabNotifications()

        self.__uiEpicBattleLogger.startAction(EpicBattleLogActions.VIEW_WATCHED.value)
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.REWARDS.value, parentScreen=currentScreen)
        self.__rewardsSelectionWindow = showEpicRewardsSelectionWindow(_onRewardReceived, _logRewardSelectionClosed, isAutoDestroyWindowsOnReceivedRewards=False)

    def __onEpicUpdate(self, diff):
        if 'metaLevel' in diff:
            newLevel, _ = diff['metaLevel']
            if newLevel is not self.__frontlineLevel:
                self.__frontlineLevel = newLevel
                self._fillModel()
        if 'seasons' in diff:
            with self.viewModel.transaction() as tx:
                self._updateFrontlineState(tx)
