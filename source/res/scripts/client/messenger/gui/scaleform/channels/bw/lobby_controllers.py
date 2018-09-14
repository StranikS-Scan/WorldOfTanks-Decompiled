# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/bw/lobby_controllers.py
import types
import BigWorld
import constants
from chat_shared import CHAT_MEMBER_GROUP
from debug_utils import LOG_DEBUG
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.formatters.invites import AutoInviteTextFormatter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent, AutoInviteEvent
from helpers import i18n
from messenger import g_settings
from messenger.ext.player_helpers import isCurrentPlayer
from messenger.gui import events_dispatcher
from messenger.gui.Scaleform.channels._layout import _LobbyLayout
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.bw import cooldown
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

class _ChannelController(_LobbyLayout):

    def __init__(self, channel):
        super(_ChannelController, self).__init__(channel)
        self.__isChat2Enabled = g_settings.server.BW_CHAT2.isEnabled()

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto_v2(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def join(self):
        if not self._channel.isJoined():
            self.proto.channels.joinToChannel(self._channel.getID())

    def exit(self):
        if self._channel.isJoined():
            self.proto.channels.exitFromChannel(self._channel.getID())

    def canSendMessage(self):
        result, errorMsg = True, ''
        if cooldown.isBroadcatInCooldown():
            result, errorMsg = False, cooldown.BROADCAST_COOL_DOWN_MESSAGE
        return (result, errorMsg)

    def _broadcast(self, message):
        if self.__isChat2Enabled:
            result, _ = self.proto_v2.adminChat.parseLine(message, self._channel.getClientID())
            if result:
                return
        self.proto.channels.sendMessage(self._channel.getID(), message)

    def _format(self, message, doFormatting = True):
        isString = type(message) is types.StringType
        if not doFormatting or isString:
            if isString:
                return message
            return message.data
        group = message.group
        dbID = message.originator
        if CHAT_MEMBER_GROUP.member.index() == group or isCurrentPlayer(dbID):
            self._mBuilder.setGuiType(dbID)
        else:
            self._mBuilder.setGroup(CHAT_MEMBER_GROUP[group].name())
        return self._mBuilder.setName(dbID, message.originatorNickName).setTime(message.time).setText(message.data).build()

    def _addListeners(self):
        self._channel.onConnectStateChanged += self._onConnectStateChanged
        self._channel.onMembersListChanged += self._onMembersListChanged

    def _removeListeners(self):
        self._channel.onConnectStateChanged -= self._onConnectStateChanged
        self._channel.onMembersListChanged -= self._onMembersListChanged

    def _onConnectStateChanged(self, channel):
        if self._view:
            self._view.as_setJoinedS(channel.isJoined())

    def _onMembersListChanged(self):
        self._refreshMembersDP()


class LazyChannelController(_ChannelController):
    __EXIT_DELAY = 10.0

    def __init__(self, channel):
        super(LazyChannelController, self).__init__(channel)
        self.__exitCallbackID = None
        self.fireInitEvent()
        return

    def setView(self, view):
        super(LazyChannelController, self).setView(view)
        self.__clearExitCallback()
        if not self._channel.isJoined():
            self.proto.channels.joinToChannel(self._channel.getID())

    def activate(self):
        super(LazyChannelController, self).activate()
        self.__clearExitCallback()
        self.join()

    def deactivate(self, entryClosing = False):
        super(LazyChannelController, self).deactivate()
        if not entryClosing:
            self.__clearExitCallback()
            if self._channel.isJoined():
                self.__exitCallbackID = BigWorld.callback(self.__EXIT_DELAY, self.__exitFromLazyChannel)

    def addMessage(self, message, doFormatting = True):
        super(LazyChannelController, self).addMessage(message, doFormatting)
        return True

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
            LOG_DEBUG('Send request to exit from lazy channel', i18n.encodeUtf8(self._channel.getName()))
            self.exit()
        return


class BSLazyChannelController(LazyChannelController):
    NOTIFICATION_ICON = {constants.PREBATTLE_TYPE.CLAN: 'ClanBattleResultIcon-1',
     constants.PREBATTLE_TYPE.TOURNAMENT: 'TournamentBattleResultIcon-1'}
    NOTIFICATION_ICON_DEFAULT = 'BattleResultIcon-1'

    def __init__(self, channel):
        self.__notifications = []
        super(BSLazyChannelController, self).__init__(channel)

    def clear(self):
        super(BSLazyChannelController, self).clear()
        self.__notifications = []

    def getHistory(self):
        history = super(BSLazyChannelController, self).getHistory()
        history.extend(self.__notifications)
        return history

    def _addListeners(self):
        super(BSLazyChannelController, self)._addListeners()
        for invite in g_prbLoader.getAutoInvitesNotifier().getNotified():
            self.__addNotification(invite)

        g_eventBus.addListener(AutoInviteEvent.INVITE_RECEIVED, self.__handleAutoInviteReceived, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        super(BSLazyChannelController, self)._removeListeners()
        g_eventBus.removeListener(AutoInviteEvent.INVITE_RECEIVED, self.__handleAutoInviteReceived, scope=EVENT_BUS_SCOPE.LOBBY)

    def __addNotification(self, invite):
        formatted = g_settings.htmlTemplates.format('inviteToSpecialBattle', ctx={'icon': self.NOTIFICATION_ICON.get(invite.prbType, self.NOTIFICATION_ICON_DEFAULT),
         'text': AutoInviteTextFormatter().getText(invite)})
        self.__notifications.append(formatted)
        if self._activated:
            if self._view:
                self._view.as_addMessageS(formatted)
        else:
            events_dispatcher.notifyCarousel(self._channel.getClientID())

    def __handleAutoInviteReceived(self, event):
        self.__addNotification(event.invite)


class LobbyChannelController(_ChannelController):

    def _addListeners(self):
        super(LobbyChannelController, self)._addListeners()
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.__me_onUsersReceived
        usersEvents.onUserActionReceived += self.__me_onUserActionReceived

    def _removeListeners(self):
        super(LobbyChannelController, self)._removeListeners()
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self.__me_onUsersReceived
        usersEvents.onUserActionReceived -= self.__me_onUserActionReceived

    def _fireInitEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LOBBY_CHANNEL_CTRL_INITED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _fireDestroyEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.LOBBY_CHANNEL_CTRL_DESTROYED, {'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onConnectStateChanged(self, channel):
        super(LobbyChannelController, self)._onConnectStateChanged(channel)
        if channel.isJoined():
            self.fireInitEvent()
        else:
            self.fireDestroyEvent()
            self.proto.channels.removeChannelFromClient(self._channel)

    def __me_onUsersReceived(self, _):
        self._refreshMembersDP()

    def __me_onUserActionReceived(self, _, user):
        if self._channel.hasMember(user.getID()):
            self._refreshMembersDP()
