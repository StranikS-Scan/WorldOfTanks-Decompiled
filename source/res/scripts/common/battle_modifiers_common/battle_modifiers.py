# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_modifiers_common/battle_modifiers.py
from ResMgr import DataSection
from typing import TYPE_CHECKING, Optional, Any, Tuple, Union
if TYPE_CHECKING:
    from items.vehicles import VehicleType
    from battle_modifiers_ext.battle_modifiers import BattleModifier
EXT_DATA_MODIFIERS_KEY = 'battleModifiers'

class BattleParams(object):
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
    ARMOR_DAMAGE = 29
    DEVICE_DAMAGE = 30
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
    ALL = None


BattleParams.ALL = set((v for k, v in BattleParams.__dict__.iteritems() if not k.startswith('_') and k != 'ALL'))

class BattleModifiers(object):

    def __init__(self, source=None):
        pass

    def __call__(self, paramId, value):
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

    def domain(self):
        pass

    def haveDomain(self, domain):
        return False

    def id(self):
        pass


class VehicleModificationCache(object):

    def __init__(self, layerCount=0):
        pass

    def get(self, vehType, battleModifiers):
        return vehType

    def clear(self):
        pass


_modificationCache = VehicleModificationCache()

def getModificationCache():
    return _modificationCache


def getGlobalModifiers():
    return None
