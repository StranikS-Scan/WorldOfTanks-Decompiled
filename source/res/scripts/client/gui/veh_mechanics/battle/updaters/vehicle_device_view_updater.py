# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/vehicle_device_view_updater.py
import typing
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class IVehicleDeviceStatusView(object):

    def vehicleDeviceStatusChanged(self, devicesStatuses):
        raise NotImplementedError


class VehicleDeviceStatusUpdater(ViewUpdater):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, observed, view):
        super(VehicleDeviceStatusUpdater, self).__init__(view)
        self.__observed = observed
        self.__devicesStatuses = {}

    def initialize(self):
        super(VehicleDeviceStatusUpdater, self).initialize()
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            values = ctrl.getStateValue(VEHICLE_VIEW_STATE.DEVICES)
            if values:
                self.__devicesStatuses = {value[0]:value[2] for value in values}
                self.view.vehicleDeviceStatusChanged(self.__devicesStatuses)
        return

    def finalize(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(VehicleDeviceStatusUpdater, self).finalize()
        return

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.DEVICES and isinstance(value, tuple):
            self.__onVehicleDeviceStatusChanged(value[0], value[2])

    def __onVehicleDeviceStatusChanged(self, deviceName, status):
        if deviceName in self.__observed:
            if status in self.__observed[deviceName]:
                self.__devicesStatuses[deviceName] = status
                self.view.vehicleDeviceStatusChanged(self.__devicesStatuses)
            elif deviceName in self.__devicesStatuses:
                del self.__devicesStatuses[deviceName]
                self.view.vehicleDeviceStatusChanged(self.__devicesStatuses)
