# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/hb_constants.py
from enum import IntEnum, Enum
HB_GAME_PARAMS_KEY = 'historical_battles'
HB_SHOP_GAME_PARAMS_KEY = 'historical_battles_shop'
HB_FRONT_COUPONS_GAME_PARAMS_KEY = 'historical_battles_front_coupons'
HB_COINS_GAME_PARAMS_KEY = 'hb_coins'
HB_BATTLES_ENABLED = 'isBattlesEnabled'
FRONT_COUPON_TOKEN_PREFIX = 'hb_front_coupon_'
FRONT_COUPON_RECHARGE_QUEST_GROUP_ID = FRONT_COUPON_TOKEN_PREFIX + 'recharge'
RESERVED_FRONT_COUPON_SUFFIX = ':reserved'
HB_BATTLE_QUESTS_PREFIX = 'HBBattleQuest'
FRONTMAN_PROGRESS_QUEST_PREFIX_TPL = 'hb_frontman_{}'
FRONTMAN_PROGRESS_QUEST_GROUP_TPL = FRONTMAN_PROGRESS_QUEST_PREFIX_TPL + ':progress'
FRONTMAN_PROGRESS_POINTS_TOKEN_TPL = FRONTMAN_PROGRESS_QUEST_PREFIX_TPL + '_event_points'

class EventShop(object):

    class CurrencyType(IntEnum):
        REAL = 0
        VIRTUAL = 1

    class PriceType(IntEnum):
        SINGLE = 0
        MULTI = 1
        OPTIONAL = 2

    PURCHASES_COUNTER_TOKEN_TTL = 2160
    PURCHASES_COUNTER_TOKEN_SUFFIX = ':purchased'
    PURCHASES_COUNTER_TOKEN_LIMIT = 10000

    @classmethod
    def getBundlePurchaseCounterTokenName(cls, bundleID):
        return bundleID + cls.PURCHASES_COUNTER_TOKEN_SUFFIX


class GoalState(IntEnum):
    ACTIVE = 0
    WIN = 1
    LOSE = 2


class GoalBossId(Enum):
    ONE = 'ATT_goal_final_one_boss'
    FEW = 'ATT_goal_final_few_boss'


class VehicleRole(IntEnum):
    regular = 0
    elite = 1
    boss = 2
    aimer = 3
    runner = 4

    def hasUniqueIcon(self):
        return self in [VehicleRole.aimer, VehicleRole.runner, VehicleRole.boss]


class AttackDirectionMarker(IntEnum):
    Arrow = 0
    ArrowBT = 1
    ArrowTB = 2


class FrontmanRoleID(IntEnum):
    ENGINEER = 1
    AVIATION = 2
    ARTILLERY = 3


class BattleResultType(Enum):
    VICTORY = 'victory'
    DEFEAT = 'defeat'
    DRAW = 'draw'


class BoosterType(Enum):
    EMPTY = 'empty'
    X5 = 'x5'
    X10 = 'x10'
    X15 = 'x15'


class AccountSettingsKeys(object):
    EXPIRE_DATE_ACCOUNT_SETTINGS = 'expireDateAccountSettings'
    EVENT_KEY = 'hb_keys'
    HISTORICAL_BATTLES_FRONTS = 'fronts'
    HISTORICAL_BATTLES_INFO_WINDOWS = 'infoWindows'
    SELECTED_HISTORICAL_BATTLES_FRONT = 'selectedHistoricalBattlesFront'
    SEEN_HISTORICAL_BATTLES_FRONTS = 'seenHistoricalBattlesFronts'
    SEEN_HISTORICAL_BATTLES_SHOP = 'seenHistoricalBattlesShop'
    SEEN_historical_battles_POINTS = 'seenHistoricalBattlesProgressionPoints'
    SELECTED_HISTORICAL_BATTLES_FRONTMEN = 'selectedHistoricalBattlesFrontmen'
    FRONTMEN_SELECTED_VEHICLE = 'frontmenSelectedVehicle'
    FRONTMEN_PREVIOUS_PROGRESS = 'frontmenPreviousProgress'
    FRONT_COUPONS_VIEWED = 'frontCouponsViewed'
    VIEWED_VEHICLES = 'viewedVehicles'
    MAP_LOADING_VOICEOVER_DATESTAMPS = 'mapLoadingVoiceoverTimestamp'
    PROGRESSION_MUSIC_INTRO_DATESTAMP = 'progressionMusicIntroDatestamp'
    PROGRESSION_MUSIC_OUTRO_DATESTAMP = 'progressionMusicOutroDatestamp'
    PROGRESSION_INTRO_PLAYED_ON_ACCOUNT = 'progressionIntroPlayedOnAccount'


ACCOUNT_DEFAULT_SETTINGS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS: {AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONT: 0,
                                                                                 AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_FRONTS: {},
                                                                                 AccountSettingsKeys.SEEN_historical_battles_POINTS: 0},
                                 AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONTMEN: {},
                                 AccountSettingsKeys.FRONTMEN_SELECTED_VEHICLE: {},
                                 AccountSettingsKeys.FRONTMEN_PREVIOUS_PROGRESS: {},
                                 AccountSettingsKeys.HISTORICAL_BATTLES_INFO_WINDOWS: {},
                                 AccountSettingsKeys.FRONT_COUPONS_VIEWED: {},
                                 AccountSettingsKeys.EXPIRE_DATE_ACCOUNT_SETTINGS: 0,
                                 AccountSettingsKeys.VIEWED_VEHICLES: {},
                                 AccountSettingsKeys.MAP_LOADING_VOICEOVER_DATESTAMPS: {},
                                 AccountSettingsKeys.PROGRESSION_MUSIC_INTRO_DATESTAMP: 0,
                                 AccountSettingsKeys.PROGRESSION_MUSIC_OUTRO_DATESTAMP: 0,
                                 AccountSettingsKeys.PROGRESSION_INTRO_PLAYED_ON_ACCOUNT: False}}
DEFAULT_NOTIFICATIONS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_SHOP: False}}
BADGE_QUEST_ID = 'hb22_badge'
