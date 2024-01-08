# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/video/video_view.py
import logging
import Windowing
import BigWorld
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.video.video_view_model import VideoViewModel
from gui.impl.lobby.video.video_sound_manager import DummySoundManager
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.Scaleform.Waiting import Waiting
from gui.sounds.filters import switchVideoOverlaySoundFilter
from helpers import getClientLanguage, dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.app_loader import IAppLoader
_logger = logging.getLogger(__name__)

class _SubtitlesLanguages(CONST_CONTAINER):
    CS = 1
    DE = 2
    EN = 3
    ES = 4
    FR = 5
    ITA = 6
    JA = 7
    KO = 8
    LATAM = 9
    PL = 10
    ptBR = 11
    ZHSG = 12
    TH = 13
    TR = 14
    ZHTW = 15


_SUBTITLE_TO_LOCALES_MAP = {_SubtitlesLanguages.CS: {'cs'},
 _SubtitlesLanguages.DE: {'de'},
 _SubtitlesLanguages.EN: {'bg',
                          'da',
                          'el',
                          'en',
                          'et',
                          'fi',
                          'hr',
                          'hu',
                          'id',
                          'lt',
                          'lv',
                          'nl',
                          'no',
                          'pt',
                          'ro',
                          'sr',
                          'sv',
                          'vi'},
 _SubtitlesLanguages.ES: {'es'},
 _SubtitlesLanguages.FR: {'fr'},
 _SubtitlesLanguages.ITA: {'it'},
 _SubtitlesLanguages.JA: {'ja'},
 _SubtitlesLanguages.KO: {'ko'},
 _SubtitlesLanguages.LATAM: {'es_ar'},
 _SubtitlesLanguages.PL: {'pl'},
 _SubtitlesLanguages.ptBR: {'pt_br'},
 _SubtitlesLanguages.TH: {'th'},
 _SubtitlesLanguages.TR: {'tr'},
 _SubtitlesLanguages.ZHTW: {'zh_tw'},
 _SubtitlesLanguages.ZHSG: {'zh_sg', 'zh_cn'}}
_LOCALE_TO_SUBTITLE_MAP = {loc:subID for subID, locales in _SUBTITLE_TO_LOCALES_MAP.iteritems() for loc in locales}
_LAYERS = [WindowLayer.OVERLAY,
 WindowLayer.CURSOR,
 WindowLayer.WAITING,
 WindowLayer.SERVICE_LAYOUT]

class VideoView(ViewImpl):
    __slots__ = ('__onVideoStartedHandle', '__onVideoStoppedHandle', '__onVideoClosedHandle', '__isAutoClose', '__soundControl', '__previouslyVisibleLayers', '__app')
    __appFactory = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.video.video_view.VideoView())
        settings.model = VideoViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(VideoView, self).__init__(settings)
        self.__onVideoStartedHandle = kwargs.get('onVideoStarted')
        self.__onVideoStoppedHandle = kwargs.get('onVideoStopped')
        self.__onVideoClosedHandle = kwargs.get('onVideoClosed')
        self.__isAutoClose = kwargs.get('isAutoClose')
        self.__soundControl = kwargs.get('soundControl') or DummySoundManager()
        self.__previouslyVisibleLayers = []
        self.__app = self.__appFactory.getApp()

    @property
    def viewModel(self):
        return super(VideoView, self).getViewModel()

    def _onLoading(self, videoSource, *args, **kwargs):
        super(VideoView, self)._onLoading(*args, **kwargs)
        if videoSource is None:
            _logger.error('__videoSource is not specified!')
        else:
            self.viewModel.setVideoSource(videoSource)
            language = getClientLanguage()
            self.viewModel.setSubtitleTrack(_LOCALE_TO_SUBTITLE_MAP.get(language, 0))
            self.viewModel.setIsWindowAccessible(Windowing.isWindowAccessible())
            g_playerEvents.onAccountBecomeNonPlayer += self.__removeClosedHandle
            Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
            switchVideoOverlaySoundFilter(on=True)
        return

    def _onLoaded(self, *args, **kwargs):
        Waiting.suspend(id(self))

    def _initialize(self, *args, **kwargs):
        super(VideoView, self)._initialize(*args, **kwargs)
        self.__hideBack()

    def _getEvents(self):
        return ((self.viewModel.onCloseBtnClick, self.__onCloseWindow),
         (self.viewModel.onVideoStarted, self.__onVideoStarted),
         (self.viewModel.onVideoStopped, self.__onVideoStopped),
         (self.viewModel.onLoadError, self.__onLoadError))

    def _finalize(self):
        Waiting.resume(id(self))
        self.__showBack()
        g_playerEvents.onAccountBecomeNonPlayer -= self.__removeClosedHandle
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        if self.__onVideoClosedHandle is not None:
            self.__onVideoClosedHandle()
            self.__onVideoClosedHandle = None
        self.__soundControl.stop()
        self.__soundControl = DummySoundManager()
        self.__app = None
        self.__previouslyVisibleLayers = None
        switchVideoOverlaySoundFilter(on=False)
        return

    def __onCloseWindow(self, _=None):
        self.destroyWindow()

    def __removeClosedHandle(self):
        self.__onVideoClosedHandle = None
        return

    def __onVideoStarted(self, _=None):
        if self.__onVideoStartedHandle is not None:
            self.__onVideoStartedHandle()
            self.__onVideoStartedHandle = None
        self.__soundControl.start()
        if not self.viewModel.getIsWindowAccessible():
            self.__soundControl.pause()
        return

    def __onVideoStopped(self, _=None):
        if self.__onVideoStoppedHandle is not None:
            self.__onVideoStoppedHandle()
            self.__onVideoStoppedHandle = None
        self.__soundControl.stop()
        if self.__isAutoClose:
            self.destroyWindow()
        return

    def __onLoadError(self, _=None):
        self.__onVideoStopped()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self.__soundControl.unpause()
        else:
            self.__soundControl.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def __hideBack(self):
        BigWorld.worldDrawEnabled(False)
        if self.__app is not None:
            containerManager = self.__app.containerManager
            self.__previouslyVisibleLayers = containerManager.getVisibleLayers()
            containerManager.setVisibleLayers(_LAYERS)
        return

    def __showBack(self):
        BigWorld.worldDrawEnabled(True)
        if self.__app is not None:
            self.__app.containerManager.setVisibleLayers(self.__previouslyVisibleLayers)
        return


class VideoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(VideoViewWindow, self).__init__(content=VideoView(*args, **kwargs), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.OVERLAY, decorator=None)
        return
