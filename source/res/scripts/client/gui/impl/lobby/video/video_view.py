# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/video/video_view.py
import logging
import Windowing
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.video.video_view_model import VideoViewModel
from gui.impl.lobby.video.video_sound_manager import DummySoundManager
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
_logger = logging.getLogger(__name__)

class VideoView(ViewImpl):
    __slots__ = ('__onVideoStartedHandle', '__onVideoStoppedHandle', '__onVideoClosedHandle', '__isAutoClose', '__soundControl')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.video.video_view_model.VideoView())
        settings.model = VideoViewModel()
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.OVERLAY_VIEW
        super(VideoView, self).__init__(settings)
        self.__onVideoStartedHandle = kwargs.get('onVideoStarted')
        self.__onVideoStoppedHandle = kwargs.get('onVideoStopped')
        self.__onVideoClosedHandle = kwargs.get('onVideoClosed')
        self.__isAutoClose = kwargs.get('isAutoClose')
        self.__soundControl = kwargs.get('soundControl') or DummySoundManager()

    @property
    def viewModel(self):
        return super(VideoView, self).getViewModel()

    def _onLoading(self, videoSource, *args, **kwargs):
        super(VideoView, self)._initialize(*args, **kwargs)
        if videoSource is None:
            _logger.error('__videoSource is not specified!')
            self.__onCloseWindow()
        else:
            self.viewModel.setVideoSource(videoSource)
            self.viewModel.setIsWindowAccessible(Windowing.isWindowAccessible())
            self.viewModel.onCloseBtnClick += self.__onCloseWindow
            self.viewModel.onVideoStarted += self.__onVideoStarted
            self.viewModel.onVideoStopped += self.__onVideoStopped
            Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        return

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseWindow
        self.viewModel.onVideoStarted -= self.__onVideoStarted
        self.viewModel.onVideoStopped -= self.__onVideoStopped
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        if self.__onVideoClosedHandle is not None:
            self.__onVideoClosedHandle()
            self.__onVideoClosedHandle = None
        self.__soundControl.stop()
        self.__soundControl = DummySoundManager()
        return

    def __onCloseWindow(self, _=None):
        self.destroyWindow()

    def __onVideoStarted(self, _=None):
        if self.__onVideoStartedHandle is not None:
            self.__onVideoStartedHandle()
            self.__onVideoStartedHandle = None
        self.__soundControl.start()
        return

    def __onVideoStopped(self, _=None):
        if self.__onVideoStoppedHandle is not None:
            self.__onVideoStoppedHandle()
            self.__onVideoStoppedHandle = None
        self.__soundControl.stop()
        if self.__isAutoClose:
            self.destroyWindow()
        return

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self.__soundControl.unpause()
        else:
            self.__soundControl.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)


class VideoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(VideoViewWindow, self).__init__(content=VideoView(*args, **kwargs), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return
