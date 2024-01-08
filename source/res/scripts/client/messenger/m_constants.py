# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/m_constants.py
from collections import namedtuple
from shared_utils import CONST_CONTAINER
MESSENGER_XML_FILE = 'messenger'
MESSENGER_I18N_FILE = 'messenger'
MESSENGER_XML_FILE_PATH = 'gui/{0:>s}.xml'.format(MESSENGER_XML_FILE)
MESSAGE_FLOOD_COOLDOWN = 20
BREAKERS_MAX_LENGTH = 1
MESSAGES_HISTORY_MAX_LEN = 50
BATTLE_SHARED_HISTORY_MAX_LEN = 250
SCH_MSGS_MAX_LENGTH = 250

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


class UserEntityScope(CONST_CONTAINER):
    LOBBY = 1
    BATTLE = 2


PROTO_TYPE_NAMES = {v:k for k, v in PROTO_TYPE.__dict__.iteritems() if not k.startswith('_')}

class MESSENGER_COMMAND_TYPE(object):
    UNDEFINED = 0
    BATTLE = 1
    ADMIN = 2


class LAZY_CHANNEL(object):
    COMMON = '#chat:channels/common'
    SPECIAL_BATTLES = '#chat:channels/special_battles'
    XMPP_COMMON = '#chat:channels/xmpp_common'
    ALL = (COMMON, SPECIAL_BATTLES, XMPP_COMMON)


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


USER_DEFAULT_NAME_PREFIX = '#settings:defaultNamePrefix'

class USER_TAG(object):
    CACHED = 'cached'
    WO_NOTIFICATION = 'woNotification'
    FRIEND = 'friend'
    IGNORED = 'ignored'
    IGNORED_TMP = 'tmp_ignored'
    MUTED = 'muted'
    CURRENT = 'himself'
    CLAN_MEMBER = 'ownClanMember'
    OTHER_CLAN_MEMBER = 'otherClanMember'
    IGR_BASE = 'igr/base'
    IGR_PREMIUM = 'igr/premium'
    INVALID_NAME = 'invalid/name'
    INVALID_RATING = 'invalid/rating'
    SEARCH = 'search'
    TEMP = 'temp'
    SUB_NONE = 'sub/none'
    SUB_PENDING_IN = 'sub/pendingIn'
    SUB_PENDING_OUT = 'sub/pendingOut'
    SUB_APPROVED = 'sub/approved'
    SUB_CANCELED = 'sub/canceled'
    SUB_IN_PROCESS = 'sub/inProcess'
    SUB_TO = 'sub/to'
    SUB_FROM = 'sub/from'
    PRESENCE_DND = 'presence/dnd'
    BAN_CHAT = 'ban/chat'
    _SHARED_TAGS = {CLAN_MEMBER, SEARCH, TEMP}
    _CLOSED_CONTACTS = {FRIEND, CLAN_MEMBER}
    _ALL_CONTACTS = {CLAN_MEMBER,
     FRIEND,
     IGNORED,
     IGNORED_TMP,
     SUB_PENDING_IN,
     MUTED}

    @classmethod
    def filterAllContactsTags(cls, tags):
        return tags & cls._ALL_CONTACTS

    @classmethod
    def filterClosedContactsTags(cls, tags):
        return tags & cls._CLOSED_CONTACTS

    @classmethod
    def filterSharedTags(cls, tags):
        return tags & cls._SHARED_TAGS

    @classmethod
    def filterToRemoveTags(cls, tags):
        return USER_TAG.TEMP in tags and not USER_TAG.filterAllContactsTags(tags)


class USER_ACTION_ID(object):
    UNDEFINED, FRIEND_ADDED, FRIEND_REMOVED, IGNORED_ADDED, IGNORED_REMOVED, TMP_IGNORED_ADDED, TMP_IGNORED_REMOVED, MUTE_SET, MUTE_UNSET, GROUPS_CHANGED, SUBSCRIPTION_CHANGED, NOTE_CHANGED = range(12)


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
    GENERIC, LOCKED, WRONG_ARGS, NOT_CONNECTED, NOT_SUPPORTED, DBID_INVALID, NAME_EMPTY, NAME_INVALID, COOLDOWN, WAITING_BEFORE_START = range(1, 11)


CLIENT_ERROR_NAMES = {v:k for k, v in CLIENT_ERROR_ID.__dict__.iteritems() if not k.startswith('_')}

class CLIENT_ACTION_ID(object):
    ADD_FRIEND, REMOVE_FRIEND, ADD_IGNORED, REMOVE_IGNORED, SET_MUTE, UNSET_MUTE, ADD_GROUP, CHANGE_GROUP, RQ_FRIENDSHIP, APPROVE_FRIENDSHIP, CANCEL_FRIENDSHIP, SET_NOTE, REMOVE_NOTE, SEND_MESSAGE, RQ_HISTORY, CREATE_USER_ROOM, JOIN_USER_ROOM, LEAVE_USER_ROOM, SEARCH_USER_ROOM, FIND_USERS_BY_PREFIX, JOIN_CLAN_ROOM = range(1, 22)


CLIENT_ACTION_NAMES = {v:k for k, v in CLIENT_ACTION_ID.__dict__.iteritems() if not k.startswith('_')}

class GAME_ONLINE_STATUS(object):
    UNDEFINED = 0
    IN_CLAN_CHAT = 1
    IN_SEARCH = 2
    ONLINE = IN_CLAN_CHAT

    @classmethod
    def addBit(cls, status, bit):
        if not status & bit:
            status |= bit
        return status

    @classmethod
    def removeBit(cls, status, bit):
        if status & bit > 0:
            status ^= bit
        return status

    @classmethod
    def update(cls, status, bit):
        if bit > 0:
            status = cls.addBit(status, bit)
        else:
            status = cls.removeBit(status, abs(bit))
        return status


class PRIMARY_CHANNEL_ORDER(object):
    LAZY = 1
    CLAN = 2
    SYSTEM = 3
    OTHER = 4


class SCH_CLIENT_MSG_TYPE(object):
    SYS_MSG_TYPE = 0
    PREMIUM_ACCOUNT_EXPIRY_MSG = 1
    AOGAS_NOTIFY_TYPE = 2
    ACTION_NOTIFY_TYPE = 3
    KOREA_PARENTAL_CONTROL_TYPE = 5
    TECH_TREE_ACTION_DISCOUNT = 6
    BLUEPRINTS_CONVERT_SALE = 7
    MAPBOX_PROGRESSION_REWARD = 8
    MAPBOX_SURVEY_AVAILABLE = 9
    MAPBOX_EVENT_ENDED = 10
    MAPBOX_EVENT_STARTED = 11
    BATTLE_MATTERS_TOKEN_AWARD = 14
    BATTLE_MATTERS_BATTLE_AWARD = 15
    WOTPLUS_GOLDRESERVE_ENABLED = 16
    WOTPLUS_GOLDRESERVE_DISABLED = 17
    WOTPLUS_PASSIVEXP_ENABLED = 18
    WOTPLUS_PASSIVEXP_DISABLED = 19
    INTEGRATED_AUCTION_RESULT = 20
    WOTPLUS_FEATURE_DISABLED = 21
    WOTPLUS_FREE_DEMOUNT_ENABLED = 22
    WOTPLUS_FREE_DEMOUNT_DISABLED = 23
    BONUS_EXCLUDED_MAP_ENABLED = 24
    BONUS_EXCLUDED_MAP_DISABLED = 25
    WOTPLUS_EXCLUSIVE_VEHICLE_ENABLED = 26
    WOTPLUS_EXCLUSIVE_VEHICLE_DISABLED = 27
    WINBACK_SELECTABLE_REWARD = 28
    WINBACK_BATTLERESULTS_REWARD = 29
    ACHIEVEMENTS20_SM_TYPE = 30
    WOTPLUS_DAILY_ATTENDANCES_ENABLED = 31
    WOTPLUS_DAILY_ATTENDANCES_DISABLED = 32
    WOTPLUS_DAILY_ATTENDANCE_REWARDED = 33
