# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_constants.py
from items.components.ny_constants import CurrentNYConstants, CustomizationObjects, PREV_NY_TOYS_COLLECTIONS, YEARS, YEARS_INFO
from shared_utils import CONST_CONTAINER

class AnchorNames(CONST_CONTAINER):
    TREE = 'ChristmasTree'
    FIELD_KITCHEN = 'FieldKitchen'
    SCULPTURE = 'SnowSculpture'
    ILLUMINATION = 'OuterTreesIllumination'
    MEGAZONE = 'Megazone'
    HEROTANK = 'HeroTank'
    LEVEL_UP_CAMERA = 'LevelUpCamera'


ANCHOR_TO_OBJECT = {AnchorNames.TREE: CustomizationObjects.FIR}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
NY_LEVEL_PREFIX = 'ny{}:level'.format(YEARS_INFO.CURRENT_YEAR)
TOY_COLLECTIONS = PREV_NY_TOYS_COLLECTIONS + [CurrentNYConstants.TOYS]
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr', 'ny21:cr', 'ny22:cr', 'ny23:cr', 'ny24:cr')
NY_COLLECTION_MEGA_PREFIX = 'ny22:cr:mega'
NY_OLD_COLLECTION_PREFIX = 'ny18:cr'
NY_MARKETPLACE_UNLOCK_ENTITLEMENT = 'ny24_marketplace_unlock'
TANK_SLOT_BONUS_ORDER = ['xpFactor', 'tankmenXPFactor', 'freeXPFactor']
NY_TUTORIAL_NOTIFICATION_LOCK_KEY = 'nyTutorial'

class Collections(CONST_CONTAINER):
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
    INFO = 'info'
    GLADE = 'glade'
    REWARDS = 'rewards'
    DECORATIONS = 'decorations'
    SHARDS = 'shards'
    COLLECTIONS = 'collections'
    LEFT = (GLADE, DECORATIONS, SHARDS)
    RIGHT = (COLLECTIONS, REWARDS, INFO)
    ALL = LEFT + RIGHT


class NyTabBarMainView(object):
    FIR = CustomizationObjects.FIR
    ALL = (FIR,)


class NyTabBarRewardsView(object):
    FOR_LEVELS = 'forLevels'
    COLLECTION_NY24 = Collections.NewYear24
    COLLECTIONS = (COLLECTION_NY24,)
    ALL = (FOR_LEVELS,) + COLLECTIONS


class NyTabBarAlbumsView(object):
    NY_2024 = Collections.NewYear24
    ALL = (NY_2024,)


PERCENT = 100
