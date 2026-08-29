# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/shell_mechanics_helper.py
from __future__ import absolute_import
from typing import Tuple, List, Optional, TYPE_CHECKING
from enum import Enum
from gui.shared.items_parameters import params_helper
from items.utils import getVehicleDescriptorWithoutMechanics
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import hasVehicleDescrMechanic
if TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_modules import Shell
    from items.vehicles import VehicleDescr

class ShellMechanicState(int, Enum):
    UNDEFINED = 0
    ON = 1
    OFF = 2


def getShellParameters(vehicle, shell):
    vehicleDescr = vehicle.descriptor
    mechanic = next(shell.getMechanics(vehicleDescr), None)
    handler = _MECHANICS_PARAMS_HANDLERS.get(mechanic, _getDefaultShellParams)
    parameters = handler(shell, vehicle)
    return (mechanic, parameters)


def _getDefaultShellMechanic(vehicleDescr):
    mechanics = (m for m in _MECHANICS_PARAMS_HANDLERS if hasVehicleDescrMechanic(vehicleDescr, m))
    return next(mechanics, None)


def _getDefaultShellParams(shell, vehicle):
    return [(ShellMechanicState.UNDEFINED, params_helper.getParameters(shell, vehicle.descriptor))]


def _getLowChargeParams(shell, vehicle):
    vehicleDescr = vehicle.descriptor
    params = [(ShellMechanicState.OFF, params_helper.getParameters(shell, vehicleDescr.defaultVehicleDescr)), (ShellMechanicState.ON, params_helper.getParameters(shell, vehicleDescr.siegeVehicleDescr))]
    return params


def _getSwitchedParams(shell, vehicle):
    vehicleDescr = vehicle.descriptor
    params = [(ShellMechanicState.OFF, params_helper.getParameters(shell, vehicleDescr)), (ShellMechanicState.ON, params_helper.getParameters(shell, vehicleDescr.siegeVehicleDescr))]
    return params


def _getShellCalibrationParams(shell, vehicle):
    vehicleDescrWithoutMechanic = getVehicleDescriptorWithoutMechanics(vehicle.descriptor, VehicleMechanic.SHELL_CALIBRATION.value)
    vehicleDescr = vehicle.descriptor
    params = [(ShellMechanicState.OFF, params_helper.getParameters(shell, vehicleDescrWithoutMechanic)), (ShellMechanicState.ON, params_helper.getParameters(shell, vehicleDescr))]
    return params


def _getBustleFeedParams(shell, vehicle):
    vehicleDescr = vehicle.descriptor.defaultVehicleDescr
    vehicleDescrWithoutMechanics = getVehicleDescriptorWithoutMechanics(vehicleDescr, VehicleMechanic.BUSTLE_FEED.value)
    params = [(ShellMechanicState.OFF, params_helper.getParameters(shell, vehicleDescrWithoutMechanics)), (ShellMechanicState.ON, params_helper.getParameters(shell, vehicleDescr))]
    return params


_MECHANICS_PARAMS_HANDLERS = {VehicleMechanic.LOW_CHARGE_SHOT: _getLowChargeParams,
 VehicleMechanic.SHELL_PARAMS_SWITCHER: _getSwitchedParams,
 VehicleMechanic.SHELL_CALIBRATION: _getShellCalibrationParams,
 VehicleMechanic.BUSTLE_FEED: _getBustleFeedParams}
