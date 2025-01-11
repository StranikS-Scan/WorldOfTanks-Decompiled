# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/video/guest_c_reward_view.py
import Windowing
from constants import CURRENT_REALM
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.video.guest_c_reward_view_model import GuestCRewardViewModel
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import GuestCVideoEvents
from gui.impl.new_year.sounds_helper.video_handler import GuestVideoStartStopHandler
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import uniprof, dependency
from new_year.ny_constants import NYObjects
from skeletons.account_helpers.settings_core import ISettingsCore
_VIDEO_BUFFER_TIME = 1.0

class GuestCRewardView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('_videoStartStopHandler',)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.views.NyGuestCReward())
        settings.model = GuestCRewardViewModel()
        self._videoStartStopHandler = self._getStartStopHandler()
        super(GuestCRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(GuestCRewardView, self).getViewModel()

    @staticmethod
    def _getStartStopHandler():
        return GuestVideoStartStopHandler()

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(GuestCRewardView, self)._initialize()
        setOverlayHangarGeneral(onState=True)
        Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
        self.viewModel.onContinue += self._onContinue
        self.viewModel.onGoQuests += self._onGoQuests
        self.viewModel.onClose += self._onContinue
        self.viewModel.onVideoStarted += self._onVideoStarted
        self.viewModel.onVideoStopped += self._onVideoStopped
        with self.viewModel.transaction() as model:
            model.setStreamBufferLength(_VIDEO_BUFFER_TIME)
            model.setIsViewAccessible(Windowing.isWindowAccessible())
            model.setRealm(CURRENT_REALM)

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='exit')
    def _finalize(self):
        setOverlayHangarGeneral(onState=False)
        Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        self.viewModel.onContinue -= self._onContinue
        self.viewModel.onGoQuests -= self._onGoQuests
        self.viewModel.onClose -= self._onContinue
        self.viewModel.onVideoStarted -= self._onVideoStarted
        self.viewModel.onVideoStopped -= self._onVideoStopped
        self._videoStartStopHandler.onVideoDone()
        self._videoStartStopHandler = None
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_SHOW_GUEST_C_IDLE), EVENT_BUS_SCOPE.LOBBY)
        super(GuestCRewardView, self)._finalize()
        return

    def _onContinue(self, _=None):
        self.destroyWindow()

    def _onGoQuests(self):
        NewYearNavigation.switchTo(NYObjects.CELEBRITY_CAT, instantly=True)
        self.destroyWindow()

    def _onVideoStopped(self, _=None):
        self._videoStartStopHandler.onVideoDone()

    def _onVideoStarted(self, _=None):
        self._videoStartStopHandler.onVideoStartEvent(GuestCVideoEvents.VIDEO_START_GUEST_C)

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        self._videoStartStopHandler.setIsNeedPause(not isWindowAccessible)
        self.viewModel.setIsViewAccessible(isWindowAccessible)


class GuestCRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(GuestCRewardWindow, self).__init__(content=GuestCRewardView(), parent=parent, layer=WindowLayer.TOP_WINDOW)
