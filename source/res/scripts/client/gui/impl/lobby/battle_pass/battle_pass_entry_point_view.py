# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_entry_point_view.py
import random
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BattlePassState
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.BattlePassEntryPointMeta import BattlePassEntryPointMeta
from gui.battle_pass.battle_pass_helpers import getSeasonHistory, getLevelFromStats, getNotChosen3DStylesCount, getSupportedCurrentArenaBonusType
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_entry_point_view_model import BattlePassEntryPointViewModel, AnimationState, BPState
from gui.impl.lobby.battle_pass.tooltips.battle_pass_3d_style_not_chosen_tooltip import BattlePass3dStyleNotChosenTooltip
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view import BattlePassNotStartedTooltipView
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.formatters.invites import getPreQueueName
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression, showBattlePass3dStyleChoiceWindow
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController

class BattlePassEntryPointStates(object):

    def __init__(self):
        self.isFirstShow = True
        self.isBPBought = False
        self.curLevel = -1
        self.curChapter = -1
        self.prevState = None
        self.showSwitchToNewChapter = False
        self.showProgressionCompleted = False
        g_playerEvents.onDisconnected += self.reset
        g_playerEvents.onAccountBecomePlayer += self.reset
        return

    def reset(self):
        self.isFirstShow = True
        self.isBPBought = False
        self.curLevel = -1
        self.curChapter = -1
        self.prevState = None
        self.showSwitchToNewChapter = False
        self.showProgressionCompleted = False
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


class BaseBattlePassEntryPointView(IGlobalListener):
    _battlePassController = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        super(BaseBattlePassEntryPointView, self).__init__()
        self._widgetState = BPState.DISABLED
        self._widgetChapter = -1
        self._widgetLevel = -1

    def onPrbEntitySwitched(self):
        self._updateData()

    def _start(self):
        self._updateWidgetValues()
        if g_BPEntryPointStates.curChapter != -1 and g_BPEntryPointStates.curChapter != self._widgetChapter:
            g_BPEntryPointStates.showSwitchToNewChapter = True
        if g_BPEntryPointStates.prevState == BattlePassState.BASE and self._isCompleted():
            g_BPEntryPointStates.showProgressionCompleted = True
        g_BPEntryPointStates.prevState = self._widgetState
        g_BPEntryPointStates.curChapter = self._widgetChapter
        self._addListeners()
        self._updateData()

    def _stop(self):
        self._removeListeners()

    def _updateData(self, *_):
        self._updateWidgetValues()

    def _onClick(self):
        if getNotChosen3DStylesCount(battlePass=self._battlePassController) > 0 and self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.INTRO_SHOWN) and not self._battlePassController.isOffSeasonEnable():
            showBattlePass3dStyleChoiceWindow()
        else:
            showMissionsBattlePassCommonProgression()

    def _addListeners(self):
        self._battlePassController.onPointsUpdated += self._updateData
        self._battlePassController.onBattlePassIsBought += self._updateData
        self._battlePassController.onSeasonStateChange += self._updateData
        self._battlePassController.onBattlePassSettingsChange += self._updateData
        g_playerEvents.onClientUpdated += self._updateData
        g_eventBus.addListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.startGlobalListening()

    def _removeListeners(self):
        self._battlePassController.onPointsUpdated -= self._updateData
        self._battlePassController.onBattlePassIsBought -= self._updateData
        self._battlePassController.onSeasonStateChange -= self._updateData
        self._battlePassController.onBattlePassSettingsChange -= self._updateData
        g_playerEvents.onClientUpdated -= self._updateData
        g_eventBus.removeListener(events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.stopGlobalListening()

    def _isBought(self):
        if self._battlePassController.isOffSeasonEnable():
            prevSeasonStats = self._battlePassController.getLastFinishedSeasonStats()
            if prevSeasonStats.seasonID is not None:
                return self._battlePassController.isBought(prevSeasonStats.seasonID)
        return self._battlePassController.isBought(chapter=self._widgetChapter)

    def _getTooltip(self):
        if self._isBattlePassPaused():
            tooltip = 0
        elif self._battlePassController.isOffSeasonEnable():
            tooltip = R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView()
        elif self._isCompleted():
            tooltip = R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView()
        elif not self._is3DStyleChosen():
            tooltip = R.views.lobby.battle_pass.tooltips.BattlePass3dStyleNotChosenTooltip()
        else:
            tooltip = R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView()
        return tooltip

    def _getNotChosenRewardCountWith3d(self):
        return self._battlePassController.getNotChosenRewardCount() + getNotChosen3DStylesCount(battlePass=self._battlePassController)

    def _is3DStyleChosen(self):
        return getNotChosen3DStylesCount(battlePass=self._battlePassController) == 0

    def _isCompleted(self):
        return True if self._isBattlePassPaused() and self._battlePassController.getCurrentLevel() == self._battlePassController.getMaxLevel() else self._widgetState == BattlePassState.COMPLETED

    def _updateWidgetValues(self):
        if self._battlePassController.isOffSeasonEnable():
            prevSeasonStats = self._battlePassController.getLastFinishedSeasonStats()
            if prevSeasonStats is None:
                return (BattlePassState.BASE, 0, 0)
            prevOtherStats = prevSeasonStats.otherStats
            prevSeasonHistory = getSeasonHistory(prevSeasonStats.seasonID)
            if prevSeasonHistory is None:
                return (BattlePassState.BASE, 0, 0)
            state, currentLevel = getLevelFromStats(prevOtherStats, prevSeasonHistory)
            currentChapter = 0
        else:
            state = self._battlePassController.getState()
            currentLevel = self._battlePassController.getCurrentLevel()
            currentChapter = self._battlePassController.getCurrentChapter()
        self._widgetState = state
        self._widgetLevel = currentLevel
        self._widgetChapter = currentChapter
        return

    def _getCurrentArenaBonusType(self):
        return getSupportedCurrentArenaBonusType(self._getQueueType())

    def _isBattlePassPaused(self):
        return self._battlePassController.isPaused() or not self._battlePassController.isGameModeEnabled(self._getCurrentArenaBonusType())

    def _getQueueType(self):
        dispatcher = g_prbLoader.getDispatcher()
        return dispatcher.getEntity().getQueueType() if dispatcher else None

    def __onAwardViewClose(self, _):
        currentState = self._battlePassController.getState()
        currentChapter = self._battlePassController.getCurrentChapter()
        if currentState == BattlePassState.COMPLETED:
            g_BPEntryPointStates.showProgressionCompleted = True
            g_BPEntryPointStates.prevState = currentState
            self._updateData()
        elif g_BPEntryPointStates.curChapter != -1 and g_BPEntryPointStates.curChapter != currentChapter:
            g_BPEntryPointStates.showSwitchToNewChapter = True
            g_BPEntryPointStates.curChapter = currentChapter
            self._updateData()


class BattlePassEntryPointView(ViewImpl, BaseBattlePassEntryPointView):
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
        self._start()
        self.__notifications.addNotificator(PeriodicNotifier(self.__attentionTickTime, self.__showAttentionAnimation))

    def _finalize(self):
        self.__notifications.clearNotification()
        self._stop()
        super(BattlePassEntryPointView, self)._finalize()

    def _addListeners(self):
        super(BattlePassEntryPointView, self)._addListeners()
        self.viewModel.onClick += self._onClick

    def _removeListeners(self):
        super(BattlePassEntryPointView, self)._removeListeners()
        self.viewModel.onClick -= self._onClick

    def _updateData(self, *_):
        super(BattlePassEntryPointView, self)._updateData()
        self.__updateViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView():
            return BattlePassNotStartedTooltipView()
        if contentID == R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView():
            return BattlePassCompletedTooltipView()
        return BattlePass3dStyleNotChosenTooltip() if contentID == R.views.lobby.battle_pass.tooltips.BattlePass3dStyleNotChosenTooltip() else BattlePassInProgressTooltipView()

    def __showAttentionAnimation(self):
        with self.getViewModel().transaction() as model:
            model.setAnimState(AnimationState.SHOW_NOT_TAKEN_REWARDS)
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
        currentLevel = min(self._widgetLevel + 1, self._battlePassController.getMaxLevel())
        notChosenRewardCount = 0
        is3DStyleChosen = False
        if self._isBattlePassPaused():
            state = BPState.DISABLED
        elif self._battlePassController.isOffSeasonEnable():
            state = BPState.SEASON_WAITING
        else:
            notChosen3DStylesCount = getNotChosen3DStylesCount(battlePass=self._battlePassController)
            notChosenRewardCount = self._battlePassController.getNotChosenRewardCount() + notChosen3DStylesCount
            is3DStyleChosen = notChosen3DStylesCount == 0
            state = BPState.ATTENTION if notChosenRewardCount > 0 else BPState.NORMAL
            if state == BPState.ATTENTION:
                self.__startAttentionTimer()
            else:
                self.__stopAttentionTimer()
        with self.getViewModel().transaction() as model:
            curPoints, limitPoints = self._battlePassController.getLevelProgression()
            hasBattlePass = self._isBought()
            progression = curPoints * 100 / limitPoints if limitPoints else 100
            prevProgression = model.getProgression() if model.getProgression() != -1 else progression
            model.setIsSmall(self.__isSmall)
            model.setTooltipID(self._getTooltip())
            model.setPrevLevel(g_BPEntryPointStates.curLevel)
            model.setLevel(currentLevel)
            model.setChapterNumber(self._widgetChapter)
            model.setPrevProgression(prevProgression)
            model.setProgression(progression)
            model.setBattlePassState(state)
            model.setNotChosenRewardCount(notChosenRewardCount)
            model.setIs3DStyleChosen(is3DStyleChosen)
            if not self._battlePassController.isGameModeEnabled(self._getCurrentArenaBonusType()):
                model.setBattleType(getPreQueueName(self._getQueueType(), True))
            model.setIsProgressionCompleted(self._isCompleted())
            model.setHasBattlePass(hasBattlePass)
            animState = AnimationState.NORMAL
            if g_BPEntryPointStates.showProgressionCompleted:
                animState = AnimationState.SHOW_PROGRESSION_COMPLETED
            elif g_BPEntryPointStates.showSwitchToNewChapter:
                animState = AnimationState.SHOW_NEW_CHAPTER
            elif g_BPEntryPointStates.curLevel != currentLevel and g_BPEntryPointStates.curLevel != -1:
                animState = AnimationState.SHOW_NEW_LEVEL
            elif not g_BPEntryPointStates.isBPBought and hasBattlePass and not g_BPEntryPointStates.isFirstShow:
                animState = AnimationState.SHOW_BUY_BP
            elif prevProgression != progression:
                animState = AnimationState.SHOW_CHANGE_PROGRESS
            model.setAnimState(animState)
            model.setIsFirstShow(g_BPEntryPointStates.isFirstShow)
            g_BPEntryPointStates.curLevel = currentLevel
            g_BPEntryPointStates.isFirstShow = False
            g_BPEntryPointStates.isBPBought = hasBattlePass
            g_BPEntryPointStates.showSwitchToNewChapter = False
            g_BPEntryPointStates.showProgressionCompleted = False
        g_BPEntryPointStates.prevState = self._widgetState
