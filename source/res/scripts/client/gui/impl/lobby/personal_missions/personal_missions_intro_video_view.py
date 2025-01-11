# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_intro_video_view.py
import logging
import BigWorld
import Windowing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_intro_video_view_model import PersonalMissionsIntroVideoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.lobby.personal_missions.video_sound_control.video_sound_control import PM3VideoSoundControl
_logger = logging.getLogger(__name__)

class PersonalMissionsIntroVideoView(ViewImpl):
    __slots__ = ('__soundControl',)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsIntroVideoViewModel()
        super(PersonalMissionsIntroVideoView, self).__init__(settings)
        BigWorld.worldDrawEnabled(False)
        self.__soundControl = PM3VideoSoundControl()

    def _finalize(self):
        BigWorld.worldDrawEnabled(True)
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.__soundControl.stop()
        super(PersonalMissionsIntroVideoView, self)._finalize()

    @property
    def viewModel(self):
        return super(PersonalMissionsIntroVideoView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsIntroVideoView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setIsWindowAccessible(Windowing.isWindowAccessible())
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onError, self.__onError), (self.viewModel.onVideoStarted, self.__onVideoStarted))

    def __onClose(self):
        self.destroyWindow()

    def __onError(self, args):
        errorFilePath = str(args.get('errorFilePath', ''))
        _logger.error('Reward video error: %s', errorFilePath)
        self.__onClose()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self.__soundControl.unpause()
        else:
            self.__soundControl.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def __onVideoStarted(self):
        self.__soundControl.start()
        if not Windowing.isWindowAccessible():
            self.__soundControl.pause()


class PersonalMissionsIntroVideoWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PersonalMissionsIntroVideoWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PersonalMissionsIntroVideoView(R.views.lobby.personal_missions.PersonalMissionsIntroVideoView()), parent=parent, layer=WindowLayer.OVERLAY)
