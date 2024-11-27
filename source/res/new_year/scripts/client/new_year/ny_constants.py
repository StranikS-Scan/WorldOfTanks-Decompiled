# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/ny_constants.py
import itertools
from new_year_common.items.components.ny_constants import CurrentNYConstants, CustomizationObjects, PREV_NY_TOYS_COLLECTIONS, YEARS, YEARS_INFO
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
    MAIN_TANK = 'R219_Waffentrager_E100_Gold'
    NY_25_TANKS = 'ny_2025_tanks'
    LEGENDARY_TANKS = ('G36_PzII_J', 'R50_SU76I', 'F69_AMX13_57_100G48_E')
    REWARDS = {MAIN_TANK: 'tank_main',
     NY_25_TANKS: 'lootbox_legendary'}
    LEGENDARY_REWARDS = {vehicleName:'tank_legendary' for vehicleName in LEGENDARY_TANKS}
    ALL = {}
    for rewards in (REWARDS, LEGENDARY_REWARDS):
        ALL.update(rewards)


class NewYearCategories(CONST_CONTAINER):
    NEWYEAR_24 = 'ny_2024'
    NEWYEAR_25 = 'ny_2025'


ALL_LUNAR_NY_LOOT_BOX_TYPES = ('lunar_base', 'lunar_simple', 'lunar_special')
LUNAR_NY_LOOT_BOXES_CATEGORIES = 'LunarNY'

class AnchorNames(CONST_CONTAINER):
    TREE = 'ChristmasTree'
    HEROTANK = 'HeroTank'
    LEVEL_UP_CAMERA = 'LevelUpCamera'
    FIELD_KITCHEN = 'FieldKitchen'
    ILLUMINATION = 'Illumination'
    ATTRACTIONS = 'Attractions'
    SNOW_SCULPTURE = 'SnowSculpture'
    SKATING = 'Skating'
    CHALLENGE = 'Challenge'
    RACCOON = 'Raccoon'
    MACHINE = 'Machine'


class InternalViewState(CONST_CONTAINER):
    DEFAULT = ''
    TREE = 'ChristmasTree'
    FIELD_KITCHEN = 'FieldKitchen'
    ILLUMINATION = 'Illumination'
    ATTRACTIONS = 'Attractions'
    SNOW_SCULPTURE = 'SnowSculpture'
    SKATING = 'Skating'
    PANORAMA_SMALL_WINDOW = 'panoramaSmall'
    MACHINE_MAIN = 'MachineMain'
    BUY_MACHINE_COIN = 'BuyMachineCoin'
    MACHINE_REWARDING = 'MachineRewarding'
    VEHICLE_MACHINE_REWARDING = 'VehicleMachineRewarding'
    CHALLENGE = 'Challenge'
    RACCOON = 'Raccoon'
    ONBOARDING_DEFAULT = 'onboarding_default'
    ONBOARDING_FIR = 'onboarding_fir'
    ONBOARDING_PANORAMA = 'onboarding_panorama'
    ONBOARDING_PANORAMA_SMALL = 'onboarding_panorama_small'


ANCHOR_TO_OBJECT = {AnchorNames.TREE: CustomizationObjects.FIR,
 AnchorNames.FIELD_KITCHEN: CustomizationObjects.FAIR,
 AnchorNames.SNOW_SCULPTURE: CustomizationObjects.INSTALLATIONS,
 AnchorNames.ATTRACTIONS: CustomizationObjects.ATTRACTIONS,
 AnchorNames.ILLUMINATION: CustomizationObjects.LIGHTS,
 AnchorNames.SKATING: CustomizationObjects.SKATING}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
OBJECT_TO_VIEW_SATE = {CustomizationObjects.FIR: InternalViewState.TREE,
 CustomizationObjects.FAIR: InternalViewState.FIELD_KITCHEN,
 CustomizationObjects.INSTALLATIONS: InternalViewState.SNOW_SCULPTURE,
 CustomizationObjects.ATTRACTIONS: InternalViewState.ATTRACTIONS,
 CustomizationObjects.SKATING: InternalViewState.SKATING,
 CustomizationObjects.LIGHTS: InternalViewState.ILLUMINATION}
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
NY_LEVEL_PREFIX = 'ny{}:level'.format(YEARS_INFO.CURRENT_YEAR)
TOY_COLLECTIONS = PREV_NY_TOYS_COLLECTIONS + [CurrentNYConstants.TOYS]
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr', 'ny21:cr', 'ny22:cr', 'ny23:cr', 'ny24:cr')
NY_COLLECTION_MEGA_PREFIX = 'ny22:cr:mega'
NY_OLD_COLLECTION_PREFIX = 'ny18:cr'
NY_MARKETPLACE_UNLOCK_ENTITLEMENT = 'ny25_marketplace_unlock'
TANK_SLOT_BONUS_ORDER = ['xpFactor', 'tankmenXPFactor', 'freeXPFactor']
NY_TUTORIAL_NOTIFICATION_LOCK_KEY = 'nyTutorial'

class Collections(CONST_CONTAINER):
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
    QUESTS = 'quests'
    SURPRISE_MACHINE = 'surprise_machine'
    REWARDS = 'rewards'
    PET = 'pet'
    INFO = 'info'
    LEFT = ()
    RIGHT = (CITY,
     QUESTS,
     SURPRISE_MACHINE,
     REWARDS,
     PET,
     INFO)
    ALL = LEFT + RIGHT
    BUBBLE_NAVIGATION = (CITY,
     QUESTS,
     SURPRISE_MACHINE,
     REWARDS,
     PET)


class NyTabBarRewardsView(object):
    FOR_LEVELS = 'forLevels'
    COLLECTION_NY25 = Collections.NewYear25
    COLLECTIONS = (COLLECTION_NY25,)
    ALL = (FOR_LEVELS,) + COLLECTIONS


class NyTabBarAlbumsView(object):
    NY_2025 = Collections.NewYear24
    ALL = (NY_2025,)


PERCENT = 100

class ViewAliases(CONST_CONTAINER):
    CITY_VIEW = 'NyCityView'
    QUESTS_VIEW = 'NyQuestView'
    SURPRISE_MACHINE_VIEW = 'NySurpriseMachineView'
    REWARDS_VIEW = 'NyRewardsInfoView'
    PET_VIEW = 'NyPetView'
    INFO_VIEW = 'NyInfoView'
    ONBOARDING_VIEW = 'NyOnboardingView'


ANCHOR_TO_VIEW_ALIAS = {AnchorNames.MACHINE: ViewAliases.SURPRISE_MACHINE_VIEW,
 AnchorNames.CHALLENGE: ViewAliases.QUESTS_VIEW,
 AnchorNames.RACCOON: ViewAliases.PET_VIEW}
NEW_YEAR = 'newYearSettings'
NY_SHOW_NAVIGATION_BUBBLE = 'NYShowNavigationBubble'
NY_CAN_BUY_ZONE = 'NyCanBuyZone'
NY_QUESTS_UPDATED_AT = 'NyQuestsUpdatedAt'
NY_IS_FIRST_MACHINE_TOKEN = 'NyIsFirstMachineToken'
ACCOUNT_DEFAULT_SETTINGS = {NEW_YEAR: {NY_SHOW_NAVIGATION_BUBBLE: {navigationTabName:(True if navigationTabName in (NyWidgetTopMenu.PET, NyWidgetTopMenu.QUESTS) else False) for navigationTabName in NyWidgetTopMenu.BUBBLE_NAVIGATION},
            NY_CAN_BUY_ZONE: {customizationZone:False for customizationZone in CustomizationObjects.ALL},
            NY_QUESTS_UPDATED_AT: 0,
            NY_IS_FIRST_MACHINE_TOKEN: False}}
