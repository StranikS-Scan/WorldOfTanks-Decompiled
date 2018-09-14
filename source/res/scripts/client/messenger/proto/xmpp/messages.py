# Embedded file name: scripts/client/messenger/proto/xmpp/messages.py
import time
from debug_utils import LOG_ERROR
from messenger import g_settings
from messenger.ext.player_helpers import getPlayerDatabaseID, getPlayerName
from messenger.m_constants import USER_ACTION_ID, USER_TAG, CLIENT_ACTION_ID, PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IProtoLimits
from messenger.proto.shared_errors import ChatCoolDownError
from messenger.proto.xmpp import entities, find_criteria
from messenger.proto.xmpp.XmppCooldownManager import XmppCooldownManager
from messenger.proto.xmpp.decorators import xmpp_query, QUERY_SIGN
from messenger.proto.xmpp.errors import createChatBanError
from messenger.proto.xmpp.extensions.chat import ChatMessageHandler, ChatMessageHolder
from messenger.proto.xmpp.gloox_constants import GLOOX_EVENT as _EVENT, MESSAGE_TYPE
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler
from messenger.proto.xmpp.jid import makeContactJID, ContactBareJID
from messenger.proto.xmpp.wrappers import XMPPMessageData
from messenger.proto.xmpp.xmpp_constants import MESSAGE_LIMIT
from messenger.storage import storage_getter

class _MessageLimits(IProtoLimits):

    def getMessageMaxLength(self):
        return MESSAGE_LIMIT.MESSAGE_MAX_SIZE

    def getBroadcastCoolDown(self):
        return MESSAGE_LIMIT.COOLDOWN

    def getHistoryMaxLength(self):
        return MESSAGE_LIMIT.HISTORY_MAX_LEN


class _ChatSessions(ClientEventsHandler):
    __slots__ = ('__sessions',)

    def __init__(self):
        super(_ChatSessions, self).__init__()
        self.__sessions = set()

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
            channel = self._addChannel(search, jid.getDatabaseID(), name, True)
            if not channel:
                return
            g_messengerEvents.channels.onPlayerEnterChannelByAction(channel)
        else:
            g_messengerEvents.channels.onPlayerEnterChannelByAction(channel)
        self.__sessions.add(jid)

    def stopSession(self, jid):
        channel = self.channelsStorage.getChannel(entities.XMPPChatChannelEntity(jid))
        if channel:
            self._removeChannel(channel)
            self.__sessions.discard(jid)

    def sendMessage(self, jid, body, filters):
        channel = self.channelsStorage.getChannel(entities.XMPPChatChannelEntity(jid))
        if channel:
            if self.playerCtx.isChatBan():
                error = createChatBanError(self.playerCtx.getBanInfo())
                if error:
                    g_messengerEvents.onErrorReceived(error)
                    return
            dbID = getPlayerDatabaseID()
            name = getPlayerName()
            g_messengerEvents.channels.onMessageReceived(XMPPMessageData(dbID, name, filters.chainIn(dbID, body), time.time()), channel)
            self.client().sendMessage(ChatMessageHolder(jid, msgBody=body))

    def restoreSession(self, jid, state):
        channel = entities.XMPPChatChannelEntity(jid)
        jid = ContactBareJID(jid)
        if channel.setPersistentState(state):
            channel = self._addChannel(channel, jid.getDatabaseID(), channel.getProtoData().name, self.client().isConnected())
            if channel:
                self.__sessions.add(jid)

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

    def onMessageReceived(self, jid, body, _, info, sentAt):
        dbID = info['dbID']
        name = info['name']
        search = entities.XMPPChatChannelEntity(jid, name)
        channel = self.channelsStorage.getChannel(search)
        if not channel:
            channel = self._addChannel(search, dbID, name, True)
            if not channel:
                return
            self.__sessions.add(jid)
        if body:
            g_messengerEvents.channels.onMessageReceived(XMPPMessageData(dbID, name, body, sentAt), channel)

    def _addChannel(self, channel, dbID, name, isJoined):
        contact = self.usersStorage.getUser(dbID)
        if contact:
            if contact.isIgnored():
                return None
            isOnline = contact.isOnline()
        else:
            isOnline = False
        channel.addMembers([entities.XMPPMemberEntity(getPlayerDatabaseID(), getPlayerName(), True), entities.XMPPMemberEntity(dbID, name, isOnline)])
        if self.channelsStorage.addChannel(channel):
            g_messengerEvents.channels.onChannelInited(channel)
        channel.setJoined(isJoined)
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
        self.__chatSessions = _ChatSessions()
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
        register(_EVENT.CONNECTED, self.__handleConnected)
        register(_EVENT.DISCONNECTED, self.__handleDisconnected)
        register(_EVENT.MESSAGE, self.__handleMessage)
        events = g_messengerEvents.users
        events.onUsersListReceived += self.__me_onUsersListReceived
        events.onUserActionReceived += self.__me_onUserActionReceived
        events.onUserStatusUpdated += self.__me_onUserStatusUpdated

    def unregisterHandlers(self):
        unregister = self.client().unregisterHandler
        unregister(_EVENT.CONNECTED, self.__handleConnected)
        unregister(_EVENT.DISCONNECTED, self.__handleDisconnected)
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

    def __clearData(self):
        self.__chatSessions.clear()
        self.__receivedTags.clear()
        self.__pending = []

    def __setChannelsState(self, isJoined):
        channels = self.channelsStorage.getChannelsByCriteria(find_criteria.XMPPChannelFindCriteria())
        for channel in channels:
            channel.setJoined(isJoined)

    def __handleConnected(self):
        self.__setChannelsState(True)

    def __handleDisconnected(self, reason, description):
        self.__clearData()
        self.__setChannelsState(False)

    def __handleMessage(self, _, msgType, body, jid, pyGlooxTag):
        if msgType == MESSAGE_TYPE.CHAT:
            state, info, sentAt = ChatMessageHandler().handleTag(pyGlooxTag)
            if not info:
                LOG_ERROR('Can not find sender info', pyGlooxTag.getXml())
                return
            if body:
                body = self.__msgFilters.chainIn(info['dbID'], body)
            if _REQUIRED_USER_TAGS.issubset(self.__receivedTags):
                self.__chatSessions.onMessageReceived(jid, body, state, info, sentAt)
            else:
                self.__pending.insert(0, (msgType, (jid,
                  body,
                  state,
                  info,
                  sentAt)))

    def __me_onUsersListReceived(self, tags):
        self.__receivedTags.update(tags)
        if _REQUIRED_USER_TAGS.issubset(self.__receivedTags):
            while self.__pending:
                msgType, data = self.__pending.pop()
                if msgType == MESSAGE_TYPE.CHAT:
                    self.__chatSessions.onMessageReceived(*data)

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
