# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/c11n_constants.py
import constants
RENT_DEFAULT_BATTLES = 50
MAX_OUTFIT_LENGTH = 1024
MAX_CAMOUFLAGE_PATTERN_SIZE = 5

class CustomizationType(object):
    PAINT = 1
    CAMOUFLAGE = 2
    DECAL = 3
    STYLE = 4
    MODIFICATION = 5
    ITEM_GROUP = 6
    RANGE = {PAINT,
     CAMOUFLAGE,
     DECAL,
     STYLE,
     MODIFICATION,
     ITEM_GROUP}


CustomizationTypeNames = {getattr(CustomizationType, k):k for k in dir(CustomizationType) if not k.startswith('_') and k != 'RANGE'}

class ItemTags(object):
    VEHICLE_BOUND = 'vehicleBound'
    PREMIUM_IGR = 'premiumIGR'
    IGR = 'IGR'


class ApplyArea(object):
    NONE = 0
    CHASSIS = 1
    CHASSIS_1 = 2
    CHASSIS_2 = 4
    CHASSIS_3 = 8
    HULL = 16
    HULL_1 = 32
    HULL_2 = 64
    HULL_3 = 128
    TURRET = 256
    TURRET_1 = 512
    TURRET_2 = 1024
    TURRET_3 = 2048
    GUN = 4096
    GUN_1 = 8192
    GUN_2 = 16384
    GUN_3 = 32768
    ALL = 65535
    CHASSIS_PAINT_REGIONS = (CHASSIS, CHASSIS_1, CHASSIS_2)
    HULL_PAINT_REGIONS = (HULL, HULL_1, HULL_2)
    HULL_CAMOUFLAGE_REGIONS = (HULL,)
    HULL_EMBLEM_REGIONS = (HULL, HULL_1)
    HULL_INSCRIPTION_REGIONS = (HULL_2, HULL_3)
    TURRET_PAINT_REGIONS = (TURRET, TURRET_1, TURRET_2)
    TURRET_CAMOUFLAGE_REGIONS = (TURRET,)
    TURRET_EMBLEM_REGIONS = (TURRET, TURRET_1)
    TURRET_INSCRIPTION_REGIONS = (TURRET_2, TURRET_3)
    GUN_PAINT_REGIONS = (GUN, GUN_1, GUN_2)
    GUN_CAMOUFLAGE_REGIONS = (GUN,)
    GUN_EMBLEM_REGIONS = (GUN, GUN_1)
    GUN_INSCRIPTION_REGIONS = (GUN_2, GUN_3)
    RANGE = {HULL,
     HULL_1,
     HULL_2,
     HULL_3,
     TURRET,
     TURRET_1,
     TURRET_2,
     TURRET_3,
     GUN,
     GUN_1,
     GUN_2,
     GUN_3,
     CHASSIS,
     CHASSIS_1,
     CHASSIS_2,
     CHASSIS_3}
    DECAL_REGIONS = HULL_EMBLEM_REGIONS + HULL_INSCRIPTION_REGIONS + TURRET_EMBLEM_REGIONS + TURRET_INSCRIPTION_REGIONS
    CAMOUFLAGE_REGIONS = HULL_CAMOUFLAGE_REGIONS + TURRET_CAMOUFLAGE_REGIONS + GUN_CAMOUFLAGE_REGIONS
    PAINT_REGIONS = CHASSIS_PAINT_REGIONS + HULL_PAINT_REGIONS + TURRET_PAINT_REGIONS + GUN_PAINT_REGIONS
    USER_PAINT_ALLOWED_REGIONS = {CHASSIS,
     HULL,
     TURRET,
     GUN,
     GUN_2}
    EMBLEM_REGIONS = HULL_EMBLEM_REGIONS + TURRET_EMBLEM_REGIONS + GUN_EMBLEM_REGIONS
    INSCRIPTION_REGIONS = HULL_INSCRIPTION_REGIONS + TURRET_INSCRIPTION_REGIONS + GUN_INSCRIPTION_REGIONS
    USER_PAINT_ALLOWED_REGIONS_VALUE = reduce(int.__or__, USER_PAINT_ALLOWED_REGIONS)
    DECAL_REGIONS_VALUE = reduce(int.__or__, DECAL_REGIONS)
    CAMOUFLAGE_REGIONS_VALUE = reduce(int.__or__, CAMOUFLAGE_REGIONS)
    EMBLEM_REGIONS_VALUE = reduce(int.__or__, EMBLEM_REGIONS)
    INSCRIPTION_REGIONS_VALUE = reduce(int.__or__, INSCRIPTION_REGIONS)


class SeasonType(object):
    UNDEFINED = 0
    WINTER = 1
    SUMMER = 2
    DESERT = 4
    EVENT = 8
    ALL = WINTER | SUMMER | DESERT | EVENT
    RANGE = (WINTER,
     SUMMER,
     DESERT,
     EVENT,
     ALL)
    SEASONS = (WINTER,
     SUMMER,
     DESERT,
     EVENT)
    COMMON_SEASONS = (WINTER, SUMMER, DESERT)

    @staticmethod
    def fromArenaKind(arenaKind):
        """Convert season from arena type camouflage kind. see vehicles.CAMOUFLAGE_KINDS"""
        if arenaKind == 0:
            return SeasonType.WINTER
        if arenaKind == 1:
            return SeasonType.SUMMER
        if arenaKind == 2:
            return SeasonType.DESERT
        raise ValueError('unknown arenaKind', arenaKind)


SeasonTypeNames = {getattr(SeasonType, k):k for k in dir(SeasonType) if not k.startswith('_') and isinstance(getattr(SeasonType, k), int)}

class ModificationType(object):
    UNDEFINED = 0
    PAINT_AGE = 1
    CAMOUFLAGE_AGE = 2
    PAINT_FADING = 3
    GLOSS = 4
    METALLIC = 5


class DecalType(object):
    EMBLEM = 1
    INSCRIPTION = 2
