# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/vehicle_misc_status_view_updater.py
import typing
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, DestroyTimerViewState
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
MISC_STATUS_LEVEL_CRITICAL = 'critical'
MISC_STATUS_LEVEL_WARNING = 'warning'
MISC_STATUSES_ORDER = (MISC_STATUS_LEVEL_CRITICAL, MISC_STATUS_LEVEL_WARNING)

class IVehicleMiscStatusView(object):

    def vehicleMiscStatusChanged(self, miscStatuses):
        raise NotImplementedError


class _ObservableMiscStatuses(object):

    def __init__(self, observed):
        self.__observed = observed
        self.__miscStatuses = {}

    @property
    def statuses(self):
        return self.__miscStatuses

    @property
    def hasNegativeEffect(self):
        return bool(self.__miscStatuses)

    def addStatus(self, code, level):
        if code in self.__observed and level in self.__observed[code]:
            self.__miscStatuses[code] = level

    def updateStatus(self, code, level):
        if code in self.__observed:
            if level in self.__observed[code]:
                self.__miscStatuses[code] = level
                return True
            if code in self.__miscStatuses:
                del self.__miscStatuses[code]
                return True
        return False

    def clear(self):
        self.__observed = None
        return


class VehicleMiscStatusUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, observed, view):
        super(VehicleMiscStatusUpdater, self).__init__(view)
        self.__miscStatuses = _ObservableMiscStatuses(observed)

    def initialize(self):
        super(VehicleMiscStatusUpdater, self).initialize()
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            stateValue = ctrl.getStateValue(VEHICLE_VIEW_STATE.DESTROY_TIMER)
            if stateValue:
                self.__miscStatuses.addStatus(stateValue.code, stateValue.level)
                self.view.vehicleMiscStatusChanged(self.__miscStatuses)
        return

    def finalize(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.__miscStatuses.clear()
        self.__miscStatuses = None
        super(VehicleMiscStatusUpdater, self).finalize()
        return

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.DESTROY_TIMER and isinstance(value, DestroyTimerViewState) and self.__miscStatuses.updateStatus(value.code, value.level):
            self.view.vehicleMiscStatusChanged(self.__miscStatuses)
