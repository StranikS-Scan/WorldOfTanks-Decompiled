# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_special_reward_view.py
import Windowing
from constants import CURRENT_REALM
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.reward_kit_special_reward_view_model import RewardKitSpecialRewardViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_helper import showStyledVehicleByStyleCD
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideos
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import selectVehicleInHangar
from helpers import uniprof
from gui.impl.lobby.loot_box.reward_kit_special_reward_base import RewardKitSpecialRewardBase
_CONGRATS_TYPE_TO_SOUND_EVENT = {LootCongratsTypes.CONGRAT_TYPE_STYLE: LootBoxVideos.STYLE,
 LootCongratsTypes.CONGRAT_TYPE_VEHICLE: LootBoxVideos.VEHICLE,
 LootCongratsTypes.CONGRAT_TYPE_GUEST_C: LootBoxVideos.GUEST_C}
_VIDEO_BUFFER_TIME = 1.0

class LootBoxSpecialRewardView(RewardKitSpecialRewardBase):
    __slots__ = ()

    def __init__(self, specialRewardData):
        settings = ViewSettings(R.views.lobby.new_year.views.NyRewardKitSpecialReward())
        settings.model = RewardKitSpecialRewardViewModel()
        settings.args = (specialRewardData,)
        super(LootBoxSpecialRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(LootBoxSpecialRewardView, self).getViewModel()

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='enter')
    def _initialize(self, *args, **kwargs):
        if args:
            specialRewardData = args[0]
            self._congratsSourceId = specialRewardData.congratsSourceId
            self._backToSingleOpening = specialRewardData.backToSingleOpening
            Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
            self.viewModel.onContinue += self._onContinue
            self.viewModel.onGoToReward += self._onGoToReward
            self.viewModel.onClose += self._onContinue
            self.viewModel.onVideoStarted += self.__onVideoStarted
            self.viewModel.onVideoStopped += self._onVideoStopped
            with self.viewModel.transaction() as model:
                model.setVideoSource(specialRewardData.sourceName)
                model.setCongratsType(specialRewardData.congratsType)
                model.setVehicleLvl(specialRewardData.vehicleLvl)
                model.setVehicleName(specialRewardData.vehicleName)
                model.setVehicleType(specialRewardData.vehicleType)
                model.setVehicleIsElite(specialRewardData.vehicleIsElite)
                model.setStreamBufferLength(_VIDEO_BUFFER_TIME)
                model.setIsViewAccessible(Windowing.isWindowAccessible())
                model.setIsGuaranteedReward(specialRewardData.isGuaranteedReward)
                model.setRealm(CURRENT_REALM)
        else:
            self._onContinue()
        super(LootBoxSpecialRewardView, self)._initialize()

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='exit')
    def _finalize(self):
        super(LootBoxSpecialRewardView, self)._finalize()
        Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        self.viewModel.onContinue -= self._onContinue
        self.viewModel.onGoToReward -= self._onGoToReward
        self.viewModel.onClose -= self._onContinue
        self.viewModel.onVideoStarted -= self.__onVideoStarted
        self.viewModel.onVideoStopped -= self._onVideoStopped

    def _getVideosList(self):
        return ['StyleLootBoxCongrats/A116_XM551.webm',
         'StyleLootBoxCongrats/Cz17_Vz_55.webm',
         'StyleLootBoxCongrats/Cz17_Vz_55_CN.webm',
         'StyleLootBoxCongrats/F38_Bat_Chatillon155_58.webm',
         'StyleLootBoxCongrats/F114_Projet_4_1.webm',
         'StyleLootBoxCongrats/GB83_FV4005.webm',
         'StyleLootBoxCongrats/GB91_Super_Conqueror.webm',
         'StyleLootBoxCongrats/It15_Rinoceronte.webm',
         'StyleLootBoxCongrats/It23_CC_3.webm',
         'StyleLootBoxCongrats/R149_Object_268_4.webm',
         'StyleLootBoxCongrats/R169_ST_II.webm',
         'StyleLootBoxCongrats/S11_Strv_103B.webm',
         'VehicleLootBoxCongrats/A152_M_Project_2.webm',
         'VehicleLootBoxCongrats/A149_AMBT.webm',
         'VehicleLootBoxCongrats/Ch47_BZ_176.webm',
         'VehicleLootBoxCongrats/F118_Char_Mle_75.webm',
         'VehicleLootBoxCongrats/It30_CC_mod_64_Prem.webm',
         'GuestRewardKitCongrats/guestC.webm'] if self._isMemoryRiskySystem else []

    def _onGoToReward(self, _=None):
        congratsType = self.viewModel.getCongratsType()
        if congratsType == LootCongratsTypes.CONGRAT_TYPE_VEHICLE:
            self._flowLogger.logVehicleShow()
            selectVehicleInHangar(self._congratsSourceId)
            if self._backToSingleOpening and self._isMemoryRiskySystem:
                self.destroyWindow()
            else:
                self._closeToHangar()
        elif congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE:
            self._flowLogger.logStylePreview()
            self.destroyWindow()
            isMultiOpening = self._isMemoryRiskySystem and not self._backToSingleOpening
            showStyledVehicleByStyleCD(self._congratsSourceId, isMultiOpening)

    def __onVideoStarted(self, _=None):
        videoId = _CONGRATS_TYPE_TO_SOUND_EVENT.get(self.viewModel.getCongratsType())
        if videoId is not None:
            self._videoStartStopHandler.onVideoStart(videoId, self.viewModel.getVideoSource())
        return

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        super(LootBoxSpecialRewardView, self)._onWindowAccessibilityChanged(isWindowAccessible)
        self.viewModel.setIsViewAccessible(isWindowAccessible)


class LootBoxSpecialRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, specialRewardData, parent=None):
        super(LootBoxSpecialRewardWindow, self).__init__(content=LootBoxSpecialRewardView(specialRewardData), parent=parent, layer=WindowLayer.TOP_WINDOW)
