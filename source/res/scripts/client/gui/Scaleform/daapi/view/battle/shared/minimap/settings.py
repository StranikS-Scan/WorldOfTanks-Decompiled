# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/settings.py
from account_helpers.settings_core.options import MinimapVehModelsSetting
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from shared_utils import BitmaskHelper
MINIMAP_COMPONENT_PATH = '_level0.root.{}.main.minimap.entriesContainer'.format(APP_CONTAINERS_NAMES.VIEWS)
MINIMAP_MIN_SIZE_INDEX = 0
MINIMAP_MAX_SIZE_INDEX = 5
MINIMAP_WAS_SPOTTED_RESET_DELAY = 5.0

class CONTAINER_NAME(object):
    TEAM_POINTS = 'points'
    ICONS = 'icons'
    EQUIPMENTS = 'equipments'
    DEAD_VEHICLES = 'deadVehicles'
    ALIVE_VEHICLES = 'aliveVehicles'
    PERSONAL = 'personal'
    FLAGS = 'flags'


class ENTRY_SYMBOL_NAME(object):
    ALLY_TEAM_BASE = 'AllyTeamBaseEntry'
    ENEMY_TEAM_BASE = 'EnemyTeamBaseEntry'
    ALLY_TEAM_SPAWN = 'AllyTeamSpawnEntry'
    ENEMY_TEAM_SPAWN = 'EnemyTeamSpawnEntry'
    CONTROL_POINT = 'ControlPointEntry'
    TUTORIAL_TARGET = 'TutorialTargetEntry'
    ARTILLERY_ENTRY = 'ArtilleryEntry'
    BOMBER_ENTRY = 'BomberEntry'
    VEHICLE = 'VehicleEntry'
    VIEW_POINT = 'ViewPointEntry'
    DEAD_POINT = 'DeadPointEntry'
    VIDEO_CAMERA = 'VideoCameraEntry'
    ARCADE_CAMERA = 'ArcadeCameraEntry'
    STRATEGIC_CAMERA = 'StrategicCameraEntry'
    VIEW_RANGE_CIRCLES = 'ViewRangeCirclesEntry'
    ANIMATION = 'AnimationEntry'
    MARK_CELL = 'CellFlashEntry'
    ALLY_REPAIR_POINT = 'AllyRepairEntry'
    ENEMY_REPAIR_POINT = 'EnemyRepairEntry'
    FLAG_ENTRY = 'FlagEntry'
    ALLY_ABSORPTION_FLAG = 'AllyAbsorptionFlagEntry'
    ENEMY_ABSORPTION_FLAG = 'EnemyAbsorptionFlagEntry'
    RESOURCE_POINT = 'ResourcePointEntry'


class TRANSFORM_FLAG(object):
    FULL = 4294967295L
    NO_POSITION = 1
    NO_ROTATION = 2
    NO_SCALE = 4
    DEFAULT = FULL ^ NO_SCALE


class CIRCLE_TYPE(object):
    EMPTY = 0
    DRAW_RANGE = 1
    MAX_VIEW_RANGE = 2
    VIEW_RANGE = 4


class CIRCLE_STYLE(object):
    ALPHA = 50

    class COLOR(object):
        DRAW_RANGE = 16776960
        MAX_VIEW_RANGE = 16777215
        VIEW_RANGE = 2621223


class VIEW_RANGE_CIRCLES_AS3_DESCR(object):
    """
    VIEW_RANGE_CIRCLES_AS3_DESCR calling as3 functions by [invokePy2As]  ViewRangeCirclesMinimapEntry.as
    
    [as_addDrawRange] Set max draw range
    :param color : Number
    :param alpha : Number
    :param range : Number
    """
    AS_ADD_MAX_DRAW_CIRCLE = 'as_addDrawRange'
    AS_ADD_DYN_CIRCLE = 'as_addDynamicViewRange'
    AS_ADD_MAX_VIEW_CIRCLE = 'as_addMaxViewRage'
    AS_UPDATE_DYN_CIRCLE = 'as_updateDynRange'
    AS_DEL_MAX_DRAW_CIRCLE = 'as_delDrawRange'
    AS_DEL_DYN_CIRCLE = 'as_delDynRange'
    AS_DEL_MAX_VIEW_CIRCLE = 'as_delMaxViewRage'
    AS_INIT_ARENA_SIZE = 'as_initArenaSize'
    AS_REMOVE_ALL_CIRCLES = 'as_removeAllCircles'


EQ_MARKER_TO_SYMBOL = {'artillery': ENTRY_SYMBOL_NAME.ARTILLERY_ENTRY,
 'bomber': ENTRY_SYMBOL_NAME.BOMBER_ENTRY}

class RESOURCE_ENTRY_STATE(object):
    CONFLICT = 'conflict'
    COOLDOWN = 'cooldown'
    READY = 'ready'
    OWN_MINING = 'own_mining'
    ENEMY_MINING = 'enemy_mining'


class FLAG_ENTRY_STATE(object):
    NEUTRAL = 'neutral'
    ALLY = 'ally'
    ENEMY = 'enemy'
    COOLDOWN = 'cooldown'


CAPTURE_STATE_BY_TEAMS = {True: RESOURCE_ENTRY_STATE.OWN_MINING,
 False: RESOURCE_ENTRY_STATE.ENEMY_MINING}
CAPTURE_FROZEN_STATE_BY_TEAMS = {True: RESOURCE_ENTRY_STATE.OWN_MINING,
 False: RESOURCE_ENTRY_STATE.ENEMY_MINING}

class ADDITIONAL_FEATURES(BitmaskHelper):
    OFF = 0
    BY_REQUEST = 1
    DO_REQUEST = 2
    ALWAYS = 4

    @classmethod
    def isOn(cls, mask):
        return cls.DO_REQUEST & mask > 0 or cls.ALWAYS & mask > 0

    @classmethod
    def isChanged(cls, mask):
        return cls.BY_REQUEST & mask > 0


def convertSettingToFeatures(value, previous):
    options = MinimapVehModelsSetting.OPTIONS
    indexes = MinimapVehModelsSetting.VEHICLE_MODELS_TYPES
    result = ADDITIONAL_FEATURES.OFF
    selected = indexes[value]
    if selected == options.ALT:
        result = ADDITIONAL_FEATURES.BY_REQUEST
    elif selected == options.ALWAYS:
        result = ADDITIONAL_FEATURES.ALWAYS
    if previous & ADDITIONAL_FEATURES.DO_REQUEST > 0:
        result |= ADDITIONAL_FEATURES.DO_REQUEST
    return result


def clampMinimapSizeIndex(index):
    return min(max(index, MINIMAP_MIN_SIZE_INDEX), MINIMAP_MAX_SIZE_INDEX)


MINIMAP_ATTENTION_SOUND_ID = 'minimap_attention'
