# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_entry_point_view.py
from PlayerEvents import g_playerEvents
from battle_pass_common import BattlePassState, CurrencyBP, getPresentLevel
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.BattlePassEntryPointMeta import BattlePassEntryPointMeta
from gui.battle_pass.battle_pass_helpers import getSupportedCurrentArenaBonusType
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_entry_point_view_model import AnimationState, BPState, BattlePassEntryPointViewModel
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_no_chapter_tooltip_view import BattlePassNoChapterTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view import BattlePassNotStartedTooltipView
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.formatters.invites import getPreQueueName
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers.events_handler import EventsHandler
from helpers.time_utils import MS_IN_SECOND
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache

class _LastEntryState(object):

    def __init__(self):
        self.isFirstShow = True
        self.isBought = False
        self.hasExtra = False
        self.chapterID = 0
        self.level = 0
        self.progress = 0
        self.state = None
        self.rewardsCount = 0
        return

    def update(self, isFirstShow=True, isBought=False, hasExtra=False, chapterID=0, level=0, progress=0, state=None, rewardsCount=0):
        self.isFirstShow = isFirstShow
        self.isBought = isBought
        self.hasExtra = hasExtra
        self.chapterID = chapterID
        self.level = level
        self.progress = progress
        self.state = state
        self.rewardsCount = rewardsCount


_g_entryLastState = _LastEntryState()
ATTENTION_TIMER_DELAY = 25
FULL_PROGRESS = 100

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


class BaseBattlePassEntryPointView(IGlobalListener, EventsHandler):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(BaseBattlePassEntryPointView, self).__init__()

    @property
    def chapterID(self):
        return self.__battlePassController.getCurrentChapterID()

    @property
    def level(self):
        return self.__battlePassController.getCurrentLevel()

    @property
    def isChapterChosen(self):
        return self.__battlePassController.hasActiveChapter()

    @property
    def isBought(self):
        chapterID = self.chapterID
        if chapterID and self.__battlePassController.isBought(chapterID=chapterID):
            return True
        chapterIDs = self.__battlePassController.getChapterIDs()
        return all((self.__battlePassController.isBought(chapterID=chapter) for chapter in chapterIDs))

    @property
    def isCompleted(self):
        chapterIDs = self.__battlePassController.getChapterIDs()
        return all((self.__battlePassController.isChapterCompleted(chapter) for chapter in chapterIDs))

    @property
    def isPaused(self):
        return self.__battlePassController.isPaused() or not self.__battlePassController.isGameModeEnabled(self._getCurrentArenaBonusType())

    @property
    def hasExtra(self):
        return self.__battlePassController.hasExtra()

    @property
    def battlePassState(self):
        return self.__battlePassController.getState()

    @property
    def progress(self):
        points, limit = self.__battlePassController.getLevelProgression(self.chapterID)
        return FULL_PROGRESS / (limit or FULL_PROGRESS) * points

    @property
    def notChosenRewardCount(self):
        return self.__battlePassController.getNotChosenRewardCount()

    @property
    def freePoints(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.BIT.value, 0)

    def onPrbEntitySwitched(self):
        self._updateData()

    def _start(self):
        self._addListeners()
        self._updateData()

    def _stop(self):
        self._removeListeners()
        self._saveLastState()

    def _updateData(self, *_):
        pass

    def _saveLastState(self):
        _g_entryLastState.update(False, self.isBought, self.hasExtra, self.chapterID, self.level, self.progress, self.battlePassState, self.notChosenRewardCount)

    @staticmethod
    def _onClick():
        showMissionsBattlePass()

    def _getListeners(self):
        return ((events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.__battlePassController.onPointsUpdated, self._updateData),
         (self.__battlePassController.onBattlePassIsBought, self._updateData),
         (self.__battlePassController.onSeasonStateChanged, self._updateData),
         (self.__battlePassController.onExtraChapterExpired, self._updateData),
         (self.__battlePassController.onBattlePassSettingsChange, self._updateData),
         (self.__battlePassController.onChapterChanged, self._updateData),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated))

    def _addListeners(self):
        self.startGlobalListening()

    def _removeListeners(self):
        self.stopGlobalListening()

    def _getTooltip(self):
        if self.isPaused:
            return R.invalid()
        if self.isCompleted:
            return R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView()
        return R.views.lobby.battle_pass.tooltips.BattlePassNoChapterTooltipView() if not self.chapterID else R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView()

    def _getNotChosenRewardCount(self):
        return self.__battlePassController.getNotChosenRewardCount()

    def _getCurrentArenaBonusType(self):
        return getSupportedCurrentArenaBonusType(self._getQueueType())

    def _getQueueType(self):
        dispatcher = g_prbLoader.getDispatcher()
        return None if dispatcher is None else dispatcher.getEntity().getQueueType()

    def __onAwardViewClose(self, _):
        self._updateData()

    def __onClientUpdated(self, diff, _):
        if self.isCompleted and diff.get('cache', {}).get('dynamicCurrencies', {}).get(CurrencyBP.BIT.value, ''):
            self._updateData()


class BattlePassEntryPointView(ViewImpl, BaseBattlePassEntryPointView):
    __battlePassController = dependency.descriptor(IBattlePassController)
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

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView():
            return BattlePassNotStartedTooltipView()
        if contentID == R.views.lobby.battle_pass.tooltips.BattlePassNoChapterTooltipView():
            return BattlePassNoChapterTooltipView()
        return BattlePassCompletedTooltipView() if contentID == R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView() else BattlePassInProgressTooltipView()

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
        self.viewModel.onClick -= self._onClick
        super(BattlePassEntryPointView, self)._removeListeners()

    def _updateData(self, *_):
        self.__updateViewModel()

    def __attentionTickTime(self):
        return ATTENTION_TIMER_DELAY

    def __showAttentionAnimation(self):
        with self.getViewModel().transaction() as tx:
            tx.setAnimState(AnimationState.NOT_TAKEN_REWARDS)
            tx.setAnimStateKey(MS_IN_SECOND)

    def __startAttentionTimer(self):
        if not self.__isAttentionTimerStarted:
            self.__notifications.startNotification()
            self.__isAttentionTimerStarted = True

    def __stopAttentionTimer(self):
        self.__notifications.clearNotification()
        self.__isAttentionTimerStarted = False

    def __updateViewModel(self):
        uiState = self.__getUIState()
        if uiState == BPState.ATTENTION:
            self.__startAttentionTimer()
        else:
            self.__stopAttentionTimer()
        with self.getViewModel().transaction() as tx:
            tx.setIsSmall(self.__isSmall)
            tx.setTooltipID(self._getTooltip())
            tx.setPrevHasExtra(_g_entryLastState.hasExtra)
            tx.setHasExtra(self.hasExtra)
            tx.setPrevLevel(getPresentLevel(_g_entryLastState.level))
            tx.setLevel(getPresentLevel(self.level))
            tx.setChapterID(self.chapterID)
            tx.setPreviousChapterID(_g_entryLastState.chapterID)
            tx.setPrevProgression(_g_entryLastState.progress)
            tx.setProgression(self.progress)
            tx.setBattlePassState(uiState)
            tx.setNotChosenRewardCount(self.notChosenRewardCount)
            tx.setIsProgressionCompleted(self.isCompleted)
            tx.setIsChapterChosen(self.isChapterChosen)
            tx.setFreePoints(self.freePoints)
            tx.setHasBattlePass(self.isBought)
            tx.setAnimState(self.__getAnimationState())
            tx.setIsFirstShow(_g_entryLastState.isFirstShow)
            if not self.__battlePassController.isGameModeEnabled(self._getCurrentArenaBonusType()):
                tx.setBattleType(getPreQueueName(self._getQueueType(), True))
        self._saveLastState()

    def __getAnimationState(self):
        animState = AnimationState.NORMAL
        lastState = _g_entryLastState
        if self.battlePassState == BattlePassState.COMPLETED and lastState.state != BattlePassState.COMPLETED:
            animState = AnimationState.PROGRESSION_COMPLETED
        elif self.chapterID and self.chapterID != lastState.chapterID:
            animState = AnimationState.NEW_CHAPTER
        elif not self.chapterID:
            animState = AnimationState.CHAPTER_NOT_CHOSEN
        elif self.level and self.level != lastState.level:
            animState = AnimationState.NEW_LEVEL
        elif self.isBought and not lastState.isBought:
            animState = AnimationState.BUY_BATTLE_PASS
        elif self.progress != lastState.progress:
            animState = AnimationState.CHANGE_PROGRESS
        elif self.notChosenRewardCount and self.notChosenRewardCount != lastState.rewardsCount:
            animState = AnimationState.NOT_TAKEN_REWARDS
        return animState

    def __getUIState(self):
        if self.isPaused:
            return BPState.DISABLED
        return BPState.ATTENTION if self.notChosenRewardCount and self.battlePassState != BattlePassState.BASE else BPState.NORMAL
