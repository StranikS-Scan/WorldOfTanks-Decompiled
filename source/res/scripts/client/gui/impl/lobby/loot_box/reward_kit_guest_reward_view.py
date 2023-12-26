# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/reward_kit_guest_reward_view.py
import Windowing
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from constants import CURRENT_REALM
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.reward_kit_guest_reward_view_model import RewardKitGuestRewardViewModel
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.lobby.loot_box.loot_box_helper import fireCloseToHangar
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from new_year.ny_constants import NYObjects
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import uniprof, dependency
from gui.impl.lobby.loot_box.reward_kit_special_reward_base import RewardKitSpecialRewardBase
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideos
_VIDEO_BUFFER_TIME = 1.0

class RewardKitGuestRewardView(RewardKitSpecialRewardBase):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ()

    def __init__(self, specialRewardData):
        settings = ViewSettings(R.views.lobby.new_year.views.NyRewardKitGuestReward())
        settings.model = RewardKitGuestRewardViewModel()
        settings.args = (specialRewardData,)
        super(RewardKitGuestRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RewardKitGuestRewardView, self).getViewModel()

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='enter')
    def _initialize(self, *args, **kwargs):
        setOverlayHangarGeneral(onState=True)
        if args:
            specialRewardData = args[0]
            self._backToSingleOpening = specialRewardData.backToSingleOpening
            Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
            self.viewModel.onContinue += self._onContinue
            self.viewModel.onGoQuests += self._onGoQuests
            self.viewModel.onClose += self._onContinue
            self.viewModel.onVideoStarted += self.__onVideoStarted
            self.viewModel.onVideoStopped += self._onVideoStopped
            with self.viewModel.transaction() as model:
                model.setStreamBufferLength(_VIDEO_BUFFER_TIME)
                model.setIsViewAccessible(Windowing.isWindowAccessible())
                model.setRealm(CURRENT_REALM)
        else:
            self._onContinue()
            super(RewardKitGuestRewardView, self)._initialize()

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='exit')
    def _finalize(self):
        super(RewardKitGuestRewardView, self)._finalize()
        setOverlayHangarGeneral(onState=False)
        Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        self.viewModel.onContinue -= self._onContinue
        self.viewModel.onGoQuests -= self._onGoQuests
        self.viewModel.onClose -= self._onContinue
        self.viewModel.onVideoStarted -= self.__onVideoStarted
        self.viewModel.onVideoStopped -= self._onVideoStopped
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_SHOW_GUEST_C_IDLE), EVENT_BUS_SCOPE.LOBBY)

    def _getVideosList(self):
        return ['GuestRewardKitCongrats/guestC.webm'] if self._isMemoryRiskySystem else []

    def _onGoToReward(self, _=None):
        pass

    def _onGoQuests(self):
        fireCloseToHangar()
        fireCloseToHangar()
        if not self.__tryToShowTutotial():
            NewYearNavigation.switchTo(NYObjects.CELEBRITY_CAT, instantly=True)

    def __tryToShowTutotial(self):
        if self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE, TutorialStates.INTRO) < TutorialStates.UI:
            NewYearNavigation.switchTo(NYObjects.TOWN, True)
            return True
        return False

    def __onVideoStarted(self, _=None):
        self._videoStartStopHandler.onVideoStart(LootBoxVideos.GUEST_C)

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        super(RewardKitGuestRewardView, self)._onWindowAccessibilityChanged(isWindowAccessible)
        self.viewModel.setIsViewAccessible(isWindowAccessible)


class RewardKitGuestRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, specialRewardData, parent=None):
        super(RewardKitGuestRewardWindow, self).__init__(content=RewardKitGuestRewardView(specialRewardData), parent=parent, layer=WindowLayer.TOP_WINDOW)
