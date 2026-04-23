# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/hb_constants.py
from enum import IntEnum, Enum
from constants import FAIRPLAY_VIOLATIONS
HB_GAME_PARAMS_KEY = 'historical_battles'
HB_SHOP_GAME_PARAMS_KEY = 'historical_battles_shop'
HB_FRONT_COUPONS_GAME_PARAMS_KEY = 'historical_battles_front_coupons'
HB_DIVISION_UPGRADE_OFFER_PARAMS_KEY = 'historical_battles_division_upgrade_offer'
HB_COINS_GAME_PARAMS_KEY = 'hb_coins'
HB_BATTLES_PARAMS_KEY = 'hb_battle_configs'
HB_BATTLES_ENABLED = 'isBattlesEnabled'
FRONT_COUPON_TOKEN_PREFIX = 'hb_front_coupon_'
FRONT_COUPON_RECHARGE_QUEST_GROUP_ID = FRONT_COUPON_TOKEN_PREFIX + 'recharge'
HB_BATTLE_QUESTS_PREFIX = 'HBBattleQuest'
HB_SEASON_NAME = 'HB2026'

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


class GoalId(Enum):
    OFFENCE_MAIN = 'ATT_goal_main'
    OFFENCE_COUNTER_ATTACKER = 'ATT_goal_counter_attack'
    BOSS = 'ATT_goal_final_boss'
    BOSS_ONE = 'ATT_goal_final_one_boss'
    BOSS_FEW = 'ATT_goal_final_few_boss'
    DEFENCE_SPG = 'SPG_def'
    DEFENCE_COUNTER_ATTACK = 'def_counter_attack'


class GoalState(IntEnum):
    ACTIVE = 0
    WIN = 1
    LOSE = 2


class GoalSubState(Enum):
    EMPTY = ''
    LOSE_TIME_ENDED = 'time_ended'
    LOSE_TEAM_KILLED = 'team_killed'


class GoalType(IntEnum):
    ENEMY_EXTERMINATION = 0
    BOSS_EXTERMINATION = 1
    SURVIVAL = 2


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


class BattleResultType(Enum):
    VICTORY = 'victory'
    DEFEAT = 'defeat'
    DRAW = 'draw'


class FrontType(IntEnum):
    OFFENCE = 0
    DEFENCE = 1


class AccountSettingsKeys(object):
    EXPIRE_DATE_ACCOUNT_SETTINGS = 'expireDateAccountSettings'
    EVENT_KEY = 'hb_keys'
    HISTORICAL_BATTLES_FRONTS = 'fronts'
    HISTORICAL_BATTLES_INFO_WINDOWS = 'infoWindows'
    SELECTED_HISTORICAL_BATTLES_FRONT = 'selectedHistoricalBattlesFront'
    SEEN_HISTORICAL_BATTLES_FRONTS = 'seenHistoricalBattlesFronts'
    SEEN_HISTORICAL_BATTLES_SHOP = 'seenHistoricalBattlesShop'
    SEEN_historical_battles_POINTS = 'seenHistoricalBattlesProgressionPoints'
    SEEN_HISTORICAL_BATTLES_ORDERS = 'seenHistoricalBattlesOrdersInfo'
    SELECTED_HB_DIVISION = 'selectedHBDivision'
    FRONTMEN_SELECTED_VEHICLE = 'frontmenSelectedVehicle'
    FRONTMEN_PREVIOUS_PROGRESS = 'frontmenPreviousProgress'
    FRONT_COUPONS_VIEWED = 'frontCouponsViewed'
    VIEWED_VEHICLES = 'viewedVehicles'
    MAP_LOADING_VOICEOVER_DATESTAMPS = 'mapLoadingVoiceoverTimestamp'
    LAST_FRONT_ID_IN_AWARDS = 'lastFrontIdInAwards'
    HB_MODE_SELECTOR_BATTLE_PASS_SHOWN = 'HistoricalBattlesModeSelectorBattlePassShown'
    HISTORICAL_BATTLES_VIEWED = 'historicalBattlesViewed'


ACCOUNT_DEFAULT_SETTINGS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS: {AccountSettingsKeys.SELECTED_HISTORICAL_BATTLES_FRONT: FrontType.DEFENCE.value,
                                                                                 AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_FRONTS: {},
                                                                                 AccountSettingsKeys.SEEN_historical_battles_POINTS: 0},
                                 AccountSettingsKeys.SELECTED_HB_DIVISION: {},
                                 AccountSettingsKeys.FRONTMEN_SELECTED_VEHICLE: {},
                                 AccountSettingsKeys.FRONTMEN_PREVIOUS_PROGRESS: {},
                                 AccountSettingsKeys.HISTORICAL_BATTLES_INFO_WINDOWS: {},
                                 AccountSettingsKeys.FRONT_COUPONS_VIEWED: {},
                                 AccountSettingsKeys.EXPIRE_DATE_ACCOUNT_SETTINGS: 0,
                                 AccountSettingsKeys.VIEWED_VEHICLES: {},
                                 AccountSettingsKeys.MAP_LOADING_VOICEOVER_DATESTAMPS: {},
                                 AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_ORDERS: False,
                                 AccountSettingsKeys.LAST_FRONT_ID_IN_AWARDS: 0,
                                 AccountSettingsKeys.HB_MODE_SELECTOR_BATTLE_PASS_SHOWN: None,
                                 AccountSettingsKeys.HISTORICAL_BATTLES_VIEWED: False}}
DEFAULT_NOTIFICATIONS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_SHOP: False}}
HB_VIOLATIONS = (FAIRPLAY_VIOLATIONS.HB_AFK, FAIRPLAY_VIOLATIONS.HB_DESERTER)

class HBTokens(object):
    MAIN_VEHICLE_DISCOUNT = 'historical_battles_main_discount'
    MAIN_VEHICLE_BOUGHT = 'historical_battles_bought'
    MAIN_VEHICLE_DISCOUNT_COMPENSATION = 'historical_battles_main_discount_compensation'


class HBVehicleState(IntEnum):
    DEFAULT = 0
    LAST_STAND = 1


PDATA_KEY_HISTORICAL_BATTLES = 'historicalBattles'

def historicalBattlesInitialData():
    return {'divisionsEXP': {1: 0,
                      2: 0,
                      3: 0,
                      4: 0,
                      5: 0,
                      6: 0}}
