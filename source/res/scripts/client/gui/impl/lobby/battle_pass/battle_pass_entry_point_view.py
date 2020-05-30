# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_entry_point_view.py
from PlayerEvents import g_playerEvents
from battle_pass_common import BattlePassState
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.BattlePassEntryPointMeta import BattlePassEntryPointMeta
from gui.battle_pass import battle_pass_helpers
from gui.battle_pass.final_reward_state_machine import FinalStates
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_entry_point_view_model import BattlePassEntryPointViewModel
from gui.impl.lobby.battle_pass.tooltips.battle_pass_chose_winner_tooltip_view import BattlePassChoseWinnerTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view import BattlePassNotStartedTooltipView
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

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
        self.__view = BattlePassEntryPointView(self.as_setIsMouseEnabledS, flags=ViewFlags.COMPONENT)
        self.__view.setIsSmall(self.__isSmall)
        return self.__view


class BattlePassEntryPointView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ('__setIsMouseEnabled', '__isSmall')

    def __init__(self, setIsMouseEnabled, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassEntryPointView())
        settings.flags = flags
        settings.model = BattlePassEntryPointViewModel()
        self.__setIsMouseEnabled = setIsMouseEnabled
        self.__isSmall = False
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
        currentState = self.__battlePassController.getState()
        if g_BPEntryPointStates.prevState == BattlePassState.BASE and currentState == BattlePassState.POST:
            g_BPEntryPointStates.showSwitchToPostProgression = True
        if g_BPEntryPointStates.prevState == BattlePassState.POST and currentState == BattlePassState.COMPLETED:
            g_BPEntryPointStates.showPostProgressionCompleted = True
        g_BPEntryPointStates.prevState = currentState
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        self.__setIsMouseEnabled = None
        super(BattlePassEntryPointView, self)._finalize()
        return

    def __addListeners(self):
        self.__battlePassController.onPointsUpdated += self.__updateViewModel
        self.__battlePassController.onBattlePassIsBought += self.__updateViewModel
        self.__battlePassController.onSeasonStateChange += self.__updateViewModel
        self.__battlePassController.onVoted += self.__updateViewModel
        self.__battlePassController.onBattlePassSettingsChange += self.__onBattlePassSettingsChange
        self.__battlePassController.onFinalRewardStateChange += self.__onFinalRewardStateChange
        g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onClick += self.__onClick

    def __removeListeners(self):
        self.__battlePassController.onPointsUpdated -= self.__updateViewModel
        self.__battlePassController.onBattlePassIsBought -= self.__updateViewModel
        self.__battlePassController.onSeasonStateChange -= self.__updateViewModel
        self.__battlePassController.onVoted -= self.__updateViewModel
        self.__battlePassController.onBattlePassSettingsChange -= self.__onBattlePassSettingsChange
        self.__battlePassController.onFinalRewardStateChange -= self.__onFinalRewardStateChange
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

    def __onFinalRewardStateChange(self, state):
        if state in (FinalStates.FINAL, FinalStates.STOP):
            g_BPEntryPointStates.prevState = self.__battlePassController.getState()
            g_BPEntryPointStates.showSwitchToPostProgression = True
            self.__updateViewModel()

    def __onAwardViewClose(self, _):
        currentState = self.__battlePassController.getState()
        if currentState == BattlePassState.COMPLETED:
            g_BPEntryPointStates.showPostProgressionCompleted = True
            g_BPEntryPointStates.prevState = currentState
            self.__updateViewModel()

    def __updateViewModel(self):
        currentState = self.__battlePassController.getState()
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
            state = BattlePassEntryPointViewModel.STATE_NORMAL
            if battle_pass_helpers.isNeededToVote():
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePassChoseWinnerTooltipView()
            elif currentState == BattlePassState.COMPLETED:
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView()
            else:
                tooltip = R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView()
        self.__setIsMouseEnabled(state == BattlePassEntryPointViewModel.STATE_NORMAL)
        with self.getViewModel().transaction() as model:
            curPoints, limitPoints = self.__battlePassController.getLevelProgression()
            hasBattlePass = self.__battlePassController.isBought()
            currentLevel = self.__battlePassController.getCurrentLevel() + 1
            currentLevel = min(currentLevel, self.__battlePassController.getMaxLevel(currentState == BattlePassState.BASE))
            progression = curPoints * 100 / limitPoints if limitPoints else 100
            prevProgression = model.getProgression() if model.getProgression() != -1 else progression
            model.setIsSmall(self.__isSmall)
            model.setTooltipID(tooltip)
            model.setPrevLevel(g_BPEntryPointStates.curLevel)
            model.setLevel(currentLevel)
            model.setMaxCommonLevel(self.__battlePassController.getMaxLevel())
            model.setPrevProgression(prevProgression)
            model.setProgression(progression)
            model.setIsPostProgression(currentState != BattlePassState.BASE)
            model.setHasBattlePass(hasBattlePass)
            model.setIsPostProgressionCompleted(currentState == BattlePassState.COMPLETED)
            model.setState(state)
            model.setCanPlay(self.__battlePassController.canPlayerParticipate())
            isSameLevel = g_BPEntryPointStates.curLevel == currentLevel
            isSameState = g_BPEntryPointStates.prevState == currentState
            isValidLevel = g_BPEntryPointStates.curLevel != -1
            showNewLevel = isValidLevel and not isSameLevel or isSameLevel and not isSameState
            showBuyBP = not g_BPEntryPointStates.isBPBought and hasBattlePass and not g_BPEntryPointStates.isFirstShow
            showAttention = currentState != BattlePassState.BASE and not self.__battlePassController.isPlayerVoted()
            animState = BattlePassEntryPointViewModel.ANIM_STATE_NORMAL
            if g_BPEntryPointStates.showSwitchToPostProgression:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_SWITCH_TO_POST_PROGRESSION
            elif g_BPEntryPointStates.showPostProgressionCompleted:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_POST_PROGRESSION_COMPLETED
            elif showNewLevel:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_NEW_LEVEL
            elif showBuyBP:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_BUY_BATTLEPASS
            elif showAttention:
                animState = BattlePassEntryPointViewModel.ANIM_STATE_SHOW_ATTENTION
            model.setAnimState(animState)
            model.setIsFirstShow(g_BPEntryPointStates.isFirstShow)
            g_BPEntryPointStates.curLevel = currentLevel
            g_BPEntryPointStates.isFirstShow = False
            g_BPEntryPointStates.isBPBought = hasBattlePass
            g_BPEntryPointStates.showSwitchToPostProgression = False
            g_BPEntryPointStates.showPostProgressionCompleted = False
        g_BPEntryPointStates.prevState = currentState
