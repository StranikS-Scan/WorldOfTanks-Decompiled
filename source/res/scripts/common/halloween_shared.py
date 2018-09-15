# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/halloween_shared.py
import calendar
SUPPLY_DROP_TOKENS_EXPIRY_TIME = calendar.timegm((2018, 1, 1, 0, 0, 0))
SUPPLY_DROP_LEVELS = [1,
 2,
 3,
 4]
SUPPLY_DROP_TOKEN_PREFIX = 'hsd:'
SUPPLY_DROP_TOKENS = tuple(('%s%d' % (SUPPLY_DROP_TOKEN_PREFIX, lvl) for lvl in SUPPLY_DROP_LEVELS))
SUPPLY_DROP_LEVEL_BASIC = 1
SUPPLY_DROP_LEVEL_ELITE = 2
SUPPLY_DROP_LEVEL_WEEKLY = 3
SUPPLY_DROP_LEVEL_ULTIMATE = 4
SUPPLY_DROP_INITIAL_TOKEN_GIVEN = 'hsd:initial'
LEVIATHAN_COMPACT_DESCRIPTION = 65297
MINION_COMPACT_DESCRIPTIONS = {46401, 46145}
LEVIATHAN_RAM_IMPULSE_SCALE = 2.0
MINION_RAM_IMPULSE_SCALE = 1.0
HALLOWEEN_QUEST_PREFIX = 'HE17_'
HALLOWEEN_MARATHON_QUEST_PREFIX = 'marathon:%s' % HALLOWEEN_QUEST_PREFIX
HALLOWEEN_REWARD_QUEST_PREFIX = 'HE17_OPEN_'
HALLOWEEN_ACHIEVEMENT_PREFIX = 'HE17A'
HALLOWEEN_SUPPLY_DROP_SELECTIONID_PREFIX = 'halloween_supply_drop_tier_'

class WrongParams(Exception):
    pass


class EVENT_STATE:
    NOT_STARTED = 0
    IN_PROGRESS = 1
    SUSPENDED = 2
    FINISHED = 3


EVENT_STATE_NAMES = {k:v for k, v in EVENT_STATE.__dict__.iteritems() if not k.startswith('_')}
EVENT_STATE_ACTIVE = (EVENT_STATE.IN_PROGRESS, EVENT_STATE.SUSPENDED)

def extractMyDropsFromTokens(tokens):
    """
    Get halloween supply drops info
    """
    data = {dropID:count for dropID, (_, count) in tokens.iteritems() if dropID in SUPPLY_DROP_TOKENS}
    return data
