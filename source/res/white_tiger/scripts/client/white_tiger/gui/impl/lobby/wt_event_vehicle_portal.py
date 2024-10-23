# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_vehicle_portal.py
import Windowing
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_vehicle_portal_model import WtEventVehiclePortalModel, EventTankType
from white_tiger.gui.impl.lobby.wt_event_sound import playLootBoxPortalExit
from white_tiger.gui.impl.lobby.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import closeEventPortalAwardsWindow
from gui.wt_event.wt_event_helpers import findSpecialVehicle, findBossMainVehicle, findMainVehicle
from white_tiger.gui.wt_event_models_helper import setLootBoxesCount, fillVehicleModel, fillAdditionalAwards
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import LootBoxAwardsManager
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from shared_utils import CONST_CONTAINER
from white_tiger.gui.impl.lobby.wt_event_sound import WhiteTigerVehicleAwardViewSoundControl, playLootboxVehicleRewardsLoopStopped, playLootboxVehicleRewardsLoopStarted

class WtEventVehiclePortal(WtEventBasePortalAwards):

    def __init__(self, boxType, awards=None):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.PortalVehicleAwardView(), model=WtEventVehiclePortalModel())
        super(WtEventVehiclePortal, self).__init__(settings, awards)
        self.__boxType = boxType
        self.__soundController = WhiteTigerVehicleAwardViewSoundControl()

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
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        super(WtEventVehiclePortal, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onVideoStarted, self.__onVideoStarted), (self.viewModel.onPortalRewardsStarted, self.__onPortalRewardsStarted))

    def __onVideoStarted(self):
        self.__soundController.start()

    def __onPortalRewardsStarted(self):
        playLootboxVehicleRewardsLoopStarted()

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
            mainVehicle = self._boxesCtrl.getMainVehicleName(self._awards)
            bossMainVehicle = self._boxesCtrl.getBossMainVehicleName(self._awards)
            if mainVehicle:
                model.setEventTank(EventTankType.MAIN)
                fillVehicleModel(model.vehicle, mainVehicle)
            elif bossMainVehicle:
                model.setEventTank(EventTankType.BOSS)
                fillVehicleModel(model.vehicle, bossMainVehicle)
            else:
                specialVehicle = self._boxesCtrl.getSpecialVehicleName(self._awards)
                specialVehicleName = specialVehicle.name.split(':')[1]
                isPrimaryTank = specialVehicleName == EventTankType.PRIMARY.value
                model.setEventTank(EventTankType.PRIMARY if isPrimaryTank else EventTankType.SECONDARY)
                fillVehicleModel(model.vehicle, specialVehicle)
            if self._awards is not None:
                self.__setModelAwards(model)
        return

    def _getBoxType(self):
        return self.__boxType

    def _goToPortals(self):
        closeEventPortalAwardsWindow()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_VEHICLE_AWARD_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        playLootBoxPortalExit()
        self.destroyWindow()

    def __setModelAwards(self, model):
        groupedBonuses = LootBoxAwardsManager.getBossGroupedBonuses(self._awards)
        additonalRewards = groupedBonuses.additional
        mainBonuses = [ bonus for bonus in groupedBonuses.main if bonus.getName() == 'customizations' ]
        tankReward = [ bonus for bonus in groupedBonuses.main if bonus not in mainBonuses ]
        vehicles = [ bonus for bonus in self._awards if bonus.getName() == 'vehicles' ]
        mainVehicle = findMainVehicle(vehicles) or findBossMainVehicle(vehicles) or findSpecialVehicle(vehicles)
        for vehicle in vehicles:
            if vehicle != mainVehicle:
                additonalRewards.append(vehicle)

        additonalRewards[0:0] = mainBonuses
        fillAdditionalAwards(model.rewards, tankReward, self._tooltipItems)
        fillAdditionalAwards(model.additionalRewards, additonalRewards, self._tooltipItems)

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

    def __init__(self, boxType, awards, parent=None):
        super(WtEventVehiclePortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventVehiclePortal(boxType, awards), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)


class ReRollButton(CONST_CONTAINER):
    CLAIM_AND_RELAUNCH = 'claimAndRelaunch'
    REROLL = 'reroll'
