# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/xmpp/lobby_controllers.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from gui.shared.utils import backoff
from messenger import g_settings
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.gui.Scaleform.channels.layout import LobbyLayout
from messenger.m_constants import PROTO_TYPE, CLIENT_ACTION_ID, USER_TAG
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.gloox_constants import ERROR_TYPE
from messenger.proto.xmpp.jid import makeContactJID
from messenger.proto.xmpp.messages.formatters import XmppLobbyMessageBuilder, XmppLobbyUsersChatBuilder
from messenger.proto.xmpp.xmpp_constants import MESSAGE_LIMIT
from messenger.storage import storage_getter
_LAZY_EXIT_DELAY = 10.0
_BACK_OFF_MIN_DELAY = 60
_BACK_OFF_MAX_DELAY = 1200
_BACK_OFF_MODIFIER = 30
_BACK_OFF_EXP_RANDOM_FACTOR = 5

class _ChannelController(LobbyLayout):

    def __init__(self, channel, mBuilder=None):
        super(_ChannelController, self).__init__(channel, mBuilder or XmppLobbyMessageBuilder())
        self._hasUnreadMessages = False
        self.fireInitEvent()
        self.__isChat2Enabled = g_settings.server.BW_CHAT2.isEnabled()

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto_v2(self):
        return None

    def canSendMessage(self):
        result, errorMsg = True, ''
        if self.proto.messages.isInCooldown():
            result, errorMsg = False, getBroadcastIsInCoolDownMessage(MESSAGE_LIMIT.COOLDOWN)
        return (result, errorMsg)

    def addMessage(self, message, doFormatting=True):
        activated = super(_ChannelController, self).addMessage(message, doFormatting)
        self._hasUnreadMessages = not activated
        return activated

    def hasUnreadMessages(self):
        return self._hasUnreadMessages and self._channel.getHistory()

    def _format(self, message, doFormatting=True):
        if not doFormatting:
            return message.text
        dbID = message.accountDBID
        return self._mBuilder.setGuiType(dbID).setRole(message.accountRole).setAffiliation(message.accountAffiliation).setName(dbID, message.accountName).setTime(message.sentAt).setText(message.body).build()

    def _onConnectStateChanged(self, _):
        for view in self._views:
            view.as_setJoinedS(self.isJoined())

    def _onMembersListChanged(self):
        self._refreshMembersDP()

    def _onMemberStatusChanged(self, _):
        self._refreshMembersDP()

    def _addListeners(self):
        self._channel.onConnectStateChanged += self._onConnectStateChanged
        self._channel.onMembersListChanged += self._onMembersListChanged
        self._channel.onMemberStatusChanged += self._onMemberStatusChanged

    def _removeListeners(self):
        self._channel.onConnectStateChanged -= self._onConnectStateChanged
        self._channel.onMembersListChanged -= self._onMembersListChanged
        self._channel.onMemberStatusChanged -= self._onMemberStatusChanged

    def _fireInitEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LOBBY_CHANNEL_CTRL_INITED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _fireDestroyEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LOBBY_CHANNEL_CTRL_DESTROYED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _broadcast(self, message):
        if not self.__parseCommandLine(message):
            self._sendMsg(message)

    def _sendMsg(self, message):
        raise NotImplementedError

    def __parseCommandLine(self, message):
        result = False
        if self.__isChat2Enabled:
            result, _ = self.proto_v2.adminChat.parseLine(message, self._channel.getClientID())
        return result


class ChatSessionController(_ChannelController):

    def __init__(self, channel):
        super(ChatSessionController, self).__init__(channel, XmppLobbyUsersChatBuilder())
        self._isHistoryRqRequired = True

    @storage_getter('users')
    def usersStorage(self):
        return None

    def isJoined(self):
        return self._channel.isJoined() and not self._isHistoryRqRequired

    def activate(self):
        if self._isHistoryRqRequired:
            self.proto.messages.requestChatSessionHistory(self._channel.getID())
        super(ChatSessionController, self).activate()

    def exit(self):
        self.proto.messages.stopChatSession(self._channel.getID())

    def setHistory(self, history):
        super(ChatSessionController, self).setHistory(history)
        if self._isHistoryRqRequired:
            self._isHistoryRqRequired = False
            self._onConnectStateChanged(self._channel)

    def hasUntrustedMembers(self):
        getter = self.usersStorage.getUser
        for member in self._channel.getMembers():
            user = getter(member.getID().getDatabaseID())
            if user is None:
                return True
            if user.isCurrentPlayer():
                continue
            if not USER_TAG.filterClosedContactsTags(user.getTags()):
                return True

        return False

    def _addListeners(self):
        super(ChatSessionController, self)._addListeners()
        g_messengerEvents.users.onUserStatusUpdated += self.__onUserStatusUpdated

    def _removeListeners(self):
        g_messengerEvents.users.onUserStatusUpdated -= self.__onUserStatusUpdated
        super(ChatSessionController, self)._removeListeners()

    def _sendMsg(self, message):
        self.proto.messages.sendChatMessage(self._channel.getID(), message)

    def __onUserStatusUpdated(self, user):
        if not user.isCurrentPlayer():
            if user.getProtoType() == PROTO_TYPE.XMPP:
                uid = user.getJID()
            else:
                uid = makeContactJID(user.getID())
            member = self._channel.getMember(uid)
            if member is not None:
                member.update(status=user.isOnline())
        return


class UserRoomController(_ChannelController):

    def exit(self):
        self.proto.messages.leaveFromMUC(self._channel.getID())

    def _addListeners(self):
        super(UserRoomController, self)._addListeners()
        events = g_messengerEvents.users
        events.onUsersListReceived += self.__me_onUsersListReceived
        events.onUserActionReceived += self.__me_onUserActionReceived

    def _removeListeners(self):
        events = g_messengerEvents.users
        events.onUsersListReceived -= self.__me_onUsersListReceived
        events.onUserActionReceived -= self.__me_onUserActionReceived
        super(UserRoomController, self)._removeListeners()

    def _sendMsg(self, message):
        self.proto.messages.sendGroupChatMessage(self._channel.getID(), message)

    def __me_onUsersListReceived(self, _):
        self._refreshMembersDP()

    def __me_onUserActionReceived(self, _, contact, shadowMode):
        self._refreshMembersDP()


class LazyUserRoomController(_ChannelController):

    def __init__(self, channel):
        super(LazyUserRoomController, self).__init__(channel)
        self.__exitCallbackID = None
        return

    def activate(self):
        super(LazyUserRoomController, self).activate()
        self.__clearExitCallback()
        self.join()

    def deactivate(self, entryClosing=False):
        super(LazyUserRoomController, self).deactivate()
        self.__clearExitCallback()
        if not entryClosing:
            if self._channel.isJoined():
                self.__exitCallbackID = BigWorld.callback(_LAZY_EXIT_DELAY, self.__exitFromLazyChannel)
        else:
            self.__exitFromLazyChannel()

    def join(self):
        if not self._channel.isJoined():
            self.proto.messages.joinToMUC(self._channel.getID())

    def exit(self):
        self.proto.messages.leaveFromMUC(self._channel.getID())

    def addMessage(self, message, doFormatting=True):
        super(LazyUserRoomController, self).addMessage(message, doFormatting=doFormatting)
        return True

    def _sendMsg(self, message):
        self.proto.messages.sendGroupChatMessage(self._channel.getID(), message)

    def _fireInitEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LAZY_CHANNEL_CTRL_INITED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _fireDestroyEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LAZY_CHANNEL_CTRL_DESTROYED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __clearExitCallback(self):
        if self.__exitCallbackID is not None:
            BigWorld.cancelCallback(self.__exitCallbackID)
            self.__exitCallbackID = None
        return

    def __exitFromLazyChannel(self):
        self.__exitCallbackID = None
        if self._channel and self._channel.isJoined():
            self.exit()
        return


class ClanUserRoomController(UserRoomController):

    def __init__(self, channel):
        super(ClanUserRoomController, self).__init__(channel)
        self.__reJoinCallbackID = None
        self.__expBackOff = backoff.ExpBackoff(_BACK_OFF_MIN_DELAY, _BACK_OFF_MAX_DELAY, _BACK_OFF_MODIFIER, _BACK_OFF_EXP_RANDOM_FACTOR)
        self.__doNextRejoin()
        g_messengerEvents.onErrorReceived += self.__me_onErrorReceived
        return

    def clear(self):
        g_messengerEvents.onErrorReceived -= self.__me_onErrorReceived
        self.__cancelRejoinCallback()
        self.__expBackOff.reset()
        self.exit()
        super(ClanUserRoomController, self).clear()

    def join(self):
        self.proto.messages.joinToMUC(self._channel.getID())

    def exit(self):
        if self._channel.isJoined():
            self.proto.messages.leaveFromMUC(self._channel.getID())

    def _onConnectStateChanged(self, channel):
        super(ClanUserRoomController, self)._onConnectStateChanged(channel)
        if channel.isJoined():
            self.__cancelRejoinCallback()

    def __doNextRejoin(self):
        self.__reJoinCallbackID = None
        self.join()
        return

    def __cancelRejoinCallback(self):
        if self.__reJoinCallbackID is not None:
            BigWorld.cancelCallback(self.__reJoinCallbackID)
            self.__reJoinCallbackID = None
        return

    def __setRejoinCallback(self):
        delay = self.__expBackOff.next()
        self.__reJoinCallbackID = BigWorld.callback(delay, self.__doNextRejoin)

    def __me_onErrorReceived(self, error):
        if error.getActionID() == CLIENT_ACTION_ID.JOIN_CLAN_ROOM and error.getErrorType() == ERROR_TYPE.AUTH and error.getCondition() == 'registration-required':
            if self.__reJoinCallbackID is None:
                self.__setRejoinCallback()
        return
