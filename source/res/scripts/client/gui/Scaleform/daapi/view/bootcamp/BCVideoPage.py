# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCVideoPage.py
import functools
import BigWorld
import Windowing
import SoundGroups
import ScaleformFileLoader
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.view.meta.BCOutroVideoPageMeta import BCOutroVideoPageMeta
from sound_gui_manager import CommonSoundSpaceSettings
from bootcamp.subtitles.decorators import subtitleDecorator

class _CallbackDelayer(object):

    def __init__(self, delay, func):
        super(_CallbackDelayer, self).__init__()
        self.__callbackTime = delay
        self.__function = func
        self.__callbackID = None
        self.__startTime = 0.0
        return

    def startCallback(self):
        if self.__callbackID is None:
            self.__setTime()
            self.__addCallback()
        return

    def stopCallback(self):
        if self.__callbackID is not None:
            self.__cancelCallback()
            self.__resetTime()
        return

    def cancelCallback(self):
        self.__cancelCallback()
        self.__function = None
        return

    def __setTime(self):
        self.__startTime = BigWorld.time()

    def __resetTime(self):
        self.__callbackTime -= BigWorld.time() - self.__startTime

    def __addCallback(self):
        if self.__callbackTime < 0.0:
            self.__handleCallback(self.__callbackTime)
            return
        self.__callbackID = BigWorld.callback(self.__callbackTime, functools.partial(self.__handleCallback, 0.0))

    def __cancelCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __handleCallback(self, delay):
        self.__function(delay)
        self.__function = None
        self.__callbackID = None
        return


class BCVideoPage(BCOutroVideoPageMeta):
    _DEFAULT_MASTER_VOLUME = 1.0
    _ACCESSIBILITY_MINTIME = 0.1
    _HANGAR_OVERLAY_STATE = 'STATE_video_overlay'
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar_video', entranceStates={_HANGAR_OVERLAY_STATE: '{}_on'.format(_HANGAR_OVERLAY_STATE)}, exitStates={_HANGAR_OVERLAY_STATE: '{}_off'.format(_HANGAR_OVERLAY_STATE)}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, settings):
        super(BCVideoPage, self).__init__(settings)
        self._message = {}
        self._keypoints = []
        self.__accessible = True
        self.__soundDelayer = None
        self.__pauseDelayerID = None
        return

    def stopVideo(self):
        if not self.__showVideo():
            self._onFinish()

    def handleError(self, data):
        self.stopVideo()

    def videoFinished(self):
        self.stopVideo()

    def _populate(self):
        super(BCVideoPage, self)._populate()
        movies = [ '/'.join((SCALEFORM_SWF_PATH_V3, m['video-path'])) for m in self.content['messages'] ]
        ScaleformFileLoader.enableStreaming(movies)
        self.stopVideo()
        self.__accessible = Windowing.isWindowAccessible()
        Windowing.addWindowAccessibilitynHandler(self._onAccessibilityChanged)

    def _dispose(self):
        Windowing.removeWindowAccessibilityHandler(self._onAccessibilityChanged)
        ScaleformFileLoader.disableStreaming()
        super(BCVideoPage, self)._dispose()

    def _onAccessibilityChanged(self, isAccessible):
        if self.__accessible == isAccessible:
            return
        else:
            self.__accessible = isAccessible
            if isAccessible:
                if self.__pauseDelayerID is not None:
                    BigWorld.cancelCallback(self.__pauseDelayerID)
                    self.__pauseDelayerID = None
                    return
                self.__onResume()
            else:
                self.__pauseDelayerID = BigWorld.callback(self._ACCESSIBILITY_MINTIME, self.__onPause)
            return

    def __showVideo(self):
        if self.content['messages']:
            self._message = self.content['messages'].pop(0)
            movie = self._message['video-path']
            self.soundManager.playInstantSound(self._message['event-start'])
            self.as_playVideoS({'source': movie,
             'fitToScreen': self._message['video-fit-to-screen'] == 'true',
             'volume': self._DEFAULT_MASTER_VOLUME * SoundGroups.g_instance.getMasterVolume()})
            if self.content['voiceovers']:
                self._keypoints = [ (float(point['keypoint']) if 'keypoint' in point and point['keypoint'] else 0.0) for point in self.content['voiceovers'] if point['voiceover'] ]
                self.__addKeyPoint(0.0)
            return True
        return False

    @subtitleDecorator
    def playNotification(self, delay):
        self.__soundDelayer = None
        self.__addKeyPoint(delay)
        return

    def __addKeyPoint(self, delay):
        if self._keypoints:
            delayTime = self._keypoints.pop(0)
            self.__soundDelayer = _CallbackDelayer(delayTime + delay, self.playNotification)
            self.__soundDelayer.startCallback()

    def __onPause(self):
        self.soundManager.playInstantSound(self._message['event-pause'])
        self.as_pausePlaybackS()
        self.__pauseDelayerID = None
        if self.__soundDelayer is not None:
            self.__soundDelayer.stopCallback()
        return

    def __onResume(self):
        self.soundManager.playInstantSound(self._message['event-resume'])
        self.as_resumePlaybackS()
        if self.__soundDelayer is not None:
            self.__soundDelayer.startCallback()
        return

    def _onFinish(self):
        self.soundManager.playInstantSound(self._message['event-stop'])
        if self.__pauseDelayerID is not None:
            BigWorld.cancelCallback(self.__pauseDelayerID)
            self.__pauseDelayerID = None
        if self.__soundDelayer is not None:
            self.__soundDelayer.cancelCallback()
            self.__soundDelayer = None
        self._onDestroy()
        return

    def _onDestroy(self):
        self.destroy()
