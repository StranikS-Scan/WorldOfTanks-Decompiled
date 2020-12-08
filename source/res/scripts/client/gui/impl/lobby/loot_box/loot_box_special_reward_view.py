# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_special_reward_view.py
import logging
from functools import partial
import Windowing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_special_reward_view_model import LootBoxSpecialRewardViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_helper import LootBoxHideableView, showLootBoxReward, worldDrawEnabled
from gui.impl.lobby.loot_box.loot_box_helper import fireCloseToHangar, showStyledVehicleByStyleCD
from gui.impl.lobby.loot_box.loot_box_helper import fireSpecialRewardsClosed
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler, LootBoxVideos
from gui.impl.pub.lobby_window import LobbyOverlay
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import selectVehicleInHangar
from helpers import dependency
from helpers import uniprof
from skeletons.gui.game_control import IFestivityController
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
_logger = logging.getLogger(__name__)
_CONGRATS_TYPE_TO_SOUND_EVENT = {LootCongratsTypes.CONGRAT_TYPE_STYLE: LootBoxVideos.STYLE,
 LootCongratsTypes.CONGRAT_TYPE_VEHICLE: LootBoxVideos.VEHICLE}
_VIDEO_BUFFER_TIME = 1.0

@loggerTarget(logKey=NY_LOG_KEYS.NY_LOOT_BOX_SPECIAL_REWARD_VIEW, loggerCls=NYLogger)
class LootBoxSpecialRewardView(LootBoxHideableView):
    _festivityController = dependency.descriptor(IFestivityController)

    def __init__(self, specialRewardData):
        self.__congratsSourceId = 0
        self.__backToSingleOpening = False
        settings = ViewSettings(layoutID=R.views.lobby.loot_box.views.loot_box_special_reward_view.LootBoxSpecialRewardView(), flags=ViewFlags.VIEW, model=LootBoxSpecialRewardViewModel())
        settings.args = (specialRewardData,)
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler()
        super(LootBoxSpecialRewardView, self).__init__(settings)
        self.__showRewardsAndDestroyFunc = None
        return

    @property
    def viewModel(self):
        return super(LootBoxSpecialRewardView, self).getViewModel()

    @loggerEntry
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
        else:
            _logger.error('__specialRewardData is not specified!')
            self.__onContinue()
        if self._isMemoryRiskySystem and self.__backToSingleOpening:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
            self._isCanClose = True

    @uniprof.regionDecorator(label='ny.lootbox.video', scope='exit')
    def _finalize(self):
        if self._isMemoryRiskySystem:
            worldDrawEnabled(True)
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
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
        return ['StyleLootBoxCongrats/A83_T110E4.usm',
         'StyleLootBoxCongrats/Ch41_WZ_111_5A.usm',
         'StyleLootBoxCongrats/F88_AMX_13_105.usm',
         'StyleLootBoxCongrats/G42_Maus.usm',
         'StyleLootBoxCongrats/G56_E-100.usm',
         'StyleLootBoxCongrats/G72_JagdPz_E100.usm',
         'StyleLootBoxCongrats/GB31_Conqueror_Gun.usm',
         'StyleLootBoxCongrats/J16_ST_B1.usm',
         'StyleLootBoxCongrats/Pl15_60TP_Lewandowskiego.usm',
         'StyleLootBoxCongrats/R97_Object_140.usm',
         'StyleLootBoxCongrats/R148_Object_430_U.usm',
         'VehicleLootBoxCongrats/F116_Bat_Chatillon_Bourrasque.usm',
         'VehicleLootBoxCongrats/It18_Progetto_C45_mod_71.usm',
         'VehicleLootBoxCongrats/R177_ISU_152K_BL10.usm',
         'VehicleLootBoxCongrats/GB109_GSOR_1008.usm'] if self._isMemoryRiskySystem else []

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
            selectVehicleInHangar(self.__congratsSourceId)
            if self.__backToSingleOpening and self._isMemoryRiskySystem:
                self.destroyWindow()
            else:
                self.__closeToHangar()
        elif congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE:
            self.destroyWindow()
            isMultiOpening = self._isMemoryRiskySystem and not self.__backToSingleOpening
            showStyledVehicleByStyleCD(self.__congratsSourceId, isMultiOpening)

    def __closeToHangar(self):
        fireCloseToHangar()

    def __onVideoStarted(self, _=None):
        videoId = _CONGRATS_TYPE_TO_SOUND_EVENT.get(self.viewModel.getCongratsType())
        if videoId is not None:
            self.__videoStartStopHandler.onVideoStart(videoId, self.viewModel.getVideoSource())
        if self._isMemoryRiskySystem:
            worldDrawEnabled(False)
        return

    def __onVideoStopped(self, _=None):
        self.__videoStartStopHandler.onVideoDone()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        self.__videoStartStopHandler.setIsNeedPause(not isWindowAccessible)
        self.viewModel.setIsViewAccessible(isWindowAccessible)

    @simpleLog(action=NY_LOG_ACTIONS.NY_LOOT_BOX_REWARD_INTERRUPTED)
    def __onVideoInterrupted(self):
        pass


class LootBoxSpecialRewardWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, specialRewardData, parent=None):
        super(LootBoxSpecialRewardWindow, self).__init__(content=LootBoxSpecialRewardView(specialRewardData), decorator=None, parent=parent)
        return
