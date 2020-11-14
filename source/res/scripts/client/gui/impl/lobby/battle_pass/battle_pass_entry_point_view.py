# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_entry_point_view.py
import random
from PlayerEvents import g_playerEvents
from battle_pass_common import BattlePassState
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.BattlePassEntryPointMeta import BattlePassEntryPointMeta
from gui.battle_pass.battle_pass_helpers import isNeededToVote, getSeasonHistory, getLevelFromStats
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_entry_point_view_model import BattlePassEntryPointViewModel
from gui.impl.lobby.battle_pass.tooltips.battle_pass_chose_winner_tooltip_view import BattlePassChoseWinnerTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view import BattlePassNotStartedTooltipView
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache

class BattlePassEntryPointStates(object):

    def __init__(self):
        self.isFirstShow = True
        self.isBPBought = False
        self.curLevel = -1
        self.prevState = None
        self.showSwitchToPostProgression = False
        self.showPostProgressionCompleted = False
        g_playerEvents.onDisconnected += self.reset
        g_playerEvents.onAccountBecomePlayer += self.reset
        return

    def reset(self):
        self.isFirstShow = True
        self.isBPBought = False
        self.curLevel = -1
        self.prevState = None
        self.showSwitchToPostProgression = False
        self.showPostProgressionCompleted = False
        return


g_BPEntryPointStates = BattlePassEntryPointStates()
ATTENTION_TIMER_DELAY = 25

class BattlePassEntryPointComponent(BattlePassEntryPointMeta):
    __slots__ = ('__view', '__isSmall')

    def __init__(self):
        super(BattlePassEntryPointComponent, self).__init__()
        self.__isSmall = False

    def setIsSmall(self, value):
        self.__isSmall = value
        if self.__view is not None:
            self.__view.setIsSmall(self.__isSmall)
        return

    def _dispose(self):
        self.__view = None
        super(BattlePassEntryPointComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = BattlePassEntryPointView(flags=ViewFlags.COMPONENT)
        self.__view.setIsSmall(self.__isSmall)
        return self.__view


class BattlePassEntryPointView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__isSmall', '__notifications', '__isAttentionTimerStarted')

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassEntryPointView())
        settings.flags = flags
        settings.model = BattlePassEntryPointViewModel()
        self.__isSmall = False
        self.__isAttentionTimerStarted = False
        self.__notifications = Notifiable()
        super(BattlePassEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassEntryPointView, self).getViewModel()

    def setIsSmall(self, value):
        if self.viewModel.proxy:
            self.viewModel.setIsSmall(value)
        self.__isSmall = value

    def _onLoading(self, *args, **kwargs):
        super(BattlePassEntryPointView, self)._onLoading(*args, **kwargs)
        currentState, _ = self.__getCurrentLevel()
        if g_BPEntryPointStates.prevState == BattlePassState.BASE and currentState == BattlePassState.POST:
            g_BPEntryPointStates.showSwitchToPostProgression = True
        if g_BPEntryPointStates.prevState == BattlePassState.POST and currentState == BattlePassState.COMPLETED:
            g_BPEntryPointStates.showPostProgressionCompleted = True
        g_BPEntryPointStates.prevState = currentState
        self.__notifications.addNotificator(PeriodicNotifier(self.__attentionTickTime, self.__showAttentionAnimation))
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        self.__notifications.clearNotification()
        super(BattlePassEntryPointView, self)._finalize()

    def __addListeners(self):
        self.__battlePassController.onPointsUpdated += self.__updateViewModel
        self.__battlePassController.onBattlePassIsBought += self.__updateViewModel
        self.__battlePassController.onSeasonStateChange += self.__updateViewModel
        self.__battlePassController.onVoted += self.__updateViewModel
        self.__battlePassController.onBattlePassSettingsChange += self.__onBattlePassSettingsChange
        self.__battlePassController.onFinalRewardStateChange += self.__onFinalRewardStateChange
        self.__battlePassController.onDeviceSelectChange += self.__updateViewModel
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onClick += self.__onClick

    def __removeListeners(self):
        self.__battlePassController.onPointsUpdated -= self.__updateViewModel
        self.__battlePassController.onBattlePassIsBought -= self.__updateViewModel
        self.__battlePassController.onSeasonStateChange -= self.__updateViewModel
        self.__battlePassController.onVoted -= self.__updateViewModel
        self.__battlePassController.onBattlePassSettingsChange -= self.__onBattlePassSettingsChange
        self.__battlePassController.onFinalRewardStateChange -= self.__onFinalRewardStateChange
        self.__battlePassController.onDeviceSelectChange -= self.__updateViewModel
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        g_eventBus.removeListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onClick -= self.__onClick

    def __onClick(self):
        showMissionsBattlePassCommonProgression()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView():
            return BattlePassNotStartedTooltipView()
        if contentID == R.views.lobby.battle_pass.tooltips.BattlePassChoseWinnerTooltipView():
            return BattlePassChoseWinnerTooltipView()
        return BattlePassCompletedTooltipView() if contentID == R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView() else BattlePassInProgressTooltipView()

    def __onBattlePassSettingsChange(self, *_):
        self.__updateViewModel()

    def __onSyncCompleted(self, _, diff):
        if GUI_ITEM_TYPE.VEHICLE in diff:
            with self.getViewModel().transaction() as model:
                model.setShowWarning(not self.__battlePassController.canPlayerParticipate())

    def __onFinalRewardStateChange(self):
        g_BPEntryPointStates.prevState = self.__battlePassController.getState()
        g_BPEntryPointStates.showSwitchToPostProgression = True
        self.__updateViewModel()

    def __onAwardViewClose(self, _):
        currentState = self.__battlePassController.getState()
        if currentState == BattlePassState.COMPLETED:
            g_BPEntryPointStates.showPostProgressionCompleted = True
            g_BPEntryPointStates.prevState = currentState
            self.__updateViewModel()

    def __showAttentionAnimation(self):
        with self.getViewModel().transaction() as model:
            model.setAnimState(BattlePassEntryPointViewModel.ANIM_STATE_SHOW_ATTENTION)
            model.setAnimStateKey(random.randint(0, 1000))

    def __attentionTickTime(self):
        return ATTENTION_TIMER_DELAY

    def __startAttentionTimer(self):
        if not self.__isAttentionTimerStarted:
            self.__notifications.startNotification()
            self.__isAttentionTimerStarted = True

    def __stopAttentionTimer(self):
        self.__notifications.clearNotification()
        self.__isAttentionTimerStarted = False

    def __updateViewModel(self):
        currentState, currentLevel = self.__getCurrentLevel()
        currentLevel = min(currentLevel + 1, self.__battlePassController.getMaxLevel(currentState == BattlePassState.BASE))
        if g_BPEntryPointStates.prevState == BattlePassState.BASE and currentState == BattlePassState.POST:
            return
        if g_BPEntryPointStates.prevState == BattlePassState.POST and currentState == BattlePassState.COMPLETED:
            return
        if self.__battlePassController.isPaused():
            state = BattlePassEntryPointViewModel.STATE_DISABLED
            tooltip = 0
        elif self.__battlePassController.isOffSeasonEnable():
            state = BattlePassEntryPointViewModel.STATE_SEASON_WAITING
            tooltip = R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView()
        else:
            hasDeviceTokens = self.__battlePassController.getTrophySelectTokensCount() > 0 or self.__battlePassController.getNewDeviceSelectTokensCount() > 0
            showAttention = isNeededToVote() or hasDeviceTokens and self.__battlePassController.isChooseDeviceEnabled()
            state = BattlePassEntryPointViewModel.STATE_ATTENTION if showAttention else BattlePassEntryPointViewModel.STATE_NORMAL
            if showAttention:
                self.__startAttentionTimer()
            else:
                self.__stopAttentionTimer()
            if isNeededToVote():
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePassChoseWinnerTooltipView()
            elif currentState == BattlePassState.COMPLETED:
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView()
            else:
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView()
        with self.getViewModel().transaction() as model:
            curPoints, limitPoints = self.__battlePassController.getLevelProgression()
            hasBattlePass = self.__isBought()
            progression = curPoints * 100 / limitPoints if limitPoints else 100
            prevProgression = model.getProgression() if model.getProgression() != -1 else progression
            model.setIsSmall(self.__isSmall)
            model.setTooltipID(tooltip)
            model.setPrevLevel(g_BPEntryPointStates.curLevel)
            model.setLevel(currentLevel)
            model.setPrevProgression(prevProgression)
            model.setProgression(progression)
            model.setBattlePassState(state)
            if currentState == BattlePassState.POST:
                progressionState = BattlePassEntryPointViewModel.PROGRESSION_POST
            elif currentState == BattlePassState.BASE:
                progressionState = BattlePassEntryPointViewModel.PROGRESSION_BASE
            else:
                progressionState = BattlePassEntryPointViewModel.PROGRESSION_COMPLETED
            model.setProgressionState(progressionState)
            model.setHasBattlePass(hasBattlePass)
            isSameLevel = g_BPEntryPointStates.curLevel == currentLevel
            isSameState = g_BPEntryPointStates.prevState == currentState
            isValidLevel = g_BPEntryPointStates.curLevel != -1
            showNewLevel = isValidLevel and not isSameLevel or isSameLevel and not isSameState
            showBuyBP = not g_BPEntryPointStates.isBPBought and hasBattlePass and not g_BPEntryPointStates.isFirstShow
            showProgressionChange = prevProgression != progression
            animState = BattlePassEntryPointViewModel.ANIM_STATE_NORMAL
            if g_BPEntryPointStates.showSwitchToPostProgression:
                if showBuyBP:
                    animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_BUY_AND_SWITCH_TO_POST
                else:
                    animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_SWITCH_TO_POST_PROGRESSION
            elif g_BPEntryPointStates.showPostProgressionCompleted:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_POST_PROGRESSION_COMPLETED
            elif showNewLevel:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_NEW_LEVEL
            elif showBuyBP:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_BUY_BATTLEPASS
            elif showProgressionChange:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_CHANGE_PROGRESS
            model.setAnimState(animState)
            model.setAnimStateKey(random.randint(0, 1000))
            model.setIsFirstShow(g_BPEntryPointStates.isFirstShow)
            model.setShowWarning(not self.__battlePassController.canPlayerParticipate())
            g_BPEntryPointStates.curLevel = currentLevel
            g_BPEntryPointStates.isFirstShow = False
            g_BPEntryPointStates.isBPBought = hasBattlePass
            g_BPEntryPointStates.showSwitchToPostProgression = False
            g_BPEntryPointStates.showPostProgressionCompleted = False
        g_BPEntryPointStates.prevState = currentState

    def __getCurrentLevel(self):
        if self.__battlePassController.isOffSeasonEnable():
            prevSeasonStats = self.__battlePassController.getLastFinishedSeasonStats()
            if prevSeasonStats is None:
                return (BattlePassState.BASE, 0)
            prevOtherStats = prevSeasonStats.otherStats
            prevSeasonHistory = getSeasonHistory(prevSeasonStats.seasonID)
            if prevSeasonHistory is None:
                return (BattlePassState.BASE, 0)
            state, currentLevel = getLevelFromStats(prevOtherStats, prevSeasonHistory)
        else:
            state = self.__battlePassController.getState()
            currentLevel = self.__battlePassController.getCurrentLevel()
        return (state, currentLevel)

    def __isBought(self):
        if self.__battlePassController.isOffSeasonEnable():
            prevSeasonStats = self.__battlePassController.getLastFinishedSeasonStats()
            if prevSeasonStats.seasonID is not None:
                return self.__battlePassController.isBought(prevSeasonStats.seasonID)
        return self.__battlePassController.isBought()
