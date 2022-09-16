# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier_constants.py
from battle_modifiers_common.battle_modifiers import BattleParams, EXT_DATA_MODIFIERS_KEY
BATTLE_PARAMS_XML_PATH = 'scripts/item_defs/battle_params.xml'
BATTLE_MODIFIERS_DIR = 'scripts/server_xml/battle_modifiers/'
BATTLE_MODIFIERS_XML = 'battle_modifiers.xml'
USE_MODIFICATION_CACHE = True
MAX_MODIFICATION_LAYER_COUNT = 5

class DataType(object):
    INT = 0
    FLOAT = 1
    ID_TO_NAME = {INT: 'int',
     FLOAT: 'float'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.iteritems()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class UseType(object):
    VAL = 0
    MUL = 1
    ADD = 2
    DIMENSIONAL_TYPES = {VAL, ADD}
    ID_TO_NAME = {VAL: 'val',
     MUL: 'mul',
     ADD: 'add'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.iteritems()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class PhysicalType(object):
    UNDEFINED = 0
    METERS_PER_SECOND = 1
    RADIANS = 2
    HIT_POINTS = 3
    MILLIMETERS = 4
    SECONDS = 5
    METERS = 6
    RADIANS_PER_SECOND = 7
    METER_PER_SECOND_SQUARED = 8
    PROBABILITY = 9
    DEVIATION = 10
    ID_TO_NAME = {UNDEFINED: 'undefined',
     METERS_PER_SECOND: 'metersPerSecond',
     RADIANS: 'radians',
     HIT_POINTS: 'hitPoints',
     MILLIMETERS: 'millimeters',
     SECONDS: 'seconds',
     METERS: 'meters',
     RADIANS_PER_SECOND: 'radians_per_second',
     METER_PER_SECOND_SQUARED: 'meter_per_second_squared',
     PROBABILITY: 'probability',
     DEVIATION: 'deviation'}
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
    SHELL_COMPONENTS = SHELL | SHELL_TYPE
    SHOT_COMPONENTS = SHOT | SHELL_COMPONENTS
    GUN_COMPONENTS = GUN | SHOT_COMPONENTS
    TURRET_COMPONENTS = TURRET | GUN_COMPONENTS
    VEH_TYPE_COMPONENTS = VEH_TYPE | CHASSIS | TURRET_COMPONENTS | RADIO | PHYSICS
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
     PHYSICS: 'physics'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.items()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


class ClientDomain(object):
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


ClientDomain.ALL = set([ v for k, v in ClientDomain.__dict__.iteritems() if not k.startswith('_') and k != 'ALL' ])

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
    ID_TO_NAME = {MIN: 'min',
     MAX: 'max',
     USE_TYPES: 'useTypes'}
    NAME_TO_ID = dict(((v, k) for k, v in ID_TO_NAME.items()))
    ALL = set(NAME_TO_ID.itervalues())
    NAMES = set(ID_TO_NAME.itervalues())


__all__ = ('BATTLE_PARAMS_XML_PATH', 'BATTLE_MODIFIERS_DIR', 'BATTLE_MODIFIERS_XML', 'USE_MODIFICATION_CACHE', 'MAX_MODIFICATION_LAYER_COUNT', 'EXT_DATA_MODIFIERS_KEY', 'BattleParams', 'DataType', 'UseType', 'PhysicalType', 'ModifierDomain', 'ClientDomain', 'GameplayImpact', 'ModifierRestriction')
