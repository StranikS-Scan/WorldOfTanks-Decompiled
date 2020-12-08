# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/settings.py
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
    REGULAR_SLOT_BONUS = 'regularSlotBonuses'
    VEH_CHANGE_PRICE = 'vehChangePrice'
    VEH_CHANGE_COOLDOWN = 'vehChangeCooldown'
    STYLE_ID = 'newYearStyleID'
    EXTRA_SLOT_BONUS_CHOICES = 'bonusChoices'
    SLOTS = 'slots'
    SLOT_TYPE = 'slotType'
    VEHICLE_LEVELS = 'levels'


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
    COST_BY_RANK = 'costByRank'
    NY20_COST_BY_RANK = 'ny20costByRank'
    NY19_COST_BY_RANK = 'ny19costByRank'
    NY18_COST_BY_RANK = 'ny18costByRank'
    SETTING_COST_FACTOR = 'settingCostFactor'
    CUSTOMIZATION_COST_FACTOR = 'customizationCostFactor'
    USUAL_TOYS_COST = 'usualToysCost'
    USUAL_TOYS = (COST_BY_RANK,
     NY20_COST_BY_RANK,
     NY19_COST_BY_RANK,
     NY18_COST_BY_RANK)
    MEGA_TOYS_COST = 'megaToysCost'
    MEGA_COST_BY_COUNT = 'megaCostByCount'
    NY20_MEGA_COST = 'ny20megaCost'
    MEGA_TOYS_COSTS = (MEGA_COST_BY_COUNT, NY20_MEGA_COST)


class CelebrityConsts(object):
    CONFIG_NAME = 'celebrity_config'
    SIMPLIFICATION_COSTS = 'simplificationCosts'
    QUEST_COUNT = 'questCount'


class SnowGirlConsts(object):
    CONFIG_NAME = 'snowgirl_config'
    SEQUENCE_STAGE_COST = 'sequenceStageCost'
    ADDITIONAL_PROBABILITIES = 'additionalProbabilities'
    TOY_LIMITS_PER_STAGE = 'toyLimitsPerStage'
    RANK_PROBABILITIES = 'rankProbabilities'
    SEQUENCE_STAGE = 'sequenceStage'
    PROBABILITIES = 'probabilities'
