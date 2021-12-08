# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_constants.py
from items.components.ny_constants import CurrentNYConstants, CustomizationObjects, PREV_NY_TOYS_COLLECTIONS, YEARS
from shared_utils import CONST_CONTAINER

class AnchorNames(CONST_CONTAINER):
    TREE = 'ChristmasTree'
    FIELD_KITCHEN = 'FieldKitchen'
    SCULPTURE = 'SnowSculpture'
    ILLUMINATION = 'OuterTreesIllumination'
    CELEBRITY = 'Celebrity'
    MEGAZONE = 'Megazone'
    HEROTANK = 'HeroTank'
    CELEBRITY_COMPLETED = 'CelebrityCompleted'


class AdditionalCameraObject(CONST_CONTAINER):
    CELEBRITY = 'Celebrity'


ANCHOR_TO_OBJECT = {AnchorNames.TREE: CustomizationObjects.FIR,
 AnchorNames.FIELD_KITCHEN: CustomizationObjects.FAIR,
 AnchorNames.SCULPTURE: CustomizationObjects.INSTALLATION,
 AnchorNames.MEGAZONE: CustomizationObjects.MEGAZONE,
 AnchorNames.CELEBRITY: AdditionalCameraObject.CELEBRITY}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
NY_LEVEL_PREFIX = 'ny22:level'
NY_GIFT_SYSTEM_TOKEN_PREFIX = 'ny22:giftSystem:'
NY_GIFT_SYSTEM_SUBPROGRESS_TOKEN = NY_GIFT_SYSTEM_TOKEN_PREFIX + 'subprogress'
NY_GIFT_SYSTEM_PROGRESSION_TOKEN = NY_GIFT_SYSTEM_TOKEN_PREFIX + 'progression'
NY_GIFT_SYSTEM_SUBPROGRESS_PREFIX = NY_GIFT_SYSTEM_SUBPROGRESS_TOKEN
NY_GIFT_SYSTEM_PROGRESSION_PREFIX = NY_GIFT_SYSTEM_PROGRESSION_TOKEN
TOY_COLLECTIONS = PREV_NY_TOYS_COLLECTIONS + (CurrentNYConstants.TOYS,)
NY_FILTER = 'newYear'
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr', 'ny21:cr', 'ny22:cr')
NY_COLLECTION_MEGA_PREFIX = 'ny22:cr:mega'
NY_OLD_COLLECTION_PREFIX = 'ny18:cr'
TANK_SLOT_BONUS_ORDER = ['xpFactor', 'tankmenXPFactor', 'freeXPFactor']

class Collections(CONST_CONTAINER):
    NewYear22 = YEARS.getYearStrFromYearNum(22)
    NewYear21 = YEARS.getYearStrFromYearNum(21)
    NewYear20 = YEARS.getYearStrFromYearNum(20)
    NewYear19 = YEARS.getYearStrFromYearNum(19)
    NewYear18 = YEARS.getYearStrFromYearNum(18)


class SyncDataKeys(CONST_CONTAINER):
    INVENTORY_TOYS = 'inventoryToys'
    SLOTS = 'slots'
    TOY_FRAGMENTS = 'toyFragments'
    LEVEL = 'level'
    POINTS = 'atmospherePoints'
    TOY_COLLECTION = 'toyCollection'
    COLLECTION_DISTRIBUTIONS = 'collectionDistributions'
    ALBUMS = 'albums'
    FILLERS = 'fillers'
    VEHICLE_BRANCH = 'vehicleBranch'
    VEHICLE_COOLDOWN = 'cooldowns'
    VEHICLE_BONUS_CHOICES = 'bonusChoices'
    MAX_BONUS = 'maxReachedSettingBonus'
    MAX_BONUS_VALUE = 'value'
    MAX_BONUS_INFO = 'info'
    SELECTED_DISCOUNTS = 'selectedDiscounts'
    PURE_SLOTS = 'pureSlots'


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
    GIFT_SYSTEM = 'gift'
    VEHICLES = 'vehicles'
    CHALLENGE = 'challenge'
    LEFT = (GLADE,
     CHALLENGE,
     GIFT_SYSTEM,
     VEHICLES)
    RIGHT = (SHARDS,
     DECORATIONS,
     COLLECTIONS,
     REWARDS)
    ALL = LEFT + RIGHT
    ACTIVE = (GLADE,
     CHALLENGE,
     VEHICLES,
     SHARDS,
     DECORATIONS,
     COLLECTIONS,
     REWARDS)
    ALTERNATIVE = (GLADE,
     CHALLENGE,
     SHARDS,
     DECORATIONS,
     COLLECTIONS,
     REWARDS)


class NyTabBarMainView(object):
    FIR = CustomizationObjects.FIR
    FAIR = CustomizationObjects.FAIR
    INSTALLATION = CustomizationObjects.INSTALLATION
    MEGAZONE = CustomizationObjects.MEGAZONE
    ALL = (FIR,
     FAIR,
     INSTALLATION,
     MEGAZONE)


class NyTabBarRewardsView(object):
    FOR_LEVELS = 'forLevels'
    COLLECTION_NY18 = Collections.NewYear18
    COLLECTION_NY19 = Collections.NewYear19
    COLLECTION_NY20 = Collections.NewYear20
    COLLECTION_NY21 = Collections.NewYear21
    COLLECTION_NY22 = Collections.NewYear22
    COLLECTIONS = (COLLECTION_NY22,
     COLLECTION_NY21,
     COLLECTION_NY20,
     COLLECTION_NY19,
     COLLECTION_NY18)
    ALL = (FOR_LEVELS,) + COLLECTIONS


class NyTabBarAlbumsView(object):
    NY_2018 = Collections.NewYear18
    NY_2019 = Collections.NewYear19
    NY_2020 = Collections.NewYear20
    NY_2021 = Collections.NewYear21
    NY_2022 = Collections.NewYear22
    ALL = (NY_2022,
     NY_2021,
     NY_2020,
     NY_2019,
     NY_2018)


class NyBonusNames(CONST_CONTAINER):
    ALBUM_ACCESS = 'newYearAlbumsAccess'
    VEHICLE_SLOT = 'newYearSlot'


PERCENT = 100
