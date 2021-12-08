# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_special_reward_view.py
import logging
from functools import partial
import Windowing
from constants import CURRENT_REALM
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_special_reward_view_model import LootBoxSpecialRewardViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_helper import LootBoxHideableView, showLootBoxReward
from gui.impl.lobby.loot_box.loot_box_helper import fireCloseToHangar, showStyledVehicleByStyleCD
from gui.impl.lobby.loot_box.loot_box_helper import fireSpecialRewardsClosed
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler, LootBoxVideos
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import selectVehicleInHangar
from helpers import dependency
from helpers import uniprof
from skeletons.gui.game_control import IFestivityController
from uilogging.ny.loggers import NyLootBoxesRewardsFlowLogger
_logger = logging.getLogger(__name__)
_CONGRATS_TYPE_TO_SOUND_EVENT = {LootCongratsTypes.CONGRAT_TYPE_STYLE: LootBoxVideos.STYLE,
 LootCongratsTypes.CONGRAT_TYPE_VEHICLE: LootBoxVideos.VEHICLE}
_VIDEO_BUFFER_TIME = 1.0

class LootBoxSpecialRewardView(LootBoxHideableView):
    _festivityController = dependency.descriptor(IFestivityController)
    __flowLogger = NyLootBoxesRewardsFlowLogger()

    def __init__(self, specialRewardData):
        self.__congratsSourceId = 0
        self.__backToSingleOpening = False
        settings = ViewSettings(R.views.lobby.new_year.views.NyLootBoxSpecialReward())
        settings.model = LootBoxSpecialRewardViewModel()
        settings.args = (specialRewardData,)
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler()
        super(LootBoxSpecialRewardView, self).__init__(settings)
        self.__showRewardsAndDestroyFunc = None
        return

    @property
    def viewModel(self):
        return super(LootBoxSpecialRewardView, self).getViewModel()

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(LootBoxSpecialRewardView, self)._initialize()
        if args:
            specialRewardData = args[0]
            self.__congratsSourceId = specialRewardData.congratsSourceId
            self.__backToSingleOpening = specialRewardData.backToSingleOpening
            Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
            self.viewModel.onContinueBtnClick += self.__onContinue
            self.viewModel.onGoToRewardBtnClick += self.__onGoToReward
            self.viewModel.onCloseBtnClick += self.__onContinue
            self.viewModel.onVideoStarted += self.__onVideoStarted
            self.viewModel.onVideoStopped += self.__onVideoStopped
            self.viewModel.onVideoInterrupted += self.__onVideoInterrupted
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
            _logger.error('__specialRewardData is not specified!')
            self.__onContinue()
        if self._isMemoryRiskySystem and self.__backToSingleOpening:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
            self._isCanClose = True
        self.setHoldSwfs(True)

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='exit')
    def _finalize(self):
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.setHoldSwfs(False)
        self.viewModel.onContinueBtnClick -= self.__onContinue
        self.viewModel.onGoToRewardBtnClick -= self.__onGoToReward
        self.viewModel.onCloseBtnClick -= self.__onContinue
        self.viewModel.onVideoStarted -= self.__onVideoStarted
        self.viewModel.onVideoStopped -= self.__onVideoStopped
        self.viewModel.onVideoInterrupted -= self.__onVideoInterrupted
        self.__videoStartStopHandler.onVideoDone()
        self.__videoStartStopHandler = None
        super(LootBoxSpecialRewardView, self)._finalize()
        return

    def _getVideosList(self):
        return ['StyleLootBoxCongrats/A116_XM551.webm',
         'StyleLootBoxCongrats/Ch41_WZ_111_5A.webm',
         'StyleLootBoxCongrats/Cz17_Vz_55.webm',
         'StyleLootBoxCongrats/G42_Maus.webm',
         'StyleLootBoxCongrats/GB31_Conqueror_Gun.webm',
         'StyleLootBoxCongrats/GB83_FV4005.webm',
         'StyleLootBoxCongrats/It15_Rinoceronte.webm',
         'StyleLootBoxCongrats/J16_ST_B1.webm',
         'StyleLootBoxCongrats/Pl15_60TP_Lewandowskiego.webm',
         'StyleLootBoxCongrats/R149_Object_268_4.webm',
         'StyleLootBoxCongrats/R169_ST_II.webm',
         'VehicleLootBoxCongrats/A141_M_IV_Y.webm',
         'VehicleLootBoxCongrats/Ch43_WZ_122_2.webm',
         'VehicleLootBoxCongrats/Cz14_Skoda_T-56.webm',
         'VehicleLootBoxCongrats/GB112_Caliban.webm',
         'VehicleLootBoxCongrats/S32_Bofors_Tornvagn.webm'] if self._isMemoryRiskySystem else []

    def __onContinue(self, _=None):
        if self._isMemoryRiskySystem and self.__backToSingleOpening:
            if not self._isCanClose or not self._festivityController.isEnabled():
                return
            self.__showRewardsAndDestroyFunc = partial(showLootBoxReward, None, None, None, self.__backToSingleOpening)
            self._startFade(self.__showRewardsAndDestroy, withPause=True)
        else:
            fireSpecialRewardsClosed()
            self.destroyWindow()
        return

    def __showRewardsAndDestroy(self):
        if self.__showRewardsAndDestroyFunc is not None:
            self.__showRewardsAndDestroyFunc()
            self.__showRewardsAndDestroyFunc = None
        self.destroyWindow()
        return

    def __onGoToReward(self, _=None):
        congratsType = self.viewModel.getCongratsType()
        if congratsType == LootCongratsTypes.CONGRAT_TYPE_VEHICLE:
            self.__flowLogger.logVehicleShow()
            selectVehicleInHangar(self.__congratsSourceId)
            if self.__backToSingleOpening and self._isMemoryRiskySystem:
                self.destroyWindow()
            else:
                self.__closeToHangar()
        elif congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE:
            self.__flowLogger.logStylePreview()
            self.destroyWindow()
            isMultiOpening = self._isMemoryRiskySystem and not self.__backToSingleOpening
            showStyledVehicleByStyleCD(self.__congratsSourceId, isMultiOpening)

    def __closeToHangar(self):
        fireCloseToHangar()

    def __onVideoStarted(self, _=None):
        videoId = _CONGRATS_TYPE_TO_SOUND_EVENT.get(self.viewModel.getCongratsType())
        if videoId is not None:
            self.__videoStartStopHandler.onVideoStart(videoId, self.viewModel.getVideoSource())
        return

    def __onVideoStopped(self, _=None):
        self.__videoStartStopHandler.onVideoDone()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        self.__videoStartStopHandler.setIsNeedPause(not isWindowAccessible)
        self.viewModel.setIsViewAccessible(isWindowAccessible)

    def __onVideoInterrupted(self):
        pass


class LootBoxSpecialRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, specialRewardData, parent=None):
        super(LootBoxSpecialRewardWindow, self).__init__(content=LootBoxSpecialRewardView(specialRewardData), parent=parent, layer=WindowLayer.TOP_WINDOW)
