# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_constants.py
from __future__ import absolute_import
from enum import Enum
from items.vehicle_mechanics_types import VehicleMechanic, VehicleMechanicKeys, ALL_VEHICLE_MECHANIC_KEYS
VEHICLE_MECHANIC_DYN_COMPONENT_NAMES = {VehicleMechanic.ACCURACY_STACKS: 'accuracyStacksController',
 VehicleMechanic.AUTO_SHOOT_GUN: 'autoShootGunController',
 VehicleMechanic.AUTORELOADER_SURGE: 'autoreloaderSurgeController',
 VehicleMechanic.AUXILIARY_ROCKET_LAUNCHER: 'auxiliaryRocketLauncherComponent',
 VehicleMechanic.BATTLE_FURY: 'battleFuryController',
 VehicleMechanic.BUSTLE_FEED: 'bustleFeedController',
 VehicleMechanic.CHARGE_SHOT: 'chargeShotComponent',
 VehicleMechanic.CHARGEABLE_BURST: 'chargeableBurstComponent',
 VehicleMechanic.CONCENTRATION_MODE: 'concentrationModeComponent',
 VehicleMechanic.CREST_MOVING: 'CrestMovingController',
 VehicleMechanic.DUAL_ACCURACY: 'dualAccuracy',
 VehicleMechanic.EXTRA_SHOT_CLIP: 'extraShotClipComponent',
 VehicleMechanic.HEATING_ZONES_GUN: 'heatingZonesGunComponent',
 VehicleMechanic.IMPROVED_RAMMING: 'improvedRammingController',
 VehicleMechanic.LOW_CHARGE_SHOT: 'lowChargeShotController',
 VehicleMechanic.OVERHEAT_GUN: 'overheatGunComponent',
 VehicleMechanic.OVERHEAT_STACKS: 'overheatStacksController',
 VehicleMechanic.PILLBOX_SIEGE_MODE: 'pillboxSiegeComponent',
 VehicleMechanic.POWER_MODE: 'powerModeController',
 VehicleMechanic.PROPELLANT_GUN: 'propellantGunController',
 VehicleMechanic.RECHARGEABLE_NITRO: 'rechargeableNitroController',
 VehicleMechanic.ROCKET_ACCELERATION: 'rocketAccelerationController',
 VehicleMechanic.SHELL_CALIBRATION: 'ShellCalibrationController',
 VehicleMechanic.SHELL_PARAMS_SWITCHER: 'shellParamsSwitcherController',
 VehicleMechanic.SIGHT_POINTER: 'sightPointerComponent',
 VehicleMechanic.SPEC_BOOST_MODE: 'specBoostModeComponent',
 VehicleMechanic.STAGED_JET_BOOSTERS: 'stagedJetBoostersController',
 VehicleMechanic.STANCE_DANCE: 'stanceDanceController',
 VehicleMechanic.STATIONARY_RELOAD: 'stationaryReloadController',
 VehicleMechanic.SUPPORT_WEAPON: 'supportWeaponComponent',
 VehicleMechanic.TARGET_DESIGNATOR: 'targetDesignatorController',
 VehicleMechanic.TEMPERATURE_GUN: 'temperatureGunController',
 VehicleMechanic.TWIN_GUN: 'twinGunController',
 VehicleMechanic.WHEELED_DASH: 'wheeledDashController'}
TRACKABLE_VEHICLE_MECHANICS = frozenset((m for m in ALL_VEHICLE_MECHANIC_KEYS if m.mechanic in VEHICLE_MECHANIC_DYN_COMPONENT_NAMES))
VEHICLE_MECHANIC_TAGS = {VehicleMechanic.ROCKET_ACCELERATION: 'rocketAcceleration',
 VehicleMechanic.DUAL_ACCURACY: 'dualAccuracy',
 VehicleMechanic.AUTO_SHOOT_GUN: 'autoShoot',
 VehicleMechanic.TWIN_GUN: 'twinGun'}

class VehicleMechanicCommand(Enum):
    PREPARING = 'preparing'
    CANCELLED = 'cancelled'
    ACTIVATE = 'activate'
    ALTERNATIVE_ACTIVATE = 'altActivate'
    DEACTIVATE = 'deactivate'
    SWITCH = 'switch'
    MANUAL_RELOAD = 'manual_reload'


VEHICLE_MECHANIC_USED_COMMANDS = {VehicleMechanicKeys.AUTORELOADER_SURGE: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.AUXILIARY_ROCKET_LAUNCHER: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.BUSTLE_FEED: (VehicleMechanicCommand.SWITCH,),
 VehicleMechanicKeys.CHARGE_SHOT: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.COMBAT_THROTTLE: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.CONCENTRATION_MODE: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.PILLBOX_SIEGE_MODE: (VehicleMechanicCommand.PREPARING,
                                          VehicleMechanicCommand.CANCELLED,
                                          VehicleMechanicCommand.ACTIVATE,
                                          VehicleMechanicCommand.ALTERNATIVE_ACTIVATE),
 VehicleMechanicKeys.PROPELLANT_GUN: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.RECHARGEABLE_NITRO: (VehicleMechanicCommand.ACTIVATE, VehicleMechanicCommand.DEACTIVATE),
 VehicleMechanicKeys.SIGHT_POINTER: (VehicleMechanicCommand.ACTIVATE, VehicleMechanicCommand.DEACTIVATE),
 VehicleMechanicKeys.SHELL_PARAMS_SWITCHER: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.STAGED_JET_BOOSTERS: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.STANCE_DANCE: (VehicleMechanicCommand.ACTIVATE, VehicleMechanicCommand.SWITCH),
 VehicleMechanicKeys.STATIONARY_RELOAD: (VehicleMechanicCommand.MANUAL_RELOAD,),
 VehicleMechanicKeys.SUPPORT_WEAPON: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.TARGET_DESIGNATOR: (VehicleMechanicCommand.ACTIVATE,),
 VehicleMechanicKeys.WHEELED_DASH: (VehicleMechanicCommand.ACTIVATE,)}
