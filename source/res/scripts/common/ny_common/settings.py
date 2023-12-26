# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/settings.py
NY_CONFIG_NAME = 'ny_config'

class NYLootBoxConsts(object):
    CONFIG_NAME = 'lootBox_config'
    URL = 'url'
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
    EVENT_START_TIME = 'eventStartTime'
    EVENT_END_TIME = 'eventEndTime'
    FRIEND_SERVICE_ENABLED = 'friendServiceEnabled'
    FRIEND_SERVICE_REQUEST_DELAY = 'friendServiceRequestDelay'
    MAX_NAME_TITLE_ID = 'maxNameTitleID'
    MAX_NAME_DESCRIPTION_ID = 'maxNameDescriptionID'
    SURPRISE_TOKEN = 'surpriseToken'


class CelebrityConsts(object):
    CONFIG_NAME = 'celebrity_config'
    QUEST_COUNT = 'questCount'


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
    CHECK_PREV_NY_LEVEL = 'checkPrevNYLevel'
    ACTIONS = (FILL_COLLECTION, BUY_REWARDS, CHECK_PREV_NY_LEVEL)


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
    GIFT_MACHINE_COIN_TYPE = 'giftMachineCoinType'
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
    RESOURCES_COLLECTING = 'resourcesCollecting'
    RESOURCES = 'resources'
    COOLDOWN = 'cooldown'
    NOTIFY_TIMEOUT = 'notifyTimeout'
    NOTIFY_NO_FRIENDS_TIMEOUT = 'notifyNoFriendsTimeout'


class NYPiggyBankConsts(object):
    CONFIG_NAME = 'ny_piggy_bank_config'
    ITEMS = 'items'
    ITEM = 'item'
    ID = 'id'
    DEPENDENCIES = 'dependencies'
    TOKEN = 'token'
    REWARDS = 'rewards'


class NYDogConsts(object):
    CONFIG_NAME = 'ny_dog_config'
    TOKEN_NAME = 'tokenName'
    LEVELS = 'levels'
    LEVEL = 'level'
    LEVEL_PRICE = 'price'
    LEVEL_LOOTBOX = 'lootboxCategory'
    LEVEL_TOYS = 'toys'
    LEVEL_TOY = 'toy'
    LEVEL_TOY_ID = 'toyID'
    LEVEL_TOY_SLOT_ID = 'slotID'
