# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_constants.py
import typing
from enum import Enum, unique
from constants import ARENA_BONUS_TYPE
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple
_FIRST_YEAR = 18
_CURRENT_YEAR = 24
UNDEFINED_TOY_RANK = 0
MAX_TOY_RANK = 5
MIN_TOY_RANK = 1
MAX_MEGA_TOY_RANK = 1
MAX_DOG_TOY_RANK = 1
NY_FACTOR_BONUS_AVAILABLE_RANGE = (ARENA_BONUS_TYPE.REGULAR,
 ARENA_BONUS_TYPE.EPIC_RANDOM,
 ARENA_BONUS_TYPE.VERSUS_AI,
 ARENA_BONUS_TYPE.COMP7)

class ToySettings(object):
    NEW_YEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    FAIRYTALE = 'Fairytale'
    ORIENTAL = 'Oriental'
    SOVIET = 'soviet'
    TRADITIONAL_WESTERN = 'traditionalWestern'
    MODERN_WESTERN = 'modernWestern'
    ASIAN = 'asian'
    MEGA_TOYS = 'Mega'
    DOG_TOYS = 'Dog'
    NEW = (NEW_YEAR,
     CHRISTMAS,
     FAIRYTALE,
     ORIENTAL)
    OLD = (SOVIET,
     TRADITIONAL_WESTERN,
     MODERN_WESTERN,
     ASIAN)
    ALL = NEW + OLD
    MEGA = (MEGA_TOYS,)
    DOG = (DOG_TOYS,)


class YEARS(object):
    ALL = tuple(xrange(_FIRST_YEAR, _CURRENT_YEAR + 1))

    @staticmethod
    def getYearNumFromYearStr(yearStr):
        return int(yearStr[-2:])

    @staticmethod
    def getYearStrFromYearNum(yearNum):
        return 'ny{}'.format(yearNum)

    @staticmethod
    def getFullYearNumFromYearStr(yearStr):
        return 2000 + YEARS.getYearNumFromYearStr(yearStr)


for year in YEARS.ALL:
    setattr(YEARS, 'YEAR{}'.format(year), year)

class YEARS_INFO(object):
    FIRST_YEAR = YEARS.ALL[0]
    CURRENT_YEAR = YEARS.ALL[-1]
    CURRENT_YEAR_STR = YEARS.getYearStrFromYearNum(CURRENT_YEAR)
    YearType = typing.Union[str, int]
    _COLLECTION_TYPES_BY_YEAR = {YEARS.YEAR18: ToySettings.OLD,
     YEARS.YEAR19: ToySettings.NEW,
     YEARS.YEAR20: ToySettings.NEW + ToySettings.MEGA,
     YEARS.YEAR21: ToySettings.NEW + ToySettings.MEGA,
     YEARS.YEAR22: ToySettings.NEW + ToySettings.MEGA,
     YEARS.YEAR23: ToySettings.NEW + ToySettings.DOG,
     YEARS.YEAR24: ToySettings.NEW}
    _COLLECTION_KEY_BY_YEAR = {year:'ny{}Toys'.format(year) for year in YEARS.ALL}
    CURRENT_SETTINGS = _COLLECTION_TYPES_BY_YEAR[CURRENT_YEAR]
    CURRENT_SETTING_IDS_BY_NAME = {name:idx for idx, name in enumerate(CURRENT_SETTINGS)}
    _MAX_TOY_RANK_BY_YEAR = {YEARS.YEAR18: 5,
     YEARS.YEAR19: 5,
     YEARS.YEAR20: 5,
     YEARS.YEAR21: 5,
     YEARS.YEAR22: 1,
     YEARS.YEAR23: 1,
     YEARS.YEAR24: 5}
    _TOY_COLLECTION_BYTES_BY_YEAR = {YEARS.YEAR18: 37,
     YEARS.YEAR19: 41,
     YEARS.YEAR20: 50,
     YEARS.YEAR21: 47,
     YEARS.YEAR22: 36,
     YEARS.YEAR23: 21,
     YEARS.YEAR24: 42}
    _YEAR_OFFSET = 4
    _COLLECTION_TYPES_RANGES = None
    _TOY_COLLECTION_OFFSETS = None
    _COLLECTION_SETTING_IDS_BY_NAME = None

    @staticmethod
    def convertYearToNum(year):
        if isinstance(year, str):
            year = YEARS.getYearNumFromYearStr(year)
        return year

    @staticmethod
    def getToyCollectionBytesForYear(year):
        year = YEARS_INFO.convertYearToNum(year)
        return YEARS_INFO._TOY_COLLECTION_BYTES_BY_YEAR[year]

    @classmethod
    def getToyCollectionMaxToyID(cls, year):
        return cls.getToyCollectionBytesForYear(year) * 8 - 1

    @classmethod
    def currYearMaxToyRank(cls):
        return cls.getMaxToyRankByYear(cls.CURRENT_YEAR)

    @staticmethod
    def getMaxToyRankByYear(year):
        year = YEARS_INFO.convertYearToNum(year)
        return YEARS_INFO._MAX_TOY_RANK_BY_YEAR[year]

    @staticmethod
    def getCollectionTypesByYear(year, useMega=True):
        year = YEARS_INFO.convertYearToNum(year)
        return YEARS_INFO._COLLECTION_TYPES_BY_YEAR[year] if useMega else filter(lambda x: x != ToySettings.MEGA_TOYS, YEARS_INFO._COLLECTION_TYPES_BY_YEAR[year])

    @staticmethod
    def prevYearsDecreasingIter():
        for year in xrange(YEARS_INFO.CURRENT_YEAR - 1, YEARS_INFO.FIRST_YEAR - 1, -1):
            yield year

    @staticmethod
    def allYearsDecreasingIter():
        for year in xrange(YEARS_INFO.CURRENT_YEAR, YEARS_INFO.FIRST_YEAR - 1, -1):
            yield year

    @staticmethod
    def _checkCorrectYearNum(year):
        return YEARS_INFO.FIRST_YEAR <= year <= YEARS_INFO.CURRENT_YEAR

    @staticmethod
    def getCollectionSettingIDsByYear(year):
        if YEARS_INFO._COLLECTION_SETTING_IDS_BY_NAME is None:
            YEARS_INFO._initCollectionSettingIDsByName()
        year = YEARS_INFO.convertYearToNum(year)
        return YEARS_INFO._COLLECTION_SETTING_IDS_BY_NAME[year]

    @staticmethod
    def getToyCollectionOffsetForYear(year):
        if YEARS_INFO._TOY_COLLECTION_OFFSETS is None:
            YEARS_INFO._initToyCollectionOffsets()
        year = YEARS_INFO.convertYearToNum(year)
        return YEARS_INFO._TOY_COLLECTION_OFFSETS[year]

    @staticmethod
    def getCollectionKeyForYear(year):
        return YEARS_INFO._COLLECTION_KEY_BY_YEAR[year]

    @staticmethod
    def getCollectionDistributionsRangeForYear(year):
        if YEARS_INFO._COLLECTION_TYPES_RANGES is None:
            YEARS_INFO._initCollectionTypesRanges()
        year = YEARS_INFO.convertYearToNum(year)
        return YEARS_INFO._COLLECTION_TYPES_RANGES[year]

    @staticmethod
    def getCollectionIntID(collectionStrID):
        year, collectionID = YEARS_INFO.splitCollectionStrID(collectionStrID)
        beg, _ = YEARS_INFO.getCollectionDistributionsRangeForYear(year)
        return beg + collectionID

    @staticmethod
    def splitCollectionStrID(collectionStrID):
        return (collectionStrID[:YEARS_INFO._YEAR_OFFSET], int(collectionStrID[YEARS_INFO._YEAR_OFFSET:]))

    @staticmethod
    def getCollectionSettingID(setting, year):
        settingIDs = YEARS_INFO.getCollectionSettingIDsByYear(year)
        return year + str(settingIDs[setting])

    @staticmethod
    def getCollectionSettingNameAndYear(collectionStrID):
        yearStr, idx = YEARS_INFO.splitCollectionStrID(collectionStrID)
        year = YEARS_INFO.convertYearToNum(yearStr)
        return (YEARS_INFO._COLLECTION_TYPES_BY_YEAR[year][idx], yearStr)

    @staticmethod
    def _initCollectionTypesRanges():
        YEARS_INFO._COLLECTION_TYPES_RANGES = {}
        beg = 0
        for year in YEARS_INFO.allYearsDecreasingIter():
            end = beg + len(YEARS_INFO._COLLECTION_TYPES_BY_YEAR[year])
            YEARS_INFO._COLLECTION_TYPES_RANGES[year] = (beg, end)
            beg = end

    @staticmethod
    def _initToyCollectionOffsets():
        YEARS_INFO._TOY_COLLECTION_OFFSETS = {}
        offset = 0
        for year in YEARS_INFO.allYearsDecreasingIter():
            YEARS_INFO._TOY_COLLECTION_OFFSETS[year] = offset
            offset += YEARS_INFO.getToyCollectionBytesForYear(year)

    @staticmethod
    def _initCollectionSettingIDsByName():
        YEARS_INFO._COLLECTION_SETTING_IDS_BY_NAME = {}
        for year in YEARS_INFO.allYearsDecreasingIter():
            collection = YEARS_INFO._COLLECTION_TYPES_BY_YEAR[year]
            YEARS_INFO._COLLECTION_SETTING_IDS_BY_NAME[year] = {name:idx for idx, name in enumerate(collection)}


COLLECTION_SLOTS_XML_PATH = 'scripts/item_defs/ny{}/slots.xml'.format(YEARS_INFO.CURRENT_YEAR)
TOYS_TRANSFORMATIONS_XML_PATH = 'scripts/item_defs/ny{}/slot_toy_pairs.xml'.format(YEARS_INFO.CURRENT_YEAR)
VARIADIC_DISCOUNTS_XML_PATH = 'scripts/item_defs/ny{}/variadic_discounts.xml'.format(YEARS_INFO.CURRENT_YEAR)
TOKEN_VARIADIC_DISCOUNT_PREFIX = 'ny{}:vd'.format(YEARS_INFO.CURRENT_YEAR)
NEW_YEAR_QUEST_GROUP_ID = 'ny{}:groupQuest'.format(YEARS_INFO.CURRENT_YEAR)
PREV_NY_TOYS_COLLECTIONS = [ 'ny{}Toys'.format(prevYear) for prevYear in YEARS_INFO.prevYearsDecreasingIter() ]
ALL_NY_TOYS_BONUSES = [ 'ny{}Toy'.format(prevYear) for prevYear in YEARS_INFO.allYearsDecreasingIter() ]
LEVEL_REWARD_ID_TEMPLATE = '{}:level:{}'
COLLECTION_REWARD_ID_TEMPLATE = '{}:cr:{}:complete'
RANDOM_TYPE = 'random'
CURRENT_YEAR_BADGE_ID = 128
PREVIOUS_YEARS_BADGE_IDS = (86, 100, 107)

@unique
class FillerState(Enum):
    INACTIVE = 0
    USE_CHARGES = 1
    USE_SHARDS = 2
    ERROR = -1

    @property
    def isActive(self):
        return self in (self.USE_SHARDS,)


class CurrentNYConstants(object):
    TOYS = 'ny{}Toys'.format(YEARS_INFO.CURRENT_YEAR)
    TOY_BONUS = 'ny{}Toy'.format(YEARS_INFO.CURRENT_YEAR)
    TOY_FRAGMENTS = 'nyToyFragments'
    FILLERS = 'nyFillers'
    ANY_OF = 'nyAnyOf'
    NEW_TOYS = 'newNYToys'
    IP_TYPE_CUSTOM_TOYS = 'custom/{}'.format(TOYS)
    IP_TYPE_CUSTOM_ANYOF_TOYS = 'custom/{}'.format(ANY_OF)


class CustomizationObjects(object):
    FIR = 'Fir'
    WITHOUT_MEGA = (FIR,)
    ALL = WITHOUT_MEGA
    WITH_RANDOM = ALL + (RANDOM_TYPE,)


TOY_OBJECTS_IDS_BY_NAME = {name:idx for idx, name in enumerate(CustomizationObjects.ALL)}

class ToyTypes(object):
    ATTRACTION = 'attraction'
    BALL = 'ball'
    DECORATION = 'decoration'
    EXPOSITION = 'exposition'
    FLOOR = 'floor'
    GARLAND = 'garland'
    GARLAND_FIR = 'garland_fir'
    GARLAND_FAIR = 'garland_fair'
    GARLAND_INSTALLATION = 'garland_installation'
    GROUND_LIGHT = 'ground_light'
    KIOSK = 'kiosk'
    KITCHEN = 'kitchen'
    PAVILION = 'pavilion'
    PYRO = 'pyro'
    SCULPTURE = 'sculpture'
    SCULPTURE_LIGHT = 'sculpture_light'
    SNOW_ITEM = 'snow_item'
    TABLE = 'table'
    TENT = 'tent'
    TOP = 'top'
    TREES = 'trees'
    AIR_BALLOON = 'air_balloon'
    BRIDGE = 'bridge'
    AIRSHIP = 'airship'
    CASTLE = 'castle'
    FERRIS_WHEEL = 'ferris_wheel'
    MEGA_COMMON = 'mega'
    MEGA_FIR = 'mega_fir'
    MEGA_ILLUMINATION = 'mega_illumination'
    MEGA_INSTALLATION = 'mega_installation'
    MEGA_TABLEFUL = 'mega_tableful'
    DOG_TOY = 'dog_toy'
    DOG_BOWL = 'dog_bowl'
    DOG_HOUSE = 'dog_house'
    DOG_COLLAR = 'dog_collar'
    USUAL_TYPES = (TOP,
     GARLAND_FIR,
     BALL,
     FLOOR)
    MEGA = ()
    DOG = ()
    ALL = USUAL_TYPES


MEGA_TOY_TYPES = ToyTypes.MEGA
TOY_USUAL_TYPES = ToyTypes.USUAL_TYPES
DOG_TOY_TYPES = ToyTypes.DOG
TOY_TYPES = ToyTypes.ALL
TOY_TYPE_IDS_BY_NAME = {name:idx for idx, name in enumerate(TOY_TYPES)}
TOY_TYPES_WITH_RANDOM = (RANDOM_TYPE,) + TOY_TYPES
RANDOM_VALUE = -1
INVALID_TOY_ID = -1

class NY_STATE(object):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    SUSPENDED = 'suspended'
    POST_EVENT = 'post_event'
    FINISHED = 'finished'
    ENABLED = (IN_PROGRESS, SUSPENDED)
    ALL = (NOT_STARTED,
     IN_PROGRESS,
     SUSPENDED,
     POST_EVENT,
     FINISHED)


MAX_ATMOSPHERE_LVL = 10
MIN_ATMOSPHERE_LVL = 1
MIN_TANK_SLOTS_LVL = 5
MAX_COLLECTION_LEVEL = 5
NY_BRANCH_MIN_LEVEL = 5
NY_BRANCH_MAX_LEVEL = 10
TOY_TYPES_BY_OBJECT_WITHOUT_MEGA = {CustomizationObjects.FIR: (ToyTypes.TOP,
                            ToyTypes.GARLAND_FIR,
                            ToyTypes.BALL,
                            ToyTypes.FLOOR)}
TOY_TYPES_BY_OBJECT = dict(TOY_TYPES_BY_OBJECT_WITHOUT_MEGA, **{})
TOY_TYPES_BY_OBJECT_WITH_RANDOM = dict(TOY_TYPES_BY_OBJECT_WITHOUT_MEGA, **{RANDOM_TYPE: (RANDOM_TYPE,)})
TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA = tuple((toyType for custObj in CustomizationObjects.WITHOUT_MEGA for toyType in TOY_TYPES_BY_OBJECT_WITHOUT_MEGA[custObj]))
TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA = (RANDOM_TYPE,) + TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA

class TOY_SEEN_MASK(object):
    NONE = 0
    INVENTORY = 1
    COLLECTION = 16
    ANY = INVENTORY | COLLECTION


class TOY_CRAFT_LOG_OFFSET(object):
    FILLER = 0
    RANK = 1
    SETTING = 2
    TYPE = 3

    @classmethod
    def getLogValue(cls, toyTypeID, settingID, rank, filler):
        sourceID = (toyTypeID != RANDOM_VALUE) << cls.TYPE
        sourceID |= (settingID != RANDOM_VALUE) << cls.SETTING
        sourceID |= (rank != RANDOM_VALUE) << cls.RANK
        sourceID |= filler << cls.FILLER
        return str(sourceID)


INV_TOYS_DEFAULT_VALUE = (0, 0, 0)
