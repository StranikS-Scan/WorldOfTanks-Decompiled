# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/lootbox_video_reward_view.py
import Windowing
from gui.impl.lobby.video.video_sound_manager import DummySoundManager
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_REWARD_VIDEO_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import BaseUniqueRewardsView
from helpers import dependency
from frameworks.wulf import WindowFlags, WindowLayer
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_video_reward_view_model import LootboxVideoRewardViewModel
from gui.impl.pub.lobby_window import LobbyWindow
from skeletons.gui.shared import IItemsCache
from items.vehicles import getVehicleClassFromVehicleType

class LootboxVehicleVideoRewardView(BaseUniqueRewardsView):
    __slots__ = ('_vehicle', '_soundControl', '__isWindowAccessibleHandlerInit', '_videoRes', '_isGuaranteedReward')
    __itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = LOOT_BOXES_REWARD_VIDEO_SOUND_SPACE

    def __init__(self, layoutID, vehicle, videoRes, rewards, isGuaranteedReward=False, soundControl=DummySoundManager()):
        super(LootboxVehicleVideoRewardView, self).__init__(layoutID, rewards, LootboxVideoRewardViewModel())
        self._vehicle = vehicle
        self._soundControl = soundControl
        self._videoRes = videoRes
        self._isGuaranteedReward = isGuaranteedReward
        self.__isWindowAccessibleHandlerInit = False

    def _finalize(self):
        if self.__isWindowAccessibleHandlerInit:
            Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
            self.__isWindowAccessibleHandlerInit = False
        self._soundControl.stop()
        super(LootboxVehicleVideoRewardView, self)._finalize()

    @property
    def viewModel(self):
        return super(LootboxVehicleVideoRewardView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LootboxVehicleVideoRewardView, self)._onLoading(*args, **kwargs)
        self._update()
        Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
        self.__isWindowAccessibleHandlerInit = True

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onVideoStarted, self._onVideoStarted))

    def _update(self):
        with self.viewModel.transaction() as vm:
            vm.setVehicleName(self._vehicle.userName)
            vm.setVehicleLvl(self._vehicle.level)
            vm.setVehicleType(getVehicleClassFromVehicleType(self._vehicle.descriptor.type))
            vm.setIsElite(self._vehicle.isElite)
            vm.setIsWindowAccessible(Windowing.isWindowAccessible())
            vm.setVideoRes(self._videoRes)
            vm.setIsGuaranteedReward(self._isGuaranteedReward)

    def _onClose(self):
        self.destroyWindow()

    def _onVideoStarted(self):
        self._soundControl.start()
        if not Windowing.isWindowAccessible():
            self._soundControl.pause()

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self._soundControl.unpause()
        else:
            self._soundControl.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)


class LootboxVideoRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, contentView, parent=None):
        super(LootboxVideoRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=contentView, parent=parent, layer=WindowLayer.OVERLAY)
