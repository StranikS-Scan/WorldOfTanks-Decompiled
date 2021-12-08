# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_constants.py
import typing
from enum import Enum, unique
from constants import ARENA_BONUS_TYPE
COLLECTION2018_REWARDS_XML_PATH = 'scripts/item_defs/ny18/collection_rewards.xml'
COLLECTION2019_REWARDS_XML_PATH = 'scripts/item_defs/ny19/collection_rewards.xml'
COLLECTION2020_REWARDS_XML_PATH = 'scripts/item_defs/ny20/collection_rewards.xml'
COLLECTION2021_REWARDS_XML_PATH = 'scripts/item_defs/ny21/collection_rewards.xml'
COLLECTION2022_REWARDS_XML_PATH = 'scripts/item_defs/ny22/collection_rewards.xml'
COLLECTION2022_SLOTS_XML_PATH = 'scripts/item_defs/ny22/slots.xml'
COLLECTION2022_LEVEL_REWARDS_XML_PATH = 'scripts/item_defs/ny22/level_rewards.xml'
TOYS_TRANSFORMATIONS_XML_PATH = 'scripts/item_defs/ny22/slot_toy_pairs.xml'
VARIADIC_DISCOUNTS_XML_PATH = 'scripts/item_defs/ny22/variadic_discounts.xml'
TOKEN_THIS_IS_THE_END = 'ny22:thisIsTheEnd'
TOKEN_VARIADIC_DISCOUNT_PREFIX = 'ny22:vd'
NEW_YEAR_QUEST_GROUP_ID = 'ny22:groupQuest'
NY_SENIORITY_SECRET_BOX_QUEST_ID = 'NY2022_seniority_secret_box'
NEW_DAY_EXPIRES = {'endOfGameDay': True}
VEH_BRANCH_EXTRA_SLOT_TOKEN = 'ny22:extraSlot'
PREV_NY_TOYS_COLLECTIONS = ('ny18Toys', 'ny19Toys', 'ny20Toys', 'ny21Toys')
PREV_NY_TOYS_BONUSES = ('ny18Toy', 'ny19Toy', 'ny20Toy', 'ny21Toy')
RANDOM_TYPE = 'random'
CURRENT_YEAR_BADGE_ID = 107
PREVIOUS_YEARS_BADGE_IDS = (86, 100)
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple

@unique
class FillerState(Enum):
    INACTIVE = 0
    USE_CHARGES = 1
    USE_SHARDS = 2
    ERROR = -1

    @property
    def isActive(self):
        return self in (self.USE_CHARGES, self.USE_SHARDS)


class CurrentNYConstants(object):
    TOYS = 'ny22Toys'
    TOY_BONUS = 'ny22Toy'
    TOY_FRAGMENTS = 'ny22ToyFragments'
    FILLERS = 'ny22Fillers'
    ANY_OF = 'ny22AnyOf'


class CustomizationObjects(object):
    FIR = 'Fir'
    FAIR = 'Fair'
    INSTALLATION = 'Installation'
    MEGAZONE = 'Megazone'
    WITHOUT_MEGA = (FIR, FAIR, INSTALLATION)
    WITH_RANDOM = (RANDOM_TYPE,) + WITHOUT_MEGA
    ALL = WITHOUT_MEGA + (MEGAZONE,)


TOY_OBJECTS_IDS_BY_NAME = {name:idx for idx, name in enumerate(CustomizationObjects.ALL)}

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


class ToyTypes(object):
    ATTRACTION = 'attraction'
    BALL = 'ball'
    DECORATION = 'decoration'
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
    CASTLE = 'castle'
    FERRIS_WHEEL = 'ferris_wheel'
    MEGA_COMMON = 'mega'
    MEGA_FIR = 'mega_fir'
    MEGA_ILLUMINATION = 'mega_illumination'
    MEGA_INSTALLATION = 'mega_installation'
    MEGA_TABLEFUL = 'mega_tableful'
    USUAL_TYPES = (TOP,
     GARLAND_FIR,
     BALL,
     FLOOR,
     PAVILION,
     KITCHEN,
     GARLAND_FAIR,
     ATTRACTION,
     SCULPTURE,
     SCULPTURE_LIGHT,
     GARLAND_INSTALLATION,
     PYRO,
     KIOSK)
    MEGA = (AIR_BALLOON,
     FERRIS_WHEEL,
     BRIDGE,
     CASTLE)
    ALL = USUAL_TYPES + MEGA


MEGA_TOY_TYPES = ToyTypes.MEGA
TOY_USUAL_TYPES = ToyTypes.USUAL_TYPES
TOY_TYPES = ToyTypes.ALL
TOY_TYPE_IDS_BY_NAME = {name:idx for idx, name in enumerate(TOY_TYPES)}
TOY_TYPES_WITH_RANDOM = (RANDOM_TYPE,) + TOY_TYPES
UNDEFINED_TOY_RANK = 0
MAX_TOY_RANK = 5
MIN_TOY_RANK = 1
MAX_MEGA_TOY_RANK = 1
RANDOM_VALUE = -1
INVALID_TOY_ID = -1
RANK_COLORS = ('orange', 'yellow', 'green', 'blue', 'violet')
COLORS_BY_RANK = {name:idx for idx, name in enumerate(RANK_COLORS, 1)}
RANK_NAMES = ('simple', 'unusual', 'rare', 'unique', 'epic')
NAMES_BY_RANK = {name:idx for idx, name in enumerate(RANK_NAMES, 1)}

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


TOY_COLLECTION_BYTES = 50
MAX_TOY_ID = TOY_COLLECTION_BYTES * 8 - 1
MAX_ATMOSPHERE_LVL = 10
MIN_ATMOSPHERE_LVL = 1
MIN_TANK_SLOTS_LVL = 5
TOY_RATING_BY_RANK = (1, 1, 1, 1, 1)
MAX_COLLECTION_LEVEL = 5
NY_BRANCH_MIN_LEVEL = 5
NY_BRANCH_MAX_LEVEL = 10
CELEBRITY_LOCK_VEHICLE_MIN_LEVEL = 4
CELEBRITY_LOCK_ARENA_BONUS_TYPES = ARENA_BONUS_TYPE.RANDOM_RANGE
TOY_TYPES_BY_OBJECT_WITHOUT_MEGA = {CustomizationObjects.FIR: (ToyTypes.TOP,
                            ToyTypes.GARLAND_FIR,
                            ToyTypes.BALL,
                            ToyTypes.FLOOR),
 CustomizationObjects.FAIR: (ToyTypes.PAVILION,
                             ToyTypes.KITCHEN,
                             ToyTypes.GARLAND_FAIR,
                             ToyTypes.ATTRACTION),
 CustomizationObjects.INSTALLATION: (ToyTypes.SCULPTURE,
                                     ToyTypes.SCULPTURE_LIGHT,
                                     ToyTypes.GARLAND_INSTALLATION,
                                     ToyTypes.PYRO,
                                     ToyTypes.KIOSK)}
TOY_TYPES_BY_OBJECT = dict(TOY_TYPES_BY_OBJECT_WITHOUT_MEGA, **{CustomizationObjects.MEGAZONE: (ToyTypes.FERRIS_WHEEL,
                                 ToyTypes.CASTLE,
                                 ToyTypes.BRIDGE,
                                 ToyTypes.AIR_BALLOON)})
TOY_TYPES_BY_OBJECT_WITH_RANDOM = dict(TOY_TYPES_BY_OBJECT_WITHOUT_MEGA, **{RANDOM_TYPE: (RANDOM_TYPE,)})
TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA = tuple((toyType for custObj in CustomizationObjects.WITHOUT_MEGA for toyType in TOY_TYPES_BY_OBJECT_WITHOUT_MEGA[custObj]))
TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA = (RANDOM_TYPE,) + TOY_TYPES_FOR_OBJECTS_WITHOUT_MEGA
DEFAULT_VEH_BRANCH_BONUS_CHOICE = 0
EMPTY_VEH_INV_ID = 0

class TOY_SEEN_MASK(object):
    NONE = 0
    INVENTORY = 1
    COLLECTION = 16
    ANY = INVENTORY | COLLECTION


class TOY_SLOT_USAGE(object):
    TYPE = int
    PURE = 0
    USED = 1
    ALL = (PURE, USED)
    SECTION_MAP = {'pureToy': PURE,
     'usedToy': USED,
     'pureSlot': PURE,
     'usedSlot': USED}
    POINTS_MARK_FORBIDDEN = -1


INV_TOYS_DEFAULT_VALUE = (0, 0, 0, 0)

class YEARS(object):
    YEAR18 = 18
    YEAR19 = 19
    YEAR20 = 20
    YEAR21 = 21
    YEAR22 = 22
    ALL = (YEAR18,
     YEAR19,
     YEAR20,
     YEAR21,
     YEAR22)

    @staticmethod
    def getYearNumFromYearStr(yearStr):
        return int(yearStr[-2:])

    @staticmethod
    def getYearStrFromYearNum(yearNum):
        return 'ny{}'.format(yearNum)

    @staticmethod
    def getFullYearNumFromYearStr(yearStr):
        return 2000 + YEARS.getYearNumFromYearStr(yearStr)


class YEARS_INFO(object):
    FIRST_YEAR = YEARS.ALL[0]
    CURRENT_YEAR = YEARS.ALL[-1]
    CURRENT_YEAR_STR = YEARS.getYearStrFromYearNum(CURRENT_YEAR)
    YearType = typing.Union[str, int]
    _COLLECTION_TYPES_BY_YEAR = {YEARS.YEAR18: ToySettings.OLD,
     YEARS.YEAR19: ToySettings.NEW,
     YEARS.YEAR20: ToySettings.NEW + ToySettings.MEGA,
     YEARS.YEAR21: ToySettings.NEW + ToySettings.MEGA,
     YEARS.YEAR22: ToySettings.NEW + ToySettings.MEGA}
    _COLLECTION_KEY_BY_YEAR = {YEARS.YEAR18: 'ny18Toys',
     YEARS.YEAR19: 'ny19Toys',
     YEARS.YEAR20: 'ny20Toys',
     YEARS.YEAR21: 'ny21Toys',
     YEARS.YEAR22: 'ny22Toys'}
    CURRENT_SETTINGS = _COLLECTION_TYPES_BY_YEAR[CURRENT_YEAR]
    CURRENT_SETTING_IDS_BY_NAME = {name:idx for idx, name in enumerate(CURRENT_SETTINGS)}
    _MAX_TOY_RANK_BY_YEAR = {YEARS.YEAR18: MAX_TOY_RANK,
     YEARS.YEAR19: MAX_TOY_RANK,
     YEARS.YEAR20: MAX_TOY_RANK,
     YEARS.YEAR21: MAX_TOY_RANK,
     YEARS.YEAR22: 1}
    _TOY_COLLECTION_BYTES_BY_YEAR = {YEARS.YEAR18: 42,
     YEARS.YEAR19: 42,
     YEARS.YEAR20: 50,
     YEARS.YEAR21: 50,
     YEARS.YEAR22: TOY_COLLECTION_BYTES}
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


class CelebrityQuestLevels(object):
    NONE = -1
    EASY = 0
    HARD = 1
    ALL = (EASY, HARD)
    LEVEL_BY_NAME = {'easy': EASY,
     'hard': HARD}
    NAME_BY_LEVEL = {level:name for name, level in LEVEL_BY_NAME.iteritems()}

    @classmethod
    def getLevelByName(cls, levelName):
        return cls.LEVEL_BY_NAME.get(levelName, cls.NONE)

    @classmethod
    def getNameByLevel(cls, level):
        return cls.NAME_BY_LEVEL.get(level, None)

    @classmethod
    def getHardestLevel(cls):
        return cls.ALL[-1]

    @classmethod
    def getEasiestLevel(cls):
        return cls.ALL[0]


class CelebrityQuestTokenParts(object):
    PREFIX = 'NY2022_clbty'
    MARATHON_PREFIX = 'NY2022_mrthn_clbty'
    POSTFIX_DONE = 'done'
    POSTFIX_SIMPLIFIED = 'smpl'
    SEPARATOR = ':'

    @classmethod
    def sameQuestValidator(cls, quest1, quest2):
        if not quest1.startswith(cls.PREFIX) or not quest2.startswith(cls.PREFIX):
            return False
        questsPostfixes = (quest1.split(cls.SEPARATOR)[-1], quest1.rsplit(cls.SEPARATOR)[-1])
        return False if any([ cls.POSTFIX_SIMPLIFIED != postfix for postfix in questsPostfixes ]) else quest1.split(cls.SEPARATOR)[:2] == quest2.split(cls.SEPARATOR)[:2]

    @classmethod
    def getQuestInfo(cls, questToken):
        parts = questToken.rsplit(cls.SEPARATOR, 1)
        if len(parts) < 2:
            return (None, None)
        else:
            questLevel = CelebrityQuestLevels.getLevelByName(parts[1])
            if questLevel == CelebrityQuestLevels.NONE:
                return (None, None)
            questPrefix = parts[0]
            return (None, None) if not questPrefix.startswith(cls.PREFIX) else (questLevel, questPrefix)

    @classmethod
    def getLevelFromSimplificationToken(cls, simplificationToken):
        levelName = simplificationToken.rsplit(cls.SEPARATOR, 2)[-2]
        levelNum = CelebrityQuestLevels.getLevelByName(levelName)
        return None if levelNum == CelebrityQuestLevels.NONE else levelNum

    @classmethod
    def getDayNum(cls, questGroupToken):
        dayStr = questGroupToken.rsplit(cls.SEPARATOR, 1)[-1]
        return int(dayStr.replace('d', ''))

    @classmethod
    def getSimplificationTokenByQuestToken(cls, questToken):
        return '{}{}{}'.format(questToken, cls.SEPARATOR, cls.POSTFIX_SIMPLIFIED)

    @classmethod
    def generateSimplificationToken(cls, simplLevel, questPrefix):
        levelName = CelebrityQuestLevels.getNameByLevel(simplLevel)
        return None if levelName is None else '{prefix}{separator}{levelName}{separator}{postfixSimpl}'.format(separator=cls.SEPARATOR, prefix=questPrefix, levelName=levelName, postfixSimpl=cls.POSTFIX_SIMPLIFIED)

    @classmethod
    def getQuestNameForLevel(cls, questLevel, questPrefix):
        levelName = CelebrityQuestLevels.getNameByLevel(questLevel)
        return None if levelName is None else '{}{}{}'.format(questPrefix, cls.SEPARATOR, levelName)


class NY_LOGS(object):

    @classmethod
    def makeLogValueForVehBranchSlotID(cls, slotID):
        return slotID + 1

    @classmethod
    def makeLogValueForVehBranchChoiceID(cls, choiceID):
        return choiceID + 1
