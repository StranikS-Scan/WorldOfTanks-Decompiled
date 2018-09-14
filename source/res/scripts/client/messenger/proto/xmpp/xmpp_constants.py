# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_constants.py
from constants import IS_CLIENT
from debug_utils import LOG_WARNING
_COOLDOWN_OFFSET = 0.0 if IS_CLIENT else -0.1

class MESSAGE_LIMIT(object):
    COOLDOWN = 0.5
    MESSAGE_MAX_SIZE = 512
    HISTORY_MAX_LEN = 100


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
    NAME_MIN_CHARS_COUNT = 3
    NAME_MAX_CHARS_COUNT = 100
    PWD_MIN_CHARS_COUNT = 3
    PWD_MAX_CHARS_COUNT = 32


class USER_SEARCH_LIMITS(object):
    FIND_USERS_BY_NAME_MAX_RESULT_SIZE = 50
    FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC = 5.0 + _COOLDOWN_OFFSET


class CONTACT_ERROR_ID(object):
    CONTACT_ITEM_NOT_FOUND, ROSTER_ITEM_EXISTS, ROSTER_ITEM_NOT_FOUND, FRIENDSHIP_APPROVED, FRIENDSHIP_CANCELED, FRIENDSHIP_RQ_PROCESS, BLOCK_ITEM_EXISTS, BLOCK_ITEM_NOT_FOUND, MUTED_ITEM_NOT_FOUND, GROUP_EMPTY, GROUP_EXISTS, GROUP_NOT_FOUND, GROUP_INVALID_NAME, NOTE_EMPTY, NOTE_NOT_FOUND = range(1, 16)


CONTACT_ERROR_NAMES = {v:k for k, v in CONTACT_ERROR_ID.__dict__.iteritems() if not k.startswith('_')}

class LIMIT_ERROR_ID(object):
    MAX_ROSTER_ITEMS, MAX_GROUP, MAX_BLOCK_ITEMS, GROUP_INVALID_LENGTH, NOTE_INVALID_LENGTH, CHANNEL_INVALID_LENGTH, PWD_INVALID_LENGTH = range(1, 8)


LIMIT_ERROR_NAMES = {v:k for k, v in LIMIT_ERROR_ID.__dict__.iteritems() if not k.startswith('_')}

class CHANNEL_ERROR_ID(object):
    NAME_EMPTY, NAME_INVALID, PASSWORD_EMPTY, PASSWORD_INVALID, RETYPE_EMPTY, RETYPE_INVALID, PASSWORDS_NOT_EQUALS, NAME_ALREADY_EXISTS = range(1, 9)


CHANNEL_ERROR_NAMES = {v:k for k, v in CHANNEL_ERROR_ID.__dict__.iteritems() if not k.startswith('_')}

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
            LOG_WARNING('Component is not supported', component)

        return bitmask


class MUC_STATUS(object):
    SELF_PRESENCE = 110
    CREATE_ROOM = 201
    INCLUDE_PRESENCE_STANZA = (CREATE_ROOM, SELF_PRESENCE)


class SERVICE_DISCO_FEATURE(object):
    MUC_PASSWORD_PROTECTED = 'muc_passwordprotected'


class FORM_TYPE(object):
    UNDEFINED = ''
    FORM = 'form'
    SUBMIT = 'submit'
    CANCEL = 'cancel'
    RESULT = 'result'
    RANGE = (FORM,
     SUBMIT,
     CANCEL,
     RESULT)


class MUC_CREATION_ERROR(object):
    UNDEFINED = 0
    NAME_EXISTS = 201
    LIMIT_COUNT = 202
    LIMIT_PASS = 203
    LIMIT_NAME = 204
    WRONG_SYMBOL = 205
    WRONG_WORD = 206


MUC_CREATION_ERROR_NAMES = {v:k for k, v in MUC_CREATION_ERROR.__dict__.iteritems() if not k.startswith('_')}

class XMPP_MUC_CHANNEL_TYPE(object):
    UNKNOWN = 0
    STANDARD = 1
    USERS = 2
    CLANS = 3
    COMPANY = 4


XMPP_MUC_USER_TEMPLATE_GROUPS = {'owner': 'channelOwner',
 'admin': 'chatAdmin',
 'moderator': 'channelModerator'}
