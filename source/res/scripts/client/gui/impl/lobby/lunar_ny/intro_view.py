# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/intro_view.py
import Settings
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LUNAR_NY_INTRO_VIEWED, IS_LUNAR_NY_INTRO_VIDEO_VIEWED
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.intro_view_model import IntroViewModel
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showVideoView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from lunar_ny.lunar_ny_sounds import LunarNYVideoStartStopHandler, PausedSoundManager

class IntroView(ViewImpl):
    __slots__ = ('__videoStartStopHandler',)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = IntroViewModel()
        super(IntroView, self).__init__(settings)
        self.__videoStartStopHandler = LunarNYVideoStartStopHandler()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        super(IntroView, self)._initialize()
        self.viewModel.onClose += self.__onCloseAction

    def _onLoading(self, *args, **kwargs):
        super(IntroView, self)._onLoading()
        AccountSettings.setSettings(IS_LUNAR_NY_INTRO_VIEWED, True)

    def __onCloseAction(self):
        showVideoView(R.videos.lunar_ny.red_envelope_event_intro(), onVideoStopped=self.__onVideoDone, onVideoStarted=self.__onVideoStarted, isAutoClose=True, soundControl=PausedSoundManager())

    def __onVideoDone(self):
        self.__videoStartStopHandler.onVideoDone()
        self.destroyWindow()
        Settings.g_instance.save()

    def __onVideoStarted(self):
        AccountSettings.setSettings(IS_LUNAR_NY_INTRO_VIDEO_VIEWED, True)
        self.__videoStartStopHandler.onVideoStart()

    def _finalize(self):
        self.viewModel.onClose -= self.__onCloseAction
        super(IntroView, self)._finalize()


class IntroViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(IntroViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=IntroView(R.views.lobby.lunar_ny.IntroView()), layer=WindowLayer.OVERLAY, parent=parent)
