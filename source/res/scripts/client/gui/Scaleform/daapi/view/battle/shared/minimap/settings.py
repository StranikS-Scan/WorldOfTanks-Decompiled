# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/settings.py
from enum import Enum
from account_helpers.settings_core.options import MinimapVehModelsSetting, MinimapHPSettings
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from shared_utils import BitmaskHelper
MINIMAP_COMPONENT_PATH = '_level0.root.{}.main.minimap.entriesContainer'.format(LAYER_NAMES.VIEWS)
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
    ZONES = 'zones'
    PROTECTION_ZONE = 'landingZone'
    HQS = 'hqs'


class ENTRY_SYMBOL_NAME(object):
    ALLY_TEAM_BASE = 'AllyTeamBaseEntry'
    ENEMY_TEAM_BASE = 'EnemyTeamBaseEntry'
    ALLY_TEAM_SPAWN = 'AllyTeamSpawnEntry'
    ENEMY_TEAM_SPAWN = 'EnemyTeamSpawnEntry'
    CONTROL_POINT = 'ControlPointEntry'
    TUTORIAL_TARGET = 'TutorialTargetEntry'
    BOOTCAMP_TARGET = 'BootcampTargetEntry'
    ARTILLERY_ENTRY = 'ArtilleryEntry'
    ARTILLERY_YELLOW_ENTRY = 'ArtilleryYellowEntry'
    AOE_ARTILLERY_ENTRY = 'AOEArtilleryMinimapEntry'
    BOMBER_ENTRY = 'BomberEntry'
    RECON_ENTRY = 'ReconEntry'
    SMOKE_ENTRY = 'SmokeEntry'
    VEHICLE = 'VehicleEntry'
    VIEW_POINT = 'ViewPointEntry'
    DEAD_POINT = 'DeadPointEntry'
    VIDEO_CAMERA = 'VideoCameraEntry'
    ARCADE_CAMERA = 'ArcadeCameraEntry'
    STRATEGIC_CAMERA = 'StrategicCameraEntry'
    VIEW_RANGE_CIRCLES = 'ViewRangeCirclesEntry'
    ANIMATION = 'AnimationEntry'
    MARK_OBJECTIVE_DEF = 'PositionDefendEntry'
    MARK_OBJECTIVE_ATK = 'PositionAttackEntry'
    MARK_OBJECTIVE_REPLY_DEF = 'PositionDefendReplyEntry'
    MARK_OBJECTIVE_REPLY_ATK = 'PositionAttackReplyEntry'
    MARK_POSITION = 'PositionFlashEntry'
    MARK_POSITION_HW = 'HWPositionFlashEntry'
    ARTY_MARKER = 'ArtyMarkerMinimapEntry'
    ARTY_HIT_DOT_MARKER = 'ArtyHitDotMarkerUI'
    LOCATION_MARKER = 'MarkGoingToPositionEntryUI'
    ATTENTION_MARKER = 'MarkAttentionEntryUI'
    SHOOTING_POINT_MARKER = 'ShootingPointEntryUI'
    NAVIGATION_POINT_MARKER = 'NavigationPointEntryUI'
    EPIC_SECTOR_ENEMY_BASE = 'SectorBaseEnemyEntry'
    EPIC_SECTOR_ALLY_BASE = 'SectorBaseAllyEntry'
    EPIC_HQ_ENEMY = 'HeadquarterEnemyEntry'
    EPIC_HQ_ALLY = 'HeadquarterAllyEntry'
    EPIC_SECTOR = 'SectorEntry'
    EPIC_SECTOR_OVERLAY = 'SectorOverlayEntry'
    EPIC_HQ = 'HeadquarterEntry'
    EPIC_FLP = 'FrontLinePointEntry'
    EPIC_REPAIR = 'ResupplyEntry'
    EPIC_PROTECTION_ZONE = 'LandingZoneEntry'
    EPIC_DEPLOY_SECTOR_BASE_ALLY = 'SectorBaseEntryDeploymentAlly'
    EPIC_DEPLOY_SECTOR_BASE_ENEMY = 'SectorBaseEntryDeploymentEnemy'
    EPIC_DEPLOY_HQ_ALLY = 'HeadquarterEntryDeploymentAlly'
    EPIC_DEPLOY_HQ_ENEMY = 'HeadquarterEntryDeploymentEnemy'
    RADAR_ANIM = 'RadarUI'
    DISCOVERED_ITEM_MARKER = 'net.wg.gui.battle.views.minimap.components.entries.battleRoyale.DiscoveredItemMarker'
    COMP7_RECON = 'Comp7PointReconMinimapEntryUI'


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
    MIN_SPOTTING_RANGE = 8


class CIRCLE_STYLE(object):
    ALPHA = 50

    class COLOR(object):
        DRAW_RANGE = 16776960
        MAX_VIEW_RANGE = 16777215
        VIEW_RANGE = 2621223
        MIN_SPOTTING_RANGE = 4499630


class VIEW_RANGE_CIRCLES_AS3_DESCR(object):
    AS_ADD_MAX_DRAW_CIRCLE = 'as_addDrawRange'
    AS_ADD_DYN_CIRCLE = 'as_addDynamicViewRange'
    AS_ADD_MAX_VIEW_CIRCLE = 'as_addMaxViewRage'
    AS_ADD_MIN_SPOTTING_CIRCLE = 'as_addMinSpottingRange'
    AS_UPDATE_DYN_CIRCLE = 'as_updateDynRange'
    AS_DEL_MAX_DRAW_CIRCLE = 'as_delDrawRange'
    AS_DEL_DYN_CIRCLE = 'as_delDynRange'
    AS_DEL_MAX_VIEW_CIRCLE = 'as_delMaxViewRage'
    AS_DEL_MIN_SPOTTING_CIRCLE = 'as_delMinSpottingRange'
    AS_INIT_ARENA_SIZE = 'as_initArenaSize'
    AS_REMOVE_ALL_CIRCLES = 'as_removeAllCircles'


EQ_MARKER_TO_SYMBOL = {'artillery': ENTRY_SYMBOL_NAME.ARTILLERY_ENTRY,
 'artillery_yellow': ENTRY_SYMBOL_NAME.ARTILLERY_YELLOW_ENTRY,
 'artillery_fort_ally': ENTRY_SYMBOL_NAME.AOE_ARTILLERY_ENTRY,
 'artillery_fort_enemy': ENTRY_SYMBOL_NAME.AOE_ARTILLERY_ENTRY,
 'bomber': ENTRY_SYMBOL_NAME.BOMBER_ENTRY,
 'recon': ENTRY_SYMBOL_NAME.RECON_ENTRY,
 'smoke': ENTRY_SYMBOL_NAME.SMOKE_ENTRY}

class SettingsTypes(Enum):
    MinimapVehicles = 0
    MinimapHitPoint = 1


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


def convertSettingToFeatures(value, previous, settingsType):
    if settingsType == SettingsTypes.MinimapVehicles:
        options = MinimapVehModelsSetting.OPTIONS
        indices = MinimapVehModelsSetting.VEHICLE_MODELS_TYPES
        selected = indices[value]
    else:
        options = MinimapHPSettings.Options
        selected = MinimapHPSettings.Options(value)
    result = ADDITIONAL_FEATURES.OFF
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
