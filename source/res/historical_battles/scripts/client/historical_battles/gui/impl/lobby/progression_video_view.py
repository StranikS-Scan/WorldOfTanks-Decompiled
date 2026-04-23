# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/progression_video_view.py
import logging
import BigWorld
import Windowing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.sounds.filters import switchVideoOverlaySoundFilter
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby import progression_video_view_model
from historical_battles.gui.sounds import progression_video_sound_control
from skeletons.gui.app_loader import IAppLoader
_logger = logging.getLogger(__name__)
_LAYERS = [WindowLayer.OVERLAY,
 WindowLayer.CURSOR,
 WindowLayer.WAITING,
 WindowLayer.SERVICE_LAYOUT]

class ProgressionVideoView(ViewImpl):
    __slots__ = ('__soundControl', '__videoRes', '__previouslyVisibleLayers', '__app', '__worldDrawStatus')
    __appFactory = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID, videoName):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = progression_video_view_model.ProgressionVideoViewModel()
        super(ProgressionVideoView, self).__init__(settings)
        self.__soundControl = progression_video_sound_control.HBProgressionVideoSoundControl(videoName)
        self.__videoRes = videoName
        self.__previouslyVisibleLayers = []
        self.__app = self.__appFactory.getApp()
        self.__worldDrawStatus = True

    def _initialize(self, *args, **kwargs):
        super(ProgressionVideoView, self)._initialize(*args, **kwargs)
        self.__hideBack()
        switchVideoOverlaySoundFilter(on=True)

    def _finalize(self):
        switchVideoOverlaySoundFilter(on=False)
        self.__showBack()
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.__soundControl.stop()
        self.__app = None
        self.__previouslyVisibleLayers = None
        super(ProgressionVideoView, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(ProgressionVideoView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ProgressionVideoView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setIsWindowAccessible(Windowing.isWindowAccessible())
            vm.setVideoName(self.__videoRes)
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onError, self.__onError),
         (self.viewModel.onVideoStarted, self.__onVideoStarted),
         (self.viewModel.onVideoEnded, self.__onVideoEnded))

    def __hideBack(self):
        self.__worldDrawStatus = BigWorld.worldDrawEnabled()
        BigWorld.worldDrawEnabled(False)
        if self.__app is not None:
            containerManager = self.__app.containerManager
            self.__previouslyVisibleLayers = containerManager.getVisibleLayers()
            containerManager.setVisibleLayers(_LAYERS)
        return

    def __showBack(self):
        BigWorld.worldDrawEnabled(self.__worldDrawStatus)
        if self.__app is not None:
            self.__app.containerManager.setVisibleLayers(self.__previouslyVisibleLayers)
        return

    def __onClose(self):
        self.destroyWindow()

    def __onError(self, args):
        errorFilePath = str(args.get('errorFilePath', ''))
        _logger.error('Historical battles progression video error: %s', errorFilePath)
        self.__onClose()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        isSoundStarted = self.__soundControl.isSoundStarted()
        if isSoundStarted:
            if isWindowAccessible:
                self.__soundControl.unpause()
            else:
                self.__soundControl.pause()
        else:
            self.__onVideoStarted()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def __onVideoStarted(self):
        self.__soundControl.start()
        if not Windowing.isWindowAccessible():
            self.__soundControl.pause()

    def __onVideoEnded(self):
        self.__soundControl.stop()
        self.destroyWindow()


class ProgressionVideoWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, videoName, parent=None):
        super(ProgressionVideoWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ProgressionVideoView(R.views.historical_battles.lobby.ProgressionVideoView(), videoName), parent=parent, layer=WindowLayer.OVERLAY)
