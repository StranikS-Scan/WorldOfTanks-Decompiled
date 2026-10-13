# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/vehicle_mechanics_types.py
from __future__ import absolute_import
import typing
from future.utils import viewitems
from enum import Enum
from items import _xml
if typing.TYPE_CHECKING:
    from items.components.shared_components import MechanicsParams

class VehicleMechanic(Enum):
    ACCURACY_STACKS = 'accuracyStacks'
    AUTO_LOADER_GUN = 'autoLoaderGun'
    AUTO_LOADER_GUN_BOOST = 'autoLoaderGunBoost'
    AUTORELOADER_SURGE = 'autoreloaderSurge'
    AUTO_SHOOT_GUN = 'autoShootGun'
    AUXILIARY_ROCKET_LAUNCHER = 'auxiliaryRocketLauncher'
    BATTLE_FURY = 'battleFury'
    BUSTLE_FEED = 'bustleFeed'
    CHARGEABLE_BURST = 'chargeableBurst'
    CHARGE_SHOT = 'chargeShot'
    CONCENTRATION_MODE = 'concentrationMode'
    CREST_MOVING = 'crestMoving'
    DAMAGE_MUTABLE = 'damageMutable'
    DUAL_ACCURACY = 'dualAccuracy'
    DUAL_GUN = 'dualGun'
    EXTRA_SHOT_CLIP = 'extraShotClip'
    HEATING_ZONES_GUN = 'heatingZonesGun'
    HYDRAULIC_CHASSIS = 'hydraulicChassis'
    HYDRAULIC_WHEELED_CHASSIS = 'hydraulicWheeledChassis'
    IMPROVED_RAMMING = 'improvedRamming'
    LOW_CHARGE_SHOT = 'lowChargeShot'
    MAGAZINE_GUN = 'magazineGun'
    OVERHEAT_GUN = 'overheatGun'
    OVERHEAT_STACKS = 'overheatStacks'
    PILLBOX_SIEGE_MODE = 'pillboxSiegeMode'
    POWER_MODE = 'powerMode'
    PROPELLANT_GUN = 'propellantAfterburnerGun'
    RECHARGEABLE_NITRO = 'rechargeableNitro'
    ROCKET_ACCELERATION = 'rocketAcceleration'
    SHELL_PARAMS_SWITCHER = 'shellParamsSwitcher'
    SHELL_CALIBRATION = 'shellCalibration'
    SIEGE_MODE = 'siegeMode'
    SIGHT_POINTER = 'sightPointer'
    SPEC_BOOST_MODE = 'specBoostMode'
    STAGED_JET_BOOSTERS = 'stagedJetBoosters'
    STANCE_DANCE = 'stanceDance'
    STATIONARY_RELOAD = 'stationaryReload'
    STUN = 'stun'
    SUPPORT_WEAPON = 'supportWeapon'
    TARGET_DESIGNATOR = 'targetDesignator'
    TEMPERATURE_GUN = 'temperatureGun'
    TRACK_WITHIN_TRACK = 'trackWithinTrack'
    TURBOSHAFT_ENGINE = 'turboshaftEngine'
    TWIN_GUN = 'twinGun'
    WHEELED_DASH = 'wheeledDash'

    @classmethod
    def find(cls, value):
        return cls._value2member_map_.get(value)


VEHICLE_MECHANIC_VALUES = frozenset((m.value for m in VehicleMechanic))

class VehicleMechanicVariant(object):

    @classmethod
    def fromString(cls, value):
        return cls(value) if value else None


class SpecBoostModeMechanicVariant(VehicleMechanicVariant, Enum):
    COMBAT_THROTTLE = 'combatThrottle'


class VehicleMechanicKey(typing.NamedTuple('VehicleMechanicKey', (('mechanic', VehicleMechanic), ('mechanicVariant', VehicleMechanicVariant)))):
    __slots__ = ()

    def __new__(cls, mechanic, mechanicVariant=None):
        return super(VehicleMechanicKey, cls).__new__(cls, mechanic, mechanicVariant)

    @property
    def uniqueName(self):
        return self.mechanicVariant.value if self.mechanicVariant is not None else self.mechanic.value


class VehicleMechanicKeys(object):
    ACCURACY_STACKS = VehicleMechanicKey(VehicleMechanic.ACCURACY_STACKS)
    AUTO_LOADER_GUN = VehicleMechanicKey(VehicleMechanic.AUTO_LOADER_GUN)
    AUTO_LOADER_GUN_BOOST = VehicleMechanicKey(VehicleMechanic.AUTO_LOADER_GUN_BOOST)
    AUTORELOADER_SURGE = VehicleMechanicKey(VehicleMechanic.AUTORELOADER_SURGE)
    AUTO_SHOOT_GUN = VehicleMechanicKey(VehicleMechanic.AUTO_SHOOT_GUN)
    AUXILIARY_ROCKET_LAUNCHER = VehicleMechanicKey(VehicleMechanic.AUXILIARY_ROCKET_LAUNCHER)
    BATTLE_FURY = VehicleMechanicKey(VehicleMechanic.BATTLE_FURY)
    BUSTLE_FEED = VehicleMechanicKey(VehicleMechanic.BUSTLE_FEED)
    CHARGEABLE_BURST = VehicleMechanicKey(VehicleMechanic.CHARGEABLE_BURST)
    CHARGE_SHOT = VehicleMechanicKey(VehicleMechanic.CHARGE_SHOT)
    CONCENTRATION_MODE = VehicleMechanicKey(VehicleMechanic.CONCENTRATION_MODE)
    CREST_MOVING = VehicleMechanicKey(VehicleMechanic.CREST_MOVING)
    DAMAGE_MUTABLE = VehicleMechanicKey(VehicleMechanic.DAMAGE_MUTABLE)
    DUAL_ACCURACY = VehicleMechanicKey(VehicleMechanic.DUAL_ACCURACY)
    DUAL_GUN = VehicleMechanicKey(VehicleMechanic.DUAL_GUN)
    EXTRA_SHOT_CLIP = VehicleMechanicKey(VehicleMechanic.EXTRA_SHOT_CLIP)
    HEATING_ZONES_GUN = VehicleMechanicKey(VehicleMechanic.HEATING_ZONES_GUN)
    HYDRAULIC_CHASSIS = VehicleMechanicKey(VehicleMechanic.HYDRAULIC_CHASSIS)
    HYDRAULIC_WHEELED_CHASSIS = VehicleMechanicKey(VehicleMechanic.HYDRAULIC_WHEELED_CHASSIS)
    IMPROVED_RAMMING = VehicleMechanicKey(VehicleMechanic.IMPROVED_RAMMING)
    LOW_CHARGE_SHOT = VehicleMechanicKey(VehicleMechanic.LOW_CHARGE_SHOT)
    MAGAZINE_GUN = VehicleMechanicKey(VehicleMechanic.MAGAZINE_GUN)
    OVERHEAT_GUN = VehicleMechanicKey(VehicleMechanic.OVERHEAT_GUN)
    OVERHEAT_STACKS = VehicleMechanicKey(VehicleMechanic.OVERHEAT_STACKS)
    PILLBOX_SIEGE_MODE = VehicleMechanicKey(VehicleMechanic.PILLBOX_SIEGE_MODE)
    POWER_MODE = VehicleMechanicKey(VehicleMechanic.POWER_MODE)
    PROPELLANT_GUN = VehicleMechanicKey(VehicleMechanic.PROPELLANT_GUN)
    RECHARGEABLE_NITRO = VehicleMechanicKey(VehicleMechanic.RECHARGEABLE_NITRO)
    ROCKET_ACCELERATION = VehicleMechanicKey(VehicleMechanic.ROCKET_ACCELERATION)
    SHELL_PARAMS_SWITCHER = VehicleMechanicKey(VehicleMechanic.SHELL_PARAMS_SWITCHER)
    SHELL_CALIBRATION = VehicleMechanicKey(VehicleMechanic.SHELL_CALIBRATION)
    SIGHT_POINTER = VehicleMechanicKey(VehicleMechanic.SIGHT_POINTER)
    SIEGE_MODE = VehicleMechanicKey(VehicleMechanic.SIEGE_MODE)
    STAGED_JET_BOOSTERS = VehicleMechanicKey(VehicleMechanic.STAGED_JET_BOOSTERS)
    STANCE_DANCE = VehicleMechanicKey(VehicleMechanic.STANCE_DANCE)
    STATIONARY_RELOAD = VehicleMechanicKey(VehicleMechanic.STATIONARY_RELOAD)
    STUN = VehicleMechanicKey(VehicleMechanic.STUN)
    SUPPORT_WEAPON = VehicleMechanicKey(VehicleMechanic.SUPPORT_WEAPON)
    TARGET_DESIGNATOR = VehicleMechanicKey(VehicleMechanic.TARGET_DESIGNATOR)
    TEMPERATURE_GUN = VehicleMechanicKey(VehicleMechanic.TEMPERATURE_GUN)
    TRACK_WITHIN_TRACK = VehicleMechanicKey(VehicleMechanic.TRACK_WITHIN_TRACK)
    TURBOSHAFT_ENGINE = VehicleMechanicKey(VehicleMechanic.TURBOSHAFT_ENGINE)
    TWIN_GUN = VehicleMechanicKey(VehicleMechanic.TWIN_GUN)
    WHEELED_DASH = VehicleMechanicKey(VehicleMechanic.WHEELED_DASH)
    COMBAT_THROTTLE = VehicleMechanicKey(VehicleMechanic.SPEC_BOOST_MODE, SpecBoostModeMechanicVariant.COMBAT_THROTTLE)


ALL_VEHICLE_MECHANIC_KEYS = tuple((v for v in vars(VehicleMechanicKeys).values() if isinstance(v, VehicleMechanicKey)))
MECHANIC_KEY_BY_NAME = {k.uniqueName:k for k in ALL_VEHICLE_MECHANIC_KEYS}
_MECHANIC_VARIANT_TYPES_BY_MECHANIC = {VehicleMechanic.SPEC_BOOST_MODE: SpecBoostModeMechanicVariant}
_MECHANIC_VARIANT_VALUES_BY_MECHANIC = {mechanic:frozenset((variant.value for variant in variantType)) for mechanic, variantType in viewitems(_MECHANIC_VARIANT_TYPES_BY_MECHANIC)}

def getVehicleMechanicKey(mechanic, mechanicParams):
    variant = getattr(mechanicParams, 'mechanicVariant', None)
    uniqueName = variant if variant is not None else mechanic.value
    return MECHANIC_KEY_BY_NAME[uniqueName]


def readMechanicVariant(xmlCtx, section, mechanic):
    allowedVariants = _MECHANIC_VARIANT_VALUES_BY_MECHANIC.get(VehicleMechanic.find(mechanic))
    if not allowedVariants:
        _xml.raiseWrongXml(xmlCtx, 'mechanicVariant', '[{}] Section <mechanicVariant> is not supported for this mechanic'.format(mechanic))
    mechanicVariant = _xml.readStringOrEmpty(xmlCtx, section, 'mechanicVariant')
    if mechanicVariant not in allowedVariants:
        _xml.raiseWrongXml(xmlCtx, 'mechanicVariant', '[{}] Section <mechanicVariant> with value {} is invalid!'.format(mechanic, mechanicVariant))
    return mechanicVariant
