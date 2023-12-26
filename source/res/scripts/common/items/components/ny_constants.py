# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_constants.py
import typing
from constants import ARENA_BONUS_TYPE
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple
_FIRST_YEAR = 18
_CURRENT_YEAR = 24
UNDEFINED_TOY_RANK = 0
MAX_TOY_RANK = 5
MIN_TOY_RANK = 1

class RewartKitSettings(object):
    NEW_YEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    FAIRYTALE = 'Fairytale'
    ORIENTAL = 'Oriental'


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
     YEARS.YEAR24: ToySettings.NEW + ToySettings.DOG}
    _COLLECTION_KEY_BY_YEAR = {year:'ny{}Toys'.format(year) for year in YEARS.ALL}
    CURRENT_SETTINGS = _COLLECTION_TYPES_BY_YEAR[CURRENT_YEAR]
    CURRENT_SETTING_IDS_BY_NAME = {name:idx for idx, name in enumerate(CURRENT_SETTINGS)}
    _MAX_TOY_RANK_BY_YEAR = {YEARS.YEAR18: 5,
     YEARS.YEAR19: 5,
     YEARS.YEAR20: 5,
     YEARS.YEAR21: 5,
     YEARS.YEAR22: 1,
     YEARS.YEAR23: 1,
     YEARS.YEAR24: 1}
    _TOY_COLLECTION_BYTES_BY_YEAR = {YEARS.YEAR18: 37,
     YEARS.YEAR19: 41,
     YEARS.YEAR20: 50,
     YEARS.YEAR21: 47,
     YEARS.YEAR22: 36,
     YEARS.YEAR23: 21,
     YEARS.YEAR24: 26}
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
    def getCollectionTypesByYear(year):
        year = YEARS_INFO.convertYearToNum(year)
        return YEARS_INFO._COLLECTION_TYPES_BY_YEAR[year]

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


COLLECTION_SLOTS_XML_PATH = 'scripts/item_defs/ny{}/slots.xml'.format(YEARS_INFO.CURRENT_YEAR)
VARIADIC_DISCOUNTS_XML_PATH = 'scripts/item_defs/ny{}/variadic_discounts.xml'.format(YEARS_INFO.CURRENT_YEAR)
TOKEN_VARIADIC_DISCOUNT_PREFIX = 'ny:vd'
NEW_YEAR_QUEST_GROUP_ID = 'ny{}:groupQuest'.format(YEARS_INFO.CURRENT_YEAR)
PREV_NY_TOYS_COLLECTIONS = [ 'ny{}Toys'.format(prevYear) for prevYear in YEARS_INFO.prevYearsDecreasingIter() ]
PREV_NY_TOYS_BONUSES = [ 'ny{}Toy'.format(prevYear) for prevYear in YEARS_INFO.prevYearsDecreasingIter() ]
LEVEL_REWARD_ID_TEMPLATE = 'ny:level:{}'
COLLECTION_REWARD_ID_TEMPLATE = '{}:cr:{}:complete'
RANDOM_TYPE = 'random'
CURRENT_YEAR_BADGE_ID = 141
PREVIOUS_YEARS_BADGE_IDS = (86,
 100,
 107,
 128)

class CurrentNYConstants(object):
    TOYS = 'ny{}Toys'.format(YEARS_INFO.CURRENT_YEAR)
    TOY_BONUS = 'ny{}Toy'.format(YEARS_INFO.CURRENT_YEAR)
    PDATA_KEY = 'newYear{}'.format(YEARS_INFO.CURRENT_YEAR)


class CustomizationObjects(object):
    FIR = 'Fir'
    FAIR = 'Fair'
    INSTALLATION = 'Installation'
    ALL = (FIR, FAIR, INSTALLATION)
    WITH_RANDOM = (RANDOM_TYPE,) + ALL


class FriendCustomizationObjects(object):
    FIR = 'FriendFir'
    FAIR = 'FriendFair'
    INSTALLATION = 'FriendInstallation'
    ALL = (FIR, FAIR, INSTALLATION)
    WITH_RANDOM = (RANDOM_TYPE,) + ALL


TOY_OBJECTS_IDS_BY_NAME = {name:idx for idx, name in enumerate(CustomizationObjects.ALL)}
MAX_MEGA_TOY_RANK = 1
MAX_DOG_TOY_RANK = 1

def _makeATMRewardFullName(name):
    return 'ny_{}'.format(name)


def _makeATMRewardUnlockToken(name):
    return 'ny:{}_unlock'.format(name)


class NyATMReward(object):

    class ShortName(object):
        DOG = 'dog'
        MARKETPLACE = 'marketplace'

    DOG = _makeATMRewardFullName(ShortName.DOG)
    MARKETPLACE = _makeATMRewardFullName(ShortName.MARKETPLACE)
    DOG_TOKEN = _makeATMRewardUnlockToken(ShortName.DOG)
    MARKETPLACE_TOKEN = _makeATMRewardUnlockToken(ShortName.MARKETPLACE)


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
    COLOR_FIR = 'color_fir'
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
     FLOOR,
     COLOR_FIR,
     PAVILION,
     KITCHEN,
     GARLAND_FAIR,
     ATTRACTION,
     EXPOSITION,
     SCULPTURE,
     SCULPTURE_LIGHT,
     GARLAND_INSTALLATION,
     PYRO,
     KIOSK)
    MEGA = (AIRSHIP, FERRIS_WHEEL, CASTLE)
    DOG = (DOG_BOWL,
     DOG_TOY,
     DOG_COLLAR,
     DOG_HOUSE)
    ALL = USUAL_TYPES + MEGA + DOG


MEGA_TOY_TYPES = ToyTypes.MEGA
TOY_USUAL_TYPES = ToyTypes.USUAL_TYPES
DOG_TOY_TYPES = ToyTypes.DOG
TOY_TYPES = ToyTypes.ALL
TOY_TYPE_IDS_BY_NAME = {name:idx for idx, name in enumerate(TOY_TYPES)}
TOY_TYPES_WITH_RANDOM = (RANDOM_TYPE,) + TOY_TYPES

class ToyDropSources(object):
    DOG = 'dog'
    BIG_BOXES = 'big_boxes'
    GUEST = 'guest'
    CUSTOMIZATION_OBJECTS = 'customization_objects'
    ALL = (DOG,
     BIG_BOXES,
     GUEST,
     CUSTOMIZATION_OBJECTS)


RANDOM_VALUE = -1
INVALID_TOY_ID = -1

class NY_STATE(object):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    SUSPENDED = 'suspended'
    FINISHED = 'finished'
    ENABLED = (IN_PROGRESS, SUSPENDED)
    ALL = (NOT_STARTED,
     IN_PROGRESS,
     SUSPENDED,
     FINISHED)


MAX_ATMOSPHERE_LVL = 10
MIN_ATMOSPHERE_LVL = 1
MIN_TANK_SLOTS_LVL = 5
MAX_COLLECTION_LEVEL = 5
NY_BRANCH_MIN_LEVEL = 5
NY_BRANCH_MAX_LEVEL = 10
OBJECT_MIN_LEVEL = 0
OBJECT_MAX_LEVEL = 5
GUEST_QUEST_DEFAULT_INDEX = -1
CELEBRITY_LOCK_VEHICLE_MIN_LEVEL = 4
CELEBRITY_LOCK_ARENA_BONUS_TYPES = ARENA_BONUS_TYPE.RANDOM_RANGE
TOY_TYPES_BY_OBJECT = {CustomizationObjects.FIR: (ToyTypes.TOP,
                            ToyTypes.GARLAND_FIR,
                            ToyTypes.BALL,
                            ToyTypes.FLOOR,
                            ToyTypes.COLOR_FIR),
 CustomizationObjects.FAIR: (ToyTypes.PAVILION,
                             ToyTypes.KITCHEN,
                             ToyTypes.GARLAND_FAIR,
                             ToyTypes.ATTRACTION,
                             ToyTypes.EXPOSITION),
 CustomizationObjects.INSTALLATION: (ToyTypes.SCULPTURE,
                                     ToyTypes.SCULPTURE_LIGHT,
                                     ToyTypes.GARLAND_INSTALLATION,
                                     ToyTypes.PYRO,
                                     ToyTypes.KIOSK)}
TOY_TYPES_BY_FRIEND_OBJECT = {FriendCustomizationObjects.FIR: (ToyTypes.TOP,
                                  ToyTypes.GARLAND_FIR,
                                  ToyTypes.BALL,
                                  ToyTypes.FLOOR),
 FriendCustomizationObjects.FAIR: (ToyTypes.PAVILION,
                                   ToyTypes.KITCHEN,
                                   ToyTypes.GARLAND_FAIR,
                                   ToyTypes.ATTRACTION,
                                   ToyTypes.EXPOSITION),
 FriendCustomizationObjects.INSTALLATION: (ToyTypes.SCULPTURE,
                                           ToyTypes.SCULPTURE_LIGHT,
                                           ToyTypes.GARLAND_INSTALLATION,
                                           ToyTypes.PYRO,
                                           ToyTypes.KIOSK)}
GUEST_D_SLOT_GROUPS = (ToyTypes.DOG_BOWL,
 ToyTypes.DOG_TOY,
 ToyTypes.DOG_COLLAR,
 ToyTypes.DOG_HOUSE)
TOY_TYPES_BY_OBJECT_WITH_RANDOM = dict(TOY_TYPES_BY_OBJECT, **{RANDOM_TYPE: (RANDOM_TYPE,)})
DEFAULT_XP_BONUS_CHOICE = 0

class TOY_SEEN_MASK(object):
    NONE = 0
    INVENTORY = 1
    COLLECTION = 16
    ANY = INVENTORY | COLLECTION


INV_TOYS_DEFAULT_VALUE = (0, 0, 0)

class CelebrityBattleQuestTypes(object):
    SKILL = '1'
    DILIGENCE = '2'


class CelebrityQuestTokenParts(object):
    PREFIX = 'NY_clbty'
    MARATHON_PREFIX = 'NY_mrthn_clbty'
    SEPARATOR = ':'
    TYPE = 'type'
    QUEST = 'quest'
    DAY = 'day'
    ADD = 'additional'
    QUEST_TYPES = (DAY, ADD)
    STYLE = 'style'
    DECAL = 'decal'
    INSCRIPTION = 'inscription'
    COMMANDER = 'commander'
    ADDITIONAL_TYPES_ORDERED = (INSCRIPTION,
     DECAL,
     STYLE,
     COMMANDER)
    ADDITIONAL_TYPES_ORDER = {t:i for i, t in enumerate(ADDITIONAL_TYPES_ORDERED, 1)}
    REROLL = 'reroll'
    REROLL_TOKEN = '{prefix}{separator}{reroll}'.format(separator=SEPARATOR, prefix=PREFIX, reroll=REROLL)

    @classmethod
    def isCelebrityFullQuestID(cls, fullQuestID):
        parts = cls.__splitQuestID(fullQuestID)
        if parts is None:
            return False
        else:
            questPrefix, questType, questID, questInfo = parts
            return questPrefix == cls.PREFIX and questType.startswith(cls.TYPE) and questID.startswith(cls.QUEST) and any((questInfo.startswith(prefix) for prefix in cls.QUEST_TYPES))

    @classmethod
    def isRerollToken(cls, tokenID):
        parts = cls.__splitQuestID(tokenID, 3)
        if parts is None:
            return False
        else:
            prefix, type, info = parts
            return prefix == cls.PREFIX and type.startswith(cls.REROLL) and any((info.startswith(prefix) for prefix in cls.QUEST_TYPES))

    @classmethod
    def isAddQuestID(cls, questID):
        qType, _ = cls.getFullQuestInfo(questID)
        return qType == cls.ADD

    @classmethod
    def isDayQuestID(cls, questID):
        qType, _ = cls.getFullQuestInfo(questID)
        return qType == cls.DAY

    @classmethod
    def makeQuestID(cls, *args):
        return cls.SEPARATOR.join((cls.PREFIX,) + args)

    @classmethod
    def makeQuestRerollToken(cls, questInfo):
        return cls.makeQuestID(cls.REROLL, questInfo)

    @classmethod
    def makeAdditionalBonusQuestID(cls, questType):
        return cls.makeQuestID(questType, 'done')

    @classmethod
    def makeQuestIDFromFullQuestID(cls, fullQuestID):
        parts = cls.__splitQuestID(fullQuestID)
        if parts is None:
            return
        else:
            _, questType, questID, _ = parts
            return cls.makeQuestID(questType, questID)

    @classmethod
    def makeTokenQuestIDFromFullQuestID(cls, fullQuestID):
        return cls.makeAdditionalBonusQuestID(cls.getFullQuestInfo(fullQuestID)[-1])

    @classmethod
    def makeQuestRerollTokenByFullQuestID(cls, fullQuestID):
        parts = cls.__splitQuestID(fullQuestID)
        return None if parts is None else cls.makeQuestRerollToken(parts[-1])

    @classmethod
    def getTypeFromFullQuestID(cls, fullQuestID):
        parts = cls.__splitQuestID(fullQuestID)
        if parts is None:
            return
        else:
            _, questType, _, _ = parts
            return questType

    @classmethod
    def compareFullQuestsIDs(cls, qAID, qBID):
        qAType, qANum = cls.getFullQuestOrderInfo(qAID)
        qBType, qBNum = cls.getFullQuestOrderInfo(qBID)
        return cmp(cls.QUEST_TYPES.index(qAType), cls.QUEST_TYPES.index(qBType)) or cmp(qANum, qBNum) if all((qType in cls.QUEST_TYPES for qType in (qAType, qBType))) else 0

    @classmethod
    def getFullQuestOrderInfo(cls, fullQuestID):
        qType, qData = cls.getFullQuestInfo(fullQuestID)
        return (qType, cls.ADDITIONAL_TYPES_ORDER.get(qData, 0) if qType == cls.ADD else ((int(qData) if qData.isdigit() else 0) if qType == cls.DAY else -1))

    @classmethod
    def isFinalAdditionalQuestID(cls, questID):
        parts = cls.__splitQuestID(questID, 3)
        if parts is None:
            return False
        else:
            questPrefix, questType, questInfo = parts
            return questPrefix == cls.PREFIX and questType in cls.ADDITIONAL_TYPES_ORDERED and questInfo == 'done'

    @classmethod
    def getFullQuestInfo(cls, questID):
        parts = cls.__splitQuestID(questID)
        if parts is None:
            return ('', '')
        else:
            questInfo = parts[-1].split('_')
            return questInfo if len(questInfo) == 2 else ('', '')

    @classmethod
    def isBattleQuestID(cls, questID):
        parts = cls.__splitQuestID(questID, 3)
        if parts is None:
            return False
        else:
            questInfo = parts[-1].split('_')
            return False if len(questInfo) != 2 else questInfo[0] == cls.QUEST and questInfo[1].isdigit()

    @classmethod
    def isRerollQuestsID(cls, questID):
        parts = cls.__splitQuestID(questID, partsCount=3)
        if parts is None:
            return False
        else:
            questPrefix, questInfo, questType = parts
            questInfo = questInfo.split('_')[0]
            return questPrefix == cls.PREFIX and questInfo in cls.QUEST_TYPES + cls.ADDITIONAL_TYPES_ORDERED and questType.startswith(cls.REROLL)

    @classmethod
    def __splitQuestID(cls, questID, partsCount=4):
        if not isinstance(questID, basestring):
            return None
        else:
            parts = tuple(str(questID).split(cls.SEPARATOR))
            return None if len(parts) != partsCount or parts[0] != cls.PREFIX else parts


class NY_LOGS(object):

    @classmethod
    def makeLogValueForXPBonusChoiceID(cls, choiceID):
        return choiceID + 1


class NyCurrency(object):
    CRYSTAL = 'ny_crystal'
    EMERALD = 'ny_emerald'
    AMBER = 'ny_amber'
    IRON = 'ny_iron'
    ALL = (CRYSTAL,
     EMERALD,
     AMBER,
     IRON)


NY_CURRENCY_NAME_TO_IDX = {key:idx for idx, key in enumerate(NyCurrency.ALL)}
NY_CURRENCY_IDX_TO_NAME = {idx:key for key, idx in NY_CURRENCY_NAME_TO_IDX.iteritems()}

class NYFriendServiceDataTokens(object):
    CELEBRITY_QUEST_COMPLETED = CelebrityQuestTokenParts.MARATHON_PREFIX
    NY_PIGGY_BANK_RESOURCE_COLLECTING = 'ny_piggy_bank_resource_collecting'
    GUEST_A_QUEST_COMPLETED = 'guest_A_quest_complete'
    GUEST_CAT_QUEST_COMPLETED = 'guest_cat_quest_complete'
    GUEST_QUESTS = (GUEST_A_QUEST_COMPLETED, GUEST_CAT_QUEST_COMPLETED)
    CAT_UNLOCK = 'ny:cat_unlock'
    DOG_UNLOCK = 'ny:dog_unlock'
    UNLOCKS = (CAT_UNLOCK, DOG_UNLOCK)
    GUEST_A_QUEST_DECORATION_1 = 'ny:guest_A:decoration:1'
    GUEST_A_QUEST_DECORATION_2 = 'ny:guest_A:decoration:2'
    GUEST_A_QUEST_DECORATION_3 = 'ny:guest_A:decoration:3'
    GUEST_A_QUEST_DECORATION_4 = 'ny:guest_A:decoration:4'
    GUEST_A_QUEST_DECORATION_5 = 'ny:guest_A:decoration:5'
    GUEST_A_DECORATIONS = (GUEST_A_QUEST_DECORATION_1,
     GUEST_A_QUEST_DECORATION_2,
     GUEST_A_QUEST_DECORATION_3,
     GUEST_A_QUEST_DECORATION_4,
     GUEST_A_QUEST_DECORATION_5)
    HANGAR_DECORATION_FIR = 'ny:deco:fir'
    HANGAR_DECORATION_FAIR = 'ny:deco:fair'
    HANGAR_DECORATION_INSTALLATION = 'ny:deco:installation'
    HANGAR_DECORATIONS = (HANGAR_DECORATION_FIR, HANGAR_DECORATION_FAIR, HANGAR_DECORATION_INSTALLATION)
    GUEST_A_QUEST_ANIM_1 = 'ny:guest_A:anim:1'
    GUEST_A_QUEST_ANIM_2 = 'ny:guest_A:anim:2'
    GUEST_A_QUEST_ANIM_3 = 'ny:guest_A:anim:3'
    GUEST_C_QUEST_ANIM_1 = 'ny:guest_cat:anim:1'
    GUEST_C_QUEST_ANIM_2 = 'ny:guest_cat:anim:2'
    GUEST_C_QUEST_ANIM_3 = 'ny:guest_cat:anim:3'
    GUEST_A_QUEST_STORY_1 = 'ny:guest_A:story:1'
    GUEST_ANIMS = (GUEST_A_QUEST_ANIM_1,
     GUEST_A_QUEST_ANIM_2,
     GUEST_A_QUEST_ANIM_3,
     GUEST_C_QUEST_ANIM_1,
     GUEST_C_QUEST_ANIM_2,
     GUEST_C_QUEST_ANIM_3)
    ALL = (CELEBRITY_QUEST_COMPLETED, NY_PIGGY_BANK_RESOURCE_COLLECTING, GUEST_A_QUEST_STORY_1) + GUEST_QUESTS + UNLOCKS + GUEST_A_DECORATIONS + HANGAR_DECORATIONS + GUEST_ANIMS
    ALL_DECORATIONS = HANGAR_DECORATIONS + GUEST_A_DECORATIONS


class NySackLootBox(object):
    TYPE = 'nySack'
    LEVEL_1 = 'nySackLevel1'
    LEVEL_2 = 'nySackLevel2'
    LEVEL_3 = 'nySackLevel3'
    LEVEL_4 = 'nySackLevel4'
    ALL = (LEVEL_1,
     LEVEL_2,
     LEVEL_3,
     LEVEL_4)


NY_SACK_CATEGORY_TO_LEVEL = {key:idx for idx, key in enumerate(NySackLootBox.ALL, start=1)}
NY_SACK_LEVEL_TO_CATEGORY = {idx:key for idx, key in enumerate(NySackLootBox.ALL, start=1)}
