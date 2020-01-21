# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCIntroVideoPage.py
import ScaleformFileLoader
import WWISE
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
        self._backgroundMusicToLoopEvent = settings.get('backgroundMusicToLoopEvent', '')
        self._goToBattleEvent = g_bootcampEvents.onBootcampGoNext
        self._delaySpaceLoaded = False
        self._started = False

    def stopVideo(self):
        self._onFinish()

    def updateSpaceLoadProgress(self, progress):
        if not self._videoPlayerVisible:
            self.as_updateProgressS(progress)

    def _getVideoFiles(self):
        return [ '/'.join((SCALEFORM_SWF_PATH_V3, videoName)) for videoName in (self._movieFile, self._backgroundVideo) if videoName ]

    def _populate(self):
        videoFiles = self._getVideoFiles()
        if videoFiles:
            ScaleformFileLoader.enableStreaming(videoFiles)
            self._videoPlayerVisible = True
        g_bootcampEvents.onArenaStarted += self._onArenaStarted
        g_bootcampEvents.onBootcampSpaceLoaded += self._onBootcampSpaceLoaded
        self.sessionProvider.addArenaCtrl(self)
        super(BCIntroVideoPage, self)._populate()

    def _dispose(self):
        if self._getVideoFiles():
            ScaleformFileLoader.disableStreaming()
        g_bootcampEvents.onBootcampSpaceLoaded -= self._onBootcampSpaceLoaded
        g_bootcampEvents.onArenaStarted -= self._onArenaStarted
        self.sessionProvider.removeArenaCtrl(self)
        super(BCIntroVideoPage, self)._dispose()

    def _onBootcampSpaceLoaded(self):
        if self._started:
            self._onLoaded()
        else:
            self._delaySpaceLoaded = True

    def _onArenaStarted(self):
        self.destroy()

    def _onFinish(self):
        if self._movieFile and self._backgroundMusicToLoopEvent:
            WWISE.WW_eventGlobal(self._backgroundMusicToLoopEvent)
        g_bootcampEvents.onIntroVideoStop()
        if self._videoPlayerVisible:
            self._showHighlight()

    def _start(self):
        super(BCIntroVideoPage, self)._start()
        self._started = True
        if self._delaySpaceLoaded:
            self._onLoaded()

    def _onLoaded(self):
        self.as_loadedS()
        if not self._videoPlayerVisible:
            self._showHighlight()

    def _showHighlight(self):
        if self._shouldHighlight(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, True)
        if self._isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, False)
