# Embedded file name: scripts/client/messenger/m_constants.py
from collections import namedtuple
MESSENGER_XML_FILE = 'messenger'
MESSENGER_I18N_FILE = 'messenger'
MESSENGER_XML_FILE_PATH = 'gui/{0:>s}.xml'.format(MESSENGER_XML_FILE)
MESSAGE_FLOOD_COOLDOWN = 20
BREAKERS_MAX_LENGTH = 1
MESSAGES_HISTORY_MAX_LEN = 50
BATTLE_SHARED_HISTORY_MAX_LEN = 250
SCH_MSGS_MAX_LENGTH = 250
CHANNEL_NAME_MIN_LENGTH = 3
CHANNEL_NAME_MAX_LENGTH = 32
CHANNEL_PWD_MIN_LENGTH = 3
CHANNEL_PWD_MAX_LENGTH = 12

class MESSENGER_SCOPE(object):
    UNKNOWN = 0
    LOGIN = 1
    LOBBY = 2
    BATTLE = 3


GUI_FORCED_CLOSE_ON_LOGIN = (MESSENGER_SCOPE.LOBBY, MESSENGER_SCOPE.BATTLE)

class PROTO_TYPE(object):
    BW = 1
    XMPP = 2
    BW_CHAT2 = 3
    MIGRATION = 4


PROTO_TYPE_NAMES = {v:k for k, v in PROTO_TYPE.__dict__.iteritems() if not k.startswith('_')}

class MESSENGER_COMMAND_TYPE(object):
    UNDEFINED = 0
    BATTLE = 1
    ADMIN = 2


class LAZY_CHANNEL(object):
    COMMON = '#chat:channels/common'
    COMPANIES = '#chat:channels/company'
    SPECIAL_BATTLES = '#chat:channels/special_battles'
    ALL = (COMMON, COMPANIES, SPECIAL_BATTLES)


class BATTLE_CHANNEL(object):
    _ITEM = namedtuple('_ITEM', 'initFlag name label')
    TEAM = _ITEM(1, 'team', 'TEAM : ')
    COMMON = _ITEM(2, 'common', 'COMMON : ')
    SQUAD = _ITEM(0, 'squad', 'SQUAD : ')
    REQUIRED = (TEAM, COMMON)
    ALL = (TEAM, COMMON, SQUAD)
    NAMES = tuple((x.name for x in ALL))

    @classmethod
    def isInitialized(cls, mask):
        for item in cls.REQUIRED:
            if not mask & item.initFlag:
                return False

        return True


class USER_TAG(object):
    CACHED = 'cached'
    WO_NOTIFICATION = 'woNotification'
    FRIEND = 'friend'
    IGNORED = 'ignored'
    MUTED = 'muted'
    CURRENT = 'himself'
    CLAN_MEMBER = 'clanMember'
    REFERRER = 'referrer'
    REFERRAL = 'referral'
    IGR_BASE = 'igr/base'
    IGR_PREMIUM = 'igr/premium'
    SUB_NONE = 'sub/none'
    SUB_PENDING_IN = 'sub/pendingIn'
    SUB_PENDING_OUT = 'sub/pendingOut'
    SUB_APPROVED = 'sub/approved'
    SUB_CANCELED = 'sub/canceled'
    SUB_IN_PROCESS = 'sub/inProcess'
    SUB_TO = 'sub/to'
    SUB_FROM = 'sub/from'
    PRESENCE_DND = 'presence/dnd'
    _SHARED_TAGS = {CLAN_MEMBER, REFERRER, REFERRAL}
    _CONTACT_LIST = {FRIEND, IGNORED, MUTED}
    _STORED_TO_CACHE = {MUTED}

    @classmethod
    def includeToContactsList(cls, tags):
        return tags & cls._CONTACT_LIST

    @classmethod
    def filterToStore(cls, tags):
        return tags & cls._STORED_TO_CACHE

    @classmethod
    def filterSharedTags(cls, tags):
        return tags & cls._SHARED_TAGS


class USER_ACTION_ID(object):
    UNDEFINED, FRIEND_ADDED, FRIEND_REMOVED, IGNORED_ADDED, IGNORED_REMOVED, MUTE_SET, MUTE_UNSET, GROUPS_CHANGED, SUBSCRIPTION_CHANGED, NOTE_CHANGED, IGR_CHANGED = range(11)


USER_ACTION_ID_NAMES = {v:k for k, v in USER_ACTION_ID.__dict__.iteritems() if not k.startswith('_')}

class USER_GUI_TYPE(object):
    CURRENT_PLAYER = 'himself'
    FRIEND = 'friend'
    IGNORED = 'ignored'
    OTHER = 'other'
    BREAKER = 'breaker'
    RANGE = (CURRENT_PLAYER,
     FRIEND,
     IGNORED,
     OTHER,
     BREAKER)


class CLIENT_ERROR_ID(object):
    GENERIC, LOCKED, WRONG_ARGS, NOT_CONNECTED, NOT_SUPPORTED, DBID_INVALID, NAME_EMPTY, NAME_INVALID, COOLDOWN = range(1, 10)


CLIENT_ERROR_NAMES = {v:k for k, v in CLIENT_ERROR_ID.__dict__.iteritems() if not k.startswith('_')}

class CLIENT_ACTION_ID(object):
    ADD_FRIEND, REMOVE_FRIEND, ADD_IGNORED, REMOVE_IGNORED, SET_MUTE, UNSET_MUTE, ADD_GROUP, CHANGE_GROUP, RQ_FRIENDSHIP, APPROVE_FRIENDSHIP, CANCEL_FRIENDSHIP, SET_NOTE, REMOVE_NOTE, SEND_MESSAGE = range(1, 15)


CLIENT_ACTION_NAMES = {v:k for k, v in CLIENT_ACTION_ID.__dict__.iteritems() if not k.startswith('_')}
