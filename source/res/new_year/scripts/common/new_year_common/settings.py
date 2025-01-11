# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/common/new_year_common/settings.py
from items.components.ny_constants import YEARS_INFO, ToySettings
NY_CONFIG_NAME = 'ny_config'
IS_ENABLED = 'isEnabled'

class NyFeaturesConsts(object):
    MACHINE = 'machine'
    CRAFT = 'craft'
    TOY_DESTROY = 'toy_destroy'
    TOY_BUYING = 'toy_buying'
    ALL = (MACHINE,
     CRAFT,
     TOY_DESTROY,
     TOY_BUYING)


class NYGeneralConsts(object):
    CONFIG_NAME = 'general_config'
    ATMOSPHERE_LEVEL_LIMITS = 'atmosphereLevelLimits'
    ATMOSPHERE_POINTS_PER_RANK = 'atmospherePointsPerUsedToyRank'
    DAILY_PREFIX = 'dailyPrefix'
    WEEKLY_PREFIX = 'weeklyPrefix'
    SMALL_LOOTBOX_ID = 'smallLootBoxId'
    FIRST_ENTRANCE_TOKEN = 'firstEntranceToken'
    PET_VISIBLE = 'petVisible'
    NEW_YEAR_GREETINGS_DATE = 'newYearGreetingsDate'
    NEW_YEAR_START_DATE = 'newYearStartDate'
    NEW_YEAR_END_DATE = 'newYearEndDate'


class MachineConsts(object):
    CONFIG_NAME = 'machine_config'
    ENABLED = IS_ENABLED
    COIN_LOOTBOX_ID = 'coinLootboxId'
    COIN_PRICE = 'coinPrice'


class CraftProbsConsts(object):
    CONFIG_NAME = 'craft_probabilities_config'
    RANK = 'rank'
    SETTING = 'setting'
    TYPE = 'type'
    PROBABILITY = 'probability'
    RANK_PROBABILITIES = 'rankProbabilities'
    SETTING_PROBABILITIES = 'settingProbabilities'
    TYPE_PROBABILITIES = 'typeProbabilities'


class SettingBonusConsts(object):
    CONFIG_NAME = 'settingBonus_config'
    TOY_RATINGS = 'toyRatingByRank'
    COLLECTION_LEVELS_RATING = 'collectionLevelsRating'
    UNIQUE_TOY_LEVELS_RATING = 'uniqueToysLevelsRating'
    ATMOSPHERE_MULTIPLIERS = 'multiplierByAtmosphereLevel'
    BATTLE_BONUSES = 'battleBonuses'
    COLLECTION_BONUSES = 'collectionBonuses'
    UNIQUE_TOYS_BONUSES = 'uniqueToysBonus'


class ToyDecayCostConsts(object):
    CONFIG_NAME = 'toy_decay_cost_config'
    RANKS = 'ranks'
    FRAGMENTS = 'fragments'
    TYPE = 'type'
    TOY_TYPE = 'toyType'
    TOY_TYPES = 'toyTypes'


class CraftCostConsts(object):
    CONFIG_NAME = 'craft_cost_config'
    FILLER_CONVERT_COST = 'fillerConvertCost'
    USUAL_TOYS_COST = 'usualToysCost'
    CRAFT_COST_SECTION = 'craftCost'
    CRAFT_COST_RANDOM_TYPE = 'randomType'
    CRAFT_COST_SPECIFIED_TYPE = 'specifiedType'
    CRAFT_COST_RANDOM_SETTING = 'randomSetting'
    CRAFT_COST_SPECIFIED_SETTING = 'specifiedSetting'
    CRAFT_COST_RANDOM_RANK = 'randomRank'
    CRAFT_COST_SPECIFIED_RANK = 'specifiedRank'
    CRAFT_COST_PAID_FILLER = 'paidFiller'
    CRAFT_COST_SETTINGS = (CRAFT_COST_RANDOM_TYPE,
     CRAFT_COST_SPECIFIED_TYPE,
     CRAFT_COST_RANDOM_SETTING,
     CRAFT_COST_SPECIFIED_SETTING,
     CRAFT_COST_RANDOM_RANK,
     CRAFT_COST_PAID_FILLER)
    USUAL_TOYS = {year:'ny{}costByRank'.format(year) for year in YEARS_INFO.prevYearsDecreasingIter()}
    MEGA_TOYS_COST = 'megaToysCost'
    MEGA_COST_BY_COUNT = 'megaCostByCount'
    MEGA_TOYS = {year:'ny{}megaCost'.format(year) for year in YEARS_INFO.prevYearsDecreasingIter() if set(ToySettings.MEGA) & set(YEARS_INFO.getCollectionTypesByYear(year))}
    MEGA_TOYS_COSTS = ()
    QUEST_COUNT = 'questCount'


class NyObjectsConsts(object):
    CONFIG_NAME = 'objects_config'
    OBJECTS = 'objects'
    OBJECT_LEVELS = 'levels'
    OBJECT_LEVEL_ID = 'id'
    OBJECT_LEVEL_PRICE = 'price'
    OBJECT_LEVEL_BONUS = 'bonus'
    OBJECT_TOKEN = 'token'


class NyBuyToyConsts(object):
    CONFIG_NAME = 'buy_toy_config'
    TOY_COUNT_FOR_ONE_PURCHASE = 'toyCountForOnePurchase'


CURRENT_PDATA_KEY = 'newYear{}'.format(YEARS_INFO.CURRENT_YEAR)
