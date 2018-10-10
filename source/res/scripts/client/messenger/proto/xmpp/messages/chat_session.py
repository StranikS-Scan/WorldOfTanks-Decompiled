# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/messages/chat_session.py
import operator
import time
import BigWorld
from gui.shared import utils
from messenger import g_settings
from messenger.m_constants import CLIENT_ACTION_ID, PROTO_TYPE, USER_TAG, USER_ACTION_ID
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp import errors, entities
from messenger.proto.xmpp import jid as jid_entity
from messenger.proto.xmpp.XmppCooldownManager import XmppCooldownManager
from messenger.proto.xmpp.extensions import chat as chat_ext
from messenger.proto.xmpp.gloox_constants import IQ_TYPE, PRESENCE, MESSAGE_TYPE
from messenger.proto.xmpp.gloox_wrapper import ClientHolder
from messenger.proto.xmpp.log_output import g_logOutput, CLIENT_LOG_AREA
from messenger.proto.xmpp.messages.provider import ChatProvider
from messenger.proto.xmpp.wrappers import ChatMessage
from messenger.storage import storage_getter

class _HISTORY_RQ_STATE(object):
    FREE = 0
    WAIT = 1
    RESULT = 2
    COOLDOWN = 3
    UNAVAILABLE = 4


class ChatSessionHistoryRequester(ClientHolder):

    def __init__(self, limits):
        super(ChatSessionHistoryRequester, self).__init__()
        self.__cooldown = XmppCooldownManager(limits.getBroadcastCoolDown())
        self.__limit = limits.getHistoryMaxLength()
        self.__iqID = ''
        self.__pool = []
        self.__history = []
        self.__callbackID = None
        self.__state = _HISTORY_RQ_STATE.FREE
        self.__isSuspend = True
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    def release(self):
        if self.__isSuspend:
            self.__isSuspend = False
            self.__doNextRequest()

    def suspend(self):
        if not self.__isSuspend:
            self.__isSuspend = True
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__state = _HISTORY_RQ_STATE.FREE
            self.__iqID = ''
            self.__history = []
        return

    def clear(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self.__iqID = ''
        self.__pool = []
        self.__state = _HISTORY_RQ_STATE.FREE
        return

    def request(self, jid):
        if self.__state == _HISTORY_RQ_STATE.UNAVAILABLE:
            self.__setChannelHistory(jid)
            return
        if jid not in self.__pool:
            self.__pool.append(jid)
        if self.__isSuspend:
            return
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
                error = errors.createServerActionIQError(CLIENT_ACTION_ID.RQ_HISTORY, tag)
                if error:
                    g_messengerEvents.onErrorReceived(error)
                while self.__pool:
                    self.__setChannelHistory(self.__pool.pop(0))

            result = True
        else:
            result = False
        return result

    def addHistory(self, message):
        if message.body:
            self.__history.append(message)
        if message.isFinalInHistory:
            self.__setChannelHistory(self.__pool.pop(0))
            self.__history = []
            self.__state = _HISTORY_RQ_STATE.FREE
            self.__doNextRequest()

    def __setChannelHistory(self, jid):
        channel = self.channelsStorage.getChannel(entities.XMPPChatChannelEntity(jid))
        if channel:
            g_messengerEvents.channels.onHistoryReceived(sorted(self.__history, key=operator.attrgetter('sentAt')), channel)

    def __doNextRequest(self):
        if self.__cooldown.isInProcess(CLIENT_ACTION_ID.RQ_HISTORY):
            self.__state = _HISTORY_RQ_STATE.COOLDOWN
            self.__callbackID = BigWorld.callback(self.__cooldown.getTime(CLIENT_ACTION_ID.RQ_HISTORY), self.__callback)
        else:
            if not self.__pool:
                return
            self.__state = _HISTORY_RQ_STATE.WAIT
            self.__iqID = self.client().sendIQ(chat_ext.GetChatHistoryQuery(self.__pool[0], self.__limit))
            self.__cooldown.process(CLIENT_ACTION_ID.RQ_HISTORY, 5.0)

    def __callback(self):
        self.__callbackID = None
        self.__state = _HISTORY_RQ_STATE.FREE
        self.__doNextRequest()
        return


class ChatSessionsProvider(ChatProvider):
    __slots__ = ('__historyRQ',)

    def __init__(self, limits):
        super(ChatSessionsProvider, self).__init__()
        self.__historyRQ = ChatSessionHistoryRequester(limits)

    def clear(self):
        self.__historyRQ.clear()
        super(ChatSessionsProvider, self).clear()

    def release(self):
        for channel in self._getChannelsIterator(MESSAGE_TYPE.CHAT):
            channel.setJoined(True)

        self.__historyRQ.release()
        super(ChatSessionsProvider, self).release()

    def suspend(self):
        for channel in self._getChannelsIterator(MESSAGE_TYPE.CHAT):
            channel.setJoined(False)

        self.__historyRQ.suspend()
        super(ChatSessionsProvider, self).suspend()

    def startSession(self, jid, name):
        dbID = jid.getDatabaseID()
        created, exists = self._searchChannel(jid, name)
        if exists is None:
            self.__addSession(created, dbID, byAction=True)
        else:
            g_messengerEvents.channels.onPlayerEnterChannelByAction(exists)
        return

    def stopSession(self, jid):
        exists = self.getChannelByJID(jid)
        if exists is not None:
            self.__removeSession(exists)
            self.__historyRQ.cancel(jid)
        return

    def setUserAction(self, actionID, contact):
        if actionID in (USER_ACTION_ID.IGNORED_ADDED, USER_ACTION_ID.TMP_IGNORED_ADDED):
            self.stopSession(jid_entity.makeContactJID(contact.getID()))

    def restore(self, jid, state):
        jid = jid_entity.ContactBareJID(jid)
        channel = entities.XMPPChatChannelEntity(jid_entity.ContactBareJID(jid))
        result = channel.setPersistentState(state)
        if result and not self.hasChannel(channel.getID()):
            self.__addSession(channel, jid.getDatabaseID())
        return result

    def setContactPresence(self, contact):
        dbID = contact.getID()
        if contact.getProtoType() == PROTO_TYPE.XMPP:
            jid = contact.getJID()
        else:
            jid = jid_entity.makeContactJID(dbID)
        exists = self.getChannelByJID(jid)
        if exists is not None:
            member = exists.getMember(dbID)
            if member is not None:
                member.setOnline(contact.isOnline())
        return

    def addMessage(self, jid, message):
        if message.isHistory():
            self.__historyRQ.addHistory(message)
            return
        else:
            contactDBID = message.accountDBID or jid.getDatabaseID()
            nickname = message.accountName or jid.getNode()
            created, exists = self._searchChannel(jid, nickname)
            if exists is None and g_settings.userPrefs.chatContactsListOnly:
                contact = self.usersStorage.getUser(contactDBID)
                if not contact or not USER_TAG.filterClosedContactsTags(contact.getTags()):
                    g_logOutput.debug(CLIENT_LOG_AREA.MESSAGE, "There is not closed contact in player's contacts list,contact's message is ignored", jid, nickname)
                    return
            if exists is None:
                if self.__addSession(created, contactDBID):
                    exists = created
                else:
                    return
            if message.body:
                g_messengerEvents.channels.onMessageReceived(message, exists)
            return

    def requestHistory(self, jid):
        if self.hasChannel(jid):
            self.__historyRQ.request(jid)

    def handleIQ(self, iqID, iqType, pyGlooxTag):
        return self.__historyRQ.handleIQ(iqID, iqType, pyGlooxTag)

    def _searchChannel(self, jid, name=''):
        created = entities.XMPPChatChannelEntity(jid, name=name)
        exists = self.channelsStorage.getChannel(created)
        return (created, exists)

    def _repeatMessage(self, channel, body, filters):
        dbID = utils.getPlayerDatabaseID()
        name = utils.getPlayerName()
        g_messengerEvents.channels.onMessageReceived(ChatMessage(dbID, name, filters.chainIn(dbID, body), time.time()), channel)

    def __addSession(self, session, contactDBID=0L, byAction=False):
        jid = session.getID()
        presence = PRESENCE.UNAVAILABLE
        if contactDBID:
            contact = self.usersStorage.getUser(contactDBID)
            if contact is not None:
                if contact.isIgnored():
                    return False
                if contact.isOnline():
                    presence = PRESENCE.AVAILABLE
                else:
                    presence = PRESENCE.UNAVAILABLE
        userDBID = utils.getPlayerDatabaseID()
        session.setUser(jid_entity.makeContactJID(userDBID), utils.getPlayerName())
        session.setContact(jid, presence, contactDBID)
        super(ChatSessionsProvider, self)._addChannel(session, byAction)
        return True

    def __removeSession(self, session):
        super(ChatSessionsProvider, self)._removeChannel(session)
