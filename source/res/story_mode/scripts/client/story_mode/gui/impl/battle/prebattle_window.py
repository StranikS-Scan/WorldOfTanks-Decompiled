# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/battle/prebattle_window.py
from functools import partial
from logging import getLogger
import typing
import BattleReplay
import BigWorld
import SoundGroups
from frameworks.wulf import ViewSettings, WindowFlags
from gui.app_loader import app_getter
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.game_loading import loading
from gui.impl.gen import R
from gui.impl.pub import WindowImpl
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.impl import IGuiLoader
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.impl.base_queue_view import BaseWaitQueueView
from story_mode.gui.impl.battle.lore_settings_model import getLoreSettings
from story_mode.gui.impl.gen.view_models.views.battle.prebattle_window_view_model import PrebattleWindowViewModel
from story_mode.gui.impl.mixins import DestroyWindowOnDisconnectMixin
from story_mode.gui.shared.event_dispatcher import showQueueWindow, sendViewLoadedEvent
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogWindows, LogButtons
from story_mode.uilogging.story_mode.loggers import MissionWindowLogger
from story_mode_common.story_mode_constants import LOGGER_NAME
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.application import AppEntry
_logger = getLogger(LOGGER_NAME)

class PrebattleView(BaseWaitQueueView, IArenaLoadController):
    __slots__ = ('missionId', '_uiLogger', '_missionLoreSettings')
    LAYOUT_ID = R.views.story_mode.battle.PrebattleWindow()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, missionId):
        settings = ViewSettings(self.LAYOUT_ID)
        settings.model = PrebattleWindowViewModel()
        super(PrebattleView, self).__init__(settings)
        self.missionId = missionId
        self._uiLogger = MissionWindowLogger(LogWindows.PRE_BATTLE)
        data = getLoreSettings()
        self._missionLoreSettings = next((mission for mission in data.mission if mission.id == self.missionId), None)
        return

    @property
    def viewModel(self):
        return super(PrebattleView, self).getViewModel()

    @app_getter
    def app(self):
        return None

    def spaceLoadCompleted(self):
        if BattleReplay.isPlaying() or BigWorld.checkUnattended():
            sendViewLoadedEvent(self.LAYOUT_ID)
            self._gotoBattleHandler()
        else:
            self.viewModel.setIsLoading(False)
            self._uiLogger.logButtonShown(LogButtons.BATTLE)

    @UseStoryModeFading(show=False)
    def arenaLoadCompleted(self):
        self.destroyWindow()

    def restart(self):
        self._sessionProvider.addArenaCtrl(self)

    def _onLoading(self, *args, **kwargs):
        super(PrebattleView, self)._onLoading(*args, **kwargs)
        self.viewModel.setMissionNumber(self.missionId)
        self.viewModel.setIsLoading(True)
        self._sessionProvider.addArenaCtrl(self)
        if not BattleReplay.isPlaying() and not BigWorld.checkUnattended():
            self.app.attachCursor()

    def _onLoaded(self, *args, **kwargs):
        super(PrebattleView, self)._onLoaded(*args, **kwargs)
        self._storyModeCtrl.startOnboardingMusic()
        if self._missionLoreSettings is not None:
            SoundGroups.g_instance.playSound2D(self._missionLoreSettings.music)
            SoundGroups.g_instance.playSound2D(self._missionLoreSettings.vo)
        self._uiLogger.logOpen(missionId=self.missionId, info=None if self.viewModel and self.viewModel.getIsLoading() else LogButtons.BATTLE)
        loading.getLoader().idl()
        return

    def _finalize(self):
        self._sessionProvider.removeArenaCtrl(self)
        self._uiLogger.logClose()
        super(PrebattleView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onGotoBattle, self._gotoBattleHandler), (self.viewModel.onLoaded, partial(sendViewLoadedEvent, self.LAYOUT_ID)))

    @UseStoryModeFading(hide=False)
    def _gotoBattleHandler(self):
        self._uiLogger.logClick(LogButtons.BATTLE)
        if self._missionLoreSettings is not None:
            SoundGroups.g_instance.playSound2D(self._missionLoreSettings.battleMusic)
        self.app.detachCursor()
        self.viewModel.setIsLoading(True)
        self._storyModeCtrl.goToBattle()
        return

    @UseStoryModeFading(waitForLayoutReady=R.views.story_mode.common.OnboardingQueueView())
    def _onWaitQueueTimeout(self):
        super(PrebattleView, self)._onWaitQueueTimeout()
        showQueueWindow(isSkipButtonVisible=True)


class PrebattleWindow(DestroyWindowOnDisconnectMixin, WindowImpl):
    __slots__ = ()

    def __init__(self, missionId):
        super(PrebattleWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PrebattleView(missionId=missionId))


def getOpenedPrebattleView():
    uiLoader = dependency.instance(IGuiLoader)
    return None if not uiLoader or not uiLoader.windowsManager else uiLoader.windowsManager.getViewByLayoutID(R.views.story_mode.battle.PrebattleWindow())
