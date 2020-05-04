# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCOutroVideoPage.py
import Windowing
import SoundGroups
import ScaleformFileLoader
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.view.meta.BCOutroVideoPageMeta import BCOutroVideoPageMeta
from tutorial.gui.Scaleform.pop_ups import TutorialDialog
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_ACTIONS, BC_LOG_KEYS
from gui.Scaleform.daapi.view.bootcamp.BCSubtitlesWindow import subtitleDecorator
from gui.Scaleform.framework.entities.view_sound import CommonSoundSpaceSettings

@loggerTarget(logKey=BC_LOG_KEYS.BC_OUTRO_VIDEO)
class BCOutroVideoPage(TutorialDialog, BCOutroVideoPageMeta):
    DEFAULT_MASTER_VOLUME = 0.5
    _HANGAR_OVERLAY_STATE = 'STATE_video_overlay'
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar_video', entranceStates={_HANGAR_OVERLAY_STATE: '{}_on'.format(_HANGAR_OVERLAY_STATE)}, exitStates={_HANGAR_OVERLAY_STATE: '{}_off'.format(_HANGAR_OVERLAY_STATE)}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, settings):
        super(BCOutroVideoPage, self).__init__(settings)
        self.__message = {}
        self.__accessible = True

    def stopVideo(self):
        if not self.__showVideo():
            self.__onFinish()

    def handleError(self, data):
        self.stopVideo()

    def videoFinished(self):
        self.stopVideo()

    @loggerEntry
    def _populate(self):
        super(BCOutroVideoPage, self)._populate()
        movies = [ '/'.join((SCALEFORM_SWF_PATH_V3, m['video-path'])) for m in self.content['messages'] ]
        ScaleformFileLoader.enableStreaming(movies)
        if not self.__showVideo():
            self._stop()
            return
        self.__accessible = Windowing.isWindowAccessible()
        Windowing.addWindowAccessibilitynHandler(self._onAccessibilityChanged)

    def _dispose(self):
        Windowing.removeWindowAccessibilityHandler(self._onAccessibilityChanged)
        ScaleformFileLoader.disableStreaming()
        super(BCOutroVideoPage, self)._dispose()

    def _onAccessibilityChanged(self, isAccessible):
        if self.__accessible == isAccessible:
            return
        self.__accessible = isAccessible
        if self.__accessible:
            self.__onResume()
        else:
            self.__onPause()

    @subtitleDecorator
    def __showVideo(self):
        if self.content['messages']:
            self.__message = self.content['messages'].pop(0)
            movie = self.__message['video-path']
            self.soundManager.playInstantSound(self.__message['event-start'])
            self.as_playVideoS({'source': movie,
             'volume': BCOutroVideoPage.DEFAULT_MASTER_VOLUME * SoundGroups.g_instance.getMasterVolume()})
            return True
        return False

    def __onPause(self):
        self.soundManager.playInstantSound(self.__message['event-pause'])
        self.as_pausePlaybackS()

    def __onResume(self):
        self.soundManager.playInstantSound(self.__message['event-resume'])
        self.as_resumePlaybackS()

    @simpleLog(action=BC_LOG_ACTIONS.SKIP_VIDEO)
    def __onFinish(self):
        self.soundManager.playInstantSound(self.__message['event-stop'])
        self._stop()
