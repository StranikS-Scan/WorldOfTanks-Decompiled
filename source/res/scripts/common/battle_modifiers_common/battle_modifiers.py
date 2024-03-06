# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_modifiers_common/battle_modifiers.py
from ResMgr import DataSection
from constants import AOI, PIERCING_POWER_INTERPOLATION_DIST_FIRST, PIERCING_POWER_INTERPOLATION_DIST_LAST, DAMAGE_INTERPOLATION_DIST_FIRST, DAMAGE_INTERPOLATION_DIST_LAST
from typing import TYPE_CHECKING, Optional, Any, Tuple, Union
if TYPE_CHECKING:
    from items.vehicles import VehicleType
    from items.vehicle_items import Shell, Gun
    from battle_modifiers_ext.battle_modifiers import BattleModifier
EXT_DATA_MODIFIERS_KEY = 'battleModifiers'

class BattleParams(object):
    FAKE_PARAM = 0
    VEHICLE_HEALTH = 1
    GRAVITY_FACTOR = 2
    DISP_FACTOR_CHASSIS_MOVEMENT = 3
    DISP_FACTOR_CHASSIS_ROTATION = 4
    TURRET_ROTATION_SPEED = 5
    GUN_ROTATION_SPEED = 6
    RELOAD_TIME = 7
    CLIP_INTERVAL = 8
    BURST_INTERVAL = 9
    AUTORELOAD_TIME = 10
    AIMING_TIME = 11
    SHOT_DISPERSION_RADIUS = 12
    DISP_FACTOR_TURRET_ROTATION = 13
    DISP_FACTOR_AFTER_SHOT = 14
    DISP_FACTOR_WHILE_GUN_DAMAGED = 15
    SHELL_GRAVITY = 16
    SHELL_SPEED = 17
    PIERCING_POWER_FIRST = 18
    PIERCING_POWER_LAST = 19
    DAMAGE_RANDOMIZATION = 20
    PIERCING_POWER_RANDOMIZATION = 21
    NORMALIZATION_ANGLE = 22
    RICOCHET_ANGLE = 23
    ENGINE_POWER = 24
    FW_MAX_SPEED = 25
    BK_MAX_SPEED = 26
    ROTATION_SPEED_ON_STILL = 27
    ROTATION_SPEED_ON_MOVE = 28
    ARMOR_DAMAGE_FIRST = 29
    DEVICE_DAMAGE_FIRST = 30
    INVISIBILITY_ON_STILL = 31
    INVISIBILITY_ON_MOVE = 32
    VISION_RADIUS = 33
    RADIO_DISTANCE = 34
    BATTLE_LENGTH = 35
    VEHICLE_RAMMING_DAMAGE = 36
    VEHICLE_PRESSURE_DAMAGE = 37
    TURRET_RAMMING_DAMAGE = 38
    TURRET_PRESSURE_DAMAGE = 39
    ENV_HULL_DAMAGE = 40
    ENV_CHASSIS_DAMAGE = 41
    ENV_TANKMAN_DAMAGE_CHANCE = 42
    ENV_MODULE_DAMAGE_CHANCE = 43
    REPAIR_SPEED = 44
    VISION_MIN_RADIUS = 45
    VISION_TIME = 46
    EQUIPMENT_COOLDOWN = 47
    FWD_FRICTION = 48
    SIDE_FRICTION = 49
    DIRT_RELEASE_RATE = 50
    MAX_DIRT = 51
    SHOT_EFFECTS = 52
    GUN_EFFECTS = 53
    CHASSIS_DECALS = 54
    ENGINE_SOUNDS = 55
    EXHAUST_EFFECT = 56
    ARMOR_SPALLS_ARMOR_DAMAGE_FIRST = 57
    ARMOR_SPALLS_DEVICE_DAMAGE_FIRST = 58
    ARMOR_SPALLS_IMPACT_RADIUS = 59
    ARMOR_SPALLS_CONE_ANGLE = 60
    ARMOR_SPALLS_DAMAGE_ABSORPTION = 61
    MODE_CREDITS_FACTOR = 62
    INVISIBILITY_FACTOR_AT_SHOT = 63
    VEHICLE_AOI_RADIUS = 64
    SOUND_NOTIFICATIONS = 65
    DIVING_DESTRUCTION_DELAY = 66
    STUN_FACTOR_ENGINE_POWER = 67
    STUN_FACTOR_VEHICLE_ROTATION_SPEED = 68
    STUN_FACTOR_TURRET_TRAVERSE = 69
    STUN_FACTOR_MAX_SPEED = 70
    ARMOR_DAMAGE_LAST = 71
    DEVICE_DAMAGE_LAST = 72
    ARMOR_SPALLS_ARMOR_DAMAGE_LAST = 73
    ARMOR_SPALLS_DEVICE_DAMAGE_LAST = 74
    PIERCING_POWER_INTERPOLATION_DIST_FIRST = 75
    PIERCING_POWER_INTERPOLATION_DIST_LAST = 76
    DAMAGE_INTERPOLATION_DIST_FIRST = 77
    DAMAGE_INTERPOLATION_DIST_LAST = 78
    ALL = None
    MAX = None


BattleParams.ALL = set((v for k, v in BattleParams.__dict__.iteritems() if not k.startswith('_') and k not in ('FAKE_PARAM', 'ALL', 'MAX')))
BattleParams.MAX = max(BattleParams.ALL)

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

    def get(self, paramId):
        return None

    def descr(self):
        pass

    def battleDescr(self):
        pass

    @staticmethod
    def retrieveBattleDescr(descr):
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

    def domain(self):
        pass

    def haveDomain(self, domain):
        return False

    def id(self):
        pass

    def getVehicleModification(self, vehType):
        return vehType

    def getConstantsModification(self):
        return CONSTANTS_ORIGINAL


class ModifiersContext(object):
    __slots__ = ('__modifiers', '__vehType', '__shellDescr', '__gun')

    def __init__(self, modifiers, vehType=None, shellDescr=None, gun=None):
        self.__modifiers = modifiers
        self.__vehType = vehType
        self.__shellDescr = shellDescr
        self.__gun = gun

    def __getattr__(self, item):
        return getattr(self.__modifiers, item)

    def __deepcopy__(self, memo):
        return ModifiersContext(self.__modifiers, self.__vehType, self.__shellDescr, self.__gun)

    def __copy__(self):
        return ModifiersContext(self.__modifiers, self.__vehType, self.__shellDescr, self.__gun)

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
        return 'ModifiersContext(vehicle = {}, shell = {}, modifiers = {})'.format(self.__vehType.name, self.__shellDescr, self.__modifiers)

    @property
    def modifiers(self):
        return self.__modifiers

    @property
    def vehicle(self):
        return self.__vehType

    @vehicle.setter
    def vehicle(self, vehType):
        self.__vehType = vehType

    @property
    def shell(self):
        return self.__shellDescr

    @shell.setter
    def shell(self, shellDescr):
        self.__shellDescr = shellDescr

    @property
    def gun(self):
        return self.__gun

    @gun.setter
    def gun(self, gun):
        self.__gun = gun


BATTLE_MODIFIERS_TYPE = Union[BattleModifiers, ModifiersContext]

def getGlobalModifiers():
    return None
