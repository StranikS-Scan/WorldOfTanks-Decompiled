# Embedded file name: scripts/client/messenger/proto/xmpp/messages.py
import time
import operator
import BigWorld
from gui.shared.utils import getPlayerDatabaseID, getPlayerName
from messenger import g_settings
from messenger.m_constants import USER_ACTION_ID, USER_TAG, CLIENT_ACTION_ID, PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IProtoLimits
from messenger.proto.shared_errors import ChatCoolDownError
from messenger.proto.xmpp import entities, find_criteria, errors
from messenger.proto.xmpp.XmppCooldownManager import XmppCooldownManager
from messenger.proto.xmpp.decorators import xmpp_query, QUERY_SIGN
from messenger.proto.xmpp.errors import createChatBanError
from messenger.proto.xmpp.extensions.chat import ChatMessageHolder, GetChatHistoryQuery, MessageHandler
from messenger.proto.xmpp.gloox_constants import GLOOX_EVENT as _EVENT, MESSAGE_TYPE, IQ_TYPE, MESSAGE_TYPE_TO_ATTR
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler, ClientHolder
from messenger.proto.xmpp.jid import makeContactJID, ContactBareJID
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA
from messenger.proto.xmpp.wrappers import ChatMessage
from messenger.proto.xmpp.xmpp_constants import MESSAGE_LIMIT, XMPP_BAN_COMPONENT
from messenger.storage import storage_getter

class _MessageLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return MESSAGE_LIMIT.MESSAGE_MAX_SIZE

    def getBroadcastCoolDown(self):
        return MESSAGE_LIMIT.COOLDOWN

    def getHistoryMaxLength(self):
        return MESSAGE_LIMIT.HISTORY_MAX_LEN


class _HISTORY_RQ_STATE(object):
    FREE = 0
    WAIT = 1
    RESULT = 2
    COOLDOWN = 3
    UNAVAILABLE = 4


class _ChatHistoryRequester(ClientHolder):

    def __init__(self, limits):
        super(_ChatHistoryRequester, self).__init__()
        self.__cooldown = XmppCooldownManager(limits.getBroadcastCoolDown())
        self.__limit = limits.getHistoryMaxLength()
        self.__iqID = ''
        self.__pool = []
        self.__history = []
        self.__callbackID = None
        self.__state = _HISTORY_RQ_STATE.FREE
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    def clear(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self.__iqID = ''
        self.__pool = []
        self.__state = _HISTORY_RQ_STATE.FREE
        self.__cooldown = None
        return

    def request(self, jid):
        if self.__state == _HISTORY_RQ_STATE.UNAVAILABLE:
            self.__setChannelAvailable(jid)
            return
        if jid not in self.__pool:
            self.__pool.append(jid)
        if self.__state == _HISTORY_RQ_STATE.FREE:
            self.__doNextRequest()

    def cancel(self, jid):
        if jid in self.__pool:
            if jid == self.__pool[0]:
                if self.__callbackID is not None:
                    BigWorld.cancelCallback(self.__callbackID)
                    self.__callbackID = None
                self.__state = _HISTORY_RQ_STATE.FREE
                self.__pool.pop(0)
                self.__iqID = ''
                self.__history = []
                self.__doNextRequest()
            else:
                self.__pool.remove(jid)
        return

    def handleIQ(self, iqID, iqType, tag):
        if iqID == self.__iqID:
            if iqType == IQ_TYPE.RESULT:
                self.__state = _HISTORY_RQ_STATE.RESULT
            elif iqType == IQ_TYPE.ERROR:
                self.__state = _HISTORY_RQ_STATE.UNAVAILABLE
                error = errors.createServerActionError(CLIENT_ACTION_ID.RQ_HISTORY, tag)
                if error:
                    g_messengerEvents.onErrorReceived(error)
                while self.__pool:
                    self.__setChannelAvailable(self.__pool.pop(0))

            result = True
        else:
            result = False
        return result

    def addHistory(self, message):
        if not self.__state == _HISTORY_RQ_STATE.RESULT:
            raise AssertionError
            if message.body:
                self.__history.append(message)
            message.isFinalInHistory and self.__setChannelAvailable(self.__pool.pop(0))
            self.__history = []
            self.__state = _HISTORY_RQ_STATE.FREE
            self.__doNextRequest()

    def __setChannelAvailable(self, jid):
        channel = self.channelsStorage.getChannel(entities.XMPPChatChannelEntity(jid))
        if channel:
            if self.__history:
                g_messengerEvents.channels.onHistoryReceived(sorted(self.__history, key=operator.attrgetter('sentAt')), channel)
            channel.setJoined(True)

    def __doNextRequest(self):
        if self.__cooldown.isInProcess(CLIENT_ACTION_ID.RQ_HISTORY):
            self.__state = _HISTORY_RQ_STATE.COOLDOWN
            self.__callbackID = BigWorld.callback(self.__cooldown.getTime(CLIENT_ACTION_ID.RQ_HISTORY), self.__callback)
        else:
            if not self.__pool:
                return
            self.__state = _HISTORY_RQ_STATE.WAIT
            self.__iqID = self.client().sendIQ(GetChatHistoryQuery(self.__pool[0], self.__limit))
            self.__cooldown.process(CLIENT_ACTION_ID.RQ_HISTORY, 5.0)

    def __callback(self):
        self.__callbackID = None
        self.__state = _HISTORY_RQ_STATE.FREE
        self.__doNextRequest()
        return


class _ChatSessions(ClientEventsHandler):
    __slots__ = ('__sessions', '__historyRQ')

    def __init__(self, limits):
        super(_ChatSessions, self).__init__()
        self.__sessions = set()
        self.__historyRQ = _ChatHistoryRequester(limits)

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def clear(self):
        self.__sessions.clear()
        super(_ChatSessions, self).clear()

    def startSession(self, jid, name):
        search = entities.XMPPChatChannelEntity(jid, name)
        channel = self.channelsStorage.getChannel(search)
        if not channel:
            channel = self._addChannel(search, jid.getDatabaseID(), name)
            if not channel:
                return
        g_messengerEvents.channels.onPlayerEnterChannelByAction(channel)
        self.__sessions.add(jid)

    def stopSession(self, jid):
        channel = self.channelsStorage.getChannel(entities.XMPPChatChannelEntity(jid))
        if channel:
            self._removeChannel(channel)
            self.__sessions.discard(jid)
            self.__historyRQ.cancel(jid)

    def restoreSession(self, jid, state):
        channel = entities.XMPPChatChannelEntity(jid)
        jid = ContactBareJID(jid)
        if channel.setPersistentState(state) and jid not in self.__sessions:
            channel = self._addChannel(channel, jid.getDatabaseID(), channel.getProtoData().name)
            if channel:
                self.__sessions.add(jid)

    def sendMessage(self, jid, body, filters):
        channel = self.channelsStorage.getChannel(entities.XMPPChatChannelEntity(jid))
        if channel:
            if self.playerCtx.isBanned(components=XMPP_BAN_COMPONENT.PRIVATE):
                error = createChatBanError(self.playerCtx.getBanInfo())
                if error:
                    g_messengerEvents.onErrorReceived(error)
                    return
            dbID = getPlayerDatabaseID()
            name = getPlayerName()
            g_messengerEvents.channels.onMessageReceived(ChatMessage(dbID, name, filters.chainIn(dbID, body), time.time()), channel)
            self.client().sendMessage(ChatMessageHolder(jid, msgBody=body))

    def setContactPresence(self, contact):
        dbID = contact.getID()
        if contact.getProtoType() == PROTO_TYPE.XMPP:
            jid = contact.getJID()
        else:
            jid = makeContactJID(dbID)
        if jid not in self.__sessions:
            return
        channel = self.channelsStorage.getChannel(entities.XMPPChatChannelEntity(jid))
        if channel:
            member = channel.getMember(dbID)
            if member:
                member.setOnline(contact.isOnline())

    def addMessage(self, jid, message):
        if message.isHistory():
            self.__historyRQ.addHistory(message)
            return
        dbID = message.accountDBID
        name = message.accountName
        if jid not in self.__sessions and g_settings.userPrefs.chatContactsListOnly:
            contact = self.usersStorage.getUser(dbID)
            if not contact or not USER_TAG.filterClosedContactsTags(contact.getTags()):
                g_logOutput.debug(CLIENT_LOG_AREA.MESSAGE, "There is not closed contact in player's contacts list,contact's message is ignored", jid, name)
                return
        search = entities.XMPPChatChannelEntity(jid, name)
        channel = self.channelsStorage.getChannel(search)
        if not channel:
            channel = self._addChannel(search, dbID, name)
            if not channel:
                return
            self.__sessions.add(jid)
        if message.body:
            g_messengerEvents.channels.onMessageReceived(message, channel)

    def requestHistory(self, jid):
        if jid in self.__sessions:
            self.__historyRQ.request(jid)

    def handleIQ(self, iqID, iqType, pyGlooxTag):
        self.__historyRQ.handleIQ(iqID, iqType, pyGlooxTag)

    def _addChannel(self, channel, dbID, name):
        contact = self.usersStorage.getUser(dbID)
        if contact:
            if contact.isIgnored():
                return None
            isOnline = contact.isOnline()
        else:
            isOnline = False
        channel.addMembers([entities.XMPPMemberEntity(getPlayerDatabaseID(), getPlayerName(), True), entities.XMPPMemberEntity(dbID, name, isOnline)])
        if self.channelsStorage.addChannel(channel):
            channel.setStored(True)
            g_messengerEvents.channels.onChannelInited(channel)
        return channel

    def _removeChannel(self, channel):
        if self.channelsStorage.removeChannel(channel, clear=False):
            g_messengerEvents.channels.onChannelDestroyed(channel)
            channel.clear()


_REQUIRED_USER_TAGS = {USER_TAG.FRIEND, USER_TAG.IGNORED}

class MessagesManager(ClientEventsHandler):
    __slots__ = ('__msgFilters', '__limits', '__chatSessions', '__receivedTags', '__pending')

    def __init__(self):
        super(MessagesManager, self).__init__()
        self.__msgFilters = None
        self.__limits = _MessageLimits()
        self.__chatSessions = _ChatSessions(self.__limits)
        self.__isInited = False
        self.__receivedTags = set()
        self.__pending = []
        self.__cooldown = XmppCooldownManager(self.__limits.getBroadcastCoolDown())
        self.channelsStorage.onRestoredFromCache += self.__cs_onChannelsRestoredFromCache
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    def clear(self):
        self.channelsStorage.onRestoredFromCache -= self.__cs_onChannelsRestoredFromCache
        self.__clearData()
        super(MessagesManager, self).clear()

    def registerHandlers(self):
        register = self.client().registerHandler
        register(_EVENT.DISCONNECTED, self.__handleDisconnected)
        register(_EVENT.IQ, self.__handleIQ)
        register(_EVENT.MESSAGE, self.__handleMessage)
        events = g_messengerEvents.users
        events.onUsersListReceived += self.__me_onUsersListReceived
        events.onUserActionReceived += self.__me_onUserActionReceived
        events.onUserStatusUpdated += self.__me_onUserStatusUpdated

    def unregisterHandlers(self):
        unregister = self.client().unregisterHandler
        unregister(_EVENT.DISCONNECTED, self.__handleDisconnected)
        unregister(_EVENT.IQ, self.__handleIQ)
        unregister(_EVENT.MESSAGE, self.__handleMessage)
        events = g_messengerEvents.users
        events.onUsersListReceived -= self.__me_onUsersListReceived
        events.onUserActionReceived -= self.__me_onUserActionReceived
        events.onUserStatusUpdated -= self.__me_onUserStatusUpdated

    def setFilters(self, msgFilters):
        self.__msgFilters = msgFilters

    def isInCooldown(self):
        return self.__cooldown.isInProcess(CLIENT_ACTION_ID.SEND_MESSAGE)

    @xmpp_query(QUERY_SIGN.DATABASE_ID, QUERY_SIGN.ACCOUNT_NAME)
    def startChatSession(self, dbID, name):
        self.__chatSessions.startSession(makeContactJID(dbID), name)
        return (True, None)

    def stopChatSession(self, jid):
        self.__chatSessions.stopSession(ContactBareJID(jid))

    def sendChatMessage(self, jid, body):
        if self.__cooldown.isInProcess(CLIENT_ACTION_ID.SEND_MESSAGE):
            g_messengerEvents.onErrorReceived(ChatCoolDownError(CLIENT_ACTION_ID.SEND_MESSAGE, self.__limits.getBroadcastCoolDown()))
            return
        body = self.__msgFilters.chainOut(body, self.__limits)
        if not body:
            return
        self.__chatSessions.sendMessage(ContactBareJID(jid), body, self.__msgFilters)
        self.__cooldown.process(CLIENT_ACTION_ID.SEND_MESSAGE)

    def requestChatHistory(self, jid):
        self.__chatSessions.requestHistory(ContactBareJID(jid))

    def __clearData(self):
        self.__chatSessions.clear()
        self.__receivedTags.clear()
        self.__pending = []

    def __handleDisconnected(self, reason, description):
        self.__clearData()
        channels = self.channelsStorage.getChannelsByCriteria(find_criteria.XMPPChannelFindCriteria())
        for channel in channels:
            channel.setJoined(False)

    def __handleIQ(self, iqID, iqType, pyGlooxTag):
        self.__chatSessions.handleIQ(iqID, iqType, pyGlooxTag)

    def __handleMessage(self, _, msgType, body, jid, pyGlooxTag):
        if msgType not in MESSAGE_TYPE_TO_ATTR:
            return
        message = MessageHandler(MESSAGE_TYPE_TO_ATTR[msgType]).handleTag(pyGlooxTag)
        if not message.accountDBID:
            g_logOutput.error(CLIENT_LOG_AREA.MESSAGE, 'Can not find sender info', pyGlooxTag.getXml())
            return
        if body:
            message.body = self.__msgFilters.chainIn(message.accountDBID, body)
        if not _REQUIRED_USER_TAGS.issubset(self.__receivedTags):
            self.__pending.insert(0, (msgType, (jid, message)))
            return
        if msgType == MESSAGE_TYPE.CHAT or msgType == MESSAGE_TYPE.NORMAL and message.isHistory():
            self.__chatSessions.addMessage(jid, message)

    def __me_onUsersListReceived(self, tags):
        self.__receivedTags.update(tags)
        if _REQUIRED_USER_TAGS.issubset(self.__receivedTags):
            while self.__pending:
                msgType, data = self.__pending.pop()
                if msgType == MESSAGE_TYPE.CHAT:
                    self.__chatSessions.addMessage(*data)

    def __me_onUserActionReceived(self, actionID, user):
        if actionID == USER_ACTION_ID.IGNORED_ADDED:
            self.__chatSessions.stopSession(makeContactJID(user.getID()))

    def __me_onUserStatusUpdated(self, contact):
        self.__chatSessions.setContactPresence(contact)

    def __cs_onChannelsRestoredFromCache(self, stateGenerator):
        if not stateGenerator or not g_settings.server.XMPP.isEnabled():
            return
        for jid, state in stateGenerator(PROTO_TYPE.XMPP):
            self.__chatSessions.restoreSession(jid, state)
