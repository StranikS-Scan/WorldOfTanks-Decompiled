# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/vehicle_view_states.py
from helpers import dependency
from gui.prb_control import prbDispatcherProperty
from gui.shared.system_factory import registerVehicleViewState, collectVehicleViewStates
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IWotPlusController

class IVehicleViewState(object):
    __slots__ = ()

    @classmethod
    def isSuitableVehicle(cls, vehicle):
        raise NotImplementedError

    def isLocked(self):
        raise NotImplementedError

    def isEliteShown(self):
        raise NotImplementedError

    def isLevelShown(self):
        raise NotImplementedError

    def isRoleShown(self):
        raise NotImplementedError

    def isUIShown(self):
        raise NotImplementedError

    def isCrewOpsEnabled(self):
        raise NotImplementedError

    def isMaintenanceEnabled(self):
        raise NotImplementedError

    def isMaintenanceVisible(self):
        raise NotImplementedError

    def isCustomizationEnabled(self):
        raise NotImplementedError

    def isCustomizationVisible(self):
        raise NotImplementedError

    def isOnlyForEventBattles(self):
        raise NotImplementedError

    def isOptionalDevicesOpsEnabled(self):
        raise NotImplementedError

    def getCustomizationTooltip(self):
        raise NotImplementedError


class NoPresentViewState(IVehicleViewState):

    @classmethod
    def isSuitableVehicle(cls, vehicle):
        return False

    def isLocked(self):
        return False

    def isEliteShown(self):
        return False

    def isLevelShown(self):
        return False

    def isRoleShown(self):
        return False

    def isUIShown(self):
        return False

    def isCrewOpsEnabled(self):
        return False

    def isMaintenanceEnabled(self):
        return False

    def isMaintenanceVisible(self):
        return False

    def isCustomizationEnabled(self):
        return False

    def isCustomizationVisible(self):
        return False

    def isOnlyForEventBattles(self):
        return False

    def isOptionalDevicesOpsEnabled(self):
        return False

    def getCustomizationTooltip(self):
        pass


class SelectedViewState(IVehicleViewState):
    __slots__ = ('_locked', '_isInHangar', '_isBroken', '_isDisabledInRent', '_isOnlyForEventBattles', '_isOutfitLocked', '_isCustomizationEnabled', '_isEliteShown', '_isLevelShown', '_isRoleShown', '_isMaintenanceVisible', '_isCustomizationVisible')

    def __init__(self, vehicle):
        super(SelectedViewState, self).__init__()
        self._isEliteShown = self._isLevelShown = self._isRoleShown = True
        self._isMaintenanceVisible = self._isCustomizationVisible = True
        self._resolveVehicleState(vehicle)
        self._resolvePrbState()

    @classmethod
    def isSuitableVehicle(cls, vehicle):
        return True

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getCustomizationTooltip(self):
        pass

    def isLocked(self):
        return self._locked

    def isEliteShown(self):
        return self._isEliteShown

    def isLevelShown(self):
        return self._isLevelShown

    def isRoleShown(self):
        return self._isRoleShown

    def isUIShown(self):
        return True

    def isCrewOpsEnabled(self):
        return not self._locked and not self._isOnlyForEventBattles

    def isMaintenanceEnabled(self):
        return not self._locked and self._isInHangar

    def isMaintenanceVisible(self):
        return self._isMaintenanceVisible

    def isCustomizationEnabled(self):
        return self._isCustomizationEnabled

    def isCustomizationVisible(self):
        return self._isCustomizationVisible

    def isOnlyForEventBattles(self):
        return self._isOnlyForEventBattles

    def isOptionalDevicesOpsEnabled(self):
        return self.isMaintenanceEnabled() and not self._isBroken

    def isOutfitLocked(self):
        return self._isOutfitLocked

    def _resolveVehicleState(self, vehicle):
        self._isInHangar = vehicle.isInHangar() and not vehicle.isDisabled()
        self._isBroken = vehicle.isBroken()
        self._isDisabledInRent = vehicle.isDisabledInRent()
        self._isOnlyForEventBattles = vehicle.isOnlyForEventBattles()
        self._isOutfitLocked = vehicle.isOutfitLocked()
        self._isCustomizationEnabled = vehicle.isCustomizationEnabled()

    def _resolvePrbState(self):
        self._locked = False
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                self._locked = not permission.canChangeVehicle()
        return


class PremiumIGRViewState(SelectedViewState):
    __slots__ = ('_isDisabledInPremIGR',)

    @classmethod
    def isSuitableVehicle(cls, vehicle):
        return vehicle.isPremiumIGR()

    def isMaintenanceEnabled(self):
        return super(PremiumIGRViewState, self).isMaintenanceEnabled() and not self._isDisabledInPremIGR

    def isCustomizationEnabled(self):
        return super(PremiumIGRViewState, self).isCustomizationEnabled() and not self._isDisabledInPremIGR

    def _resolveVehicleState(self, vehicle):
        super(PremiumIGRViewState, self)._resolveVehicleState(vehicle)
        self._isDisabledInPremIGR = False
        dossier = vehicle.getDossier()
        if dossier is None or not dossier.getTotalStats().getBattlesCount():
            self._isDisabledInPremIGR |= vehicle.isDisabledInPremIGR()
        return


registerVehicleViewState(PremiumIGRViewState)

class WoTPlusVehicleViewState(SelectedViewState):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def isSuitableVehicle(cls, vehicle):
        return vehicle.isWotPlus()

    def isMaintenanceEnabled(self):
        isWotPlusMaintenanceEnabled = self._wotPlusCtrl.isEnabled() and self.lobbyContext.getServerSettings().isWoTPlusExclusiveVehicleEnabled()
        return super(WoTPlusVehicleViewState, self).isMaintenanceEnabled() and isWotPlusMaintenanceEnabled


registerVehicleViewState(WoTPlusVehicleViewState)

def createState4CurrentVehicle(vehicle):
    if vehicle.isPresent():
        viewStates = collectVehicleViewStates()
        state = findFirst(lambda s: s.isSuitableVehicle(vehicle), viewStates, SelectedViewState)(vehicle)
    else:
        state = NoPresentViewState()
    return state
