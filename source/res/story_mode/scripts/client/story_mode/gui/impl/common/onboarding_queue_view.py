# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/common/onboarding_queue_view.py
from functools import partial
import typing
import BigWorld
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowFlags, ViewSettings
from gui.game_loading import loading
from gui.game_loading.resources.consts import Milestones
from gui.impl.gen import R
from gui.impl.pub import WindowImpl
from gui.prb_control import prbEntityProperty
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.impl.base_queue_view import BaseWaitQueueView
from story_mode.gui.impl.battle.prebattle_window import getOpenedPrebattleView
from story_mode.gui.impl.gen.view_models.views.common.onboarding_queue_view_model import OnboardingQueueViewModel
from story_mode.gui.impl.mixins import DestroyWindowOnDisconnectMixin
from story_mode.gui.shared.event_dispatcher import sendViewLoadedEvent
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogWindows, LogButtons
from story_mode.uilogging.story_mode.loggers import WindowBehindGameLoadingLogger

class OnboardingQueueView(BaseWaitQueueView):
    __slots__ = ('_isButtonVisible', '_hideGameLoadingCallbackId', '_uiLogger')
    LAYOUT_ID = R.views.story_mode.common.OnboardingQueueView()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, isButtonVisible=False):
        settings = ViewSettings(self.LAYOUT_ID)
        settings.model = OnboardingQueueViewModel()
        super(OnboardingQueueView, self).__init__(settings)
        self._isButtonVisible = isButtonVisible
        self._hideGameLoadingCallbackId = None
        self._uiLogger = WindowBehindGameLoadingLogger(LogWindows.QUEUE)
        return

    @property
    def viewModel(self):
        return super(OnboardingQueueView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def _onLoading(self, *args, **kwargs):
        super(OnboardingQueueView, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsVisibleButton(self._isButtonVisible)
        if not self._isButtonVisible:
            self.startWaitQueue()
        self._hideGameLoadingCallbackId = BigWorld.callback(self._storyModeCtrl.settings.hideGameLoadingTimeout, self._hideGameLoading)
        g_playerEvents.onLoadingMilestoneReached(Milestones.ONBOARDING_ENQUEUED)
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self._handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def _onLoaded(self, *args, **kwargs):
        super(OnboardingQueueView, self)._onLoaded(*args, **kwargs)
        self._uiLogger.logOpen(info=LogButtons.SKIP if self.viewModel and self.viewModel.getIsVisibleButton() else None)
        return

    def _finalize(self):
        if self._hideGameLoadingCallbackId is not None:
            BigWorld.cancelCallback(self._hideGameLoadingCallbackId)
            self._hideGameLoadingCallbackId = None
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self._handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self._uiLogger.logClose()
        super(OnboardingQueueView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onQuit, self._onQuitButtonClick), (self.viewModel.onLoaded, partial(sendViewLoadedEvent, self.LAYOUT_ID)))

    def _onWaitQueueTimeout(self):
        self._uiLogger.logButtonShown(LogButtons.SKIP)
        super(OnboardingQueueView, self)._onWaitQueueTimeout()
        self.viewModel.setIsVisibleButton(True)

    def _onQuitButtonClick(self):
        self._uiLogger.logClick(LogButtons.SKIP)
        self._storyModeCtrl.quitBattle()
        if self.prbEntity is not None:
            self.prbEntity.exitFromQueue()
        prebattleWindow = getOpenedPrebattleView()
        if prebattleWindow is not None:
            prebattleWindow.destroyWindow()
        self.destroyWindow()
        return

    def _hideGameLoading(self):
        self._uiLogger.logGameLoadingClose()
        self._hideGameLoadingCallbackId = None
        loading.getLoader().idl()
        return

    @UseStoryModeFading()
    def _handleBattleLoading(self, *_):
        self.destroyWindow()


class OnboardingQueueWindow(DestroyWindowOnDisconnectMixin, WindowImpl):
    __slots__ = ()

    def __init__(self, isButtonVisible=False):
        super(OnboardingQueueWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=OnboardingQueueView(isButtonVisible))
