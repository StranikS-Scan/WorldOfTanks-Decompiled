# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/ny_constants.py
import itertools
from enum import Enum
from new_year_common.items.components.ny_constants import CurrentNYConstants, CustomizationObjects, PREV_NY_TOYS_COLLECTIONS, YEARS, YEARS_INFO, ToyTypes
from shared_utils import CONST_CONTAINER

class NewYearLootBoxes(CONST_CONTAINER):
    PREMIUM_OLD = 'newYear_premium'
    SPECIAL_OLD = 'newYear_special'
    SPECIAL_AUTO = 'newYear_special_auto'
    COMMON_OLD = 'newYear_usual'
    NY_24_STANDARD = 'ny_2024_VI'
    NY_24_NEW_YEAR = 'ny_2024_newyear'
    NY_24_XMAS = 'ny_2024_christmas'
    NY_24_EASTERN = 'ny_2024_eastern'
    NY_24_MAGIC = 'ny_2024_magic'
    NY_25_SMALL = 'ny_2025_small'
    NY_25_TANKS = 'ny_2025_tanks'
    NY_25_BIG = 'ny_2025_big'
    NY_CUR_YEAR_SMALL = 'ny_{}_small'.format(YEARS_INFO.CURRENT_YEAR_FULL)
    NY_CUR_YEAR_TANKS = 'ny_{}_tanks'.format(YEARS_INFO.CURRENT_YEAR_FULL)
    NY_CUR_YEAR_BIG = 'ny_{}_big'.format(YEARS_INFO.CURRENT_YEAR_FULL)
    PREMIUM = (PREMIUM_OLD,
     NY_24_NEW_YEAR,
     NY_24_XMAS,
     NY_24_EASTERN,
     NY_24_MAGIC)
    COMMON = (COMMON_OLD, NY_24_STANDARD)
    SPECIAL = (SPECIAL_OLD, SPECIAL_AUTO)

    @classmethod
    def getIterator(cls):
        return itertools.chain(cls.PREMIUM, cls.COMMON, cls.SPECIAL)

    @classmethod
    def ALL(cls):
        return tuple(cls.getIterator())


class NewYearLootBoxRewards(object):
    NY_CUR_YEAR_TANKS = 'ny_2026_tanks'.format(YEARS_INFO.CURRENT_YEAR)
    MAIN_TANK = 'A175_OTAC_MT_58_02'
    LEGENDARY_TANKS = ('Cz14_Skoda_T_56', 'F116_Bat_Chatillon_Bourrasque', 'F106_Panhard_EBR_75_Mle1954', 'It13_Progetto_M35_mod_46', 'F97_ELC_EVEN_90', 'GB99_Turtle_Mk1')
    STYLES = {'GB134_FV242B_Condor': '3dstyle_01',
     'Un02_Merkava_LP': '3dstyle_02',
     'A38_T92': '3dstyle_03',
     'GB83_FV4005': '3dstyle_04',
     'G72_JagdPz_E100': '3dstyle_05'}
    REWARDS = {NY_CUR_YEAR_TANKS: 'legendary',
     MAIN_TANK: 'tank_main'}
    LEGENDARY_REWARDS = {vehicleName:'tank_legendary' for vehicleName in LEGENDARY_TANKS}
    ALL = {}
    for rewards in (REWARDS, LEGENDARY_REWARDS, STYLES):
        ALL.update(rewards)


class NewYearCategories(CONST_CONTAINER):
    NEWYEAR_24 = 'ny_2024'
    NEWYEAR_25 = 'ny_2025'
    NEWYEAR_26 = 'ny_2026'


ALL_LUNAR_NY_LOOT_BOX_TYPES = ('lunar_base', 'lunar_simple', 'lunar_special')
LUNAR_NY_LOOT_BOXES_CATEGORIES = 'LunarNY'

class AnchorNames(CONST_CONTAINER):
    SNOW_SCULPTURE = 'SnowSculpture'
    TREE = 'ChristmasTree'
    TEREM = 'Terem'
    SNOW_SLIDE = 'SnowSlide'
    FIELD_KITCHEN = 'FieldKitchen'
    FIREWORKS = 'Fireworks'
    HEROTANK = 'HeroTank'
    LEVEL_UP_CAMERA = 'LevelUpCamera'
    CHALLENGE = 'Challenge'
    RACCOON = 'Raccoon'
    MACHINE = 'Machine'


class InternalViewState(CONST_CONTAINER):
    DEFAULT = ''
    TREE = 'ChristmasTree'
    TREE_TOP = 'ChristmasTree_Top'
    TREE_DOWN = 'ChristmasTree_Toy_Down'
    FIELD_KITCHEN = 'FieldKitchen'
    TEREM = 'Terem'
    SNOW_SLIDE = 'SnowSlide'
    SNOW_SCULPTURE = 'SnowSculpture'
    FIREWORKS = 'Fireworks'
    MACHINE_MAIN = 'MachineMain'
    BUY_MACHINE_COIN = 'BuyMachineCoin'
    MACHINE_REWARDING = 'MachineRewarding'
    VEHICLE_MACHINE_REWARDING = 'VehicleMachineRewarding'
    CHALLENGE = 'Challenge'
    RACCOON = 'Raccoon'
    RACCOON_FLY = 'Raccoon_fly'
    ONBOARDING_DEFAULT = 'onboarding_default'
    ONBOARDING_FIR = 'onboarding_fir'
    ONBOARDING_PANORAMA = 'onboarding_panorama'


class InternalViewStateID(object):
    DEFAULT = 0
    TREE = 1
    FIELD_KITCHEN = 2
    TEREM = 3
    SNOW_SLIDE = 4
    SNOW_SCULPTURE = 5
    FIREWORKS = 6
    MACHINE_MAIN = 7
    BUY_MACHINE_COIN = 8
    MACHINE_REWARDING = 9
    VEHICLE_MACHINE_REWARDING = 10
    CHALLENGE = 11
    RACCOON = 12

    @classmethod
    def stateToID(cls, name, default=None):
        stateKey = InternalViewState.getKeyByValue(name)
        return getattr(cls, stateKey, default)


ANCHOR_TO_OBJECT = {AnchorNames.SNOW_SCULPTURE: CustomizationObjects.INSTALLATIONS,
 AnchorNames.TREE: CustomizationObjects.FIR,
 AnchorNames.TEREM: CustomizationObjects.TEREM,
 AnchorNames.SNOW_SLIDE: CustomizationObjects.SNOW_SLIDE,
 AnchorNames.FIELD_KITCHEN: CustomizationObjects.FAIR,
 AnchorNames.FIREWORKS: CustomizationObjects.FIREWORKS}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
OBJECT_TO_VIEW_SATE = {CustomizationObjects.FIR: InternalViewState.TREE,
 CustomizationObjects.FAIR: InternalViewState.FIELD_KITCHEN,
 CustomizationObjects.INSTALLATIONS: InternalViewState.SNOW_SCULPTURE,
 CustomizationObjects.TEREM: InternalViewState.TEREM,
 CustomizationObjects.SNOW_SLIDE: InternalViewState.SNOW_SLIDE,
 CustomizationObjects.FIREWORKS: InternalViewState.FIREWORKS}
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
NY_LEVEL_PREFIX = 'ny{}:level'.format(YEARS_INFO.CURRENT_YEAR)
TOY_COLLECTIONS = PREV_NY_TOYS_COLLECTIONS + [CurrentNYConstants.TOYS]
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr', 'ny21:cr', 'ny22:cr', 'ny23:cr', 'ny24:cr')
NY_COLLECTION_MEGA_PREFIX = 'ny22:cr:mega'
NY_OLD_COLLECTION_PREFIX = 'ny18:cr'
NY_MARKETPLACE_UNLOCK_ENTITLEMENT = 'ny{}_marketplace_unlock'.format(YEARS_INFO.CURRENT_YEAR)
TANK_SLOT_BONUS_ORDER = ['xpFactor', 'tankmenXPFactor', 'freeXPFactor']
NY_TUTORIAL_NOTIFICATION_LOCK_KEY = 'nyTutorial'
NY_INVOICE_TAG_PREFIX = 'ny{}'.format(YEARS_INFO.CURRENT_YEAR)
NY_INVOICE_LEADERBOARD_REWARD_PREFIX = '{}_leaderboard_'.format(NY_INVOICE_TAG_PREFIX)

class Collections(CONST_CONTAINER):
    NewYear26 = YEARS.getYearStrFromYearNum(26)
    NewYear25 = YEARS.getYearStrFromYearNum(25)
    NewYear24 = YEARS.getYearStrFromYearNum(24)
    NewYear23 = YEARS.getYearStrFromYearNum(23)
    NewYear22 = YEARS.getYearStrFromYearNum(22)
    NewYear21 = YEARS.getYearStrFromYearNum(21)
    NewYear20 = YEARS.getYearStrFromYearNum(20)
    NewYear19 = YEARS.getYearStrFromYearNum(19)
    NewYear18 = YEARS.getYearStrFromYearNum(18)
    CURRENT = YEARS.getYearStrFromYearNum(YEARS_INFO.CURRENT_YEAR)


class SyncDataKeys(CONST_CONTAINER):
    INVENTORY_TOYS = 'inventoryToys'
    SLOTS = 'slots'
    TOY_FRAGMENTS = 'toyFragments'
    MAX_LEVEL = 'maxLevel'
    POINTS = 'atmospherePoints'
    TOY_COLLECTION = 'toyCollection'
    COLLECTION_DISTRIBUTIONS = 'collectionDistributions'
    ALBUMS = 'albums'
    FILLERS = 'fillers'
    MAX_BONUS = 'maxReachedSettingBonus'
    MAX_BONUS_VALUE = 'value'
    MAX_BONUS_INFO = 'info'
    SELECTED_DISCOUNTS = 'selectedDiscounts'


class FormulaInfo(object):
    MULTIPLIER = 0
    COLLECTION_BONUS = 1
    MEGA_TOYS_BONUS = 2


class NyWidgetTopMenu(object):
    CITY = 'city'
    SURPRISE_MACHINE = 'surprise_machine'
    LEADERS = 'leaders'
    PET = 'pet'
    INFO = 'info'
    LEFT = ()
    RIGHT = (CITY,
     PET,
     LEADERS,
     SURPRISE_MACHINE,
     INFO)
    ALL = LEFT + RIGHT


class NyTabBarRewardsView(object):
    FOR_LEVELS = 'forLevels'
    COLLECTION_NY26 = Collections.NewYear26
    COLLECTIONS = (COLLECTION_NY26,)
    ALL = (FOR_LEVELS,) + COLLECTIONS


class NyTabBarAlbumsView(object):
    NY_2026 = Collections.NewYear26
    ALL = (NY_2026,)


PERCENT = 100.0

class ViewAliases(CONST_CONTAINER):
    CITY_VIEW = 'NyCityView'
    QUESTS_VIEW = 'NyQuestView'
    SURPRISE_MACHINE_VIEW = 'NySurpriseMachineView'
    REWARDS_VIEW = 'NyRewardsInfoView'
    PET_VIEW = 'NyPetView'
    INFO_VIEW = 'NyInfoView'
    ONBOARDING_VIEW = 'NyOnboardingView'
    TANK_CUSTOMIZATION = 'Customization'


ANCHOR_TO_VIEW_ALIAS = {AnchorNames.MACHINE: ViewAliases.SURPRISE_MACHINE_VIEW,
 AnchorNames.CHALLENGE: ViewAliases.QUESTS_VIEW,
 AnchorNames.RACCOON: ViewAliases.PET_VIEW}
NEW_YEAR = '{}newYearSettings'.format(YEARS_INFO.CURRENT_YEAR)
NY_LEADERBOARD_INFO_SEEN = 'NyLeaderboardInfoSeen'
NY_CAN_BUY_ZONE = 'NyCanBuyZone'
NY_QUESTS_UPDATED_AT = 'NyQuestsUpdatedAt'
NY_IS_FIRST_MACHINE_TOKEN = 'NyIsFirstMachineToken'
NY_IS_QUESTS_INTRO_SHOWED = 'NyIsQuestsIntroShowed'
NY_DAILY_QUESTS_VISITED = 'NYDailyQuestsVisited'
NY_OLD_COLLECTIONS_BY_YEAR_VISITED = 'NYOldCollectionsByYearVisited'
NY_OLD_REWARDS_BY_YEAR_VISITED = 'NYOldRewardsByYearVisited'
NY_LAST_SEEN_LEVEL_INFO = 'NYLastSeenLevelInfo'
NY_LAST_SEEN_TOTAL_BONUS = 'NYLastSeenTotalBonus'
NY_ACTIVE_WIDGET_TRANSITION_SHOWN = 'NyActiveWidgetTransitionShown'
NY_GREETINGS_SEEN = 'NYGreetingsSeen'
NY_ENVIRONMENT_STATE = 'NYEnvironmentState'
NY_ENV_SWITCHER_BTN_TIP_SKIPPED = 'NYSwitcherBtnTipSkipped'
NY_HAS_PET_ANIMATION = 'NYHasPetAnimation'
NY_IS_CELEB_VOICEOVERS_ENABLED = 'NyIsCelebVoiceoversEnabled'
NY_WEEK_IN_QUESTS_VISITED = 'NyWeekInQuestsVisited'
NY_IS_LEADERBOARD_REWARDS_CHECKED = 'NyIsLeaderboardRewardsChecked'
NY_IS_SECRET_REWARDS_CHECKED = 'NyIsSecretRewardsChecked'
NY_BIG_BOX_COUNT = 'NyBigBoxCount'
NY_SEEN_QUESTS = 'NySeenQuests'
NY_TAMAGOTCHI_SEEN_TIPS = 'nyTamagotchiSeenTips'
NY_TAMAGOTCHI_STORY_TIP = 'NyTipLastStoryIdTamagotchi'
NY_TAMAGOTCHI_STORY_BUBLE = 'NyBubbleLastStoryIdTamagotchi'
ACCOUNT_DEFAULT_SETTINGS = {NEW_YEAR: {NY_CAN_BUY_ZONE: {customizationZone:False for customizationZone in CustomizationObjects.ALL},
            NY_QUESTS_UPDATED_AT: 0,
            NY_IS_FIRST_MACHINE_TOKEN: False,
            NY_IS_QUESTS_INTRO_SHOWED: False,
            NY_LEADERBOARD_INFO_SEEN: False,
            NY_DAILY_QUESTS_VISITED: False,
            NY_OLD_COLLECTIONS_BY_YEAR_VISITED: {18: False,
                                                 19: False,
                                                 20: False,
                                                 21: False,
                                                 22: False,
                                                 23: False,
                                                 24: False},
            NY_OLD_REWARDS_BY_YEAR_VISITED: {18: False,
                                             19: False,
                                             20: False,
                                             21: False,
                                             22: False,
                                             23: False,
                                             24: False},
            NY_LAST_SEEN_LEVEL_INFO: {'level': 1,
                                      'points': 0},
            NY_SEEN_QUESTS: list(),
            NY_LAST_SEEN_TOTAL_BONUS: 0,
            NY_ACTIVE_WIDGET_TRANSITION_SHOWN: False,
            NY_GREETINGS_SEEN: False,
            NY_ENV_SWITCHER_BTN_TIP_SKIPPED: False,
            NY_HAS_PET_ANIMATION: True,
            NY_IS_CELEB_VOICEOVERS_ENABLED: True,
            NY_WEEK_IN_QUESTS_VISITED: 0,
            NY_ENVIRONMENT_STATE: None,
            NY_IS_LEADERBOARD_REWARDS_CHECKED: False,
            NY_IS_SECRET_REWARDS_CHECKED: False,
            NY_BIG_BOX_COUNT: 0,
            NY_TAMAGOTCHI_SEEN_TIPS: set(),
            NY_TAMAGOTCHI_STORY_TIP: 1,
            NY_TAMAGOTCHI_STORY_BUBLE: 1}}

class NyBtnTypes(object):
    PUSH = 'Push'
    LEFT = 'Left'
    RIGHT = 'Right'


class NySurpriseMachineStates(object):
    MACHINE = 'Machine'
    BUTTONS = 'Buttons'


TOY_TO_CAMERA = {ToyTypes.TOP: InternalViewState.TREE_TOP,
 ToyTypes.GARLAND_FIR: InternalViewState.TREE,
 ToyTypes.BALL: InternalViewState.TREE,
 ToyTypes.FLOOR: InternalViewState.TREE_DOWN}

class TamagotchiState(Enum):
    SAD = 'sad'
    NORMAL = 'normal'
    FUN = 'fun'
