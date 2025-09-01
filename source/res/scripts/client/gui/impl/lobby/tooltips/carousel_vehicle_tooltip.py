# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/carousel_vehicle_tooltip.py
import logging
import math
import typing
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillIntsArray
from gui.battle_pass.battle_pass_helpers import getSupportedCurrentArenaBonusType
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.carousel_vehicle_tooltip_model import CarouselVehicleTooltipModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleMechanicsArray
from gui.impl.lobby.hangar.presenters.crew_presenter import setCrewSlots
from gui.prestige.prestige_helpers import mapGradeIDToUI, getCurrentGrade, getCurrentProgress, getVehiclePrestige
from gui.prb_control import prbEntityProperty
from gui.shared.gui_items.dossier.achievements import isMarkOfMasteryAchieved
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBattlePassController, IWotPlusController
from skeletons.gui.shared import IItemsCache
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.impl.gen.view_models.views.lobby.tooltips.statistics_model import StatisticsModel
    from gui.impl.gen.view_models.views.lobby.tooltips.earnings_model import EarningsModel
    from gui.impl.gen.view_models.views.lobby.tooltips.service_records_model import ServiceRecordsModel
_logger = logging.getLogger(__name__)

class CarouselVehicleTooltipView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _battlePass = dependency.descriptor(IBattlePassController)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def __init__(self, inventoryId):
        self._inventoryId = inventoryId
        settings = ViewSettings(R.views.mono.hangar.vehicle_tooltip(), model=CarouselVehicleTooltipModel())
        super(CarouselVehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CarouselVehicleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        vehicle = self._itemsCache.items.getVehicle(self._inventoryId)
        if not vehicle:
            _logger.error('No vehicle for with inventoryId %s for displaying a tooltip', self._inventoryId)
            return
        vState, vStateLevel = vehicle.getState()
        with self.viewModel.transaction() as model:
            model.setStatus(vState)
            model.setStateLevel(vStateLevel)
            model.setBpEntityValid(self._battlePass.isGameModeEnabled(self.__getCurrentArenaBonusType()))
            setCrewSlots(model.statistics.getSlots(), vehicle)
            self.__setStatistics(model.statistics, vehicle)
            self.__setEarnings(model.earnings, vehicle)
            self.__setServiceRecords(model.serviceRecords, vehicle)
            fillVehicleMechanicsArray(model.getMechanics(), vehicle)

    @prbEntityProperty
    def __prbEntity(self):
        return None

    def __getCurrentArenaBonusType(self):
        return getSupportedCurrentArenaBonusType(self.__prbEntity.getQueueType())

    def __setStatistics(self, statisticsModel, vehicle):
        statisticsModel.setLevel(vehicle.level)
        statisticsModel.setType(vehicle.type)
        statisticsModel.setPremium(vehicle.isPremium)
        statisticsModel.setName(vehicle.typeDescr.userString)
        statisticsModel.setNationId(vehicle.nationID)
        statisticsModel.setRole(vehicle.role)
        statisticsModel.setElite(vehicle.isElite)
        statisticsModel.setRentLeftTime(vehicle.rentLeftTime if not math.isinf(vehicle.rentLeftTime) else -1)
        statisticsModel.setRentLeftBattles(vehicle.rentLeftBattles or 0)
        statisticsModel.setRentLeftWins(vehicle.rentLeftWins or 0)

    def __setEarnings(self, earningsModel, vehicle):
        vehicleIntCD = vehicle.intCD
        earningsModel.setXp(vehicle.xp)
        earningsModel.setBonusMultiplier(vehicle.dailyXPFactor)
        earningsModel.setWotPlus(vehicle.isWotPlus)
        earningsModel.setWotPlusExpiryTime(self._wotPlusCtrl.getExpiryTime() or -1)
        earningsModel.setWotPlusState(self._wotPlusCtrl.getState().name)
        earningsModel.setBpReward(self._battlePass.getVehicleCapBonus(vehicleIntCD))
        bpPoints, bpCap = self._battlePass.getVehicleProgression(vehicleIntCD)
        earningsModel.setMaxBpScore(bpCap)
        earningsModel.setCurrentBpScore(bpPoints)
        earningsModel.setBpActive(self._battlePass.isActive())
        daysLeft = time_utils.getServerRegionalDaysLeftInGameWeek() * time_utils.ONE_DAY
        timeLeft = daysLeft + time_utils.getDayTimeLeft()
        earningsModel.setCrystalTimeout(timeLeft)
        earningsModel.setCrystalEarning(vehicle.isEarnCrystals)
        numberOfCrystalEarned = earningsModel.getNumberOfCrystalEarned()
        fillIntsArray(vehicle.getCrystalsEarnedInfo(), numberOfCrystalEarned)

    def __setServiceRecords(self, serviceRecordsModel, vehicle):
        vehDossier = self._itemsCache.items.getVehicleDossier(vehicle.intCD)
        vehStats = vehDossier.getTotalStats()
        marksOnGun = vehStats.getAchievement(MARK_ON_GUN_RECORD)
        marksOnGunValue = marksOnGun.getValue()
        if marksOnGunValue > 0:
            serviceRecordsModel.setMarksOnGunPercentage(str(marksOnGun.getDamageRating()))
            serviceRecordsModel.setMarksOnGun(marksOnGunValue)
        randomStats = self._itemsCache.items.getAccountDossier().getRandomStats()
        vehicleRandomStats = randomStats.getVehicles() if randomStats is not None else {}
        markOfMastery = randomStats.getMarkOfMasteryForVehicle(vehicle.intCD)
        if isMarkOfMasteryAchieved(markOfMastery):
            serviceRecordsModel.setMarksOfMastery(markOfMastery)
        if vehicle.intCD in vehicleRandomStats:
            battlesCount, winsCount, _ = vehicleRandomStats.get(vehicle.intCD)
            serviceRecordsModel.setWinsCount(winsCount)
            serviceRecordsModel.setBattlesCount(battlesCount)
        currentLevel, remainingPts = getVehiclePrestige(vehicle.intCD)
        gradeType, grade = mapGradeIDToUI(getCurrentGrade(currentLevel, vehicle.intCD))
        if currentLevel > 0:
            currentXP, nextLvlXP = getCurrentProgress(vehicle.intCD, currentLevel, remainingPts)
            serviceRecordsModel.setPrestigeXp(currentXP)
            serviceRecordsModel.setPrestigeXpNextLevel(nextLvlXP)
        serviceRecordsModel.setPrestigeLevel(currentLevel)
        serviceRecordsModel.setPrestigeGrade(grade)
        serviceRecordsModel.setPrestigeType(gradeType.value)
        return
