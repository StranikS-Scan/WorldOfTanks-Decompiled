# Embedded file name: scripts/client/messenger/m_constants.py
from collections import namedtuple
import chat_shared
from constants import PREBATTLE_TYPE
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


class MESSENGER_COMMAND_TYPE(object):
    UNDEFINED = 0
    BATTLE = 1
    ADMIN = 2


PROTO_TYPE_NAMES = dict([ (v, k) for k, v in PROTO_TYPE.__dict__.iteritems() ])

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


PREBATTLE_TYPE_CHAT_FLAG = {PREBATTLE_TYPE.SQUAD: chat_shared.CHAT_CHANNEL_SQUAD,
 PREBATTLE_TYPE.EVENT_SQUAD: chat_shared.CHAT_CHANNEL_SQUAD,
 PREBATTLE_TYPE.COMPANY: chat_shared.CHAT_CHANNEL_TEAM,
 PREBATTLE_TYPE.TRAINING: chat_shared.CHAT_CHANNEL_TRAINING,
 PREBATTLE_TYPE.CLAN: chat_shared.CHAT_CHANNEL_PREBATTLE_CLAN,
 PREBATTLE_TYPE.TOURNAMENT: chat_shared.CHAT_CHANNEL_TOURNAMENT,
 PREBATTLE_TYPE.UNIT: chat_shared.CHAT_CHANNEL_UNIT,
 PREBATTLE_TYPE.SORTIE: chat_shared.CHAT_CHANNEL_UNIT}
PREBATTLE_CHAT_FLAG_TYPE = dict(((v, k) for k, v in PREBATTLE_TYPE_CHAT_FLAG.iteritems()))

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


class USER_ROSTER_ACTION(object):
    AddToFriend, RemoveFromFriend, AddToIgnored, RemoveFromIgnored, SetMuted, UnsetMuted = range(6)
