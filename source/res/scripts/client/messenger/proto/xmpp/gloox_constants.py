# Embedded file name: scripts/client/messenger/proto/xmpp/gloox_constants.py
import BigWorld
_XmppClient = BigWorld.XmppClient

class PRESENCE(object):
    UNKNOWN = _XmppClient.PRESENCE_UNKNOWN
    AVAILABLE = _XmppClient.PRESENCE_AVAILABLE
    CHAT = _XmppClient.PRESENCE_CHAT
    AWAY = _XmppClient.PRESENCE_AWAY
    DND = _XmppClient.PRESENCE_DND
    XA = _XmppClient.PRESENCE_XA
    UNAVAILABLE = _XmppClient.PRESENCE_UNAVAILABLE
    RANGE = (UNKNOWN,
     AVAILABLE,
     CHAT,
     AWAY,
     DND,
     XA,
     UNAVAILABLE)


PRESENCES_ORDER = (PRESENCE.AVAILABLE,
 PRESENCE.CHAT,
 PRESENCE.AWAY,
 PRESENCE.DND,
 PRESENCE.XA,
 PRESENCE.UNAVAILABLE,
 PRESENCE.UNKNOWN)
PRESENCES_NAMES = dict([ (v, k) for k, v in PRESENCE.__dict__.iteritems() if v in PRESENCE.RANGE ])

class SUBSCRIPTION(object):
    OFF = _XmppClient.SUBSCRIPTION_OFF
    ON = _XmppClient.SUBSCRIPTION_ON
    PENDING = _XmppClient.SUBSCRIPTION_PENDING


SUBSCRIPTION_NAMES = dict([ (v, k) for k, v in SUBSCRIPTION.__dict__.iteritems() if not k.startswith('_') ])

class CONNECTION_STATE(object):
    DISCONNECTED = _XmppClient.STATE_DISCONNECTED
    CONNECTING = _XmppClient.STATE_CONNECTING
    AUTHENTICATING = _XmppClient.STATE_AUTHENTICATING
    INITIALIZING = _XmppClient.STATE_INITIALIZING
    CONNECTED = _XmppClient.STATE_CONNECTED


class DISCONNECT_REASON(object):
    BY_REQUEST = _XmppClient.DISCONNECT_BY_REQUEST
    AUTHENTICATION = _XmppClient.DISCONNECT_AUTHENTICATION
    OTHER_ERROR = _XmppClient.DISCONNECT_OTHER_ERROR


class LOG_LEVEL(object):
    DEBUG = _XmppClient.LOG_LEVEL_DEBUG
    WARNING = _XmppClient.LOG_LEVEL_WARNING
    ERROR = _XmppClient.LOG_LEVEL_ERROR


class LOG_SOURCE(object):
    UNKNOWN = 'Unknown source'
    PARSER = 'Parser'
    CLIENT = 'Client'
    CLIENT_BASE = 'Clientbase'
    COMPONENT = 'Component'
    DND = 'Dns'
    USER = 'User'
    CONNECTION_TCP_BASE = 'ConnectionTCPBase'
    CONNECTION_HTTP_PROXY = 'ConnectionHTTPProxy'
    CONNECTION_S5_PROXY = 'ConnectionSOCKS5Proxy'
    CONNECTION_TCP_CLIENT = 'ConnectionTCPClient'
    CONNECTION_TCP_SERVER = 'ConnectionTCPServer'
    CONNECTION_BOSH = 'ConnectionBOSH'
    CONNECTION_TLS = 'ConnectionTLS'
    S5B_MANAGER = 'S5BManager'
    S5_BYTES_STREAM = 'SOCKS5Bytestream'
    XML_INCOMING = 'XmlIncoming'
    XML_OUTGOING = 'XmlOutgoing'
    XML_STREAM = (XML_INCOMING, XML_OUTGOING)


class IQ_TYPE(object):
    GET = _XmppClient.IQ_TYPE_GET
    SET = _XmppClient.IQ_TYPE_SET
    RESULT = _XmppClient.IQ_TYPE_RESULT
    ERROR = _XmppClient.IQ_TYPE_ERROR
    INVALID = _XmppClient.IQ_TYPE_INVALID


class MESSAGE_TYPE(object):
    CHAT = 1
    ERROR = 2
    GROUPCHAT = 4
    HEADLINE = 8
    NORMAL = 16
    INVALID = 32


class MESSAGE_TYPE_ATTR(object):
    CHAT = 'chat'
    GROUPCHAT = 'groupchat'
    NORMAL = 'normal'


MESSAGE_TYPE_TO_ATTR = {MESSAGE_TYPE.CHAT: MESSAGE_TYPE_ATTR.CHAT,
 MESSAGE_TYPE.GROUPCHAT: MESSAGE_TYPE_ATTR.GROUPCHAT,
 MESSAGE_TYPE.NORMAL: MESSAGE_TYPE_ATTR.NORMAL}

class ERROR_TYPE(object):
    MODIFY = 'modify'
    CANCEL = 'cancel'
    AUTH = 'auth'
    WAIT = 'wait'


class CONNECTION_IMPL_TYPE(object):
    TCP = 1
    BOSH = 2


class ROSTER_CONTEXT(object):
    REQUEST_ROSTER = 0
    PUSH_ROSTER_ITEM = 1
    REMOVE_ROSTER_ITEM = 2


class GLOOX_EVENT(object):
    CONNECTED, LOGIN, DISCONNECTED, ROSTER_RESULT, ROSTER_ITEM_SET, ROSTER_ITEM_REMOVED, PRESENCE, SUBSCRIPTION_REQUEST, LOG, IQ, ROSTER_QUERY, MESSAGE = ALL = range(0, 12)


GLOOX_EVENTS_NAMES = dict([ (v, k) for k, v in GLOOX_EVENT.__dict__.iteritems() if v in GLOOX_EVENT.ALL ])
INBOUND_SUB_BATCH_SIZE = 100
INBOUND_SUB_INTERVAL = 2

class CHAT_STATE(object):
    UNDEFINED = ''
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    GONE = 'gone'
    COMPOSING = 'composing'
    PAUSED = 'paused'
    RANGE = (ACTIVE,
     INACTIVE,
     GONE,
     COMPOSING,
     PAUSED)
