# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_constants.py
from __future__ import absolute_import
from enum import Enum
from future.utils import viewitems
from items.components import shared_components

class VehicleMechanic(Enum):
    MAGAZINE_GUN = 'magazineGun'
    AUTO_LOADER_GUN = 'autoLoaderGun'
    AUTO_LOADER_GUN_BOOST = 'autoLoaderGunBoost'
    DAMAGE_MUTABLE = 'damageMutable'
    DUAL_GUN = 'dualGun'
    HYDRAULIC_CHASSIS = 'hydraulicChassis'
    TRACK_WITHIN_TRACK = 'trackWithinTrack'
    SIEGE_MODE = 'siegeMode'
    STUN = 'stun'
    HYDRAULIC_WHEELED_CHASSIS = 'hydraulicWheeledChassis'
    TURBOSHAFT_ENGINE = 'turboshaftEngine'
    ROCKET_ACCELERATION = 'rocketAcceleration'
    DUAL_ACCURACY = 'dualAccuracy'
    AUTO_SHOOT_GUN = 'autoShootGun'
    TWIN_GUN = 'twinGun'
    IMPROVED_RAMMING = 'improvedRamming'
    CONCENTRATION_MODE = 'concentrationMode'
    BATTLE_FURY = 'battleFury'
    EXTRA_SHOT_CLIP = 'extraShotClip'
    POWER_MODE = 'powerMode'
    ACCURACY_STACKS = 'accuracyStacks'
    SUPPORT_WEAPON = 'supportWeapon'
    PILLBOX_SIEGE_MODE = 'pillboxSiegeMode'
    CHARGEABLE_BURST = 'chargeableBurst'
    RECHARGEABLE_NITRO = 'rechargeableNitro'
    CHARGE_SHOT = 'chargeShot'
    OVERHEAT_STACKS = 'overheatStacks'
    TARGET_DESIGNATOR = 'targetDesignator'
    STANCE_DANCE = 'stanceDance'
    STATIONARY_RELOAD = 'stationaryReload'
    TEMPERATURE_GUN = 'temperatureGun'
    OVERHEAT_GUN = 'overheatGun'
    HEATING_ZONES_GUN = 'heatingZonesGun'
    STAGED_JET_BOOSTERS = 'stagedJetBoosters'


VEHICLE_MECHANIC_DYN_COMPONENT_NAMES = {VehicleMechanic.IMPROVED_RAMMING: 'improvedRammingController',
 VehicleMechanic.ROCKET_ACCELERATION: 'rocketAccelerationController',
 VehicleMechanic.DUAL_ACCURACY: 'dualAccuracy',
 VehicleMechanic.AUTO_SHOOT_GUN: 'autoShootGunController',
 VehicleMechanic.TWIN_GUN: 'twinGunController',
 VehicleMechanic.CONCENTRATION_MODE: 'concentrationModeComponent',
 VehicleMechanic.BATTLE_FURY: 'battleFuryController',
 VehicleMechanic.EXTRA_SHOT_CLIP: 'extraShotClipComponent',
 VehicleMechanic.POWER_MODE: 'powerModeController',
 VehicleMechanic.ACCURACY_STACKS: 'accuracyStacksController',
 VehicleMechanic.SUPPORT_WEAPON: 'supportWeaponComponent',
 VehicleMechanic.PILLBOX_SIEGE_MODE: 'pillboxSiegeComponent',
 VehicleMechanic.CHARGEABLE_BURST: 'chargeableBurstComponent',
 VehicleMechanic.RECHARGEABLE_NITRO: 'rechargeableNitroController',
 VehicleMechanic.CHARGE_SHOT: 'chargeShotComponent',
 VehicleMechanic.OVERHEAT_STACKS: 'overheatStacksController',
 VehicleMechanic.TARGET_DESIGNATOR: 'targetDesignatorController',
 VehicleMechanic.STANCE_DANCE: 'stanceDanceController',
 VehicleMechanic.STATIONARY_RELOAD: 'stationaryReloadController',
 VehicleMechanic.TEMPERATURE_GUN: 'temperatureGunController',
 VehicleMechanic.OVERHEAT_GUN: 'overheatGunComponent',
 VehicleMechanic.HEATING_ZONES_GUN: 'heatingZonesGunComponent',
 VehicleMechanic.STAGED_JET_BOOSTERS: 'stagedJetBoostersController'}
TRACKABLE_VEHICLE_MECHANICS = set(VEHICLE_MECHANIC_DYN_COMPONENT_NAMES)
VEHICLE_MECHANIC_TAGS = {VehicleMechanic.ROCKET_ACCELERATION: 'rocketAcceleration',
 VehicleMechanic.DUAL_ACCURACY: 'dualAccuracy',
 VehicleMechanic.AUTO_SHOOT_GUN: 'autoShoot',
 VehicleMechanic.TWIN_GUN: 'twinGun'}
VEHICLE_MECHANIC_TO_PARAMS = {VehicleMechanic.IMPROVED_RAMMING: shared_components.ImprovedRammingParams.MECHANICS_NAME,
 VehicleMechanic.CONCENTRATION_MODE: shared_components.ConcentrationModeParams.MECHANICS_NAME,
 VehicleMechanic.BATTLE_FURY: shared_components.BattleFuryParams.MECHANICS_NAME,
 VehicleMechanic.EXTRA_SHOT_CLIP: shared_components.ExtraShotClipParams.MECHANICS_NAME,
 VehicleMechanic.POWER_MODE: shared_components.PowerModeParams.MECHANICS_NAME,
 VehicleMechanic.ACCURACY_STACKS: shared_components.AccuracyStacksParams.MECHANICS_NAME,
 VehicleMechanic.SUPPORT_WEAPON: shared_components.SupportWeaponParams.MECHANICS_NAME,
 VehicleMechanic.PILLBOX_SIEGE_MODE: shared_components.PillboxSiegeModeParams.MECHANICS_NAME,
 VehicleMechanic.CHARGEABLE_BURST: shared_components.ChargeableBurstParams.MECHANICS_NAME,
 VehicleMechanic.RECHARGEABLE_NITRO: shared_components.RechargeableNitroParams.MECHANICS_NAME,
 VehicleMechanic.CHARGE_SHOT: shared_components.ChargeShotParams.MECHANICS_NAME,
 VehicleMechanic.OVERHEAT_STACKS: shared_components.OverheatStacksParams.MECHANICS_NAME,
 VehicleMechanic.TARGET_DESIGNATOR: shared_components.TargetDesignatorParams.MECHANICS_NAME,
 VehicleMechanic.STANCE_DANCE: shared_components.StanceDanceParams.MECHANICS_NAME,
 VehicleMechanic.STATIONARY_RELOAD: shared_components.StationaryReloadParams.MECHANICS_NAME,
 VehicleMechanic.TEMPERATURE_GUN: shared_components.TemperatureGunParams.MECHANICS_NAME,
 VehicleMechanic.OVERHEAT_GUN: shared_components.OverheatGunParams.MECHANICS_NAME,
 VehicleMechanic.HEATING_ZONES_GUN: shared_components.HeatingZonesGunParams.MECHANICS_NAME,
 VehicleMechanic.STAGED_JET_BOOSTERS: shared_components.StagedJetBoostersParams.MECHANICS_NAME}
VEHICLE_PARAMS_TO_MECHANIC = {v:k for k, v in viewitems(VEHICLE_MECHANIC_TO_PARAMS)}
TRACKABLE_VEHICLE_DESCR_MECHANICS = set()
TRACKABLE_VEHICLE_DESCR_MECHANICS |= set(VEHICLE_MECHANIC_TAGS)
TRACKABLE_VEHICLE_DESCR_MECHANICS |= set(VEHICLE_MECHANIC_TO_PARAMS)

class VehicleMechanicCommand(Enum):
    PREPARING = 'preparing'
    CANCELLED = 'cancelled'
    ACTIVATE = 'activate'
    ALTERNATIVE_ACTIVATE = 'altActivate'
    DEACTIVATE = 'deactivate'
    SWITCH = 'switch'
    MANUAL_RELOAD = 'manual_reload'


VEHICLE_MECHANIC_USED_COMMANDS = {VehicleMechanic.CONCENTRATION_MODE: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanic.SUPPORT_WEAPON: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanic.PILLBOX_SIEGE_MODE: (VehicleMechanicCommand.PREPARING,
                                      VehicleMechanicCommand.CANCELLED,
                                      VehicleMechanicCommand.ACTIVATE,
                                      VehicleMechanicCommand.ALTERNATIVE_ACTIVATE),
 VehicleMechanic.RECHARGEABLE_NITRO: (VehicleMechanicCommand.ACTIVATE, VehicleMechanicCommand.DEACTIVATE),
 VehicleMechanic.CHARGE_SHOT: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanic.TARGET_DESIGNATOR: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanic.STANCE_DANCE: (VehicleMechanicCommand.ACTIVATE, VehicleMechanicCommand.SWITCH),
 VehicleMechanic.STATIONARY_RELOAD: (VehicleMechanicCommand.MANUAL_RELOAD,),
 VehicleMechanic.STAGED_JET_BOOSTERS: (VehicleMechanicCommand.ACTIVATE,)}
