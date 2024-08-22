# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/constants_ext.py
import typing
from collections import OrderedDict
from constants import IS_DEVELOPMENT, SHELL_TYPES, BATTLE_LOG_SHELL_TYPES
if typing.TYPE_CHECKING:
    from items.vehicle_items import Shell
BATTLE_PARAMS_XML_PATH = 'scripts/item_defs/battle_params.xml'
REMAPPING_XML_PATH = 'scripts/item_defs/remapping.xml'
BATTLE_MODIFIERS_DIR = 'scripts/server_xml/battle_modifiers/'
BATTLE_MODIFIERS_XML = 'battle_modifiers.xml'
USE_VEHICLE_CACHE = True
USE_CONSTANTS_CACHE = True
MAX_VEHICLE_CACHE_LAYER_COUNT = 5
MAX_CONSTANTS_CACHE_LAYER_COUNT = 5
FAKE_PARAM_NAME = 'fakeParam'
DEBUG_MODIFIERS = IS_DEVELOPMENT
ERROR_TEMPLATE = '[BattleModifiers] {} for param {}'

class DataType(object):
    INT = 0
    FLOAT = 1
    STRING = 2
    DICT = 3
    HASHABLE_TYPES = (INT, FLOAT, STRING)
    ID_TO_NAME = {INT: 'int',
     FLOAT: 'float',
     STRING: 'string',
     DICT: 'dict'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.iteritems()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class UseType(object):
    UNDEFINED = 0
    VAL = 1
    MUL = 2
    ADD = 3
    DIMENSIONAL_TYPES = {VAL, ADD}
    ID_TO_NAME = {VAL: 'val',
     MUL: 'mul',
     ADD: 'add'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.iteritems()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())
    ALL_WITH_UNDEFINED = ALL | {UNDEFINED}
    NON_DIMENSIONAL_TYPES = ALL_WITH_UNDEFINED - DIMENSIONAL_TYPES


class PhysicalType(object):
    UNDEFINED = 0
    SECONDS = 1
    MINUTES = 2
    MILLIMETERS = 3
    METERS = 4
    METERS_PER_SECOND = 5
    KILOMETERS_PER_HOUR = 6
    METER_PER_SECOND_SQUARED = 7
    DEGREES = 8
    RADIANS = 9
    DEGREES_PER_SECOND = 10
    RADIANS_PER_SECOND = 11
    HIT_POINTS = 12
    HORSEPOWER = 13
    PROBABILITY = 14
    DEVIATION = 15
    LOGIC = 16
    ID_TO_NAME = {UNDEFINED: 'undefined',
     SECONDS: 'seconds',
     MINUTES: 'minutes',
     MILLIMETERS: 'millimeters',
     METERS: 'meters',
     METERS_PER_SECOND: 'metersPerSecond',
     KILOMETERS_PER_HOUR: 'km_per_hour',
     METER_PER_SECOND_SQUARED: 'meter_per_second_squared',
     DEGREES: 'degrees',
     RADIANS: 'radians',
     DEGREES_PER_SECOND: 'degrees_per_second',
     RADIANS_PER_SECOND: 'radians_per_second',
     HIT_POINTS: 'hitPoints',
     HORSEPOWER: 'horsepower',
     PROBABILITY: 'probability',
     DEVIATION: 'deviation',
     LOGIC: 'logic'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.iteritems()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class ModifierDomain(object):
    COMMON = 1
    VEH_TYPE = 2
    CHASSIS = 4
    TURRET = 8
    GUN = 16
    SHOT = 32
    SHELL = 64
    SHELL_TYPE = 128
    RADIO = 256
    PHYSICS = 512
    ENGINE = 1024
    HULL = 2048
    VEHICLE = 4096
    CONSTANTS = 8192
    VSE = 16384
    FAKE = 32768
    SHELL_COMPONENTS = SHELL | SHELL_TYPE
    SHOT_COMPONENTS = SHOT | SHELL_COMPONENTS
    GUN_COMPONENTS = GUN | SHOT_COMPONENTS
    TURRET_COMPONENTS = TURRET | GUN_COMPONENTS
    VEH_TYPE_COMPONENTS = VEH_TYPE | CHASSIS | TURRET_COMPONENTS | RADIO | PHYSICS | ENGINE | HULL
    VEHICLE_COMPONENTS = VEHICLE | VEH_TYPE_COMPONENTS
    DEFAULT = COMMON
    ID_TO_NAME = {COMMON: 'common',
     VEH_TYPE: 'vehType',
     CHASSIS: 'chassis',
     TURRET: 'turret',
     GUN: 'gun',
     SHOT: 'shot',
     SHELL: 'shell',
     SHELL_TYPE: 'shellType',
     RADIO: 'radio',
     PHYSICS: 'physics',
     ENGINE: 'engine',
     HULL: 'hull',
     VEHICLE: 'vehicle',
     CONSTANTS: 'constants',
     VSE: 'vse',
     FAKE: 'fake'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.items()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class ClientDomain(object):
    UNDEFINED = 'undefined'
    ACCURACY = 'accuracy'
    ARMOR_PIERCING = 'armorPiercing'
    BATTLE_PARAMS = 'battleParams'
    CONCEALMENT = 'concealment'
    DAMAGE_DEALING = 'damageDealing'
    MOBILITY = 'mobility'
    RANDOMIZATION = 'randomization'
    SUSTAINING = 'sustaining'
    VISIBILITY = 'visibility'
    VITALITY = 'vitality'
    ALL = None


ClientDomain.ALL = set([ v for k, v in ClientDomain.__dict__.iteritems() if not k.startswith('_') and k not in ('UNDEFINED', 'ALL') ])

class GameplayImpact(object):
    UNDEFINED = 0
    POSITIVE = 1
    NEGATIVE = 2
    HIDDEN = 3
    ID_TO_NAME = {UNDEFINED: 'undefined',
     POSITIVE: 'positive',
     NEGATIVE: 'negative',
     HIDDEN: 'hidden'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.items()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class ModifierRestriction(object):
    MIN = 0
    MAX = 1
    USE_TYPES = 2
    LIMITS = (MIN, MAX)
    ID_TO_NAME = {MIN: 'min',
     MAX: 'max',
     USE_TYPES: 'useTypes'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.items()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class NodeType(object):
    ROOT = 'root'
    SHELL = 'shell'
    VEHICLE = 'vehicle'
    SUPPORTED_DOMAINS = {ROOT: 0,
     SHELL: ModifierDomain.SHOT_COMPONENTS,
     VEHICLE: ModifierDomain.VEHICLE_COMPONENTS}


class ShellCaliber(object):
    AUTO = 'auto'
    SMALL = 'small'
    MEDIUM = 'medium'
    MAIN = 'main'
    LARGE = 'large'
    HUGE = 'huge'
    NAME_TO_CALIBER = OrderedDict(((HUGE, 155),
     (LARGE, 108),
     (MAIN, 85),
     (MEDIUM, 50),
     (SMALL, 20),
     (AUTO, 7)))
    CALIBERS_AND_NAMES = None

    @classmethod
    def get(cls, targetCaliber):
        for name, caliber in cls.NAME_TO_CALIBER.iteritems():
            if targetCaliber >= caliber:
                return name

        return cls.AUTO


class ShellKind(object):
    IMPROVED_POSTFIX = SHELL_TYPES.IMPROVED_POSTFIX
    ALL_KEY = 'ALL'
    ALL_REGULAR = {SHELL_TYPES.HOLLOW_CHARGE,
     SHELL_TYPES.ARMOR_PIERCING,
     SHELL_TYPES.ARMOR_PIERCING_HE,
     SHELL_TYPES.ARMOR_PIERCING_CR,
     SHELL_TYPES.SMOKE,
     SHELL_TYPES.HIGH_EXPLOSIVE_MODERN,
     SHELL_TYPES.HIGH_EXPLOSIVE_LEGACY_STUN,
     SHELL_TYPES.HIGH_EXPLOSIVE_LEGACY_NO_STUN}
    ALL_IMPROVED = set([ key + SHELL_TYPES.IMPROVED_POSTFIX for key in ALL_REGULAR ])

    @classmethod
    def get(cls, shellDescr, withGold=True):
        return BATTLE_LOG_SHELL_TYPES.getShellType(shellDescr, withGold)


class ModifiersWithRemapping(object):
    GUN_EFFECTS = 'gunEffects'
    GUN_MAIN_PREFAB = 'gunMainPrefab'
    SHOT_EFFECTS = 'shotEffects'
    SOUND_NOTIFICATIONS = 'soundNotifications'
    ALL = {GUN_EFFECTS,
     GUN_MAIN_PREFAB,
     SHOT_EFFECTS,
     SOUND_NOTIFICATIONS}


class RemappingConditionNames(object):
    REMAPPING_NAME = 'remappingName'
    NATION = 'nation'
    OUTFIT = 'outfit'
    CALIBER = 'caliber'
    GUN_NAME = 'gunName'
    SHELL_KIND = 'shellKind'
    SHELL_SHOTS_COUNT = 'shellShotsCount'
    ALL = {REMAPPING_NAME,
     NATION,
     OUTFIT,
     CALIBER,
     GUN_NAME,
     SHELL_KIND,
     SHELL_SHOTS_COUNT}


class RemappingNames(object):
    TEST = 'test'
    ALL = set(() + ((TEST,) if IS_DEVELOPMENT else ()))
