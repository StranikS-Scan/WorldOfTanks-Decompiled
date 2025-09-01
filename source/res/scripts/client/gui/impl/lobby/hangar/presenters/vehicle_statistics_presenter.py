# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_statistics_presenter.py
from __future__ import absolute_import
import typing
import logging
from future.utils import itervalues, iteritems
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.tooltips.vehicle_points_tooltip_view import VehiclePointsTooltipView
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_statistic_model import VehicleStatisticModel
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_statistics_model import VehicleStatisticsModel
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prestige.prestige_helpers import mapGradeIDToUI, getCurrentGrade, getVehiclePrestigeMap, DEFAULT_PRESTIGE
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IPlatoonController, IBattlePassController, IRentalsController
if typing.TYPE_CHECKING:
    from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter, IAccountStyles
    from gui.shared.gui_items.dossier.stats import AccountRandomStatsBlock
_logger = logging.getLogger(__name__)

class VehiclesStatisticsPresenter(ViewComponent[VehicleStatisticsModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __battlePass = dependency.descriptor(IBattlePassController)
    __rentalsCtrl = dependency.descriptor(IRentalsController)

    def __init__(self, vehiclesComponent, accountStyles):
        super(VehiclesStatisticsPresenter, self).__init__(model=VehicleStatisticsModel)
        self._vehiclesComponent = vehiclesComponent
        self.__accountStyles = accountStyles

    @property
    def viewModel(self):
        return super(VehiclesStatisticsPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.battle_pass.tooltips.VehiclePointsTooltipView():
            return VehiclePointsTooltipView(int(event.getArgument('intCD')))
        return SimpleTooltipContent(R.views.lobby.battle_pass.tooltips.BattlePassOnPauseTooltipView()) if contentID == R.views.lobby.battle_pass.tooltips.BattlePassOnPauseTooltipView() else super(VehiclesStatisticsPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _getEvents(self):
        return ((self.__accountStyles.onChanged, self.__fillVehicles),
         (self._vehiclesComponent.onDiff, self.__onUpdateVehicles),
         (self.__platoonCtrl.onMembersUpdate, self.__onPlatoonMembersUpdate),
         (g_prbCtrlEvents.onVehicleClientStateChanged, self.__onVehicleClientStateChanged),
         (self.__rentalsCtrl.onRentChangeNotify, self.__onUpdateVehicles),
         (self.__battlePass.onVehiclesPointsUpdated, self.__onBPVehiclesPointsUpdated))

    def _onLoading(self, *args, **kwargs):
        super(VehiclesStatisticsPresenter, self)._onLoading(*args, **kwargs)
        self.__fillVehicles()

    def __onBPVehiclesPointsUpdated(self, updates):
        with self.viewModel.transaction() as model:
            statistics = model.getStatistics()
            for intCD, points in iteritems(updates):
                vehID = str(intCD)
                vehicle = statistics.get(vehID, None)
                if vehicle is None:
                    _logger.warning("Vehicle ID '%s' not found", vehID)
                    return
                vehicle.setBpProgress(points)
                statistics.set(vehID, vehicle)

        return

    def __fillVehicles(self):
        self.__updateVehicles(self._vehiclesComponent.vehicles)

    def __onVehicleClientStateChanged(self, vehicles=None):
        if vehicles:
            self.__onUpdateVehicles(vehicles)

    def __onPlatoonMembersUpdate(self):
        self.__updateVehicles(self._vehiclesComponent.vehicles)

    def __onUpdateVehicles(self, diff):
        with self.viewModel.transaction() as model:
            statistics = model.getStatistics()
            accountRandomStats = self.__itemsCache.items.getAccountDossier().getRandomStats()
            vehiclePrestige = getVehiclePrestigeMap()
            for intCD in diff:
                if intCD in self._vehiclesComponent.vehicles:
                    vehicle = self._vehiclesComponent.vehicles[intCD]
                    prestigeLevel, _ = vehiclePrestige.get(vehicle.intCD, DEFAULT_PRESTIGE)
                    item = self.__convertToStatisticsModel(vehicle, accountRandomStats, prestigeLevel)
                    statistics.set(item.getId(), item)
                statistics.remove(str(intCD))

    def __convertToStatisticsModel(self, vehicle, accountRandomStats, prestigeLevel):
        vState, vStateLvl = self.__getVehicleStatus(vehicle)
        gradeType, grade = mapGradeIDToUI(getCurrentGrade(prestigeLevel, vehicle.intCD))
        battlesCount = 0
        winsCount = 0
        vehicleRandomStats = accountRandomStats.getVehicles() if accountRandomStats is not None else {}
        if vehicle.intCD in vehicleRandomStats:
            battlesCount, winsCount, _ = vehicleRandomStats.get(vehicle.intCD)
        bpProgress, bpCap = self.__battlePass.getVehicleProgression(vehicle.intCD)
        model = VehicleStatisticModel()
        model.setId(str(vehicle.intCD))
        model.setIntCD(vehicle.intCD)
        model.setInventoryId(vehicle.invID)
        model.setXp(vehicle.xp)
        model.setBonusMultiplier(vehicle.dailyXPFactor)
        model.setElite(vehicle.isElite)
        model.setStatus(vState)
        model.setStateLevel(vStateLvl)
        model.setMastery(accountRandomStats.getMarkOfMasteryForVehicle(vehicle.intCD))
        model.setBattlesCount(battlesCount)
        model.setWinsCount(winsCount)
        model.setPrestigeLevel(prestigeLevel)
        model.setPrestigeGrade(grade)
        model.setPrestigeType(gradeType.value)
        model.setFromWotPlus(vehicle.isWotPlus)
        model.setBpSpecial(self.__battlePass.isSpecialVehicle(vehicle.intCD))
        model.setMaxBpScore(bpCap)
        model.setBpProgress(bpProgress)
        model.setOwn3DStyle(self.__accountStyles.critera(vehicle))
        if vehicle.isEarnCrystals:
            numberOfCrystalEarned = model.getNumberOfCrystalEarned()
            for numberOfCrystals in vehicle.getCrystalsEarnedInfo():
                numberOfCrystalEarned.addNumber(numberOfCrystals)

        return model

    @staticmethod
    def __getVehicleStatus(vehicle):
        vState, vStateLvl = vehicle.getState()
        if vehicle.isRotationApplied():
            if vState in (Vehicle.VEHICLE_STATE.AMMO_NOT_FULL, Vehicle.VEHICLE_STATE.LOCKED):
                vState = Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED
        if not vehicle.activeInNationGroup:
            vState = Vehicle.VEHICLE_STATE.NOT_PRESENT
        return (vState, vStateLvl)

    def __updateVehicles(self, vehicles):
        with self.viewModel.transaction() as model:
            accountRandomStats = self.__itemsCache.items.getAccountDossier().getRandomStats()
            vehiclePrestige = getVehiclePrestigeMap()
            statistics = model.getStatistics()
            for vehicle in itervalues(vehicles):
                prestigeLevel, _ = vehiclePrestige.get(vehicle.intCD, DEFAULT_PRESTIGE)
                item = self.__convertToStatisticsModel(vehicle, accountRandomStats, prestigeLevel)
                statistics.set(item.getId(), item)
