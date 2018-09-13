# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/bw/lobby_controllers.py
import types
import BigWorld
import constants
from chat_shared import CHAT_MEMBER_GROUP
from debug_utils import LOG_ERROR, LOG_DEBUG
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

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
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


class PrebattleChannelController(_ChannelController):

    def __init__(self, prbType, channel):
        super(PrebattleChannelController, self).__init__(channel)
        self.__prbType = prbType
        self.fireInitEvent()

    def _addListeners(self):
        super(PrebattleChannelController, self)._addListeners()
        g_eventBus.addListener(MessengerEvent.PRB_CHANNEL_CTRL_REQUEST_DESTROY, self.__handleRequestToDestroy, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        super(PrebattleChannelController, self)._removeListeners()
        g_eventBus.removeListener(MessengerEvent.PRB_CHANNEL_CTRL_REQUEST_DESTROY, self.__handleRequestToDestroy, scope=EVENT_BUS_SCOPE.LOBBY)

    def _fireInitEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.PRB_CHANNEL_CTRL_INITED, {'prbType': self.__prbType,
         'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _fireDestroyEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.PRB_CHANNEL_CTRL_DESTROYED, {'prbType': self.__prbType,
         'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __handleRequestToDestroy(self, event):
        ctx = event.ctx
        prbType = ctx.get('prbType')
        if not prbType:
            LOG_ERROR('Type of prebattle is not defined', ctx)
            return
        if prbType is self.__prbType and self._channel:
            self.proto.channels.removeChannelFromClient(self._channel)


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
        uEvents = g_messengerEvents.users
        uEvents.onUsersRosterReceived += self.__me_onUsersRosterReceived
        uEvents.onUserRosterChanged += self.__me_onUserRosterChanged

    def _removeListeners(self):
        super(LobbyChannelController, self)._removeListeners()
        uEvents = g_messengerEvents.users
        uEvents.onUsersRosterReceived -= self.__me_onUsersRosterReceived
        uEvents.onUserRosterChanged -= self.__me_onUserRosterChanged

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

    def __me_onUsersRosterReceived(self):
        self._refreshMembersDP()

    def __me_onUserRosterChanged(self, _, user):
        if self._channel.hasMember(user.getID()):
            self._refreshMembersDP()


class TrainingChannelController(LobbyChannelController):

    def _addListeners(self):
        super(TrainingChannelController, self)._addListeners()
        g_eventBus.addListener(MessengerEvent.PRB_CHANNEL_CTRL_REQUEST_DESTROY, self.__handleRequestToDestroy, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        super(TrainingChannelController, self)._removeListeners()
        g_eventBus.removeListener(MessengerEvent.PRB_CHANNEL_CTRL_REQUEST_DESTROY, self.__handleRequestToDestroy, scope=EVENT_BUS_SCOPE.LOBBY)

    def __handleRequestToDestroy(self, event):
        ctx = event.ctx
        prbType = ctx.get('prbType')
        if not prbType:
            LOG_ERROR('Type of prebattle is not defined', ctx)
            return
        if prbType is constants.PREBATTLE_TYPE.TRAINING and self._channel:
            self.proto.channels.removeChannelFromClient(self._channel)
