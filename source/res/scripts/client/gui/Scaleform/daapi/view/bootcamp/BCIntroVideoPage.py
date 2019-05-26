# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCIntroVideoPage.py
import ScaleformFileLoader
from bc_intro_page import BCIntroPage, INTRO_HIGHLIGHT_TYPE
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
_DEFAULT_VIDEO_BUFFERING_TIME = 0.0

class BCIntroVideoPage(BCIntroPage, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, settings):
        super(BCIntroVideoPage, self).__init__(settings)
        self._movieFile = settings.get('video', '')
        self._backgroundVideo = settings.get('backgroundVideo', '')
        self._backgroundVideoBufferTime = settings.get('bufferTime', _DEFAULT_VIDEO_BUFFERING_TIME)
        self._backgroundMusicStartEvent = settings.get('backgroundMusicStartEvent', '')
        self._backgroundMusicStopEvent = settings.get('backgroundMusicStopEvent', '')
        self._backgroundMusicPauseEvent = settings.get('backgroundMusicPauseEvent', '')
        self._backgroundMusicResumeEvent = settings.get('backgroundMusicResumeEvent', '')
        self._videoPlayerVisible = True
        self._goToBattleEvent = g_bootcampEvents.onBootcampGoNext
        self._delayVideoLoaded = False
        self._started = False

    def onIntroVideoLoaded(self):
        if self._started:
            self._onIntroVideoLoaded()
        else:
            self._delayVideoLoaded = True

    def stopVideo(self):
        self._onFinish()

    def onArenaStarted(self):
        self.destroy()

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)

    def _getVideoFiles(self):
        return [ '/'.join((SCALEFORM_SWF_PATH_V3, videoName)) for videoName in (self._movieFile, self._backgroundVideo) if videoName ]

    def _populate(self):
        videoFiles = self._getVideoFiles()
        if videoFiles:
            ScaleformFileLoader.enableStreaming(videoFiles)
        g_bootcampEvents.onArenaStarted += self.onArenaStarted
        g_bootcampEvents.onIntroVideoLoaded += self.onIntroVideoLoaded
        self.sessionProvider.addArenaCtrl(self)
        super(BCIntroVideoPage, self)._populate()

    def _dispose(self):
        if self._getVideoFiles():
            ScaleformFileLoader.disableStreaming()
        g_bootcampEvents.onIntroVideoLoaded -= self.onIntroVideoLoaded
        g_bootcampEvents.onArenaStarted -= self.onArenaStarted
        self.sessionProvider.removeArenaCtrl(self)
        super(BCIntroVideoPage, self)._dispose()

    def _onFinish(self):
        g_bootcampEvents.onIntroVideoStop()

    def _start(self):
        super(BCIntroVideoPage, self)._start()
        self._started = True
        if self._delayVideoLoaded:
            self._onIntroVideoLoaded()

    def _onIntroVideoLoaded(self):
        self.as_loadedS()
        if self._shouldHighlight(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, True)
        if self._isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, False)
