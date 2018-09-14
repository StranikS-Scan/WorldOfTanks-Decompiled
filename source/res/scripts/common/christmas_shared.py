# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/christmas_shared.py
import calendar
from itertools import imap, ifilter
CHRISTMAS_TOY_TOKEN_PREFIX = 'xm'
CHRISTMAS_TOY_TOKEN_EXPIRY_TIME = calendar.timegm((2017, 1, 16, 6, 0, 0))
FINAL_PRIZE_TOKENS_EXPIRY_TIME = calendar.timegm((2017, 7, 1, 6, 0, 0))
FINAL_PRIZE_LEVELS = [1,
 2,
 3,
 4,
 5,
 6,
 7,
 8,
 9,
 10]
FINAL_PRIZE_TOKEN_PREFIX = 'c:'
FINAL_PRIZE_TOKENS = tuple(('%s%d' % (FINAL_PRIZE_TOKEN_PREFIX, lvl) for lvl in FINAL_PRIZE_LEVELS))
TREE_RATING = [0,
 5,
 10,
 16,
 24,
 32,
 42,
 52,
 64,
 80]
SECRET_CONVERSIONS_LOWER_BOUND = 1000
CHRISTMAS_TREE_RANK_RANGE = frozenset(xrange(1, 6))
BOX_COLORS = ('yellow', 'purple', 'green', 'blue', 'orange')

class NotEnoughToys(Exception):
    pass


class UnknownToy(Exception):
    pass


class WrongToy(Exception):
    pass


class BadConversion(Exception):
    pass


class WrongParams(Exception):
    pass


def ratingToLevel(r):
    for level, rating in enumerate(TREE_RATING):
        if r < rating:
            return level

    return level + 1


def getUpperLvlBound(level):
    return TREE_RATING[level] - 1 if level < 10 else TREE_RATING[level - 1]


def ratingToLevelRange(rating):
    level = ratingToLevel(rating)
    upperLevelBound = getUpperLvlBound(level)
    return (level, TREE_RATING[level - 1], upperLevelBound)


class EVENT_STATE:
    NOT_STARTED = 0
    IN_PROGRESS = 1
    SUSPENDED = 2
    FINISHED = 3


EVENT_STATE_NAMES = {k:v for k, v in EVENT_STATE.__dict__.iteritems() if not k.startswith('_')}
EVENT_STATE_ACTIVE = (EVENT_STATE.IN_PROGRESS, EVENT_STATE.SUSPENDED)

class TOY_TYPE:
    TOP = 1
    GARLAND = 2
    HANGING = 3
    STANDING = 4
    TANK_CAMOUFLAGE = 5
    TANK_BOARD = 6
    TANK_TURRET = 7
    TANK_FRONT = 8


TOY_TYPE_NAMES = {k:v for k, v in TOY_TYPE.__dict__.iteritems() if not k.startswith('_')}
TOY_TYPE_ID_TO_NAME = {v:k for k, v in TOY_TYPE_NAMES.iteritems()}
CHRISTMAS_TREE_SCHEMA = (TOY_TYPE.TOP,
 TOY_TYPE.HANGING,
 TOY_TYPE.HANGING,
 TOY_TYPE.HANGING,
 TOY_TYPE.GARLAND,
 TOY_TYPE.HANGING,
 TOY_TYPE.HANGING,
 TOY_TYPE.GARLAND,
 TOY_TYPE.HANGING,
 TOY_TYPE.HANGING,
 TOY_TYPE.STANDING,
 TOY_TYPE.STANDING,
 TOY_TYPE.TANK_FRONT,
 TOY_TYPE.TANK_BOARD,
 TOY_TYPE.TANK_TURRET,
 TOY_TYPE.TANK_CAMOUFLAGE)
TREE_DECORATIONS = (TOY_TYPE.TOP,
 TOY_TYPE.GARLAND,
 TOY_TYPE.HANGING,
 TOY_TYPE.STANDING)
TANK_DECORATIONS = (TOY_TYPE.TANK_CAMOUFLAGE,
 TOY_TYPE.TANK_BOARD,
 TOY_TYPE.TANK_TURRET,
 TOY_TYPE.TANK_FRONT)
DEFAULT_ID = 0
DEFAULT_CHRISTMAS_TREE_FILL = (DEFAULT_ID,) * len(CHRISTMAS_TREE_SCHEMA)

def __extractToyData(tokenData):
    tokenUid, (_, count) = tokenData
    toyID = getToyID(tokenUid)
    if toyID is not None:
        return (toyID, count)
    else:
        return
        return


def getToyID(tokenUid):
    return int(tokenUid[len(CHRISTMAS_TOY_TOKEN_PREFIX):]) if tokenUid.startswith(CHRISTMAS_TOY_TOKEN_PREFIX) else None


def extractMyToysFromTokens(tokens, knownToys):
    selector = ifilter(None, imap(__extractToyData, tokens.iteritems()))
    return {toyID:count for toyID, count in selector if toyID in knownToys}


def calcChristmasTreeRating(knownToys, christmasTreeFill):
    rating = 0
    for toyID in christmasTreeFill:
        if not toyID:
            continue
        rating += knownToys[toyID]['rating']

    return rating


def extractMyChestsFromTokens(tokens):
    """
    Get christmas chests info
    """
    data = {chestID:count for chestID, (_, count) in tokens.iteritems() if chestID in FINAL_PRIZE_TOKENS}
    return data


class CHEST_STATE:
    RECEIVED = 1
    RECEIVING_GIFTS = 2
    USED = 3


class CHRISTMAS_TOOLTIPS_IDS:
    TREE = 1
    TANK = 2
    GIFT = 3
    ALL = (TREE, TANK, GIFT)
