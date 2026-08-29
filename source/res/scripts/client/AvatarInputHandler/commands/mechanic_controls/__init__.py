# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/mechanic_controls/__init__.py
from __future__ import absolute_import
import typing
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanics
from .auto_shoot_gun_control import createAutoShootGunControl
from .nitro_control import createNitroActivationControl
from .sight_pointer_control import createSightPointerActivationControl
from .simple_activation_control import createSimpleActivationControl
from .stance_dance_control import createStanceDanceControl
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
VEHICLE_MECHANIC_CONTROLS = {VehicleMechanic.ROCKET_ACCELERATION: createSimpleActivationControl,
 VehicleMechanic.RECHARGEABLE_NITRO: createNitroActivationControl,
 VehicleMechanic.AUTO_SHOOT_GUN: createAutoShootGunControl,
 VehicleMechanic.CONCENTRATION_MODE: createSimpleActivationControl,
 VehicleMechanic.SUPPORT_WEAPON: createSimpleActivationControl,
 VehicleMechanic.CHARGE_SHOT: createSimpleActivationControl,
 VehicleMechanic.TARGET_DESIGNATOR: createSimpleActivationControl,
 VehicleMechanic.STANCE_DANCE: createStanceDanceControl,
 VehicleMechanic.AUTORELOADER_SURGE: createSimpleActivationControl,
 VehicleMechanic.STATIONARY_RELOAD: createSimpleActivationControl,
 VehicleMechanic.PROPELLANT_GUN: createSimpleActivationControl,
 VehicleMechanic.SIGHT_POINTER: createSightPointerActivationControl}

def createMechanicControls(vehicleDescriptor):
    return tuple((VEHICLE_MECHANIC_CONTROLS[mechanic](mechanic) for mechanic in getVehicleDescrMechanics(vehicleDescriptor) if mechanic in VEHICLE_MECHANIC_CONTROLS))
