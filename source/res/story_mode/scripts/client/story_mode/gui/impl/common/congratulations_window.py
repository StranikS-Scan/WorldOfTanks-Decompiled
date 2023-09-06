# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/common/congratulations_window.py
from functools import partial
import typing
from frameworks.wulf import WindowFlags, ViewSettings, View
from gui.impl.gen import R
from gui.impl.pub import WindowImpl, ViewImpl
from helpers import dependency
from story_mode.gui.impl.gen.view_models.views.common.congratulations_window_view_model import CongratulationsWindowViewModel
from story_mode.gui.impl.gen.view_models.views.common.medal_tooltip_view_model import MedalTooltipViewModel
from story_mode.gui.impl.mixins import DestroyWindowOnDisconnectMixin
from story_mode.gui.shared.event_dispatcher import sendViewLoadedEvent
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogWindows, LogButtons
from story_mode.uilogging.story_mode.loggers import WindowLogger
from wg_async import wg_async, wg_await, forwardAsFuture

class CongratulationsView(ViewImpl):
    __slots__ = ('_onClose', '_isCloseVisible', '_uiLogger')
    LAYOUT_ID = R.views.story_mode.common.CongratulationsWindow()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, isCloseVisible=False, onClose=None):
        settings = ViewSettings(self.LAYOUT_ID)
        settings.model = CongratulationsWindowViewModel()
        super(CongratulationsView, self).__init__(settings)
        self._onClose = onClose
        self._isCloseVisible = isCloseVisible
        self._uiLogger = WindowLogger(LogWindows.CONGRATULATIONS)

    @property
    def viewModel(self):
        return super(CongratulationsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.story_mode.common.MedalTooltip():
            model = MedalTooltipViewModel()
            model.setConditions(R.strings.achievements.onboardingMedal_condition())
            model.setDescription(R.strings.achievements.onboardingMedal_descr())
            model.setName(R.strings.achievements.onboardingMedal())
            model.setImage(R.images.gui.maps.icons.achievement.big.onboardingMedal())
            return View(ViewSettings(contentID, model=model))
        return super(CongratulationsView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(CongratulationsView, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsCloseVisible(self._isCloseVisible)
        self.viewModel.setIsOnboarding(self._storyModeCtrl.isOnboarding)
        self._storyModeCtrl.awardShown()

    def _onLoaded(self, *args, **kwargs):
        super(CongratulationsView, self)._onLoaded(*args, **kwargs)
        self._uiLogger.logOpen(info=LogButtons.CLOSE if self.viewModel and self.viewModel.getIsCloseVisible() else None)
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self._closeHandler), (self.viewModel.onLoaded, partial(sendViewLoadedEvent, self.LAYOUT_ID)))

    def _finalize(self):
        self._onClose = None
        self._uiLogger.logClose()
        super(CongratulationsView, self)._finalize()
        return

    @wg_async
    def _closeHandler(self):
        self._uiLogger.logClick(LogButtons.CONTINUE)
        onClose = self._onClose
        if callable(onClose):
            yield wg_await(forwardAsFuture(onClose()))
        self.destroyWindow()


class CongratulationsWindow(DestroyWindowOnDisconnectMixin, WindowImpl):
    __slots__ = ()

    def __init__(self, isCloseVisible=False, onClose=None):
        super(CongratulationsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CongratulationsView(isCloseVisible, onClose))
