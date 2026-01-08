# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/mechanic_controls/__init__.py
from __future__ import absolute_import
import typing
from AvatarInputHandler.commands.mechanic_controls.auto_shoot_gun_control import createAutoShootGunControl
from AvatarInputHandler.commands.mechanic_controls.nitro_control import createNitroActivationControl
from AvatarInputHandler.commands.mechanic_controls.simple_activation_control import createSimpleActivationControl
from AvatarInputHandler.commands.mechanic_controls.stance_dance_control import createStanceDanceControl
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanics
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescr
VEHICLE_MECHANIC_CONTROLS = {VehicleMechanic.ROCKET_ACCELERATION: createSimpleActivationControl,
 VehicleMechanic.RECHARGEABLE_NITRO: createNitroActivationControl,
 VehicleMechanic.AUTO_SHOOT_GUN: createAutoShootGunControl,
 VehicleMechanic.CONCENTRATION_MODE: createSimpleActivationControl,
 VehicleMechanic.SUPPORT_WEAPON: createSimpleActivationControl,
 VehicleMechanic.CHARGE_SHOT: createSimpleActivationControl,
 VehicleMechanic.TARGET_DESIGNATOR: createSimpleActivationControl,
 VehicleMechanic.STANCE_DANCE: createStanceDanceControl,
 VehicleMechanic.STATIONARY_RELOAD: createSimpleActivationControl}

def createMechanicControls(vehicleDescriptor):
    return tuple((VEHICLE_MECHANIC_CONTROLS[mechanic](mechanic) for mechanic in getVehicleDescrMechanics(vehicleDescriptor) if mechanic in VEHICLE_MECHANIC_CONTROLS))
