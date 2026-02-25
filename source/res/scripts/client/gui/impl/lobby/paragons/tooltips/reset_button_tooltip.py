# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/reset_button_tooltip.py
from abc import abstractmethod
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.reset_button_tooltip_model import ResetButtonTooltipModel, FeatureState
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import packParagonsTooltipVehicleModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IParagonsController
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from skeletons.gui.shared import IItemsCache

class ResetButtonTooltipDataProvider(object):
    __paragonsController = dependency.descriptor(IParagonsController)
    __slots__ = ('__branchID', '__isBranchCanBeReset', '__branchVehicles')

    def __init__(self, branchID):
        self.__branchID = branchID
        self.__isBranchCanBeReset = None
        self.__branchVehicles = None
        super(ResetButtonTooltipDataProvider, self).__init__()
        return

    @property
    def controller(self):
        return self.__paragonsController

    @property
    def branchResetCompensation(self):
        return self.__paragonsController.branches.getBranchResetCompensation(self.__branchID)

    @property
    def branchResetVehicles(self):
        return self.__paragonsController.getBranchResetVehicles(self.__branchID)

    @property
    def completeBonusCoins(self):
        return self.__paragonsController.getCompleteBonusCoinsForBranch(self.__branchID)

    @property
    def isBranchCanBeReset(self):
        if self.__isBranchCanBeReset is None:
            self.__isBranchCanBeReset, self.__branchVehicles = self.__paragonsController.branches.isBranchCanBeReset(self.__branchID)
        return self.__isBranchCanBeReset

    @property
    def isFirstUnlockBranchAvailable(self):
        return self.__paragonsController.isFirstUnlockBranchAvailable(self.__branchID, False)

    @property
    def isFirstUnlockBranch(self):
        return self.__paragonsController.isFirstUnlockBranchAvailable(self.__branchID, True)

    @property
    def lockedResetVehicles(self):
        return self.__paragonsController.getLockedResetVehicles(self.__branchID)

    @property
    def branchVehicles(self):
        if self.__branchVehicles is None:
            self.__isBranchCanBeReset, self.__branchVehicles = self.__paragonsController.branches.isBranchCanBeReset(self.__branchID)
        return self.__branchVehicles

    @property
    def isBranchReset(self):
        return self.__paragonsController.isBranchReset(self.__branchID)

    @property
    def branchID(self):
        return self.__branchID


class ResetButtonTooltipStateBase(object):
    __slots__ = ('_dataProvider',)

    def __init__(self, dataProvider):
        self._dataProvider = dataProvider
        super(ResetButtonTooltipStateBase, self).__init__()

    @property
    @abstractmethod
    def state(self):
        raise NotImplementedError

    @abstractmethod
    def isInState(self):
        raise NotImplementedError

    @abstractmethod
    def packModel(self, model):
        raise NotImplementedError


class ResetButtonTooltipStatePaused(ResetButtonTooltipStateBase):

    @property
    def state(self):
        return FeatureState.IS_PAUSED

    def isInState(self):
        return self._dataProvider.controller.isPaused

    def packModel(self, model):
        pass


class ResetButtonTooltipStateIsActive(ResetButtonTooltipStateBase):

    @property
    def state(self):
        return FeatureState.IS_ACTIVE

    def isInState(self):
        return self._dataProvider.isBranchCanBeReset

    def packModel(self, model):
        controller = self._dataProvider.controller
        branchResetVehicles = self._dataProvider.branchResetVehicles
        model.setResetBranchesCount(controller.branches.resetBranchesCount)
        model.setMaxResetBranchesCount(controller.branches.maxResetBranchesCount)
        model.setParagonsPoints(sum((controller.getVehicleProgressPoints(veh.intCD) for veh in branchResetVehicles)))
        model.setBranchResetPoints(controller.getCoinsForBranchReset())
        model.setBonusPoints(self._dataProvider.completeBonusCoins)
        model.setCredits(self._dataProvider.branchResetCompensation)


class ResetButtonTooltipStateLimitReached(ResetButtonTooltipStateBase):

    @property
    def state(self):
        return FeatureState.LIMIT_REACHED

    def isInState(self):
        controller = self._dataProvider.controller
        return controller.branches.resetBranchesCount == controller.branches.maxResetBranchesCount

    def packModel(self, model):
        model.setResetBranchesCount(self._dataProvider.controller.branches.resetBranchesCount)


class ResetButtonTooltipFirstBranchState(ResetButtonTooltipStateBase):

    @property
    def state(self):
        return FeatureState.FIRST_BRANCH_RESET

    def isInState(self):
        return self._dataProvider.isFirstUnlockBranch

    def packModel(self, model):
        hashed = set()
        for lockedVehicles in self._dataProvider.lockedResetVehicles:
            hashed.add(lockedVehicles)

        packParagonsTooltipVehicleModel(model, hashed)


class ResetButtonTooltipNotAvailableState(ResetButtonTooltipFirstBranchState):

    @property
    def state(self):
        return FeatureState.PARAGONS_NOT_AVAILABLE

    def isInState(self):
        return not self._dataProvider.controller.wasBranchResetEverAvailable and self._dataProvider.isFirstUnlockBranchAvailable

    def packModel(self, model):
        super(ResetButtonTooltipNotAvailableState, self).packModel(model)
        controller = self._dataProvider.controller
        vehiclesCount = min(controller.minUnlockedNecessaryLevelVehiclesCount, controller.unlockedNecessaryLevelVehiclesCount)
        model.setVehicleCount(vehiclesCount)
        model.setNecessaryVehicleCount(controller.minUnlockedNecessaryLevelVehiclesCount)


class ResetButtonTooltipVehicleRequired(ResetButtonTooltipStateBase):

    @property
    def state(self):
        return FeatureState.VEHICLES_REQUIRED

    def isInState(self):
        controller = self._dataProvider.controller
        return controller.unlockedNecessaryLevelVehiclesCount < controller.minUnlockedNecessaryLevelVehiclesCount

    def packModel(self, model):
        controller = self._dataProvider.controller
        vehiclesCount = min(controller.minUnlockedNecessaryLevelVehiclesCount, controller.unlockedNecessaryLevelVehiclesCount)
        model.setVehicleCount(vehiclesCount)
        model.setNecessaryVehicleCount(controller.minUnlockedNecessaryLevelVehiclesCount)


class ResetButtonTooltipRulesIncomplete(ResetButtonTooltipStateBase):

    @property
    def state(self):
        return FeatureState.RULES_INCOMLETED

    def isInState(self):
        return not self._dataProvider.isBranchCanBeReset

    def packModel(self, model):
        hashed = set()
        for branchVehicles in self._dataProvider.branchVehicles.itervalues():
            for branchVehicle in branchVehicles:
                hashed.add(branchVehicle)

        packParagonsTooltipVehicleModel(model, hashed)


class ResetButtonTooltipBranchWasResetState(ResetButtonTooltipStateBase):
    __paragonsController = dependency.descriptor(IParagonsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @property
    def state(self):
        return FeatureState.DROPPED_BRANCH

    def isInState(self):
        return self._dataProvider.isBranchReset

    def packModel(self, model):
        model.setBonusPoints(self._dataProvider.completeBonusCoins)
        hashed = set()
        branchVehicles = self.__paragonsController.paragons.storage.branchPendingVehicles(self._dataProvider.branchID)
        for branchVehicle in branchVehicles:
            vehicle = self.__itemsCache.items.getItemByCD(branchVehicle)
            hashed.add(vehicle)

        packParagonsTooltipVehicleModel(model, hashed)
        battleTypes = model.getBattleTypes()
        for bonusType in ARENA_BONUS_TYPE.RANGE:
            if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.PARAGONS):
                battleTypes.addNumber(bonusType)

        battleTypes.invalidate()


class ResetButtonTooltip(ViewImpl):
    __slots__ = ('__state',)
    _STATE_ORDER = (ResetButtonTooltipStatePaused,
     ResetButtonTooltipNotAvailableState,
     ResetButtonTooltipFirstBranchState,
     ResetButtonTooltipBranchWasResetState,
     ResetButtonTooltipVehicleRequired,
     ResetButtonTooltipStateLimitReached,
     ResetButtonTooltipRulesIncomplete,
     ResetButtonTooltipStateIsActive)

    def __init__(self, branchID, layoutID):
        dataProvider = ResetButtonTooltipDataProvider(branchID)
        self.__state = None
        for stateCls in self._STATE_ORDER:
            state = stateCls(dataProvider)
            if state.isInState():
                self.__state = state
                break

        settings = ViewSettings(layoutID, model=ResetButtonTooltipModel())
        super(ResetButtonTooltip, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ResetButtonTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        if self.__state is not None:
            with self.viewModel.transaction() as transaction:
                transaction.setState(self.__state.state)
                self.__state.packModel(transaction)
        return
