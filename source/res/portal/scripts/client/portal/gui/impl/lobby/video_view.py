# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/video_view.py
import BigWorld
import SoundGroups
import Windowing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from portal.gui.impl.gen.view_models.views.lobby.video_view_model import VideoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from portal.sounds.sound_constants import PORTAL_VIDEO_VIEW_SOUND_SPACE, VideoSound
from portal.sounds.sound_helpers import play2DSound, setCutSceneSoundGlobalEvent
_LAYERS = [WindowLayer.OVERLAY,
 WindowLayer.CURSOR,
 WindowLayer.WAITING,
 WindowLayer.SERVICE_LAYOUT]

class VideoView(ViewImpl):
    __slots__ = ('__videoName',)
    _COMMON_SOUND_SPACE = PORTAL_VIDEO_VIEW_SOUND_SPACE

    def __init__(self, layoutID, videoName=''):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = VideoViewModel()
        self.__videoName = videoName
        super(VideoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VideoView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VideoView, self)._onLoading(*args, **kwargs)
        self._updateModel()
        Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            model.setVideoName(self.__videoName)

    def _finalize(self):
        self.__showBack()
        Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)

    def _initialize(self, *args, **kwargs):
        super(VideoView, self)._initialize(*args, **kwargs)
        self.__hideBack()

    def __onClose(self, *args, **kwArgs):
        play2DSound(VideoSound.STOP)
        self.destroyWindow()

    def __onVideoStarted(self, *args, **kwArgs):
        soundGroupInstance = SoundGroups.g_instance
        soundGroupInstance.updateVideoVolume()
        play2DSound(VideoSound.VIDEO[self.__videoName])

    def __onError(self, *args, **kwArgs):
        play2DSound(VideoSound.STOP)

    def __hideBack(self):
        BigWorld.worldDrawEnabled(False)

    def __showBack(self):
        BigWorld.worldDrawEnabled(True)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onVideoStarted, self.__onVideoStarted), (self.viewModel.onError, self.__onError))

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        state = VideoSound.PAUSE
        if isWindowAccessible:
            state = VideoSound.RESUME
        setCutSceneSoundGlobalEvent(state)
        self.viewModel.setIsWindowAccessible(isWindowAccessible)


class VideoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, videoName='', parent=None):
        super(VideoViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=VideoView(R.views.portal.lobby.VideoView(), videoName=videoName), parent=parent, layer=WindowLayer.OVERLAY)
