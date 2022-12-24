# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/settings.py
NY_CONFIG_NAME = 'ny_config'

class NYLootBoxConsts(object):
    CONFIG_NAME = 'lootBox_config'
    URL = 'url'
    GUARANTEED_REWARD_INFO_URL = 'guaranteedRewardInfoUrl'
    LOOT_BOX_OPENING_STREAM_URL = 'lootBoxOpeningStreamUrl'
    LOOT_BOXES_INFO_URL = 'lootBoxesInfoURL'
    SOURCE = 'source'
    IGB = 'igb'
    EXTERNAL = 'external'


class NYGeneralConsts(object):
    CONFIG_NAME = 'general_config'
    ATMOSPHERE_LEVEL_LIMITS = 'atmosphereLevelLimits'
    RESOURCE_CONVERTER_COEFFICIENTS = 'resourceConverterCoefficients'
    HANGAR_NAME_REROLL_TOKEN = 'hangarNameRerollToken'
    HANGAR_NAME_SET_TOKEN = 'hangarNameSetToken'
    EVENT_END_TIME = 'eventEndTime'
    FRIEND_SERVICE_ENABLED = 'friendServiceEnabled'
    FRIEND_SERVICE_REQUEST_DELAY = 'friendServiceRequestDelay'


class CelebrityConsts(object):
    CONFIG_NAME = 'celebrity_config'
    QUEST_COUNT = 'questCount'
    ADDITIONAL_QUESTS = 'additionalQuests'
    ADDITIONAL_QUEST_DEPENDENCIES = 'dependencies'
    TOKENS_DEPENDENCY = 'tokens'


class MarketplaceConsts(object):
    CONFIG_NAME = 'ny_marketplace_config'
    CATEGORY_NAME = 'categoryName'
    CATEGORY_ITEMS = 'categoryItems'
    ITEM_ID = 'id'
    ITEM_PRICE = 'price'
    ITEM_ACTIONS = 'actions'
    ITEM_REWARDS = 'rewards'
    FILL_COLLECTION = 'fillCollection'
    FILL_COLLECTION_YEAR = 'year'
    FILL_COLLECTION_SETTING = 'setting'
    BUY_REWARDS = 'buyRewards'
    REWARD_DISCOUNT = 'discount'
    REWARD_SKIP_DUPLICATE = 'skipDuplicate'
    ACTIONS = (FILL_COLLECTION, BUY_REWARDS)


class BattleBonusesConsts(object):
    CONFIG_NAME = 'battle_bonuses_config'
    BATTLE_BONUSES = 'battleBonuses'
    BONUSES_SECTION = 'bonuses'
    XP_BONUSES = 'xpBonuses'
    CURRENCY_BONUSES = 'currencyBonuses'
    ALL_BONUSES_TYPES = (XP_BONUSES, CURRENCY_BONUSES)
    DEPENDENCIES = 'dependencies'
    CHOOSABLE_BONUS_NAME = 'choice'
    CHOOSABLE_BONUS_ID = 'id'
    LEVEL_ERROR = 'levelError'
    VEHICLE_ERROR = 'vehicleError'
    APPLICABLE = 'applicable'


class GuestsQuestsConsts(object):
    CONFIG_NAME = 'guests_quests_config'
    GUESTS = 'guests'
    QUEST = 'quest'
    QUEST_ID = 'questID'
    QUEST_PRICE = 'price'
    QUEST_DEPENDENCIES = 'dependencies'
    QUEST_REWARDS = 'rewards'
    QUEST_BONUS = 'bonus'
    TOKENS = 'tokens'
    TOKEN = 'token'


class GiftMachineConsts(object):
    CONFIG_NAME = 'gift_machine_config'
    GIFT_MACHINE_COIN_ID = 'giftMachineCoinID'
    GIFT_MACHINE_COIN_PRICE = 'giftMachineCoinPrice'
    GIFT_MACHINE_DEPENDENCIES = 'dependencies'
    LEVEL_DEPENDENCY = 'level'
    TOKENS_DEPENDENCY = 'tokens'


class ObjectsConsts(object):
    CONFIG_NAME = 'objects_config'
    OBJECTS = 'objects'
    OBJECT_LEVELS = 'levels'
    OBJECT_LEVEL_ID = 'id'
    OBJECT_LEVEL_PRICE = 'price'
    OBJECT_LEVEL_POINTS = 'points'
    OBJECT_LEVEL_DEFAULT_TOYS_COUNT = 'defaultToysCountPerSlot'
    OBJECT_LEVEL_CUSTOM_TOYS_COUNT = 'customToysCountPerSlot'
    OBJECT_LEVEL_TOKEN = 'token'


class ResourceCollectingConsts(object):
    CONFIG_NAME = 'resource_collecting_config'
    COLLECTINGS = 'collectings'
    FRIEND_RESOURCES = 'friendResources'
    COLLECTING_ID = 'id'
    RESOURCES = 'resources'
    COOLDOWN = 'cooldown'
    COLLECTING_TYPES = 'collectingTypes'
    MANUAL_COLLECTING = 'manual'
    AUTO_COLLECTING = 'auto'
    ALL_COLLECTING_TYPES = (MANUAL_COLLECTING, AUTO_COLLECTING)
    COLLECTING_PRICE = 'price'


class NYPiggyBankConsts(object):
    CONFIG_NAME = 'ny_piggy_bank_config'
    ITEMS = 'items'
    ITEM = 'item'
    ID = 'id'
    DEPENDENCIES = 'dependencies'
    TOKEN = 'token'
    REWARDS = 'rewards'


class NYToyPricesConsts(object):
    CONFIG_NAME = 'ny_toy_prices_config'
    TOYS = 'toys'
    TOY = 'toy'
    TOY_ID = 'id'
    TOY_PRICE = 'price'
    TOY_DEPENDENCIES = 'dependencies'
    TOY_END_OF_SALE = 'endOfSale'
    TOKENS_DEPENDENCIES = 'tokens'
    END_OF_SALE_AT = 'at'
    END_OF_SALE_EVENT_END_DIFF = 'eventEndDiff'
    END_OF_SALE_KEYS = (END_OF_SALE_AT, END_OF_SALE_EVENT_END_DIFF)


class NYDogConsts(object):
    CONFIG_NAME = 'ny_dog_config'
    DAILY_STROKE_COUNT_THRESHOLD = 'dailyStrokeCountThreshold'
    STROKE_RANDOM_RESOURCES = 'strokeRandomResources'
