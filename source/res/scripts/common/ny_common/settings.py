# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/settings.py
from items.components.ny_constants import YEARS_INFO, ToySettings
NY_CONFIG_NAME = 'ny_config'

class NYGeneralConsts(object):
    CONFIG_NAME = 'general_config'
    ATMOSPHERE_LEVEL_LIMITS = 'atmosphereLevelLimits'
    ATMOSPHERE_POINTS_PER_RANK = 'atmospherePointsPerUsedToyRank'


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


CURRENT_PDATA_KEY = 'newYear{}'.format(YEARS_INFO.CURRENT_YEAR)
