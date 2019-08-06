# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/festival_constants.py
COLLECTION_XML_PATH = 'scripts/item_defs/festival/collection.xml'
PROGRESS_REWARDS_XML_PATH = 'scripts/item_defs/festival/progress_rewards.xml'

class FEST_ITEM_QUALITY(object):
    STARTING = 'starting'
    COMMON = 'common'
    SPECIAL = 'special'
    ALL = (STARTING, COMMON, SPECIAL)


class FEST_ITEM_TYPE(object):
    BASIS = 'basis'
    EMBLEM = 'emblem'
    TITLE = 'title'
    RANK = 'rank'
    ANY = 'any'
    ALL = (BASIS,
     EMBLEM,
     TITLE,
     RANK)
    RANDOM = (ANY,
     BASIS,
     EMBLEM,
     TITLE)
    INFO = (ANY, BASIS)


class FEST_CONFIG(object):
    PACKAGES = 'packages'
    RANDOM_PRICES = 'randomPrices'
    FESTIVAL_ENABLED = 'isEnabled'
    PLAYER_CARDS_ENABLED = 'isPlayerCardsEnabled'


FEST_TYPE_IDS = {name:idx for idx, name in enumerate(FEST_ITEM_TYPE.ALL)}
FEST_INVALID_COST = -1
BOT_PLAYER_CARD = (1, 35, 87, 116)
MAX_FESTIVAL_ITEM_ID = 500
