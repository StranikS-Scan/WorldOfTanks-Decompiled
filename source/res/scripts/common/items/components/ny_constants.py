# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_constants.py
import typing
from typing import Optional, Tuple
from constants import ARENA_BONUS_TYPE
COLLECTION2019_TOYS_XML_PATH = 'scripts/item_defs/ny19/toys.xml'
COLLECTION2020_TOYS_XML_PATH = 'scripts/item_defs/ny20/toys.xml'
COLLECTION2021_TOYS_XML_PATH = 'scripts/item_defs/ny21/toys.xml'
COLLECTION2018_REWARDS_XML_PATH = 'scripts/item_defs/ny18/collection_rewards.xml'
COLLECTION2019_REWARDS_XML_PATH = 'scripts/item_defs/ny19/collection_rewards.xml'
COLLECTION2020_REWARDS_XML_PATH = 'scripts/item_defs/ny20/collection_rewards.xml'
COLLECTION2021_REWARDS_XML_PATH = 'scripts/item_defs/ny21/collection_rewards.xml'
COLLECTION2021_SLOTS_XML_PATH = 'scripts/item_defs/ny21/slots.xml'
COLLECTION2021_LEVEL_REWARDS_XML_PATH = 'scripts/item_defs/ny21/level_rewards.xml'
COLLECTION2021_TALISMANS_XML_PATH = 'scripts/item_defs/ny21/talismans.xml'
TOYS_TRANSFORMATIONS_XML_PATH = 'scripts/item_defs/ny21/slot_toy_pairs.xml'
VARIADIC_DISCOUNTS_XML_PATH = 'scripts/item_defs/ny21/variadic_discounts.xml'
TOKEN_THIS_IS_THE_END = 'ny21:thisIsTheEnd'
TOKEN_FREE_TALISMANS = 'ny21:freeTalisman'
TOKEN_VARIADIC_DISCOUNT_PREFIX = 'ny21:vd'
NEW_YEAR_QUEST_GROUP_ID = 'ny21:groupQuest'
NY_SENIORITY_SECRET_BOX_QUEST_ID = 'NY2021_seniority_secret_box'
TOKEN_TALISMAN_BONUS = 'ny21:talismanBonus'
NEW_DAY_EXPIRES = {'endOfGameDay': True}
VEH_BRANCH_EXTRA_SLOT_TOKEN = 'ny21:extraSlot'
PREV_NY_TOYS_COLLECTIONS = ('ny18Toys', 'ny19Toys', 'ny20Toys')
PREV_NY_TOYS_BONUSES = ('ny18Toy', 'ny19Toy', 'ny20Toy')

class CurrentNYConstants(object):
    TOYS = 'ny21Toys'
    TOY_BONUS = 'ny21Toy'
    TOY_FRAGMENTS = 'ny21ToyFragments'
    FILLERS = 'ny21Fillers'
    ANY_OF = 'ny21AnyOf'


class CustomizationObjects(object):
    FIR = 'Fir'
    TABLEFUL = 'Tableful'
    INSTALLATION = 'Installation'
    ILLUMINATION = 'Illumination'
    ALL = (FIR,
     TABLEFUL,
     INSTALLATION,
     ILLUMINATION)


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
    TOP = 'top'
    BALL = 'ball'
    GARLAND = 'garland'
    FLOOR = 'floor'
    TABLE = 'table'
    KITCHEN = 'kitchen'
    SCULPTURE = 'sculpture'
    DECORATION = 'decoration'
    TREES = 'trees'
    GROUND_LIGHT = 'ground_light'
    TENT = 'tent'
    SNOW_ITEM = 'snow_item'
    PYRO = 'pyro'
    MEGA_COMMON = 'mega'
    MEGA_FIR = 'mega_fir'
    MEGA_TABLEFUL = 'mega_tableful'
    MEGA_INSTALLATION = 'mega_installation'
    MEGA_ILLUMINATION = 'mega_illumination'
    OLD = (TOP,
     BALL,
     GARLAND,
     FLOOR,
     TABLE,
     KITCHEN,
     SCULPTURE,
     DECORATION,
     TREES,
     GROUND_LIGHT)
    NEW_USUAL = (TENT, SNOW_ITEM, PYRO)
    ALL_USUAL = OLD + NEW_USUAL
    MEGA = (MEGA_FIR,
     MEGA_TABLEFUL,
     MEGA_INSTALLATION,
     MEGA_ILLUMINATION)
    NEW = NEW_USUAL + MEGA
    ALL = OLD + NEW


MEGA_TOY_TYPES = ToyTypes.MEGA
TOY_TYPES = ToyTypes.ALL
TOY_USUAL_TYPES = ToyTypes.ALL_USUAL
TOY_TYPE_IDS_BY_NAME = {name:idx for idx, name in enumerate(TOY_TYPES)}
MAX_TOY_RANK = 5
MIN_TOY_RANK = 1
RANDOM_VALUE = -1
INVALID_TOY_ID = -1
MAX_TALISMAN_STAGE = MAX_TOY_RANK - 1
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
TOY_TYPES_BY_OBJECT = {CustomizationObjects.FIR: (ToyTypes.TOP,
                            ToyTypes.GARLAND,
                            ToyTypes.BALL,
                            ToyTypes.FLOOR,
                            ToyTypes.MEGA_FIR),
 CustomizationObjects.TABLEFUL: (ToyTypes.TABLE,
                                 ToyTypes.KITCHEN,
                                 ToyTypes.TENT,
                                 ToyTypes.MEGA_TABLEFUL),
 CustomizationObjects.INSTALLATION: (ToyTypes.SCULPTURE,
                                     ToyTypes.DECORATION,
                                     ToyTypes.SNOW_ITEM,
                                     ToyTypes.MEGA_INSTALLATION),
 CustomizationObjects.ILLUMINATION: (ToyTypes.TREES,
                                     ToyTypes.GROUND_LIGHT,
                                     ToyTypes.PYRO,
                                     ToyTypes.MEGA_ILLUMINATION)}
DEFAULT_VEH_BRANCH_BONUS_CHOICE = 0
EMPTY_VEH_INV_ID = 0

class TOY_SEEN_MASK(object):
    NONE = 0
    INVENTORY = 1
    COLLECTION = 16
    ANY = INVENTORY | COLLECTION


class YEARS(object):
    YEAR18 = 18
    YEAR19 = 19
    YEAR20 = 20
    YEAR21 = 21
    ALL = (YEAR18,
     YEAR19,
     YEAR20,
     YEAR21)

    @staticmethod
    def getYearNumFromYearStr(yearStr):
        return int(yearStr[-2:])

    @staticmethod
    def getYearStrFromYearNum(yearNum):
        return 'ny{}'.format(yearNum)


class YEARS_INFO(object):
    FIRST_YEAR = YEARS.ALL[0]
    CURRENT_YEAR = YEARS.ALL[-1]
    CURRENT_YEAR_STR = YEARS.getYearStrFromYearNum(CURRENT_YEAR)
    YearType = typing.Union[str, int]
    _COLLECTION_TYPES_BY_YEAR = {YEARS.YEAR18: ToySettings.OLD,
     YEARS.YEAR19: ToySettings.NEW,
     YEARS.YEAR20: ToySettings.NEW + ToySettings.MEGA,
     YEARS.YEAR21: ToySettings.NEW + ToySettings.MEGA}
    _COLLECTION_KEY_BY_YEAR = {YEARS.YEAR18: 'ny18Toys',
     YEARS.YEAR19: 'ny19Toys',
     YEARS.YEAR20: 'ny20Toys',
     YEARS.YEAR21: 'ny21Toys'}
    CURRENT_SETTINGS = _COLLECTION_TYPES_BY_YEAR[CURRENT_YEAR]
    CURRENT_SETTING_IDS_BY_NAME = {name:idx for idx, name in enumerate(CURRENT_SETTINGS)}
    _MAX_TOY_RANK_BY_YEAR = {YEARS.YEAR18: 5,
     YEARS.YEAR19: 5,
     YEARS.YEAR20: 5,
     YEARS.YEAR21: MAX_TOY_RANK}
    _TOY_COLLECTION_BYTES_BY_YEAR = {YEARS.YEAR18: 42,
     YEARS.YEAR19: 42,
     YEARS.YEAR20: 50,
     YEARS.YEAR21: TOY_COLLECTION_BYTES}
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
    MEDIUM = 1
    HARD = 2
    ALL = (EASY, MEDIUM, HARD)
    LEVEL_BY_NAME = {'easy': EASY,
     'medium': MEDIUM,
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
    PREFIX = 'NY2021_clbty'
    MARATHON_PREFIX = 'NY2021_mrthn_clbty'
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
