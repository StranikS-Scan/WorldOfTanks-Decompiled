# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/xmpp/lobby_controllers.py
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.gui.Scaleform.channels._layout import _LobbyLayout
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.xmpp.xmpp_constants import MESSAGE_LIMIT

class ChatChannelController(_LobbyLayout):

    def __init__(self, channel, mBuilder = None):
        super(ChatChannelController, self).__init__(channel, mBuilder)
        self._hasUnreadMessages = False
        self.fireInitEvent()

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    def activate(self):
        if not self._channel.isJoined():
            self.proto.messages.requestChatHistory(self._channel.getID())
        super(ChatChannelController, self).activate()

    def exit(self):
        self.proto.messages.stopChatSession(self._channel.getID())

    def canSendMessage(self):
        result, errorMsg = True, ''
        if self.proto.messages.isInCooldown():
            result, errorMsg = False, getBroadcastIsInCoolDownMessage(MESSAGE_LIMIT.COOLDOWN)
        return (result, errorMsg)

    def addMessage(self, message, doFormatting = True):
        activated = super(ChatChannelController, self).addMessage(message, doFormatting)
        if not activated:
            self._hasUnreadMessages = True
        else:
            self._hasUnreadMessages = False
        return activated

    def hasUnreadMessages(self):
        return self._hasUnreadMessages and self._channel.getHistory()

    def _broadcast(self, message):
        self.proto.messages.sendChatMessage(self._channel.getID(), message)

    def _format(self, message, doFormatting = True):
        if not doFormatting:
            return message.text
        dbID = message.accountDBID
        return self._mBuilder.setGuiType(dbID).setName(dbID, message.accountName).setTime(message.sentAt).setText(message.body).build()

    def _onConnectStateChanged(self, channel):
        if self._view:
            self._view.as_setJoinedS(channel.isJoined())

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
