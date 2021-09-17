# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/c11n_constants.py
import constants
from soft_exception import SoftException
RENT_DEFAULT_BATTLES = 50
MAX_OUTFIT_LENGTH = 1024
MAX_CAMOUFLAGE_PATTERN_SIZE = 5
MAX_ITEMS_FOR_BUY_OPERATION = 100
HIDDEN_CAMOUFLAGE_ID = 1
TOTAL_COUNTER_TYPE_DESCR = -1
MAX_PROJECTION_DECALS = 9
MAX_SEQUENCES = 5
MAX_ATTACHMENTS = 5
MAX_USERS_PROJECTION_DECALS = 3
MAX_PROJECTION_DECALS_PER_AREA = 3
PROJECTION_DECALS_SCALE_ID_VALUES = (0, 1, 2, 3)
DEFAULT_DECAL_SCALE_FACTORS = (0.6, 0.8, 1.0)
DEFAULT_SCALE_FACTOR_ID = 3
DEFAULT_PALETTE = 0
DEFAULT_DECAL_CLIP_ANGLE = 0.0
DEFAULT_DECAL_TINT_COLOR = (255, 255, 255, 255)
DEFAULT_DECAL_ANCHOR_SHIFT = 0.0
RENT_IS_ALMOST_OVER_VALUE = 3
EDITABLE_STYLE_STORAGE_DEPTH = 5
EMPTY_ITEM_ID = 22222
CUSTOM_STYLE_POOL_ID = 0
SLOT_DEFAULT_ALLOWED_MODEL = 'default'
OUTFIT_POOL_EMPTY_STUB = (None, None)
DEFAULT_POSITION = (0, 0, 0)
DEFAULT_ROTATION = (0, 0, 0)
DEFAULT_SCALE = (1, 1, 1)
DEFAULT_GLOSS = 0.509
DEFAULT_METALLIC = 0.23

class CustomizationType(object):
    PAINT = 1
    CAMOUFLAGE = 2
    DECAL = 3
    STYLE = 4
    MODIFICATION = 5
    ITEM_GROUP = 6
    PROJECTION_DECAL = 7
    INSIGNIA = 8
    PERSONAL_NUMBER = 9
    FONT = 10
    SEQUENCE = 11
    ATTACHMENT = 12
    RANGE = {PAINT,
     CAMOUFLAGE,
     DECAL,
     STYLE,
     MODIFICATION,
     ITEM_GROUP,
     PROJECTION_DECAL,
     PERSONAL_NUMBER,
     FONT}
    STYLE_ONLY_RANGE = {ATTACHMENT, SEQUENCE}
    FULL_RANGE = RANGE | STYLE_ONLY_RANGE
    APPLIED_TO_TYPES = (PAINT,
     CAMOUFLAGE,
     DECAL,
     PERSONAL_NUMBER)
    SIMPLE_TYPES = (STYLE,
     MODIFICATION,
     PROJECTION_DECAL,
     SEQUENCE,
     ATTACHMENT)
    SIMPLE_OUTFIT_COMPONENT_TYPES = (MODIFICATION, PROJECTION_DECAL)
    DISMOUNT_TYPE = (PAINT,
     CAMOUFLAGE,
     DECAL,
     PERSONAL_NUMBER,
     MODIFICATION,
     PROJECTION_DECAL)
    TYPES_FOR_EDITABLE_STYLE = (PAINT,
     DECAL,
     PERSONAL_NUMBER,
     MODIFICATION,
     PROJECTION_DECAL)


CustomizationTypeNames = {getattr(CustomizationType, k):k for k in dir(CustomizationType) if isinstance(getattr(CustomizationType, k), int)}
CustomizationNamesToTypes = {v:k for k, v in CustomizationTypeNames.iteritems()}

class CustomizationDisplayType(object):
    HISTORICAL = 0
    NON_HISTORICAL = 1
    FANTASTICAL = 2


class ItemTags(object):
    VEHICLE_BOUND = 'vehicleBound'
    PREMIUM_IGR = 'premiumIGR'
    IGR = 'IGR'
    RARE = 'rare'
    HIDDEN_IN_UI = 'hiddenInUI'
    DIM = 'dim'
    FULL_RGB = 'fullRGB'
    NATIONAL_EMBLEM = 'nationalEmblem'
    STYLE_ONLY = 'styleOnly'
    PROGRESSION_REQUIRED = 'progression_required'
    ADD_NATIONAL_EMBLEM = 'addNationalEmblem'
    DISABLE_VERTICAL_MIRROR = 'disableVerticalMirror'
    STYLE_PROGRESSION = 'styleProgression'
    ONLY_VERTICAL_MIRROR = 'onlyVerticalMirror'
    HIDE_IF_INCOMPATIBLE = 'hideIfIncompatible'


class ProjectionDecalType(object):
    POSITION = 0
    TAGS = 1


class ProjectionDecalDirectionTags(object):
    PREFIX = 'direction_'
    ANY = PREFIX + 'any'
    LEFT_TO_RIGHT = PREFIX + 'left_to_right'
    RIGHT_TO_LEFT = PREFIX + 'right_to_left'
    LEFT = 'left'
    RIGHT = 'right'
    FRONT = 'front'
    ALL = (ANY,
     LEFT_TO_RIGHT,
     RIGHT_TO_LEFT,
     LEFT,
     RIGHT,
     FRONT)


class ProjectionDecalFormTags(object):
    PREFIX = 'formfactor_'
    SQUARE = PREFIX + 'square'
    RECT1X2 = PREFIX + 'rect1x2'
    RECT1X3 = PREFIX + 'rect1x3'
    RECT1X4 = PREFIX + 'rect1x4'
    RECT1X6 = PREFIX + 'rect1x6'
    ALL = (SQUARE,
     RECT1X2,
     RECT1X3,
     RECT1X4,
     RECT1X6)


class ProjectionDecalPreferredTags(object):
    PREFIX = 'preferred_'
    SQUARE = PREFIX + ProjectionDecalFormTags.SQUARE
    RECT1X2 = PREFIX + ProjectionDecalFormTags.RECT1X2
    RECT1X3 = PREFIX + ProjectionDecalFormTags.RECT1X3
    RECT1X4 = PREFIX + ProjectionDecalFormTags.RECT1X4
    RECT1X6 = PREFIX + ProjectionDecalFormTags.RECT1X6
    ALL = (SQUARE,
     RECT1X2,
     RECT1X3,
     RECT1X4,
     RECT1X6)


class ProjectionDecalMatchingTags(object):
    MIMIC = 'mimic'
    COVER = 'cover'
    SAFE = 'safe'
    ALL = (MIMIC, COVER, SAFE)


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
    CHASSIS_REGIONS = (CHASSIS,
     CHASSIS_1,
     CHASSIS_2,
     CHASSIS_3)
    CHASSIS_PAINT_REGIONS = (CHASSIS, CHASSIS_1, CHASSIS_2)
    HULL_REGIONS = (HULL,
     HULL_1,
     HULL_2,
     HULL_3)
    HULL_PAINT_REGIONS = (HULL, HULL_1, HULL_2)
    HULL_CAMOUFLAGE_REGIONS = (HULL,)
    HULL_EMBLEM_REGIONS = (HULL, HULL_1)
    HULL_INSCRIPTION_REGIONS = (HULL_2, HULL_3)
    HULL_INSIGNIA_REGIONS = (HULL, HULL_1)
    HULL_PERSONAL_NUMBER_REGIONS = (HULL_2, HULL_3)
    TURRET_REGIONS = (TURRET,
     TURRET_1,
     TURRET_2,
     TURRET_3)
    TURRET_PAINT_REGIONS = (TURRET, TURRET_1, TURRET_2)
    TURRET_CAMOUFLAGE_REGIONS = (TURRET,)
    TURRET_EMBLEM_REGIONS = (TURRET, TURRET_1)
    TURRET_INSCRIPTION_REGIONS = (TURRET_2, TURRET_3)
    TURRET_INSIGNIA_REGIONS = (TURRET, TURRET_1)
    TURRET_PERSONAL_NUMBER_REGIONS = (TURRET_2, TURRET_3)
    GUN_REGIONS = (GUN,
     GUN_1,
     GUN_2,
     GUN_3)
    GUN_PAINT_REGIONS = (GUN, GUN_1, GUN_2)
    GUN_CAMOUFLAGE_REGIONS = (GUN,)
    GUN_EMBLEM_REGIONS = (GUN, GUN_1)
    GUN_INSCRIPTION_REGIONS = (GUN_2, GUN_3)
    GUN_INSIGNIA_REGIONS = (GUN, GUN_1)
    GUN_PERSONAL_NUMBER_REGIONS = (GUN_2, GUN_3)
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
    INSIGNIA_REGIONS = HULL_INSIGNIA_REGIONS + TURRET_INSIGNIA_REGIONS + GUN_INSIGNIA_REGIONS
    PERSONAL_NUMBER_REGIONS = HULL_PERSONAL_NUMBER_REGIONS + TURRET_PERSONAL_NUMBER_REGIONS + GUN_PERSONAL_NUMBER_REGIONS
    MODIFICATION_REGIONS = (NONE,)
    PAINT_REGIONS_VALUE = reduce(int.__or__, USER_PAINT_ALLOWED_REGIONS)
    DECAL_REGIONS_VALUE = reduce(int.__or__, DECAL_REGIONS)
    CAMOUFLAGE_REGIONS_VALUE = reduce(int.__or__, CAMOUFLAGE_REGIONS)
    EMBLEM_REGIONS_VALUE = reduce(int.__or__, EMBLEM_REGIONS)
    INSCRIPTION_REGIONS_VALUE = reduce(int.__or__, INSCRIPTION_REGIONS)
    INSIGNIA_REGIONS_VALUE = reduce(int.__or__, INSIGNIA_REGIONS)
    PERSONAL_NUMBER_REGIONS_VALUE = reduce(int.__or__, PERSONAL_NUMBER_REGIONS)
    CHASSIS_REGIONS_VALUE = reduce(int.__or__, CHASSIS_REGIONS)
    GUN_REGIONS_VALUE = reduce(int.__or__, GUN_REGIONS)
    HULL_REGIONS_VALUE = reduce(int.__or__, HULL_REGIONS)
    TURRET_REGIONS_VALUE = reduce(int.__or__, TURRET_REGIONS)
    RANGE_REGIONS_VALUE = reduce(int.__or__, RANGE)

    @staticmethod
    def getAppliedCount(appliedTo, appliedRange=RANGE_REGIONS_VALUE):
        return bin(appliedTo & appliedRange).count('1')


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
    REGULAR = COMMON_SEASONS + (ALL,)

    @staticmethod
    def fromArenaKind(arenaKind):
        if arenaKind == 0:
            return SeasonType.WINTER
        if arenaKind == 1:
            return SeasonType.SUMMER
        if arenaKind == 2:
            return SeasonType.DESERT
        raise SoftException('unknown arenaKind', arenaKind)


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
    ALL = (EMBLEM, INSCRIPTION)


DecalTypeNames = {getattr(DecalType, k):k for k in dir(DecalType) if not k.startswith('_')}

class StyleFlags(object):
    ENABLED = 1
    INSTALLED = 2
    EMPTY = 0
    ACTIVE = ENABLED | INSTALLED


class Options:
    NONE = 0
    MIRRORED_HORIZONTALLY = 1
    MIRRORED_VERTICALLY = 2
    COMBO_MIRRORED = MIRRORED_HORIZONTALLY | MIRRORED_VERTICALLY
    RANGE = (NONE,
     MIRRORED_HORIZONTALLY,
     MIRRORED_VERTICALLY,
     COMBO_MIRRORED)
    PROJECTION_DECALS_ALLOWED_OPTIONS = (MIRRORED_HORIZONTALLY, MIRRORED_VERTICALLY, COMBO_MIRRORED)
    PROJECTION_DECALS_ALLOWED_OPTIONS_VALUE = reduce(int.__or__, PROJECTION_DECALS_ALLOWED_OPTIONS)


class ImageOptions:
    NONE = 0
    FULL_RGB = 1


NO_OUTFIT_DATA = ('', StyleFlags.EMPTY)
C11N_MAX_REGION_NUM = 3
C11N_GUN_REGION = 0
C11N_MASK_REGION = 2
C11N_GUN_APPLY_REGIONS = {'GUN': C11N_GUN_REGION,
 'GUN_2': C11N_MASK_REGION}
CUSTOMIZATION_SLOTS_VEHICLE_PARTS = ('hull', 'chassis', 'turret', 'gun')
UNBOUND_VEH_KEY = 0

class CamouflageTilingType(object):
    NONE = 0
    LEGACY = 1
    RELATIVE = 2
    RELATIVEWITHFACTOR = 3
    ABSOLUTE = 4
    RANGE = None


CamouflageTilingType.RANGE = tuple([ getattr(CamouflageTilingType, k) for k in dir(CamouflageTilingType) if not k.startswith('_') and k not in ('RANGE', 'NONE') ])
CamouflageTilingTypeNames = {getattr(CamouflageTilingType, k):k for k in dir(CamouflageTilingType) if not k.startswith('_') and k not in ('RANGE', 'NONE')}
CamouflageTilingTypeNameToType = {v:k for k, v in CamouflageTilingTypeNames.iteritems()}
EASING_TRANSITION_DURATION = 0.8
IMMEDIATE_TRANSITION_DURATION = 0.0

class SLOT_TYPE_NAMES(object):
    PAINT = 'paint'
    CAMOUFLAGE = 'camouflage'
    INSCRIPTION = 'inscription'
    EMBLEM = 'player'
    STYLE = 'style'
    EFFECT = 'effect'
    PROJECTION_DECAL = 'projectionDecal'
    INSIGNIA = 'insignia'
    FIXED_EMBLEM = 'fixedEmblem'
    FIXED_INSCRIPTION = 'fixedInscription'
    FIXED_PROJECTION_DECAL = 'fixedProjectionDecal'
    EDITABLE_STYLE_DELETABLE = (INSCRIPTION, EMBLEM, PROJECTION_DECAL)
    DECALS = (INSCRIPTION, EMBLEM)
    FIXED = (FIXED_EMBLEM, FIXED_INSCRIPTION, FIXED_PROJECTION_DECAL)
    ALL = (PAINT,
     CAMOUFLAGE,
     INSCRIPTION,
     EMBLEM,
     STYLE,
     EFFECT,
     PROJECTION_DECAL,
     INSIGNIA,
     FIXED_EMBLEM,
     FIXED_INSCRIPTION,
     FIXED_PROJECTION_DECAL)


class EDITING_STYLE_REASONS(object):
    IS_EDITABLE = 'isEditable'
    NOT_EDITABLE = 'notEditable'
    NOT_REACHED_LEVEL = 'notReachedLevel'
    NOT_HAVE_ANY_PROGRESIIVE_DECALS = 'notHaveAnyProgressiveDecals'
    ENABLED = (IS_EDITABLE,)
    DISABLED = (NOT_EDITABLE, NOT_REACHED_LEVEL, NOT_HAVE_ANY_PROGRESIIVE_DECALS)
