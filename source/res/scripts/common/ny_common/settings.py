# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/settings.py
NY_CONFIG_NAME = 'ny_config'

class NYLootBoxConsts(object):
    CONFIG_NAME = 'lootBox_config'
    URL = 'url'
    SOURCE = 'source'
    IGB = 'igb'
    EXTERNAL = 'external'


class NYVehBranchConsts(object):
    CONFIG_NAME = 'vehBranch_config'
    VEH_BRANCH_BONUS = 'newYearBonus'
    VEH_CHANGE_PRICE = 'vehChangePrice'
    VEH_CHANGE_COOLDOWN = 'vehChangeCooldown'
    STYLE_ID = 'newYearStyleID'


class NYGeneralConsts(object):
    CONFIG_NAME = 'general_config'
    ATMOSPHERE_POINTS_BY_TOY_RANK = 'atmospherePointsByToyRank'
    ATMOSPHERE_LEVEL_LIMITS = 'atmosphereLevelLimits'


class CraftProbabilitiesConsts(object):
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
    ATMOSPHERE_MULTIPLIERS = 'multiplierByAtmosphereLevel'
    BATTLE_BONUSES = 'battleBonuses'
    COLLECTION_BONUSES = 'collectionBonuses'
    MEGA_TOY_BONUS = 'megaToyBonus'


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
    RANDOM_TOY_COST = 'randomCost'
    MEGA_COST_BY_COUNT = 'megaCostByCount'
    COST_BY_RANK = 'costByRank'
    NY19_COST_BY_RANK = 'ny19costByRank'
    NY18_COST_BY_RANK = 'ny18costByRank'
    SETTING_COST_FACTOR = 'settingCostFactor'
    CUSTOMIZATION_COST_FACTOR = 'customizationCostFactor'
    USUAL_TOYS_COST = 'usualToysCost'
    USUAL_TOYS = (COST_BY_RANK, NY19_COST_BY_RANK, NY18_COST_BY_RANK)
