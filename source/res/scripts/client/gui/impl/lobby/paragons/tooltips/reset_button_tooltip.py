# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/reset_button_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.paragons_tooltip_vehicles_model import ParagonsTooltipVehiclesModel
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.reset_button_tooltip_model import ResetButtonTooltipModel, FeatureState
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IParagonsController
from skeletons.gui.shared import IItemsCache

class ResetButtonTooltip(ViewImpl):
    __slots__ = ('__branchID',)
    __paragonsController = dependency.descriptor(IParagonsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, branchID, layoutID):
        self.__branchID = branchID
        settings = ViewSettings(layoutID, model=ResetButtonTooltipModel())
        super(ResetButtonTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ResetButtonTooltip, self).getViewModel()

    @property
    def vechiclesRequered(self):
        unlockedNecessaryLevelVehiclesCount = self.__paragonsController.unlockedNecessaryLevelVehiclesCount
        minUnlockedNecessaryLevelVehiclesCount = self.__paragonsController.minUnlockedNecessaryLevelVehiclesCount
        return unlockedNecessaryLevelVehiclesCount < minUnlockedNecessaryLevelVehiclesCount

    @property
    def limitReached(self):
        resetBranchesCount = self.__paragonsController.branches.resetBranchesCount
        maxResetBranchesCount = self.__paragonsController.branches.maxResetBranchesCount
        return resetBranchesCount == maxResetBranchesCount

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as transaction:
            isBranchCanBeReset, branchVehicles = self.__paragonsController.branches.isBranchCanBeReset(self.__branchID)
            if self.__paragonsController.isPaused:
                transaction.setState(FeatureState.IS_PAUSED)
            elif self.vechiclesRequered:
                vehiclesCount = min(self.__paragonsController.minUnlockedNecessaryLevelVehiclesCount, self.__paragonsController.unlockedNecessaryLevelVehiclesCount)
                transaction.setState(FeatureState.VEHICLES_REQUERED)
                transaction.setVehicleCount(vehiclesCount)
                transaction.setNecessaryVehicleCount(self.__paragonsController.minUnlockedNecessaryLevelVehiclesCount)
            elif self.limitReached:
                transaction.setState(FeatureState.LIMIT_REACHED)
                transaction.setResetBranchesCount(self.__paragonsController.branches.resetBranchesCount)
            elif not isBranchCanBeReset:
                transaction.setState(FeatureState.RULES_INCOMLETED)
                hashed = set()
                for branchVehicles in branchVehicles.itervalues():
                    for branchVehicle in branchVehicles:
                        hashed.add(branchVehicle)

                vehicles = transaction.getVehicles()
                for hashedVehicle in hashed:
                    vehicle = ParagonsTooltipVehiclesModel()
                    vehicle.setVehicleName(hashedVehicle.userName)
                    vehicle.setHasProgressionPoints(hashedVehicle.isResetParagons)
                    vehicle.setNeedRepair(hashedVehicle.isBroken)
                    vehicle.setIsInBattle(hashedVehicle.isInBattle)
                    vehicle.setIsInPlatoonFormation(hashedVehicle.isInUnit)
                    vehicle.setNeedResearch(not hashedVehicle.isUnlocked)
                    vehicles.addViewModel(vehicle)

            elif isBranchCanBeReset:
                credits = self.__paragonsController.branches.getBranchResetCompensation(self.__branchID)
                branchResetVehicles = self.__paragonsController.getBranchResetVehicles(self.__branchID)
                transaction.setState(FeatureState.IS_ACTIVE)
                transaction.setResetBranchesCount(self.__paragonsController.branches.resetBranchesCount)
                transaction.setMaxResetBranchesCount(self.__paragonsController.branches.maxResetBranchesCount)
                transaction.setParagonsPoints(sum((self.__paragonsController.getVehicleProgressPoints(veh.intCD) for veh in branchResetVehicles)))
                transaction.setCredits(credits)
