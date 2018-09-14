# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/bw_chat2/battle_controllers.py
from gui.battle_control import g_sessionProvider
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from gui.battle_control.arena_info import isArenaInWaiting
from messenger.ext import isBattleChatEnabled
from messenger.formatters import chat_message
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.gui.Scaleform.channels._layout import _BattleLayout
from messenger.m_constants import PROTO_TYPE, MESSENGER_COMMAND_TYPE
from messenger.ext.player_helpers import isCurrentPlayer
from messenger.proto import proto_getter
from messenger_common_chat2 import MESSENGER_LIMITS
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_errors import ClientError
from messenger.m_constants import CLIENT_ERROR_ID

def _checkArenaInWaiting(func):

    def wrapper(*args, **kwargs):
        if not isArenaInWaiting():
            func(*args, **kwargs)
        else:
            g_messengerEvents.onErrorReceived(ClientError(CLIENT_ERROR_ID.WAITING_BEFORE_START))

    return wrapper


class _ChannelController(_BattleLayout):

    def __init__(self, channel, messageBuilder, isSecondaryChannelCtrl = False):
        super(_ChannelController, self).__init__(channel, messageBuilder, isSecondaryChannelCtrl)
        self.activate()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto(self):
        return None

    def getSettings(self):
        return self._channel.getProtoData().settings

    def clear(self):
        if not self._isSecondaryChannelCtrl:
            self._channel.setJoined(False)
        super(_ChannelController, self).clear()

    def activate(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, {'controller': self}), scope=EVENT_BUS_SCOPE.BATTLE)

    def canSendMessage(self):
        if not self.isEnabled():
            return (False, '')
        if self.proto.arenaChat.isBroadcastInCooldown():
            return (False, getBroadcastIsInCoolDownMessage(MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC))
        return (True, '')

    def _formatMessage(self, message, doFormatting = True):
        dbID = message.accountDBID
        isCurrent = isCurrentPlayer(message.accountDBID)
        if not doFormatting:
            return (isCurrent, message.text)
        return (isCurrent, self._mBuilder.setColors(dbID).setName(dbID, message.accountName).setText(message.text).build())


class TeamChannelController(_ChannelController):

    def __init__(self, channel):
        super(TeamChannelController, self).__init__(channel, chat_message.TeamMessageBuilder())

    @_checkArenaInWaiting
    def sendCommand(self, command):
        self.proto.battleCmd.send(command)

    @_checkArenaInWaiting
    def _broadcast(self, message):
        self.proto.arenaChat.broadcast(message, 0)

    def isEnabled(self):
        result = super(TeamChannelController, self).isEnabled()
        hasAnyTeammates = len(list(g_sessionProvider.getArenaDP().getVehiclesIterator())) > 1
        return result and hasAnyTeammates

    def _formatCommand(self, command):
        isCurrent = False
        if command.getCommandType() == MESSENGER_COMMAND_TYPE.BATTLE:
            dbID = command.getSenderID()
            isCurrent = command.isSender()
            text = self._mBuilder.setColors(dbID).setName(dbID).setText(command.getCommandText()).build()
        else:
            text = command.getCommandText()
        return (isCurrent, text)


class CommonChannelController(_ChannelController):

    def __init__(self, channel):
        super(CommonChannelController, self).__init__(channel, chat_message.CommonMessageBuilder())

    def isEnabled(self):
        return isBattleChatEnabled(True)

    @_checkArenaInWaiting
    def _broadcast(self, message):
        self.proto.arenaChat.broadcast(message, 1)


class SquadChannelController(_ChannelController):

    def __init__(self, channel):
        super(SquadChannelController, self).__init__(channel, chat_message.SquadMessageBuilder(), True)

    def isEnabled(self):
        return True

    def setView(self, view):
        super(SquadChannelController, self).setView(view)
        self.proto.unitChat.addHistory()

    def canSendMessage(self):
        if not self.isEnabled():
            return (False, '')
        if self.proto.unitChat.isBroadcastInCooldown():
            return (False, getBroadcastIsInCoolDownMessage(MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC))
        return (True, '')

    def _broadcast(self, message):
        self.proto.unitChat.broadcast(message, 1)
