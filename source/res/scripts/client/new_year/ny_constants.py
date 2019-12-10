# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_constants.py
from items.components.ny_constants import CustomizationObjects, YEARS, TOY_TYPES_BY_OBJECT, ToyTypes
from shared_utils import CONST_CONTAINER

class AnchorNames(CONST_CONTAINER):
    TREE = 'ChristmasTree'
    FIELD_KITCHEN = 'FieldKitchen'
    SCULPTURE = 'SnowSculpture'
    ILLUMINATION = 'OuterTreesIllumination'
    MASCOT = 'Mascot'


class AdditionalCameraObject(CONST_CONTAINER):
    MASCOT = 'Mascot'


ANCHOR_TO_OBJECT = {AnchorNames.TREE: CustomizationObjects.FIR,
 AnchorNames.FIELD_KITCHEN: CustomizationObjects.TABLEFUL,
 AnchorNames.SCULPTURE: CustomizationObjects.INSTALLATION,
 AnchorNames.ILLUMINATION: CustomizationObjects.ILLUMINATION,
 AnchorNames.MASCOT: AdditionalCameraObject.MASCOT}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
CURRENT_NY_TOYS_BONUS = 'ny20Toys'
CURRENT_NY_FRAGMENTS_BONUS = 'ny20ToyFragments'
CURRENT_NY_FILLERS_BONUS = 'ny20Fillers'
NY_LEVEL_PREFIX = 'ny20:level'
TOY_COLLECTIONS = ['ny18Toys', 'ny19Toys', 'ny20Toys']
NY_FILTER = 'newYear'
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr')

class Collections(CONST_CONTAINER):
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
    MAX_BONUS = 'maxReachedSettingBonus'
    MAX_BONUS_VALUE = 'value'
    MAX_BONUS_INFO = 'info'


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
    ALL = (FIR,
     TABLEFUL,
     INSTALLATION,
     ILLUMINATION,
     MASCOT)


class NyTabBarRewardsView(object):
    FOR_LEVELS = 'forLevels'
    COLLECTION_NY18 = Collections.NewYear18
    COLLECTION_NY19 = Collections.NewYear19
    COLLECTION_NY20 = Collections.NewYear20
    ALL = (FOR_LEVELS,
     COLLECTION_NY20,
     COLLECTION_NY19,
     COLLECTION_NY18)


class NyTabBarAlbumsView(object):
    NY_2018 = Collections.NewYear18
    NY_2019 = Collections.NewYear19
    NY_2020 = Collections.NewYear20
    ALL = (NY_2020, NY_2019, NY_2018)


TOY_TYPES_BY_OBJECT_WITHOUT_MEGA = {}
for custObj, toys in TOY_TYPES_BY_OBJECT.iteritems():
    toysWithoutMega = [ toy for toy in toys if toy not in ToyTypes.MEGA ]
    TOY_TYPES_BY_OBJECT_WITHOUT_MEGA[custObj] = tuple(toysWithoutMega)

TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA = []
for custObj in CustomizationObjects.ALL:
    for toyType in TOY_TYPES_BY_OBJECT_WITHOUT_MEGA[custObj]:
        TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA.append(toyType)

TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA = tuple(TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA)
