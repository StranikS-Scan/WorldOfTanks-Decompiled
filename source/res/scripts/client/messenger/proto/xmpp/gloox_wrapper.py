# Embedded file name: scripts/client/messenger/proto/xmpp/gloox_wrapper.py
from collections import defaultdict
import weakref
import BigWorld
from constants import IGR_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION
from external_strings_utils import unicode_from_utf8
from messenger.proto.xmpp.gloox_constants import PRESENCE, CONNECTION_STATE, DISCONNECT_REASON, GLOOX_EVENT
from messenger.proto.xmpp.jid import ContactJID, ContactBareJID
from messenger.proto.xmpp.log_output import CLIENT_LOG_AREA, g_logOutput
from messenger.proto.xmpp.resources import Resource, ResourceWithIGR
_GLOOX_EVENTS_LISTENERS = (('onConnect', 'onConnected'),
 ('onReady', 'onLogin'),
 ('onDisconnect', 'onDisconnected'),
 ('onRosterResultReceived', 'onRosterResultReceived'),
 ('onNewRosterItem', 'onRosterItemSet'),
 ('onRosterItemRemove', 'onRosterItemRemoved'),
 ('onNewRosterResource', 'onRosterResourceAdded'),
 ('onRosterResourceRemove', 'onRosterResourceRemoved'),
 ('onSubscribe', 'onSubscriptionRequest'),
 ('onLog', 'onLog'),
 ('onHandleIq', 'onHandleIq'),
 ('onRosterQuerySend', 'onRosterQuerySend'),
 ('onHandleMsg', 'onHandleMsg'),
 ('onHandlePresenceWithIGR', 'onHandlePresenceWithIGR'))

class ClientDecorator(object):

    def __init__(self):
        super(ClientDecorator, self).__init__()
        self.__client = BigWorld.XmppClient()
        self.__handlers = defaultdict(set)
        self.__address = None
        return

    def init(self):
        client = self.__client
        ClientHolder._clearClient()
        for handlerName, listenerName in _GLOOX_EVENTS_LISTENERS:
            if not hasattr(client, handlerName):
                g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Handler no is found', handlerName)
                continue
            handler = getattr(client, handlerName)
            if handler:
                g_logOutput.warning(CLIENT_LOG_AREA.PY_WRAPPER, 'Handler already is set', handlerName)
                continue
            listener = getattr(self, listenerName, None)
            if listener is None or not callable(listener):
                g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Listener no is found', listenerName)
                continue
            setattr(client, handlerName, listener)

        ClientEventsHandler._setClient(self)
        return

    def fini(self):
        client = self.__client
        for handlerName, _ in _GLOOX_EVENTS_LISTENERS:
            if not hasattr(client, handlerName):
                g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Handler no is found', handlerName)
                continue
            setattr(client, handlerName, None)

        self.__handlers.clear()
        g_logOutput.clear()
        ClientHolder._clearClient()
        return

    def connect(self, jid, host = '', port = -1):
        self.__address = (jid, host, port)
        self.__client.connect(jid, host, port)

    def connectBosh(self, jid, host = '', port = -1, url = ''):
        self.__address = (jid, host, port)
        self.__client.connectBosh(jid, host, port, url)

    def login(self, password):
        self.__client.login(password)

    def disconnect(self):
        self.__client.disconnect()

    def getConnectionState(self):
        return self.__client.connectionState

    def getConnectionAddress(self):
        return self.__address

    def isConnected(self):
        return self.__client.connectionState == CONNECTION_STATE.CONNECTED

    def isDisconnected(self):
        return self.__client.connectionState == CONNECTION_STATE.DISCONNECTED

    def isConnecting(self):
        state = self.__client.connectionState
        return state in [CONNECTION_STATE.CONNECTING, CONNECTION_STATE.AUTHENTICATING, CONNECTION_STATE.INITIALIZING]

    def getClientPresence(self):
        return self.__client.presence

    def setClientPresence(self, presence):
        if presence not in PRESENCE.RANGE:
            g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Value of presence is invalid', presence)
            return
        self.__client.presence = presence

    def setClientPresenceWithIGR(self, presence, igrID = 0, igrRoomID = 0):
        if presence not in PRESENCE.RANGE:
            g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Value of presence is invalid', presence)
            return
        self.__client.setPresenceWithIGR(presence, str(igrID), str(igrRoomID))

    def sendIQ(self, query):
        return self.__client.sendCustomQuery(query.getType(), query.getBody())

    def sendMessage(self, message):
        self.__client.sendCustomMessage(message.getType(), str(message.getTo()), message.getBody(), message.getCustomTag())

    def setContactToRoster(self, jid, name = '', groups = None):
        if groups is None:
            groups = set()
        self.__client.add(str(jid), name, groups)
        return

    def removeContactFromRoster(self, jid):
        self.__client.remove(str(jid))

    def askSubscription(self, jid, message = ''):
        self.__client.subscribe(str(jid), message)

    def removeSubscribeTo(self, jid):
        self.__client.unsubscribe(str(jid))

    def approveSubscription(self, jid, message = ''):
        self.__client.setSubscribed(str(jid), message)

    def cancelSubscription(self, jid, message = ''):
        self.__client.setUnsubscribed(str(jid), message)

    def registerHandler(self, event, handler):
        if event in GLOOX_EVENT.ALL:
            handlers = self.__handlers[event]
            if handler in handlers:
                g_logOutput.warning(CLIENT_LOG_AREA.PY_WRAPPER, 'handler already exists', event, handler)
            else:
                if not hasattr(handler, '__self__') or not isinstance(handler.__self__, ClientEventsHandler):
                    g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Class of handler is not subclass of ClientEventsHandler', handler)
                    return
                if callable(handler):
                    handlers.add(handler)
                else:
                    g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Handler is invalid', handler)
        else:
            g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Event is not found', event)

    def unregisterHandler(self, event, handler):
        if event in GLOOX_EVENT.ALL:
            handlers = self.__handlers[event]
            if handler in handlers:
                handlers.remove(handler)
        else:
            g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, 'Event is not found', event)

    def onConnected(self):
        self.__handleEvent(GLOOX_EVENT.CONNECTED)

    def onLogin(self):
        self.__handleEvent(GLOOX_EVENT.LOGIN)

    def onDisconnected(self, reason = DISCONNECT_REASON.BY_REQUEST, description = None):
        if reason != DISCONNECT_REASON.BY_REQUEST:
            self.__address = None
        self.__handleEvent(GLOOX_EVENT.DISCONNECTED, reason, description)
        return

    def onRosterResultReceived(self, roster):

        def generator():
            for jid, name, groups, to, from_ in roster:
                yield (ContactJID(jid),
                 name,
                 groups,
                 to,
                 from_)

        self.__handleEvent(GLOOX_EVENT.ROSTER_RESULT, generator)

    def onRosterItemSet(self, jid, name, groups, to, from_):
        self.__handleEvent(GLOOX_EVENT.ROSTER_ITEM_SET, ContactJID(jid), name, groups, to, from_)

    def onRosterItemRemoved(self, jid):
        self.__handleEvent(GLOOX_EVENT.ROSTER_ITEM_REMOVED, ContactJID(jid))

    def onRosterResourceAdded(self, jid, priority, status, presence):
        self.__handleEvent(GLOOX_EVENT.ROSTER_RESOURCE_ADDED, ContactJID(jid), Resource(priority, status, presence))

    def onRosterResourceRemoved(self, jid):
        self.__handleEvent(GLOOX_EVENT.ROSTER_RESOURCE_REMOVED, ContactJID(jid))

    def onSubscriptionRequest(self, jid, message, nickname):
        self.__handleEvent(GLOOX_EVENT.SUBSCRIPTION_REQUEST, ContactJID(jid), nickname, message)

    def onLog(self, level, source, message):
        self.__handleEvent(GLOOX_EVENT.LOG, level, source, message)

    def onHandleMsg(self, msgID, msgType, body, jidFrom, pyGlooxTag):
        try:
            body, _ = unicode_from_utf8(body)
        except (UnicodeDecodeError, TypeError, ValueError):
            LOG_CURRENT_EXCEPTION()

        self.__handleEvent(GLOOX_EVENT.MESSAGE, msgID, msgType, body, ContactBareJID(jidFrom), pyGlooxTag)

    def onHandlePresenceWithIGR(self, jidFrom, igrID, igrRoomID):
        if igrID and igrID.isdigit():
            igrID = int(igrID)
        else:
            igrID = IGR_TYPE.NONE
        if igrRoomID and igrRoomID.isdigit():
            igrRoomID = int(igrRoomID)
        else:
            igrRoomID = 0
        self.__handleEvent(GLOOX_EVENT.IGR, ContactJID(jidFrom), ResourceWithIGR(igrID=igrID, igrRoomID=igrRoomID))

    def onHandleIq(self, iqID, iqType, pyGlooxTag):
        self.__handleEvent(GLOOX_EVENT.IQ, iqID, iqType, pyGlooxTag)

    def onRosterQuerySend(self, iqID, jid, context):
        self.__handleEvent(GLOOX_EVENT.ROSTER_QUERY, iqID, ContactJID(jid), context)

    def __handleEvent(self, eventName, *args, **kwargs):
        handlers = self.__handlers[eventName]
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except TypeError:
                g_logOutput.error(CLIENT_LOG_AREA.PY_WRAPPER, ' Handler is invoked with error', handler)
                LOG_CURRENT_EXCEPTION()


class ClientHolder(object):
    _client = None

    @classmethod
    def _setClient(cls, client):
        ClientEventsHandler._client = weakref.proxy(client)

    @classmethod
    def _clearClient(cls):
        cls._client = lambda *args: None

    def client(self):
        return ClientEventsHandler._client


class ClientEventsHandler(ClientHolder):

    def clear(self):
        pass

    def registerHandlers(self):
        raise NotImplementedError

    def unregisterHandlers(self):
        raise NotImplementedError
