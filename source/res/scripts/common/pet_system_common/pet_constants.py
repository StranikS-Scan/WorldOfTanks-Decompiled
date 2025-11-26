# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pet_system_common/pet_constants.py
from dossiers2.custom.records import RECORD_DB_IDS
PETS_SYSTEM_CONFIG = 'pets_system_config'
PETS_SYSTEM_PDATA_KEY = 'pets_system'
PET_STORAGE_CAMERA_NAME = 'DogStorage'
PET_CAMERA_NAME = 'Dog'
PET_RTPC_DOG_TYPE = 'RTPC_ext_pet_system_dog_type'

class PetSystemGeneralConsts(object):
    CONFIG_NAME = 'pets_general_config'
    ENABLED = 'isEnabled'
    EVENT_PER_DAY = 'eventsMaxPerDay'
    EVENT_MIN_BATTLES = 'eventsMinBattles'
    EVENT_MAX_BATTLES = 'eventsMaxBattles'
    BONUSES_PER_DAY = 'bonusesPerDay'
    SHOW_CASE_ENABLED = 'isShowCaseEnabled'


class PetsConsts(object):
    CONFIG_NAME = 'pets_config'
    PETS = 'pets'
    PET = 'pet'
    PET_ID = 'id'
    PET_TYPE = 'type'
    PET_PREFAB = 'prefab'
    PET_BREED = 'breed'
    PET_EVENTS = 'events'
    PET_EVENT_IDS = 'eventIDs'
    PET_BONUSES = 'bonuses'
    PET_BONUS_IDS = 'bonusIDs'
    PET_NAMES = 'names'
    PET_NAMES_DEFAULT = 'default'
    PET_NAMES_DEFAULT_LOCKED = 'defaultLocked'
    PET_NAMES_UNLOCKED = 'unlockedNamesIDs'
    PET_SYNERGY_GROUP_ID = 'synergyGroupID'
    PET_PRICE = 'price'
    STOCK_NAMES = 'stockNames'


class PetPromoConsts(object):
    CONFIG_NAME = 'pet_promotion'
    IS_ENABLED = 'isEnabled'
    PETS = 'pets'
    PET = 'pet'
    PET_ID = 'id'
    URL = 'url'
    SOURCES = 'sources'
    SHOP_URL = 'shopUrl'
    INGAME_LINK = 'ingameLink'


class PetEventTypeConsts(object):
    BASIC = 'basic'
    UNIQUE = 'unique'


class PetEventsConsts(object):
    CONFIG_NAME = 'pets_events'
    EVENTS = 'events'
    EVENT = 'event'
    EVENT_ID = 'id'
    EVENT_TYPE = 'type'
    EVENT_REWARD = 'rewardID'


class PetBonusesConsts(object):
    CONFIG_NAME = 'pets_bonuses'
    BONUSES = 'bonuses'
    BONUS = 'bonus'
    BONUS_ID = 'id'
    BONUS_RESOURCE = 'bonusResource'
    EMPTY_BONUS = (0, 0, False)


class PET_SYSTEM_BONUS_RESOURCE_TYPE(object):
    UNKNOWN = 0
    CREDITS = 1


PET_SYSTEM_BONUS_TEXT_TO_RESOURCE = {'unknown': PET_SYSTEM_BONUS_RESOURCE_TYPE.UNKNOWN,
 'credits': PET_SYSTEM_BONUS_RESOURCE_TYPE.CREDITS}
PET_SYSTEM_RESOURCE_TO_TEXT = {v:k for k, v in PET_SYSTEM_BONUS_TEXT_TO_RESOURCE.iteritems()}

class SYNERGY_POINTS_TYPE(object):
    EVENT_INTERACTION = 'eventInteraction'
    FIRST_CLICK = 'firstClick'
    SERVER_ONLY = (EVENT_INTERACTION,)
    ALL = (EVENT_INTERACTION, FIRST_CLICK)


SYNERGY_POINTS_TYPE_TO_IDX = {key:idx for idx, key in enumerate(SYNERGY_POINTS_TYPE.ALL, 1)}
SYNERGY_POINTS_IDX_TO_TYPE = {idx:key for key, idx in SYNERGY_POINTS_TYPE_TO_IDX.iteritems()}

class PetSynergyConsts(object):
    CONFIG_NAME = 'pets_synergy'
    POINTS = 'points'
    SYNERGIES = 'synergies'
    SYNERGY = 'synergy'
    SYNERGY_ID = 'id'
    SYNERGY_LEVELS = 'levels'
    DECAY_DAYS = 'decayDays'
    DECAY_POINTS = 'decayPoints'


class PetStateBehavior(object):
    BASIC = 0
    CALM = 1
    HIDDEN = 2
    ALL = (BASIC, CALM, HIDDEN)


class PetTrigger(object):
    LOGIN = 'login'
    TO_STORAGE = 'toStorage'
    FROM_STORAGE = 'fromStorage'
    MEDAL = 'medal'
    FIRST_CLICK = 'firstClick'
    TO_EVENT_SCREEN = 'toEventScreen'
    FROM_EVENT_SCREEN = 'fromEventScreen'
    ALL = (LOGIN,
     TO_STORAGE,
     FROM_STORAGE,
     MEDAL,
     FIRST_CLICK,
     TO_EVENT_SCREEN,
     FROM_EVENT_SCREEN)


class StorageStaticTrigger(object):
    EMPTY = 0
    DISABLED = 1
    IDLE = 2


class AnimationStateName(object):
    DEFAULT = 'default'
    DISABLED = 'disabled'
    HIDDEN = 'hidden'
    PROMOTION = 'promotion'
    ALL = (DEFAULT,
     DISABLED,
     HIDDEN,
     PROMOTION)


class PetStaticTrigger(object):
    AFK = 0
    IDLE = 1
    EVENT = 2


class PetHangarObject(object):
    STORAGE = 'petStorage'
    PET = 'pet'
    ALL = (STORAGE, PET)


class PetAchievementAnimation(object):
    Warrior = RECORD_DB_IDS[('achievements', 'warrior')]


class PetSounds(object):
    PET_EVENT_HIGHLIGHT = 'pet_system_event_highlight'
    HIGHLIGHT = 'highlight'
