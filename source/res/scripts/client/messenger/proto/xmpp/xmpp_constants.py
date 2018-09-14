# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_constants.py
from debug_utils import LOG_WARNING

class MESSAGE_LIMIT(object):
    COOLDOWN = 0.5
    MESSAGE_MAX_SIZE = 512
    HISTORY_MAX_LEN = 20


class CONTACT_LIMIT(object):
    ROSTER_MAX_COUNT = 300
    BLOCK_MAX_COUNT = 1000
    GROUPS_MAX_COUNT = 100
    GROUP_MIN_LENGTH = 1
    GROUP_MAX_LENGTH = 15
    NOTE_MIN_CHARS_COUNT = 1
    NOTE_MAX_CHARS_COUNT = 140
    NOTES_PER_PAGE = 100


class CHANNEL_LIMIT(object):
    MAX_SEARCH_RESULTS = 50


class CONTACT_ERROR_ID(object):
    CONTACT_ITEM_NOT_FOUND, ROSTER_ITEM_EXISTS, ROSTER_ITEM_NOT_FOUND, FRIENDSHIP_APPROVED, FRIENDSHIP_CANCELED, FRIENDSHIP_RQ_PROCESS, BLOCK_ITEM_EXISTS, BLOCK_ITEM_NOT_FOUND, MUTED_ITEM_NOT_FOUND, GROUP_EMPTY, GROUP_EXISTS, GROUP_NOT_FOUND, GROUP_INVALID_NAME, NOTE_EMPTY, NOTE_NOT_FOUND = range(1, 16)


CONTACT_ERROR_NAMES = {v:k for k, v in CONTACT_ERROR_ID.__dict__.iteritems() if not k.startswith('_')}

class LIMIT_ERROR_ID(object):
    MAX_ROSTER_ITEMS, MAX_GROUP, MAX_BLOCK_ITEMS, GROUP_INVALID_LENGTH, NOTE_INVALID_LENGTH = range(1, 6)


LIMIT_ERROR_NAMES = {v:k for k, v in LIMIT_ERROR_ID.__dict__.iteritems() if not k.startswith('_')}

class XMPP_ITEM_TYPE:
    EMPTY_ITEM = 0
    ROSTER_ITEM = 1
    BLOCK_ITEM = 2
    SUB_PENDING = 3
    ROSTER_BLOCK_ITEM = 4
    ROSTER_LIST = (ROSTER_ITEM, ROSTER_BLOCK_ITEM)
    BLOCKING_LIST = (BLOCK_ITEM, ROSTER_BLOCK_ITEM)


ANY_ITEM_LITERAL = 'all'

class XMPP_BAN_COMPONENT(object):
    BATTLE = 1
    PREBATTLE = 2
    PRIVATE = 4
    STANDARD = 8
    USER = 16
    CLAN = 32
    ALL = BATTLE | PREBATTLE | PRIVATE | STANDARD | USER | CLAN
    _STRING_TO_BITMASK = {'battle': BATTLE,
     'prebattle': PREBATTLE,
     'private': PRIVATE,
     'standard': STANDARD,
     'user': USER,
     'clan': CLAN,
     ANY_ITEM_LITERAL: ALL}

    @classmethod
    def fromString(cls, value):
        if not value:
            return cls.ALL
        bitmask = 0
        components = value.split(',')
        for component in components:
            component = component.strip()
            if component in cls._STRING_TO_BITMASK:
                bit = cls._STRING_TO_BITMASK[component]
                if bit == cls.ALL:
                    return cls.ALL
                if bitmask & bit == 0:
                    bitmask |= bit
            else:
                LOG_WARNING('Component is not supported', component)

        return bitmask
