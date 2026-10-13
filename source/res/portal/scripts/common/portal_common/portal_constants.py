# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common/portal_constants.py
from enum import IntEnum
import Math
import constants
import UnitBase
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as ORIG_BATTLE_EVENT_TYPE
from constants_utils import ConstInjector, AbstractBattleMode
from portal_common.battle_results import portal

class BattleState(IntEnum):
    OUT_OF_BATTLE = 0
    NORMAL = 1
    BOSS_FIGHT = 2
    SUPER_BOSS_FIGHT = 3
    SUPER_BOSS_TRANSITION = 4


class PortalBossesID(IntEnum):
    BOSS_ID = 0
    SUPER_BOSS_ID = 1


class CampMarkerStatesIDs(IntEnum):
    DEFAULT_CAMP = 0
    CAN_BE_CAPTURED = 1
    CAPTURED = 2


class TeleportMarkerStatesIDs(IntEnum):
    DEFAULT_TELEPORT = 0
    TELEPORT_OCCUPIED = 1
    TELEPORT_COOLDOWN = 2


class FrontierObserverStatesIDs(IntEnum):
    INACTIVE = 0
    ACTIVE = 1


class DynamicVehicleChangeShotStates(IntEnum):
    INACTIVE = 0
    BEFORE_SHOT = 1
    AFTER_SHOT = 2
    ACTIVE = 3


class PortalBattleLevel(IntEnum):
    INVALID = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3


PORTAL_BATTLE_LEVELS_TO_VEHICLE_LEVELS = {PortalBattleLevel.EASY: (1, 4),
 PortalBattleLevel.MEDIUM: (5, 7),
 PortalBattleLevel.HARD: (8, 10)}

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    PORTAL = 301


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    PORTAL = 61


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    PORTAL = 301


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    PORTAL = 301


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    PORTAL = 2097152


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    PORTAL = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.PORTAL


class INVITATION_TYPE(constants.INVITATION_TYPE, ConstInjector):
    PORTAL = PREBATTLE_TYPE.PORTAL


class CLIENT_UNIT_CMD(UnitBase.CLIENT_UNIT_CMD, ConstInjector):
    START_UNIT_PORTAL_BATTLE = 1102
    SET_PORTAL_UNIT_BATTLE_LEVEL = 1103
    SET_PORTAL_VEHICLE = 1104


class UNIT_NOTIFY_CMD(UnitBase.UNIT_NOTIFY_CMD, ConstInjector):
    SET_PORTAL_UNIT_BATTLE_LEVEL = 101
    SET_PORTAL_VEHICLE_LEVEL = 102


class BATTLE_EVENT_TYPE(ORIG_BATTLE_EVENT_TYPE, ConstInjector):
    PORTAL_ACTION_APPLIED = 101
    HEAL_SELF_VEHICLE_APPLIED_ACTION = 102


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    PORTAL = 9


PORTAL_GAME_PARAMS_KEY = 'portal_config'
VISIBILITY_DEBUF_NAME = 'visibility'
HEALTH_DEBUF_NAME = 'health'

class PortalBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.PORTAL
    _QUEUE_TYPE = QUEUE_TYPE.PORTAL
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.PORTAL
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.PORTAL
    _INVITATION_TYPE = INVITATION_TYPE.PORTAL
    _UNIT_MGR_NAME = 'PortalUnitMgr'
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.PORTAL
    _ROSTER_TYPE = ROSTER_TYPE.PORTAL
    _GAME_PARAMS_KEY = PORTAL_GAME_PARAMS_KEY
    _SEASON_TYPE_BY_NAME = 'portal_battle'
    _SEASON_TYPE = GameSeasonType.PORTAL
    _SEASON_MANAGER_TYPE = (GameSeasonType.PORTAL, PORTAL_GAME_PARAMS_KEY)
    _BATTLE_RESULTS_CONFIG = portal
    _SM_TYPE_BATTLE_RESULT = 'portalBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT]

    @property
    def _ROSTER_CLASS(self):
        from portal_common.portal_roster_config import PortalRoster
        return PortalRoster


PDATA_KEY_PORTAL_BATTLES = 'portal'
R46_KV_13_H = 5120257
F43_AMC_35_H = 5120321
GB107_Cavalier_H = 5120337
P117_DS_PZlnz_H = 5120401
ALL_PORTAL_VEHICLES = (R46_KV_13_H,
 F43_AMC_35_H,
 GB107_Cavalier_H,
 P117_DS_PZlnz_H)
PORTAL_VEHICLES_COUNT = len(ALL_PORTAL_VEHICLES)
PORTAL_VEHICLE_EXPERIENCE_KEY = 'vehicleExperience'
PORTAL_VEHICLE_UPGRADES_KEY = 'vehicleUpgradesMask'
PORTAL_MAX_COMPLEXITY_KEY = 'maxAvailableComplexityLevel'
PORTAL_ACCOUNT_SETTINGS_KEY = 'portal26'
SELECTED_COMPLEXITY_LEVEL = 'selected_complexity_level'
EVENT_ENTRY_POINT_IS_NEW = 'eventEntryPointIsNew'
PORTAL_OUTRO_VIDEO_VIEWED = 'portalOutroVideoViewed'
PORTAL_INTRO_VIDEO_VIEWED = 'portalIntroVideoViewed'
PORTAL_FINISHED_NOTIFICATION_VIEWED = 'portalFinishedNotificationViewed'
PORTAL_STARTED_NOTIFICATION_VIEWED = 'portalStartedNotificationViewed'
PORTAL_LAST_SEASON_ID = 'portalLastSeasonID'
PORTAL_VEHICLE_UPGRADES_VIEWED = 'portalVehicleUpgradesViewed'
PORTAL_ABOUT_IMPROVEMENTS_VIEWED = 'portalAboutImprovementsViewed'
MAX_UNLOCKED_UPGRADE_LEVEL_VIEWED = 'maxUnlockedUpgradeLevelViewed'
PORTAL_MATCH_PLAYED = 'portalMatchPlayed'
PORTAL_EXPIRE_DATE_ACCOUNT_SETTINGS = 'portalExpireDateAccountSettings'
ACCOUNT_DEFAULT_SETTINGS = {PORTAL_ACCOUNT_SETTINGS_KEY: {PORTAL_EXPIRE_DATE_ACCOUNT_SETTINGS: 0,
                               SELECTED_COMPLEXITY_LEVEL: 1,
                               EVENT_ENTRY_POINT_IS_NEW: True,
                               PORTAL_OUTRO_VIDEO_VIEWED: False,
                               PORTAL_INTRO_VIDEO_VIEWED: False,
                               PORTAL_FINISHED_NOTIFICATION_VIEWED: False,
                               PORTAL_STARTED_NOTIFICATION_VIEWED: False,
                               PORTAL_LAST_SEASON_ID: 0,
                               PORTAL_ABOUT_IMPROVEMENTS_VIEWED: False,
                               PORTAL_VEHICLE_UPGRADES_VIEWED: {R46_KV_13_H: {'isViewed': False,
                                                                              'maxViewedStage': -1},
                                                                F43_AMC_35_H: {'isViewed': False,
                                                                               'maxViewedStage': -1},
                                                                GB107_Cavalier_H: {'isViewed': False,
                                                                                   'maxViewedStage': -1},
                                                                P117_DS_PZlnz_H: {'isViewed': False,
                                                                                  'maxViewedStage': -1}},
                               MAX_UNLOCKED_UPGRADE_LEVEL_VIEWED: {R46_KV_13_H: -1,
                                                                   F43_AMC_35_H: -1,
                                                                   GB107_Cavalier_H: -1,
                                                                   P117_DS_PZlnz_H: -1},
                               PORTAL_MATCH_PLAYED: 0}}
DEFAULT_NOTIFICATIONS = {PORTAL_ACCOUNT_SETTINGS_KEY: {}}

class PortalTokens(object):
    PROGRESSION_TOKEN = 'portal:token'
    LAST_LEVEL_VICTORY = 'portal:last_level_victory'
    ALL_VEHICLES_UPGRADED = 'portal:all_vehicles_upgraded'


PORTAL_GUIDED_MISSILE_OFFSET = Math.Vector3(0, 5, 0)
PORTAL_GUIDED_MISSILE_DEPLOY_START_Y = 10.0

class ScoreSystemActions(object):
    BOT_KILLED = 'botKilled'
    BASE_DEFENDER = 'baseDefender'
    DAMAGE_DEALT = 'dealDamage'
    BOSS_DAMAGE_DEALT = 'dealBossDamage'
    DAMAGE_BLOCKED = 'damageBlocked'
    ABILITY_USED = 'abilityUsed'
    BASE_CONQUEROR = 'baseConqueror'
    DAMAGE_ASSIST = 'assistDamage'


def isPortalGuidedMissileCeilingBlocked(spaceID, vehiclePosition):
    import BigWorld
    from constants import CollisionFlags
    startPos = vehiclePosition + PORTAL_GUIDED_MISSILE_OFFSET
    endPos = startPos + Math.Vector3(0, PORTAL_GUIDED_MISSILE_DEPLOY_START_Y, 0)
    return BigWorld.collideSegment(spaceID, startPos, endPos, CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE) is not None
