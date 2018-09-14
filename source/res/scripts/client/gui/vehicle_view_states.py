# Embedded file name: scripts/client/gui/vehicle_view_states.py
from gui.prb_control.prb_helpers import prbDispatcherProperty

class IVehicleViewState(object):
    __slots__ = ()

    def isLocked(self):
        raise NotImplementedError

    def isUIShown(self):
        raise NotImplementedError

    def isCrewOpsEnabled(self):
        raise NotImplementedError

    def isMaintenanceEnabled(self):
        raise NotImplementedError

    def isCustomizationEnabled(self):
        raise NotImplementedError

    def getCustomizationTooltip(self):
        raise NotImplementedError

    def isOptionalDevicesOpsEnabled(self):
        raise NotImplementedError


class NoPresentViewState(IVehicleViewState):

    def isLocked(self):
        return False

    def isUIShown(self):
        return False

    def isCrewOpsEnabled(self):
        return False

    def isMaintenanceEnabled(self):
        return False

    def isCustomizationEnabled(self):
        return False

    def isOnlyForEventBattles(self):
        return False

    def isOptionalDevicesOpsEnabled(self):
        return False


class SelectedViewState(IVehicleViewState):
    __slots__ = ('_locked', '_isInHangar', '_isBroken', '_isDisabledInRent', '_isOnlyForEventBattles')

    def __init__(self, vehicle):
        super(SelectedViewState, self).__init__()
        self._resolveVehicleState(vehicle)
        self._resolvePrbState()

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getCustomizationTooltip(self):
        return ''

    def _resolveVehicleState(self, vehicle):
        self._isInHangar = vehicle.isInHangar()
        self._isBroken = vehicle.isBroken()
        self._isDisabledInRent = vehicle.isDisabledInRent()
        self._isOnlyForEventBattles = vehicle.isOnlyForEventBattles()

    def _resolvePrbState(self):
        self._locked = False
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                self._locked = not permission.canChangeVehicle()
        return

    def isLocked(self):
        return self._locked

    def isUIShown(self):
        return True

    def isCrewOpsEnabled(self):
        return not self._locked and self._isInHangar

    def isMaintenanceEnabled(self):
        return not self._locked and self._isInHangar

    def isCustomizationEnabled(self):
        return not self._isOnlyForEventBattles and self._isInHangar and not self._locked and not self._isBroken and not self._isDisabledInRent

    def isOnlyForEventBattles(self):
        return self._isOnlyForEventBattles

    def isOptionalDevicesOpsEnabled(self):
        return self.isMaintenanceEnabled() and not self._isBroken


class PremiumIGRViewState(SelectedViewState):
    __slots__ = ('_isDisabledInPremIGR',)

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


def createState4CurrentVehicle(vehicle):
    if vehicle.isPresent():
        if vehicle.isPremiumIGR():
            state = PremiumIGRViewState(vehicle)
        else:
            state = SelectedViewState(vehicle)
    else:
        state = NoPresentViewState()
    return state
