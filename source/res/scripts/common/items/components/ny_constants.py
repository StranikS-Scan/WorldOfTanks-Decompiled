# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_constants.py
import typing
COLLECTION2019_TOYS_XML_PATH = 'scripts/item_defs/ny19/toys.xml'
COLLECTION2020_TOYS_XML_PATH = 'scripts/item_defs/ny20/toys.xml'
COLLECTION2020_SLOTS_XML_PATH = 'scripts/item_defs/ny20/slots.xml'
COLLECTION2020_LEVEL_REWARDS_XML_PATH = 'scripts/item_defs/ny20/level_rewards.xml'
COLLECTION2018_REWARDS_XML_PATH = 'scripts/item_defs/ny18/collection_rewards.xml'
COLLECTION2019_REWARDS_XML_PATH = 'scripts/item_defs/ny19/collection_rewards.xml'
COLLECTION2020_REWARDS_XML_PATH = 'scripts/item_defs/ny20/collection_rewards.xml'
COLLECTION2020_TALISMANS_XML_PATH = 'scripts/item_defs/ny20/talismans.xml'
TOKEN_FREE_TALISMANS = 'ny20:freeTalisman'
NEW_YEAR_QUEST_GROUP_ID = 'ny20:groupQuest'
NY_MAN_QUEST_ID = 'ny20:quest:ny20men'
TOKEN_TALISMAN_BONUS = 'ny20:talismanBonus'
NEW_DAY_EXPIRES = {'endOfGameDay': True}

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

class TOY_SEEN_MASK(object):
    NONE = 0
    INVENTORY = 1
    COLLECTION = 16
    ANY = INVENTORY | COLLECTION


class YEARS(object):
    YEAR18 = 18
    YEAR19 = 19
    YEAR20 = 20
    ALL = (YEAR18, YEAR19, YEAR20)

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
     YEARS.YEAR20: ToySettings.NEW + ToySettings.MEGA}
    CURRENT_SETTINGS = _COLLECTION_TYPES_BY_YEAR[CURRENT_YEAR]
    CURRENT_SETTING_IDS_BY_NAME = {name:idx for idx, name in enumerate(CURRENT_SETTINGS)}
    _MAX_TOY_RANK_BY_YEAR = {YEARS.YEAR18: 5,
     YEARS.YEAR19: 5,
     YEARS.YEAR20: MAX_TOY_RANK}
    _TOY_COLLECTION_BYTES_BY_YEAR = {YEARS.YEAR18: 42,
     YEARS.YEAR19: 42,
     YEARS.YEAR20: TOY_COLLECTION_BYTES}
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
