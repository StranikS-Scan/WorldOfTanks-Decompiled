# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_vehicle_portal.py
import logging
import Windowing
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_vehicle_portal_model import WtEventVehiclePortalModel
from white_tiger.gui.impl.lobby.wt_event_sound import playLootBoxPortalExit
from white_tiger.gui.impl.lobby.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from gui.impl.pub.lobby_window import LobbyWindow
from white_tiger.gui.shared.event_dispatcher import closeEventPortalAwardsWindow
from white_tiger.gui.wt_event_models_helper import setLootBoxesCount, fillVehicleModel, fillAdditionalAwards
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus, event_dispatcher
from shared_utils import CONST_CONTAINER
from white_tiger.gui.impl.lobby.wt_event_sound import WhiteTigerVehicleAwardViewSoundControl, playLootboxVehicleRewardsLoopStopped, playLootboxVehicleRewardsLoopStarted
_logger = logging.getLogger(__name__)

class WtEventVehiclePortal(WtEventBasePortalAwards):

    def __init__(self, boxType, awardVehicleData, awards=None):
        awardVehicle, _ = awardVehicleData
        awardsWithoutVehicle = []
        self.__awardVehicles = []
        for award in awards:
            isIgnore = False
            if award.getName() == 'vehicles':
                for vehicle, _ in award.getVehicles():
                    if vehicle.intCD == awardVehicle.intCD:
                        self.__awardVehicles.append(award)
                        isIgnore = True

            if not isIgnore:
                awardsWithoutVehicle.append(award)

        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.PortalVehicleAwardView(), model=WtEventVehiclePortalModel())
        super(WtEventVehiclePortal, self).__init__(settings, awardsWithoutVehicle)
        self.__boxType = boxType
        self.__soundController = WhiteTigerVehicleAwardViewSoundControl()
        self.__vehicleData = awardVehicleData

    @property
    def viewModel(self):
        return super(WtEventVehiclePortal, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventVehiclePortal, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsWindowAccessible(Windowing.isWindowAccessible())
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def _onLoaded(self, *args, **kwargs):
        super(WtEventVehiclePortal, self)._onLoaded(*args, **kwargs)
        Waiting.hide('updating')

    def _finalize(self):
        self.__onPortalRewardsStopped()
        self.__awardVehicles = []
        self.__soundController = None
        self.__vehicleData = None
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        super(WtEventVehiclePortal, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onVideoStarted, self.__onVideoStarted), (self.viewModel.onPortalRewardsStarted, self.__onPortalRewardsStarted))

    def __onVideoStarted(self):
        _, customData = self.__vehicleData
        self.__soundController.start(customData.sound_video_start)

    def __onPortalRewardsStarted(self):
        _, customData = self.__vehicleData
        playLootboxVehicleRewardsLoopStarted(customData.sound_video_loop_start)

    def __onPortalRewardsStopped(self):
        playLootboxVehicleRewardsLoopStopped()

    def _updateModel(self):
        super(WtEventVehiclePortal, self)._updateModel()
        with self.viewModel.transaction() as model:
            self._tooltipItems.clear()
            setLootBoxesCount(model.portalAvailability, self._getBoxType())
            model.setIsFirstLaunch(not self._boxesCtrl.isEngineerReroll())
            extra = self._boxesCtrl.getExtraRewards(self._getBoxType(), count=0)
            model.setFirstLaunchReward(extra.get('gold', 0) if extra else 0)
            if self.__vehicleData:
                vehicle, customData = self.__vehicleData
                if customData:
                    model.setShowVideoName(customData.video_show)
                    model.setIdleVideoName(customData.video_idle)
                fillVehicleModel(model.vehicle, vehicle)
            if self._awards is not None:
                fillAdditionalAwards(model.rewards, self.__awardVehicles, self._tooltipItems)
                fillAdditionalAwards(model.additionalRewards, self._awards, self._tooltipItems)
        return

    def _getBoxType(self):
        return self.__boxType

    def _goToPortals(self):
        playLootBoxPortalExit()
        parent = self.getParentWindow()
        self.destroyWindow()
        event_dispatcher.showEventStorageWindow(parent)

    def _onClose(self):
        closeEventPortalAwardsWindow()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL), scope=EVENT_BUS_SCOPE.LOBBY)
        super(WtEventVehiclePortal, self)._onClose()

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        if isWindowAccessible:
            self.__soundController.unpause()
        else:
            self.__soundController.pause()
        self.viewModel.setIsWindowAccessible(isWindowAccessible)


class WtEventVehiclePortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, boxType, awards, vehicle, parent=None):
        super(WtEventVehiclePortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventVehiclePortal(boxType=boxType, awardVehicleData=vehicle, awards=awards), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)


class ReRollButton(CONST_CONTAINER):
    CLAIM_AND_RELAUNCH = 'claimAndRelaunch'
    REROLL = 'reroll'
