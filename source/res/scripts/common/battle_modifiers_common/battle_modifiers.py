# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_modifiers_common/battle_modifiers.py
from ResMgr import DataSection
from constants import AOI, PIERCING_POWER_INTERPOLATION_DIST_FIRST, PIERCING_POWER_INTERPOLATION_DIST_LAST, DAMAGE_INTERPOLATION_DIST_FIRST, DAMAGE_INTERPOLATION_DIST_LAST
from typing import TYPE_CHECKING, Optional, Any, Tuple, Union, Dict, List
if TYPE_CHECKING:
    from items.vehicles import VehicleType
    from items.vehicle_items import Shell, Gun
    from battle_modifiers_ext.battle_modifiers import BattleModifier
EXT_DATA_MODIFIERS_KEY = 'battleModifiers'

class BattleParams(object):
    VEHICLE_HEALTH = 'vehicleHealth'
    GRAVITY_FACTOR = 'gravityFactor'
    DISP_FACTOR_CHASSIS_MOVEMENT = 'dispFactorChassisMovement'
    DISP_FACTOR_CHASSIS_ROTATION = 'dispFactorChassisRotation'
    TURRET_ROTATION_SPEED = 'turretRotationSpeed'
    GUN_ROTATION_SPEED = 'gunRotationSpeed'
    RELOAD_TIME = 'reloadTime'
    CLIP_INTERVAL = 'clipInterval'
    BURST_INTERVAL = 'burstInterval'
    AUTORELOAD_TIME = 'autoreloadTime'
    AIMING_TIME = 'aimingTime'
    SHOT_DISPERSION_RADIUS = 'shotDispersionRadius'
    DISP_FACTOR_TURRET_ROTATION = 'dispFactorTurretRotation'
    DISP_FACTOR_AFTER_SHOT = 'dispFactorAfterShot'
    DISP_FACTOR_WHILE_GUN_DAMAGED = 'dispFactorWhileGunDamaged'
    SHELL_GRAVITY = 'shellGravity'
    SHELL_SPEED = 'shellSpeed'
    PIERCING_POWER_FIRST = 'piercingPowerFirst'
    PIERCING_POWER_LAST = 'piercingPowerLast'
    DAMAGE_RANDOMIZATION = 'damageRandomization'
    PIERCING_POWER_RANDOMIZATION = 'piercingPowerRandomization'
    NORMALIZATION_ANGLE = 'normalizationAngle'
    RICOCHET_ANGLE = 'ricochetAngle'
    ENGINE_POWER = 'enginePower'
    ENGINE_FIRE_FACTOR = 'engineFireFactor'
    FW_MAX_SPEED = 'fwMaxSpeed'
    BK_MAX_SPEED = 'bkMaxSpeed'
    ROTATION_SPEED_ON_STILL = 'rotationSpeedOnStill'
    ROTATION_SPEED_ON_MOVE = 'rotationSpeedOnMove'
    ARMOR_DAMAGE_FIRST = 'armorDamageFirst'
    ARMOR_DAMAGE_LAST = 'armorDamageLast'
    DEVICE_DAMAGE_FIRST = 'deviceDamageFirst'
    DEVICE_DAMAGE_LAST = 'deviceDamageLast'
    INVISIBILITY_ON_STILL = 'invisibilityOnStill'
    INVISIBILITY_ON_MOVE = 'invisibilityOnMove'
    VISION_RADIUS = 'visionRadius'
    RADIO_DISTANCE = 'radioDistance'
    BATTLE_LENGTH = 'battleLength'
    VEHICLE_RAMMING_DAMAGE = 'vehicleRammingDamage'
    VEHICLE_PRESSURE_DAMAGE = 'vehiclePressureDamage'
    TURRET_RAMMING_DAMAGE = 'turretRammingDamage'
    TURRET_PRESSURE_DAMAGE = 'turretPressureDamage'
    ENV_HULL_DAMAGE = 'envHullDamage'
    ENV_CHASSIS_DAMAGE = 'envChassisDamage'
    ENV_TANKMAN_DAMAGE_CHANCE = 'envTankmanDamageChance'
    ENV_MODULE_DAMAGE_CHANCE = 'envModuleDamageChance'
    REPAIR_SPEED = 'repairSpeed'
    VISION_MIN_RADIUS = 'visionMinRadius'
    VISION_MAX_RADIUS = 'visionMaxRadius'
    VISION_TIME = 'visionTime'
    EQUIPMENT_COOLDOWN = 'equipmentCooldown'
    FWD_FRICTION = 'fwdFriction'
    SIDE_FRICTION = 'sideFriction'
    DIRT_RELEASE_RATE = 'dirtReleaseRate'
    MAX_DIRT = 'maxDirt'
    SHOT_EFFECTS = 'shotEffects'
    GUN_EFFECTS = 'gunEffects'
    CHASSIS_DECALS = 'chassisDecals'
    ENGINE_SOUNDS = 'engineSounds'
    EXHAUST_EFFECT = 'exhaustEffect'
    ARMOR_SPALLS_ARMOR_DAMAGE_FIRST = 'armorSpallsArmorDamageFirst'
    ARMOR_SPALLS_ARMOR_DAMAGE_LAST = 'armorSpallsArmorDamageLast'
    ARMOR_SPALLS_DEVICE_DAMAGE_FIRST = 'armorSpallsDeviceDamageFirst'
    ARMOR_SPALLS_DEVICE_DAMAGE_LAST = 'armorSpallsDeviceDamageLast'
    ARMOR_SPALLS_IMPACT_RADIUS = 'armorSpallsImpactRadius'
    ARMOR_SPALLS_CONE_ANGLE = 'armorSpallsConeAngle'
    ARMOR_SPALLS_DAMAGE_ABSORPTION = 'armorSpallsDamageAbsorption'
    MODE_CREDITS_FACTOR = 'modeCreditsFactor'
    INVISIBILITY_FACTOR_AT_SHOT = 'invisibilityFactorAtShot'
    VEHICLE_AOI_RADIUS = 'vehicleAoIRadius'
    SOUND_NOTIFICATIONS = 'soundNotifications'
    DIVING_DESTRUCTION_DELAY = 'divingDestructionDelay'
    STUN_FACTOR_ENGINE_POWER = 'stunFactorEnginePower'
    STUN_FACTOR_VEHICLE_ROTATION_SPEED = 'stunFactorVehicleRotationSpeed'
    STUN_FACTOR_TURRET_TRAVERSE = 'stunFactorTurretTraverse'
    STUN_FACTOR_MAX_SPEED = 'stunFactorMaxSpeed'
    PIERCING_POWER_INTERPOLATION_DIST_FIRST = 'piercingPowerInterpolationDistFirst'
    PIERCING_POWER_INTERPOLATION_DIST_LAST = 'piercingPowerInterpolationDistLast'
    DAMAGE_INTERPOLATION_DIST_FIRST = 'damageInterpolationDistFirst'
    DAMAGE_INTERPOLATION_DIST_LAST = 'damageInterpolationDistLast'
    BONUS_CAPS_OVERRIDES = 'bonusCapsOverrides'
    CRYSTAL_REWARDS = 'crystalRewards'
    GOLD_RESERVE_GAINS = 'goldReserveGains'
    DAMAGE_RANDOMIZATION_TYPE = 'damageRandomizationType'
    PIERCING_POWER_RANDOMIZATION_TYPE = 'piercingPowerRandomizationType'
    FORCED_RELOAD_TIME = 'forcedReloadTime'
    AUTO_SHOOT_DISPERSION_PER_SEC = 'autoShootDispersionPerSec'
    AUTO_SHOOT_MAX_SHOT_DISPERSION_FACTOR = 'autoShootMaxShotDispersionFactor'
    GUN_MAIN_PREFAB = 'gunMainPrefab'
    FAKE_MODIFIER = 'fakeModifier'
    VSE_MODIFIER = 'vseModifier'
    DYNAMIC = {FAKE_MODIFIER, VSE_MODIFIER}
    ALL = None


BattleParams.ALL = set((v for k, v in BattleParams.__dict__.iteritems() if not k.startswith('_') and k not in ('DYNAMIC', 'ALL')))

class ConstantsSet(object):
    __slots__ = ('VEHICLE_CIRCULAR_AOI_RADIUS', 'VEHICLE_CIRCULAR_AOI_RADIUS_HYSTERESIS_MARGIN', 'PIERCING_POWER_INTERPOLATION_DIST_FIRST', 'PIERCING_POWER_INTERPOLATION_DIST_LAST', 'DAMAGE_INTERPOLATION_DIST_FIRST', 'DAMAGE_INTERPOLATION_DIST_LAST')

    def __init__(self):
        self.VEHICLE_CIRCULAR_AOI_RADIUS = AOI.VEHICLE_CIRCULAR_AOI_RADIUS
        self.VEHICLE_CIRCULAR_AOI_RADIUS_HYSTERESIS_MARGIN = AOI.VEHICLE_CIRCULAR_AOI_RADIUS_HYSTERESIS_MARGIN
        self.PIERCING_POWER_INTERPOLATION_DIST_FIRST = PIERCING_POWER_INTERPOLATION_DIST_FIRST
        self.PIERCING_POWER_INTERPOLATION_DIST_LAST = PIERCING_POWER_INTERPOLATION_DIST_LAST
        self.DAMAGE_INTERPOLATION_DIST_FIRST = DAMAGE_INTERPOLATION_DIST_FIRST
        self.DAMAGE_INTERPOLATION_DIST_LAST = DAMAGE_INTERPOLATION_DIST_LAST


CONSTANTS_ORIGINAL = ConstantsSet()

class ModifierScope(object):
    BASE = 1
    CELL = 2
    CLIENT = 4
    POST_BATTLE = 8
    HANGAR = 16
    BATTLE = BASE | CELL | CLIENT | POST_BATTLE
    FULL = BATTLE | HANGAR
    ID_TO_NAME = {BASE: 'base',
     CELL: 'cell',
     CLIENT: 'client',
     POST_BATTLE: 'postBattle',
     HANGAR: 'hangar'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.items()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class BattleModifiers(object):

    def __init__(self, source=None):
        pass

    def __call__(self, paramId, value, ctx=None):
        return value

    def __iter__(self):
        return iter([])

    def __getitem__(self, paramId):
        return None

    def __len__(self):
        pass

    def __contains__(self, paramId):
        return False

    def __nonzero__(self):
        return False

    def __hash__(self):
        pass

    def __eq__(self, other):
        return False

    def __repr__(self):
        pass

    @staticmethod
    def retrieveDescr(descr, scope=ModifierScope.FULL):
        pass

    @staticmethod
    def getConstantsOriginal():
        return CONSTANTS_ORIGINAL

    @staticmethod
    def clearVehicleModifications():
        pass

    @staticmethod
    def clearConstantsModifications():
        pass

    def get(self, paramId):
        return None

    def descr(self, scope=ModifierScope.FULL):
        pass

    def domain(self):
        pass

    def haveDomain(self, domain):
        return False

    def scope(self):
        pass

    def haveScope(self, scope):
        return False

    def id(self):
        pass

    def getVehicleModification(self, vehType):
        return vehType

    def getConstantsModification(self):
        return CONSTANTS_ORIGINAL

    def getVsePlansByAspect(self, aspect):
        return []


class ModifiersContext(object):
    __slots__ = ('__modifiers', '__modificationCtx')

    def __init__(self, modifiers, **modificationCtx):
        self.__modifiers = modifiers
        self.__modificationCtx = modificationCtx or {}

    def __getattr__(self, item):
        return getattr(self.__modifiers, item)

    def __deepcopy__(self, memo):
        return ModifiersContext(self.__modifiers, **self.__modificationCtx)

    def __copy__(self):
        return ModifiersContext(self.__modifiers, **self.__modificationCtx)

    def __call__(self, paramId, value):
        return self.__modifiers(paramId, value, self)

    def __iter__(self):
        return iter(self.__modifiers)

    def __getitem__(self, paramId):
        return self.__modifiers[paramId]

    def __len__(self):
        return len(self.__modifiers)

    def __contains__(self, paramId):
        return paramId in self.__modifiers

    def __nonzero__(self):
        return bool(self.__modifiers)

    def __hash__(self):
        return hash(self.__modifiers)

    def __eq__(self, other):
        return self.modifiers == other.modifiers

    def __repr__(self):
        return 'ModifiersContext(modifiers {}, modificationCtx {})'.format(self.__modifiers, self.__modificationCtx)

    @property
    def modifiers(self):
        return self.__modifiers

    @property
    def modificationCtx(self):
        return self.__modificationCtx


BATTLE_MODIFIERS_TYPE = Union[BattleModifiers, ModifiersContext]

def getGlobalModifiers():
    return BattleModifiers()
