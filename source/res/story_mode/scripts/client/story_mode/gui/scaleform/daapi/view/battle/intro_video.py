# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/intro_video.py
import BattleReplay
import BigWorld
import WWISE
import Windowing
from account_helpers import AccountSettings
from account_helpers.settings_core.settings_constants import SOUND
from gui import g_keyEventHandlers
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.game_loading import loading
from gui.impl import backport
from gui.impl.gen import R
from helpers import i18n, dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.scaleform.daapi.view.meta.IntroVideoMeta import IntroVideoMeta
from story_mode.gui.scaleform.daapi.view.model.intro_video_settings_model import getSettings
from story_mode.gui.shared.event_dispatcher import showPrebattleWindow
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import IntroVideoLogger
from story_mode_common.story_mode_constants import FIRST_MISSION_ID

def sendWWISEEventGlobal(event):
    if event:
        WWISE.WW_eventGlobal(event)


class IntroVideo(IntroVideoMeta, IArenaLoadController):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self):
        super(IntroVideo, self).__init__()
        self._data = getSettings()
        self._uiLogger = IntroVideoLogger()
        self._isVideoStarted = False

    def spaceLoadCompleted(self):
        loading.getLoader().idl()
        if BattleReplay.isPlaying():
            self._storyModeCtrl.goToBattle()
            self.destroy()
        else:
            self.as_loadedS()

    def onVideoStarted(self):
        self._isVideoStarted = True
        self._uiLogger.logVideoStarted()
        self._storyModeCtrl.stopOnboardingMusic()
        self._storyModeCtrl.startOnboardingMusic(self._data.music.start)
        self.soundManager.playSound(self._data.vo)
        g_keyEventHandlers.add(self._handleKeyEvent)

    @UseStoryModeFading(hide=False)
    def onVideoComplete(self):
        self._closeWindow()
        showPrebattleWindow(missionId=FIRST_MISSION_ID)

    def onSkipButtonVisible(self):
        self._uiLogger.logButtonShown(LogButtons.SKIP, once=True)
        self.app.attachCursor()

    def onSkipButtonClicked(self):
        self._uiLogger.logClick(LogButtons.SKIP)
        self.onVideoComplete()

    @property
    def _canVideoBePaused(self):
        return not BigWorld.checkUnattended()

    def _populate(self):
        super(IntroVideo, self)._populate()
        isPausedAfterLoad = False
        if self._canVideoBePaused:
            Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
            if not Windowing.isWindowAccessible():
                isPausedAfterLoad = True
        self.as_setDataS({'skipButtonLabel': backport.text(R.strings.sm_battle.common.skipBtn()),
         'loadingText': backport.text(R.strings.sm_battle.introVideo.loading()),
         'loadingImage': backport.image(R.images.story_mode.gui.maps.icons.queue.back()),
         'video': self._data.videoPath,
         'isPausedAfterLoad': isPausedAfterLoad})
        self._sessionProvider.addArenaCtrl(self)
        if AccountSettings.getSettings(SOUND.SUBTITLES):
            WWISE.WW_addMarkerListener(self._soundMarkerHandler)
        self._storyModeCtrl.startOnboardingMusic()
        self.app.detachCursor()
        self._uiLogger.logOpen()

    def _dispose(self):
        self._sessionProvider.removeArenaCtrl(self)
        if self._canVideoBePaused:
            Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        WWISE.WW_removeMarkerListener(self._soundMarkerHandler)
        g_keyEventHandlers.discard(self._handleKeyEvent)
        self._uiLogger.logClose()
        super(IntroVideo, self)._dispose()

    def _closeWindow(self):
        sendWWISEEventGlobal(self._data.music.stop)
        self.soundManager.stopSound(self._data.vo)
        self.destroy()

    def _onWindowAccessibilityChanged(self, isAccessible):
        if isAccessible:
            self.as_resumePlaybackS()
        else:
            self.as_pausePlaybackS()
        if self._isVideoStarted:
            if isAccessible:
                sendWWISEEventGlobal(self._data.music.resume)
            else:
                sendWWISEEventGlobal(self._data.music.pause)

    def _soundMarkerHandler(self, marker):
        if marker == '#end':
            self.as_setCurrentSubtitleS('')
        elif marker.startswith('#'):
            self.as_setCurrentSubtitleS(i18n.makeString(marker))

    def _handleKeyEvent(self, event):
        if event.isKeyDown() and not event.isRepeatedEvent():
            self.as_handleKeydownS()
