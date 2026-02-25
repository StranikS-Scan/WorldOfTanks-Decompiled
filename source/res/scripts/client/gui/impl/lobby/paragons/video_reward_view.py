# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/video_reward_view.py
import logging
import Windowing
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.gen.view_models.views.lobby.paragons.video_reward_view_model import VideoRewardViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from tutorial.control.game_vars import getVehicleByIntCD
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
_logger = logging.getLogger(__name__)

class VideoRewardView(ViewImpl):
    __slots__ = ('__vehicleCD', '__closeCallback')

    def __init__(self, layoutID, vehicleCD, closeCallback):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = VideoRewardViewModel()
        self.__vehicleCD = vehicleCD
        self.__closeCallback = closeCallback
        super(VideoRewardView, self).__init__(settings)

    def _finalize(self):
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        super(VideoRewardView, self)._finalize()

    @property
    def viewModel(self):
        return super(VideoRewardView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VideoRewardView, self)._onLoading(*args, **kwargs)
        vehicle = getVehicleByIntCD(self.__vehicleCD)
        with self.viewModel.transaction() as model:
            fillVehicleInfo(model, vehicle)
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onError, self.__onError))

    def __onClose(self):
        closeCallback = self.__closeCallback
        self.destroyWindow()
        if closeCallback is not None:
            closeCallback()
        return

    @args2params(str)
    def __onError(self, errorFilePath):
        _logger.error('Reward video error: %s', errorFilePath)
        self.destroyWindow()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        self.viewModel.setIsWindowAccessible(isWindowAccessible)


class VideoRewardViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, vehicleCD, parent=None, closeCallback=None):
        super(VideoRewardViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=VideoRewardView(R.views.lobby.paragons.VideoRewardView(), vehicleCD, closeCallback), parent=parent, layer=WindowLayer.OVERLAY)
