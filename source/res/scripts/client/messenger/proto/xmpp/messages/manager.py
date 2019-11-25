# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/messages/manager.py
from messenger import g_settings
from messenger.m_constants import USER_TAG, CLIENT_ACTION_ID, PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_errors import ChatCoolDownError
from messenger.proto.xmpp import entities
from messenger.proto.xmpp import find_criteria
from messenger.proto.xmpp import jid as jid_entity
from messenger.proto.xmpp.XmppCooldownManager import XmppCooldownManager
from messenger.proto.xmpp.decorators import xmpp_query, QUERY_SIGN
from messenger.proto.xmpp.errors import createServerActionMessageError
from messenger.proto.xmpp.extensions import chat as chat_ext
from messenger.proto.xmpp.gloox_constants import GLOOX_EVENT as _EVENT, MESSAGE_TYPE, MESSAGE_TYPE_TO_ATTR
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler
from messenger.proto.xmpp.messages.chat_session import ChatSessionsProvider
from messenger.proto.xmpp.messages.muc import MUCProvider, ACTION_RESULT
from messenger.proto.xmpp.xmpp_constants import XMPP_MUC_CHANNEL_TYPE
from messenger.proto.xmpp.xmpp_limits import MessageLimits
from messenger.storage import storage_getter
_REQUIRED_USER_TAGS = {USER_TAG.FRIEND, USER_TAG.IGNORED}

class MessagesManager(ClientEventsHandler):
    __slots__ = ('__msgFilters', '__limits', '__chatSessions', '__muc', '__receivedTags', '__pending', '__cooldown')

    def __init__(self):
        super(MessagesManager, self).__init__()
        self.__msgFilters = None
        self.__limits = MessageLimits()
        self.__chatSessions = ChatSessionsProvider(self.__limits)
        self.__muc = MUCProvider()
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
        register(_EVENT.LOGIN, self.__handleLogin)
        register(_EVENT.PRESENCE, self.__handlePresence)
        register(_EVENT.PRESENCE_ERROR, self.__handlePresenceError)
        register(_EVENT.IQ, self.__handleIQ)
        register(_EVENT.MESSAGE, self.__handleMessage)
        register(_EVENT.MESSAGE_ERROR, self.__handleMessageError)
        events = g_messengerEvents.users
        events.onUsersListReceived += self.__me_onUsersListReceived
        events.onUserActionReceived += self.__me_onUserActionReceived
        events.onUserStatusUpdated += self.__me_onUserStatusUpdated

    def unregisterHandlers(self):
        unregister = self.client().unregisterHandler
        unregister(_EVENT.DISCONNECTED, self.__handleDisconnected)
        unregister(_EVENT.LOGIN, self.__handleLogin)
        unregister(_EVENT.PRESENCE, self.__handlePresence)
        unregister(_EVENT.PRESENCE_ERROR, self.__handlePresenceError)
        unregister(_EVENT.IQ, self.__handleIQ)
        unregister(_EVENT.MESSAGE, self.__handleMessage)
        unregister(_EVENT.MESSAGE_ERROR, self.__handleMessageError)
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
        self.__chatSessions.startSession(jid_entity.makeContactJID(dbID), name)
        return (True, None)

    def stopChatSession(self, jid):
        self.__chatSessions.stopSession(jid.getBareJID())

    def sendChatMessage(self, jid, body):
        if self.__cooldown.isInProcess(CLIENT_ACTION_ID.SEND_MESSAGE):
            g_messengerEvents.onErrorReceived(ChatCoolDownError(CLIENT_ACTION_ID.SEND_MESSAGE, self.__limits.getBroadcastCoolDown()))
            return
        body = self.__msgFilters.chainOut(body, self.__limits)
        if not body:
            return
        self.__chatSessions.sendMessage(jid.getBareJID(), body, self.__msgFilters)
        self.__cooldown.process(CLIENT_ACTION_ID.SEND_MESSAGE)

    def requestChatSessionHistory(self, jid):
        contactId = int(jid.getBareJID().getNode())
        self.__msgFilters.reset(contactId)
        self.__chatSessions.requestHistory(jid.getBareJID())

    @xmpp_query()
    def createUserRoom(self, name, password=''):
        return self.__muc.createRoom(name, password=password)

    @xmpp_query()
    def joinToMUC(self, jid, password='', name=''):
        return self.__muc.joinToRoom(jid.getBareJID(), password=password, name=name, initResult=ACTION_RESULT.DO_NOTHING)

    def leaveFromMUC(self, jid):
        self.__muc.leaveFromRoom(jid.getBareJID())

    def sendGroupChatMessage(self, jid, body):
        if self.__cooldown.isInProcess(CLIENT_ACTION_ID.SEND_MESSAGE):
            g_messengerEvents.onErrorReceived(ChatCoolDownError(CLIENT_ACTION_ID.SEND_MESSAGE, self.__limits.getBroadcastCoolDown()))
            return
        body = self.__msgFilters.chainOut(body, self.__limits)
        if not body:
            return
        self.__muc.sendMessage(jid_entity.ContactBareJID(jid), body, self.__msgFilters)
        self.__cooldown.process(CLIENT_ACTION_ID.SEND_MESSAGE)

    def _addSysChannelsToStorage(self):
        self._addCommonChannelToStorage()

    def _addCommonChannelToStorage(self):
        sysChannelConfig = g_settings.server.XMPP.getChannelByType(XMPP_MUC_CHANNEL_TYPE.STANDARD)
        if sysChannelConfig is not None and sysChannelConfig['enabled']:
            sysChannelEntity = entities.XmppSystemChannelEntity(mucChannelType=XMPP_MUC_CHANNEL_TYPE.STANDARD, name=sysChannelConfig['userString'])
            if self.channelsStorage.addChannel(sysChannelEntity):
                g_messengerEvents.channels.onChannelInited(sysChannelEntity)
        return

    def __clearData(self):
        self.__chatSessions.clear()
        self.__muc.clear()
        self.__receivedTags.clear()
        self.__pending = []

    def __setJoined(self, isJoined):
        channels = self.channelsStorage.getChannelsByCriteria(find_criteria.XMPPChannelFindCriteria())
        for channel in channels:
            channel.setJoined(isJoined)

    def __handleLogin(self):
        self.__chatSessions.release()
        self._addSysChannelsToStorage()

    def __handleDisconnected(self, reason, description):
        self.__chatSessions.suspend()
        self.__muc.suspend()

    def __handlePresence(self, jid, resource):
        self.__muc.handlePresence(jid, resource)

    def __handlePresenceError(self, jid, pyGlooxTag):
        self.__muc.handlePresenceError(jid, pyGlooxTag)

    def __handleIQ(self, iqID, iqType, pyGlooxTag):
        self.__chatSessions.handleIQ(iqID, iqType, pyGlooxTag)
        self.__muc.handleIQ(iqID, iqType, pyGlooxTag)

    def __handleMessage(self, _, msgType, body, jid, pyGlooxTag):
        if msgType not in MESSAGE_TYPE_TO_ATTR:
            return
        message = chat_ext.MessageHandler(MESSAGE_TYPE_TO_ATTR[msgType]).handleTag(pyGlooxTag)
        if body:
            message.body = self.__msgFilters.chainIn(message.accountDBID, body)
        if not _REQUIRED_USER_TAGS.issubset(self.__receivedTags):
            self.__pending.insert(0, (msgType, (jid, message)))
            return
        if self.__muc.hasChannel(jid.getBareJID()):
            self.__muc.addMessage(jid, message)
        elif msgType == MESSAGE_TYPE.CHAT or msgType == MESSAGE_TYPE.NORMAL and message.isHistory():
            self.__chatSessions.addMessage(jid, message)

    def __handleMessageError(self, _, __, ___, pyGlooxTag):
        g_messengerEvents.onErrorReceived(createServerActionMessageError(CLIENT_ACTION_ID.SEND_MESSAGE, pyGlooxTag))

    def __me_onUsersListReceived(self, tags):
        self.__receivedTags.update(tags)
        if _REQUIRED_USER_TAGS.issubset(self.__receivedTags):
            while self.__pending:
                msgType, data = self.__pending.pop()
                if msgType == MESSAGE_TYPE.CHAT:
                    self.__chatSessions.addMessage(*data)

    def __me_onUserActionReceived(self, actionID, contact, shadowMode):
        self.__chatSessions.setUserAction(actionID, contact)
        self.__muc.setUserAction(actionID, contact)

    def __me_onUserStatusUpdated(self, contact):
        self.__chatSessions.setContactPresence(contact)

    def __cs_onChannelsRestoredFromCache(self, stateGenerator):
        if not stateGenerator or not g_settings.server.XMPP.isEnabled():
            return
        for jid, state in stateGenerator(PROTO_TYPE.XMPP):
            if not self.__chatSessions.restore(jid, state):
                self.__muc.restore(jid, state)
