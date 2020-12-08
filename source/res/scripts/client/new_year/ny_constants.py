# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_constants.py
from items.components.ny_constants import CustomizationObjects, YEARS, TOY_TYPES_BY_OBJECT, ToyTypes, CurrentNYConstants, PREV_NY_TOYS_COLLECTIONS
from shared_utils import CONST_CONTAINER

class AnchorNames(CONST_CONTAINER):
    TREE = 'ChristmasTree'
    FIELD_KITCHEN = 'FieldKitchen'
    SCULPTURE = 'SnowSculpture'
    ILLUMINATION = 'OuterTreesIllumination'
    MASCOT = 'Mascot'
    CELEBRITY = 'Celebrity'
    CELEBRITY_COMPLETED = 'CelebrityCompleted'


class AdditionalCameraObject(CONST_CONTAINER):
    MASCOT = 'Mascot'
    CELEBRITY = 'Celebrity'


ANCHOR_TO_OBJECT = {AnchorNames.TREE: CustomizationObjects.FIR,
 AnchorNames.FIELD_KITCHEN: CustomizationObjects.TABLEFUL,
 AnchorNames.SCULPTURE: CustomizationObjects.INSTALLATION,
 AnchorNames.ILLUMINATION: CustomizationObjects.ILLUMINATION,
 AnchorNames.MASCOT: AdditionalCameraObject.MASCOT,
 AnchorNames.CELEBRITY: AdditionalCameraObject.CELEBRITY}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
NY_LEVEL_PREFIX = 'ny21:level'
TOY_COLLECTIONS = PREV_NY_TOYS_COLLECTIONS + (CurrentNYConstants.TOYS,)
NY_FILTER = 'newYear'
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr', 'ny21:cr')

class Collections(CONST_CONTAINER):
    NewYear21 = YEARS.getYearStrFromYearNum(21)
    NewYear20 = YEARS.getYearStrFromYearNum(20)
    NewYear19 = YEARS.getYearStrFromYearNum(19)
    NewYear18 = YEARS.getYearStrFromYearNum(18)


class SyncDataKeys(CONST_CONTAINER):
    INVENTORY_TOYS = 'inventoryToys'
    SLOTS = 'slots'
    TOY_FRAGMENTS = 'toyFragments'
    LEVEL = 'level'
    TOY_COLLECTION = 'toyCollection'
    COLLECTION_DISTRIBUTIONS = 'collectionDistributions'
    ALBUMS = 'albums'
    TALISMANS = 'talismans'
    TALISMAN_TOY_TAKEN = 'wasTalismanBonusTaken'
    FILLERS = 'fillers'
    VEHICLE_BRANCH = 'vehicleBranch'
    VEHICLE_COOLDOWN = 'cooldowns'
    VEHICLE_BONUS_CHOICES = 'bonusChoices'
    MAX_BONUS = 'maxReachedSettingBonus'
    MAX_BONUS_VALUE = 'value'
    MAX_BONUS_INFO = 'info'
    SELECTED_DISCOUNTS = 'selectedDiscounts'
    TALISMANS_SEQUENCE_STAGE = 'talismansSequenceStage'


class FormulaInfo(object):
    MULTIPLIER = 0
    COLLECTION_BONUS = 1
    MEGA_TOYS_BONUS = 2


class NyWidgetTopMenu(object):
    GLADE = 'glade'
    REWARDS = 'rewards'
    INFO = 'info'
    DECORATIONS = 'decorations'
    SHARDS = 'shards'
    COLLECTIONS = 'collections'
    LEFT = (GLADE, DECORATIONS, SHARDS)
    RIGHT = (COLLECTIONS, REWARDS, INFO)
    ALL = LEFT + RIGHT


class NyTabBarMainView(object):
    FIR = CustomizationObjects.FIR
    TABLEFUL = CustomizationObjects.TABLEFUL
    INSTALLATION = CustomizationObjects.INSTALLATION
    ILLUMINATION = CustomizationObjects.ILLUMINATION
    MASCOT = AdditionalCameraObject.MASCOT
    CELEBRITY = AdditionalCameraObject.CELEBRITY
    ALL = (FIR,
     TABLEFUL,
     INSTALLATION,
     ILLUMINATION,
     MASCOT,
     CELEBRITY)


class NyTabBarRewardsView(object):
    FOR_LEVELS = 'forLevels'
    COLLECTION_NY18 = Collections.NewYear18
    COLLECTION_NY19 = Collections.NewYear19
    COLLECTION_NY20 = Collections.NewYear20
    COLLECTION_NY21 = Collections.NewYear21
    ALL = (FOR_LEVELS,
     COLLECTION_NY21,
     COLLECTION_NY20,
     COLLECTION_NY19,
     COLLECTION_NY18)


class NyTabBarAlbumsView(object):
    NY_2018 = Collections.NewYear18
    NY_2019 = Collections.NewYear19
    NY_2020 = Collections.NewYear20
    NY_2021 = Collections.NewYear21
    ALL = (NY_2021,
     NY_2020,
     NY_2019,
     NY_2018)


TOY_TYPES_BY_OBJECT_WITHOUT_MEGA = {}
for custObj, toys in TOY_TYPES_BY_OBJECT.iteritems():
    toysWithoutMega = [ toy for toy in toys if toy not in ToyTypes.MEGA ]
    TOY_TYPES_BY_OBJECT_WITHOUT_MEGA[custObj] = tuple(toysWithoutMega)

TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA = []
for custObj in CustomizationObjects.ALL:
    for toyType in TOY_TYPES_BY_OBJECT_WITHOUT_MEGA[custObj]:
        TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA.append(toyType)

TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA = tuple(TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA)
PERCENT = 100
