# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/settings.py
from items.components.ny_constants import YEARS
NY_CONFIG_NAME = 'ny_config'

class NYLootBoxConsts(object):
    CONFIG_NAME = 'lootBox_config'
    URL = 'url'
    GUARANTEED_REWARD_INFO_URL = 'guaranteedRewardInfoUrl'
    LOOT_BOX_OPENING_STREAM_URL = 'lootBoxOpeningStreamUrl'
    SOURCE = 'source'
    IGB = 'igb'
    EXTERNAL = 'external'


class NYVehBranchConsts(object):
    CONFIG_NAME = 'vehBranch_config'
    VEH_CHANGE_PRICE = 'vehChangePrice'
    VEH_CHANGE_COOLDOWN = 'vehChangeCooldown'
    SLOT_BONUS_CHOICES = 'bonusChoices'
    SLOTS = 'slots'
    TOKEN = 'token'
    LEVEL = 'level'
    UNDEFINED = 'undefined'


class NYGeneralConsts(object):
    CONFIG_NAME = 'general_config'
    ATMOSPHERE_POINTS = 'atmospherePoints'
    ATMOSPHERE_LEVEL_LIMITS = 'atmosphereLevelLimits'


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
    NY21_COST_BY_RANK = 'ny21costByRank'
    NY20_COST_BY_RANK = 'ny20costByRank'
    NY19_COST_BY_RANK = 'ny19costByRank'
    NY18_COST_BY_RANK = 'ny18costByRank'
    USUAL_TOYS_COST = 'usualToysCost'
    CRAFT_COST_SECTION = 'craftCost'
    CRAFT_COST_RANDOM_TYPE = 'randomType'
    CRAFT_COST_SPECIFIED_TYPE = 'specifiedType'
    CRAFT_COST_RANDOM_SETTING = 'randomSetting'
    CRAFT_COST_SPECIFIED_SETTING = 'specifiedSetting'
    CRAFT_COST_PAID_FILLER = 'paidFiller'
    CRAFT_COST_SETTINGS = (CRAFT_COST_RANDOM_TYPE,
     CRAFT_COST_SPECIFIED_TYPE,
     CRAFT_COST_RANDOM_SETTING,
     CRAFT_COST_SPECIFIED_SETTING,
     CRAFT_COST_PAID_FILLER)
    USUAL_TOYS = {YEARS.YEAR21: NY21_COST_BY_RANK,
     YEARS.YEAR20: NY20_COST_BY_RANK,
     YEARS.YEAR19: NY19_COST_BY_RANK,
     YEARS.YEAR18: NY18_COST_BY_RANK}
    MEGA_TOYS_COST = 'megaToysCost'
    MEGA_COST_BY_COUNT = 'megaCostByCount'
    NY20_MEGA_COST = 'ny20megaCost'
    NY21_MEGA_COST = 'ny21megaCost'
    MEGA_TOYS_COSTS = (MEGA_COST_BY_COUNT, NY20_MEGA_COST, NY21_MEGA_COST)


class CelebrityConsts(object):
    CONFIG_NAME = 'celebrity_config'
    SIMPLIFICATION_COSTS = 'simplificationCosts'
    QUEST_COUNT = 'questCount'
