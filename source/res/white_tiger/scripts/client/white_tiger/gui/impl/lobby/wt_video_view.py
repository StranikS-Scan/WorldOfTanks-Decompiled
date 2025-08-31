# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_video_view.py
import logging
import Windowing
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.lobby.video.video_sound_manager import DummySoundManager
from gui.sounds.filters import switchVideoOverlaySoundFilter
from white_tiger.gui.impl.gen.view_models.views.lobby.video_view_model import VideoViewModel
_logger = logging.getLogger(__name__)

class WTVideoView(ViewImpl):
    __slots__ = ('__videoName', '__soundControl', '__onVideoClosedHandle')

    def __init__(self, layoutID, videoName, soundController, onVideoClose):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = VideoViewModel()
        super(WTVideoView, self).__init__(settings)
        self.__videoName = videoName
        self.__onVideoClosedHandle = onVideoClose
        self.__soundControl = soundController

    @property
    def viewModel(self):
        return super(WTVideoView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WTVideoView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setIsWindowAccessible(Windowing.isWindowAccessible())
            vm.setVideoName(self.__videoName)
        g_playerEvents.onAccountBecomeNonPlayer += self.__removeClosedHandle
        Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
        switchVideoOverlaySoundFilter(on=True)

    def _finalize(self):
        g_playerEvents.onAccountBecomeNonPlayer -= self.__removeClosedHandle
        Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        if self.__onVideoClosedHandle is not None:
            self.__onVideoClosedHandle()
            self.__onVideoClosedHandle = None
        self.__soundControl.stop()
        self.__soundControl = DummySoundManager()
        switchVideoOverlaySoundFilter(on=False)
        super(WTVideoView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onVideoStarted, self.__onVideoStarted), (self.viewModel.onClose, self.__onClose), (self.viewModel.onError, self.__onError))

    def __removeClosedHandle(self):
        self.__onVideoClosedHandle = None
        return

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self.__soundControl.unpause()
        else:
            self.__soundControl.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def __onVideoStarted(self, _=None):
        self.__soundControl.start()
        if not self.viewModel.getIsWindowAccessible():
            self.__soundControl.pause()

    def __onClose(self):
        self.destroyWindow()

    def __onError(self, args):
        errorFilePath = str(args.get('errorFilePath', ''))
        _logger.error('White tiger video error: %s', errorFilePath)
        self.destroyWindow()
