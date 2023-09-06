# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/battle/epilogue_window.py
from functools import partial
import typing
import SoundGroups
from frameworks.wulf import WindowFlags, ViewSettings
from gui.app_loader import app_getter
from gui.impl.gen import R
from gui.impl.pub import WindowImpl, ViewImpl
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.impl.battle.lore_settings_model import getLoreSettings
from story_mode.gui.impl.gen.view_models.views.battle.epilogue_window_view_model import EpilogueWindowViewModel
from story_mode.gui.impl.mixins import DestroyWindowOnDisconnectMixin
from story_mode.gui.shared.event_dispatcher import showCongratulationsWindow, sendViewLoadedEvent
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogWindows, LogButtons
from story_mode.uilogging.story_mode.loggers import WindowLogger
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.application import AppEntry

class EpilogueView(ViewImpl):
    __slots__ = ('_uiLogger',)
    LAYOUT_ID = R.views.story_mode.battle.EpilogueWindow()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _appLoader = dependency.instance(IAppLoader)

    def __init__(self):
        settings = ViewSettings(self.LAYOUT_ID)
        settings.model = EpilogueWindowViewModel()
        super(EpilogueView, self).__init__(settings)
        self._uiLogger = WindowLogger(LogWindows.EPILOGUE)

    @property
    def viewModel(self):
        return super(EpilogueView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(EpilogueView, self)._onLoaded(*args, **kwargs)
        self._uiLogger.logOpen()
        data = getLoreSettings()
        SoundGroups.g_instance.playSound2D(data.epilogue.music)
        SoundGroups.g_instance.playSound2D(data.epilogue.vo)

    def _finalize(self):
        self._uiLogger.logClose()
        super(EpilogueView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onCloseHandler), (self.viewModel.onLoaded, partial(sendViewLoadedEvent, self.LAYOUT_ID)))

    @UseStoryModeFading(hide=False)
    def _onCloseHandler(self):
        self._uiLogger.logClick(LogButtons.CONTINUE)
        if self._storyModeCtrl.needToShowAward:
            showCongratulationsWindow(onClose=self._goToHangarAnimated)
        else:
            self._storyModeCtrl.goToHangar()
        self.destroyWindow()

    @UseStoryModeFading(hide=False)
    def _goToHangarAnimated(self):
        self._appLoader.destroyBattle()
        self._storyModeCtrl.goToHangar()


class EpilogueWindow(DestroyWindowOnDisconnectMixin, WindowImpl):
    __slots__ = ()

    def __init__(self):
        super(EpilogueWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EpilogueView())

    @app_getter
    def app(self):
        return None

    def _onContentReady(self):
        super(EpilogueWindow, self)._onContentReady()
        self.app.attachCursor()
