# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/mechanic_detectors.py
from __future__ import absolute_import
import typing
from collections import namedtuple, OrderedDict
from future.utils import viewitems
from gui.shared.utils import GUN_CAN_BE_CLIP, GUN_CLIP, GUN_AUTO_RELOAD, GUN_CAN_BE_AUTO_RELOAD, GUN_DUAL_GUN, GUN_CAN_BE_DUAL_GUN, GUN_AUTO_SHOOT, GUN_CAN_BE_AUTO_SHOOT, GUN_TWIN_GUN, GUN_CAN_BE_TWIN_GUN, GUN_CAN_BE_LOW_CHARGE_SHOT, LOW_CHARGE_SHOT
from gui.shared.items_parameters import isAutoReloadGun, isAutoShootGun, isDualGun, isDualAccuracy, isTwinGun, isLowChargeShotGun
from items.vehicle_mechanics_types import VehicleMechanicKeys, SpecBoostModeMechanicVariant
from vehicles.mechanics.mechanic_helpers import getMechanicFromMechanicsParams
if typing.TYPE_CHECKING:
    from items.vehicle_mechanics_types import VehicleMechanicKey
    from items.vehicles import VehicleDescriptor
ModuleMechanicData = namedtuple('ModuleMechanicData', ('mask', 'getter'))

def isCombatThrottleEngine(vDescr):
    params = getMechanicFromMechanicsParams(vDescr.type.mechanicsParams, VehicleMechanicKeys.COMBAT_THROTTLE)
    return params is not None and params.mechanicVariant == SpecBoostModeMechanicVariant.COMBAT_THROTTLE.value


def isHydraulicChassis(vDescr):
    return vDescr.hasHydraulicChassis or vDescr.isWheeledVehicle or vDescr.hasAutoSiegeMode if vDescr.hasSiegeMode else False


def hasChassisMechanicBit(mask, mechanic):
    return bool(mask & CHASSIS_MECHANICS_BITS.get(mechanic, 0))


ENGINE_MECHANIC_DETECTORS = {VehicleMechanicKeys.ROCKET_ACCELERATION: ModuleMechanicData(1, lambda vDescr: vDescr.hasRocketAcceleration),
 VehicleMechanicKeys.TURBOSHAFT_ENGINE: ModuleMechanicData(2, lambda vDescr: vDescr.hasTurboshaftEngine),
 VehicleMechanicKeys.STAGED_JET_BOOSTERS: ModuleMechanicData(4, lambda vDescr: vDescr.hasStagedJetBoosters),
 VehicleMechanicKeys.WHEELED_DASH: ModuleMechanicData(8, lambda vDescr: vDescr.hasWheeledDash),
 VehicleMechanicKeys.COMBAT_THROTTLE: ModuleMechanicData(16, isCombatThrottleEngine)}
ENGINE_MECHANICS_BITS = {mechanic:mask for mechanic, (mask, _) in viewitems(ENGINE_MECHANIC_DETECTORS)}

class ChassisTypes(object):
    DEFAULT = 0
    WHEELED = 1
    ON_SPOT_ROTATION_WHEELED = 2
    AUTO_SIEGE = 3


CHASSIS_MECHANIC_DETECTORS = {VehicleMechanicKeys.HYDRAULIC_CHASSIS: ModuleMechanicData(1, lambda chassis, vDescr: isHydraulicChassis(vDescr)),
 VehicleMechanicKeys.HYDRAULIC_WHEELED_CHASSIS: ModuleMechanicData(2, lambda chassis, vDescr: isHydraulicChassis(vDescr) and vDescr.isWheeledVehicle),
 VehicleMechanicKeys.TRACK_WITHIN_TRACK: ModuleMechanicData(4, lambda chassis, vDescr: chassis.isTrackWithinTrack),
 ChassisTypes.WHEELED: ModuleMechanicData(8, lambda chassis, vDescr: vDescr.isWheeledVehicle),
 ChassisTypes.AUTO_SIEGE: ModuleMechanicData(16, lambda chassis, vDescr: vDescr.hasAutoSiegeMode),
 ChassisTypes.ON_SPOT_ROTATION_WHEELED: ModuleMechanicData(32, lambda chassis, vDescr: vDescr.isWheeledOnSpotRotation)}
CHASSIS_MECHANICS_BITS = {mechanic:mask for mechanic, (mask, _) in viewitems(CHASSIS_MECHANIC_DETECTORS)}
GUN_MECHANICS_TO_RELOAD_TYPES = OrderedDict(((VehicleMechanicKeys.AUTO_LOADER_GUN, (GUN_CAN_BE_AUTO_RELOAD, GUN_AUTO_RELOAD)),
 (VehicleMechanicKeys.AUTO_SHOOT_GUN, (GUN_CAN_BE_AUTO_SHOOT, GUN_AUTO_SHOOT)),
 (VehicleMechanicKeys.MAGAZINE_GUN, (GUN_CAN_BE_CLIP, GUN_CLIP)),
 (VehicleMechanicKeys.DUAL_GUN, (GUN_CAN_BE_DUAL_GUN, GUN_DUAL_GUN)),
 (VehicleMechanicKeys.TWIN_GUN, (GUN_CAN_BE_TWIN_GUN, GUN_TWIN_GUN)),
 (VehicleMechanicKeys.LOW_CHARGE_SHOT, (GUN_CAN_BE_LOW_CHARGE_SHOT, LOW_CHARGE_SHOT))))
GUN_MECHANIC_DETECTORS = {VehicleMechanicKeys.AUTO_LOADER_GUN: lambda gun, vDescr: isAutoReloadGun(gun),
 VehicleMechanicKeys.AUTO_SHOOT_GUN: lambda gun, vDescr: isAutoShootGun(gun),
 VehicleMechanicKeys.MAGAZINE_GUN: lambda gun, vDescr: gun.clip[0] > 1,
 VehicleMechanicKeys.DUAL_GUN: lambda gun, vDescr: isDualGun(gun),
 VehicleMechanicKeys.DUAL_ACCURACY: lambda gun, vDescr: isDualAccuracy(gun),
 VehicleMechanicKeys.TWIN_GUN: lambda gun, vDescr: isTwinGun(gun),
 VehicleMechanicKeys.LOW_CHARGE_SHOT: lambda gun, vDescr: isLowChargeShotGun(gun)}
