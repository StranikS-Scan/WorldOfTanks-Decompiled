# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/video_view.py
from frameworks.wulf import ViewFlags, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.video_view_model import VideoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow

class VideoView(ViewImpl):
    __slots__ = ('__onVideoStopHandler',)

    def __init__(self, *args, **kwargs):
        super(VideoView, self).__init__(R.views.lobby.video_view.VideoView(), ViewFlags.OVERLAY_VIEW, VideoViewModel, *args, **kwargs)
        self.__onVideoStopHandler = None
        return

    @property
    def viewModel(self):
        return super(VideoView, self).getViewModel()

    def _initialize(self, videoSource, onVideoStartHandler=None, onVideoStopHandler=None):
        super(VideoView, self)._initialize()
        self.viewModel.setVideoSource(videoSource)
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onVideoStopped += self.__onVideoStopped
        self.__onVideoStopHandler = onVideoStopHandler
        if onVideoStartHandler is not None:
            onVideoStartHandler()
        return

    def _finalize(self):
        self.__callVideoStopHandler()
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onVideoStopped -= self.__onVideoStopped
        super(VideoView, self)._finalize()

    def __onCloseBtnClick(self):
        self.destroyWindow()

    def __onVideoStopped(self, *_):
        self.__callVideoStopHandler()

    def __callVideoStopHandler(self):
        if self.__onVideoStopHandler is not None:
            self.__onVideoStopHandler()
            self.__onVideoStopHandler = None
        return


class VideoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, videoSource, parent=None, onVideoStartHandler=None, onVideoStopHandler=None):
        super(VideoViewWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW, decorator=None, content=VideoView(videoSource, onVideoStartHandler, onVideoStopHandler), parent=parent)
        return
