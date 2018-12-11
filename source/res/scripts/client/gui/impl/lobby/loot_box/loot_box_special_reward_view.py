# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_special_reward_view.py
import logging
from frameworks.wulf import ViewFlags
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_special_reward_view_model import LootBoxSpecialRewardViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_helper import LootBoxShowHideCloseHandler
from gui.impl.lobby.loot_box.loot_box_helper import fireCloseToHangar, showStyledVehicleByStyleCD
from gui.impl.lobby.loot_box.loot_box_helper import fireSpecialRewardsClosed
from gui.impl.lobby.loot_box.loot_box_sounds import onVideoStart, onVideoDone, LootBoxVideos
from gui.impl.pub import LobbyWindow
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import selectVehicleInHangar
_logger = logging.getLogger(__name__)
_CONGRATS_TYPE_TO_SOUND_EVENT = {LootCongratsTypes.CONGRAT_TYPE_STYLE: LootBoxVideos.STYLE,
 LootCongratsTypes.CONGRAT_TYPE_VEHICLE: LootBoxVideos.VEHICLE}

class LootBoxSpecialRewardView(ViewImpl):
    __slots__ = ('__congratsSourceId', '__showHideCloseHandler')

    def __init__(self, *args, **kwargs):
        self.__congratsSourceId = 0
        self.__showHideCloseHandler = LootBoxShowHideCloseHandler()
        super(LootBoxSpecialRewardView, self).__init__(R.views.lootBoxSpecialRewardView, ViewFlags.VIEW, LootBoxSpecialRewardViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(LootBoxSpecialRewardView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LootBoxSpecialRewardView, self)._initialize()
        self.__showHideCloseHandler.startListen(self.getParentWindow())
        if args:
            specialRewardData = args[0]
            self.__congratsSourceId = specialRewardData.congratsSourceId
            with self.viewModel.transaction() as model:
                model.setVideoSource(specialRewardData.sourceName)
                model.setCongratsType(specialRewardData.congratsType)
                model.setVehicleLvl(specialRewardData.vehicleLvl)
                model.setVehicleName(specialRewardData.vehicleName)
                model.setVehicleType(specialRewardData.vehicleType)
                model.setVehicleIsElite(specialRewardData.vehicleIsElite)
            self.viewModel.onContinueBtnClick += self.__onContinue
            self.viewModel.onGoToRewardBtnClick += self.__onGoToReward
            self.viewModel.onCloseBtnClick += self.__onContinue
            self.viewModel.onVideoStarted += self.__onVideoStarted
            self.viewModel.onVideoStopped += self.__onVideoStopped
        else:
            _logger.error('__specialRewardData is not specified!')
            self.__onContinue()

    def _finalize(self):
        self.__showHideCloseHandler.stopListen()
        self.__showHideCloseHandler = None
        self.viewModel.onContinueBtnClick -= self.__onContinue
        self.viewModel.onGoToRewardBtnClick -= self.__onGoToReward
        self.viewModel.onCloseBtnClick -= self.__onContinue
        self.viewModel.onVideoStarted -= self.__onVideoStarted
        self.viewModel.onVideoStopped -= self.__onVideoStopped
        return

    def __onContinue(self, _=None):
        fireSpecialRewardsClosed()
        self.destroyWindow()

    def __onGoToReward(self, _=None):
        congratsType = self.viewModel.getCongratsType()
        if congratsType == LootCongratsTypes.CONGRAT_TYPE_VEHICLE:
            selectVehicleInHangar(self.__congratsSourceId)
            self.__closeToHangar()
        elif congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE:
            self.destroyWindow()
            showStyledVehicleByStyleCD(self.__congratsSourceId)

    def __closeToHangar(self):
        fireCloseToHangar()

    def __onVideoStarted(self, _=None):
        event = _CONGRATS_TYPE_TO_SOUND_EVENT.get(self.viewModel.getCongratsType())
        if event is not None:
            onVideoStart(event, self.viewModel.getVideoSource())
        return

    def __onVideoStopped(self, _=None):
        onVideoDone()


class LootBoxSpecialRewardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(LootBoxSpecialRewardWindow, self).__init__(content=LootBoxSpecialRewardView(*args, **kwargs), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return
