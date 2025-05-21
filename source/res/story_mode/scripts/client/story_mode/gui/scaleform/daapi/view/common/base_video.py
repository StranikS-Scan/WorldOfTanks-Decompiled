# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/common/base_video.py
from logging import getLogger
import BigWorld
import SoundGroups
import typing
import WWISE
import Windowing
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.settings_core.settings_constants import SOUND
from gui import g_keyEventHandlers
from gui.impl import backport
from gui.impl.gen import R
from helpers import i18n, dependency
from story_mode.gui.scaleform.daapi.view.meta.IntroVideoMeta import IntroVideoMeta
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode_common.story_mode_constants import LOGGER_NAME
_logger = getLogger(LOGGER_NAME)
if typing.TYPE_CHECKING:
    from story_mode.gui.scaleform.daapi.view.model.video_settings_model import VideoSettingsModel
    from story_mode.uilogging.story_mode.loggers import BaseVideoLogger

def sendWWISEEventGlobal(event):
    if event:
        WWISE.WW_eventGlobal(event)


class BaseVideo(IntroVideoMeta):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, ctx):
        super(BaseVideo, self).__init__(ctx)
        self._uiLogger = self._getLogger()
        self._isVideoStarted = False
        self._missionId = ctx.get('missionId')
        if self._missionId is None:
            _logger.error('missionId is None')
            return
        else:
            data = self._getSettings()
            if data is None:
                _logger.error('data not exists for OutroVideoSettingsModel')
                return
            self._videoSettings = next((mission for mission in data.missions if mission.id == self._missionId), None)
            if self._videoSettings is None:
                _logger.error('_videoSettings is None for mission ID=%s', self._missionId)
            return

    def onVideoStarted(self):
        self._isVideoStarted = True
        self._uiLogger.logVideoStarted(self._missionId)
        if self._videoSettings is not None:
            hasState = self._videoSettings.music.group and self._videoSettings.music.state
            if not hasState:
                self._storyModeCtrl.stopMusic(True)
            if self._videoSettings.music.start:
                self.soundManager.playSound(self._videoSettings.music.start)
            if hasState:
                WWISE.WW_setState(self._videoSettings.music.group, self._videoSettings.music.state)
            self.soundManager.playSound(self._videoSettings.vo)
        g_keyEventHandlers.add(self._handleKeyEvent)
        return

    def onVideoComplete(self):
        self._closeWindow()

    def onSkipButtonVisible(self):
        self._uiLogger.logButtonShown(LogButtons.SKIP, once=True, state=str(self._missionId))
        self.app.attachCursor()

    def onSkipButtonClicked(self):
        self._uiLogger.logClick(LogButtons.SKIP, state=str(self._missionId))
        self.onVideoComplete()

    def _getSettings(self):
        raise NotImplementedError

    def _getLogger(self):
        raise NotImplementedError

    def _getLoadingImage(self):
        return backport.image(R.images.story_mode.gui.maps.icons.queue.back())

    @property
    def _canVideoBePaused(self):
        return not BigWorld.checkUnattended()

    def _populate(self):
        super(BaseVideo, self)._populate()
        g_playerEvents.onDisconnected += self._disconnectHandler
        isPausedAfterLoad = False
        if self._canVideoBePaused:
            Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
            if not Windowing.isWindowAccessible():
                isPausedAfterLoad = True
        self.as_setDataS({'skipButtonLabel': backport.text(R.strings.sm_battle.common.skipBtn()),
         'loadingText': backport.text(R.strings.sm_battle.introVideo.loading()),
         'loadingImage': self._getLoadingImage(),
         'video': self._videoSettings.videoPath,
         'isPausedAfterLoad': isPausedAfterLoad})
        if self._videoSettings is not None:
            if not self._videoSettings.music.group and not self._videoSettings.music.state:
                self._storyModeCtrl.startMusic()
        if AccountSettings.getSettings(SOUND.SUBTITLES):
            WWISE.WW_addMarkerListener(self._soundMarkerHandler)
        self.app.detachCursor()
        self._uiLogger.logOpen(state=str(self._missionId))
        return

    def _dispose(self):
        g_playerEvents.onDisconnected -= self._disconnectHandler
        if self._canVideoBePaused:
            Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        WWISE.WW_removeMarkerListener(self._soundMarkerHandler)
        g_keyEventHandlers.discard(self._handleKeyEvent)
        self._uiLogger.logClose(state=str(self._missionId))
        super(BaseVideo, self)._dispose()

    def _closeWindow(self):
        self.soundManager.stopSound(self._videoSettings.vo)
        if self._videoSettings.playSoundOnClose is not None:
            SoundGroups.g_instance.playSound2D(self._videoSettings.playSoundOnClose)
        self.destroy()
        return

    def _onWindowAccessibilityChanged(self, isAccessible):
        if isAccessible:
            self.as_resumePlaybackS()
        else:
            self.as_pausePlaybackS()
        if self._isVideoStarted:
            if isAccessible:
                sendWWISEEventGlobal(self._videoSettings.music.resume)
            else:
                sendWWISEEventGlobal(self._videoSettings.music.pause)

    def _soundMarkerHandler(self, marker):
        if marker == '#end':
            self.as_setCurrentSubtitleS('')
        elif marker.startswith('#'):
            self.as_setCurrentSubtitleS(i18n.makeString(marker))

    def _handleKeyEvent(self, event):
        if event.isKeyDown() and not event.isRepeatedEvent():
            self.as_handleKeydownS()

    def _disconnectHandler(self):
        self.destroy()
