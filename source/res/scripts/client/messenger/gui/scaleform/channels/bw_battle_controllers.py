# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/bw_battle_controllers.py
import BigWorld
import BattleReplay
import constants
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.BattleContext import g_battleContext
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from helpers import i18n
from messenger import g_settings
from messenger.gui.Scaleform.view.BattleChannelView import BattleChannelView
from messenger.gui.interfaces import IChannelController
from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE, MESSENGER_I18N_FILE
from messenger.ext.player_helpers import isCurrentPlayer
from messenger.proto import proto_getter
from messenger.proto.bw import cooldown, entities
from messenger.storage import storage_getter

class _ChannelController(IChannelController):
    _teamChannel = entities.BWChannelLightEntity(-1)

    def __init__(self, channel):
        self._channel = channel
        channel.onConnectStateChanged += self._onConnectStateChanged
        self._view = None
        return

    def __del__(self):
        LOG_DEBUG('Channel controller deleted:', self)

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def getChannel(self):
        return self._channel

    def setView(self, view):
        if self._view:
            LOG_ERROR('View is defined', self._view)
        elif isinstance(view, BattleChannelView):
            self._view = view
            self._view.setController(self)
        else:
            LOG_ERROR('View must be BattleChannelView', self._view)

    def removeView(self):
        if self._view is not None:
            self._view.removeController()
            self._view = None
        return

    def clear(self):
        self._channel.onConnectStateChanged -= self._onConnectStateChanged
        self._channel = None
        self.removeView()
        return

    def activate(self):
        self._onConnectStateChanged(self._channel)

    def getFullPlayerName(self, chatAction):
        return g_battleContext.getFullPlayerName(accID=chatAction.originator)

    def getMessageColors(self, message):
        return (g_settings.getColorScheme('battle/player').getHexStr('unknown'), g_settings.getColorScheme('battle/message').getHexStr('unknown'))

    def canSendMessage(self):
        result, errorMsg = True, ''
        if cooldown.isBroadcatInCooldown():
            result, errorMsg = False, cooldown.BROADCAST_COOL_DOWN_MESSAGE
        return (result, errorMsg)

    def sendMessage(self, message):
        result, errorMsg = self.canSendMessage()
        if result:
            self.proto.channels.sendMessage(self._channel.getID(), message)
        else:
            self._view.addMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': errorMsg}))
        return result

    def sendCommand(self, command):
        self.proto.channels.sendCommand(self._channel.getID(), command.getCommand(), **command.getParams())

    def isBattleChatEnabled(self):
        result = True
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is None:
            LOG_ERROR('ClientArena not found')
            return result
        else:
            guiType = arena.guiType
            if guiType is None:
                return result
            if guiType == constants.ARENA_GUI_TYPE.RANDOM:
                result = not g_settings.userPrefs.disableBattleChat
            return result

    def addMessage(self, message, doFormatting = True):
        isCurrent = isCurrentPlayer(message.originator)
        if doFormatting:
            text = self._format(message, message.data)
        else:
            text = message.data
        self._channel.addMessage(text)
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onBattleChatMessage(text, isCurrent)
        if self._view:
            self._view.addMessage(text, isCurrentPlayer=isCurrent)
        return True

    def addCommand(self, command):
        cmdData = command.getProtoData()
        isCurrent = isCurrentPlayer(cmdData.originator)
        text = self._format(cmdData, command.getCommandText())
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onBattleChatMessage(text, isCurrent)
        if self._view:
            self._view.addMessage(text, isCurrentPlayer=isCurrent)

    def _format(self, chatAction, msgText):
        playerColor, msgColor = self.getMessageColors(chatAction)
        return g_settings.battle.messageFormat % {'playerColor': playerColor,
         'playerName': unicode(self.getFullPlayerName(chatAction), 'utf-8', errors='ignore'),
         'messageColor': msgColor,
         'messageText': msgText}

    def _onConnectStateChanged(self, channel):
        pass


class TeamChannelController(_ChannelController):

    def __init__(self, channel):
        super(TeamChannelController, self).__init__(channel)
        _ChannelController._teamChannel.setID(channel.getID())

    def __del__(self):
        self._teamChannel.setID(-1)
        super(TeamChannelController, self).__del__()

    def getMessageColors(self, message):
        dbID = message.originator
        mColor = g_settings.getColorScheme('battle/message').getHexStr('team')
        pColorScheme = g_settings.getColorScheme('battle/player')
        pColor = pColorScheme.getHexStr('teammate')
        if isCurrentPlayer(dbID):
            pColor = pColorScheme.getHexStr('himself')
        elif g_battleContext.isTeamKiller(accID=dbID):
            pColor = pColorScheme.getHexStr('teamkiller')
        elif g_battleContext.isSquadMan(accID=dbID):
            pColor = pColorScheme.getHexStr('squadman')
        return (pColor, mColor)

    def _onConnectStateChanged(self, channel):
        if channel.isJoined():
            g_eventBus.handleEvent(MessengerEvent(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, {'settings': BATTLE_CHANNEL.TEAM,
             'controller': self}), scope=EVENT_BUS_SCOPE.BATTLE)

    def sendMessage(self, message):
        if self.isBattleChatEnabled():
            super(TeamChannelController, self).sendMessage(message)
        else:
            return False


class CommonChannelController(_ChannelController):
    __i18n_ally = i18n.makeString('#{0:>s}:battle/unknown/ally'.format(MESSENGER_I18N_FILE))
    __i18n_enemy = i18n.makeString('#{0:>s}:battle/unknown/enemy'.format(MESSENGER_I18N_FILE))

    def sendMessage(self, message):
        if self.isBattleChatEnabled():
            super(CommonChannelController, self).sendMessage(message)
        else:
            return False

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    def getFullPlayerName(self, chatAction):
        fullName = g_battleContext.getFullPlayerName(accID=chatAction.originator)
        if not len(fullName):
            channel = self.channelsStorage.getChannel(self._teamChannel)
            if channel and channel.hasMember(chatAction.originator):
                fullName = self.__i18n_ally
            else:
                fullName = self.__i18n_enemy
        return fullName

    def getMessageColors(self, message):
        dbID = message.originator
        mColor = g_settings.getColorScheme('battle/message').getHexStr('common')
        pColorScheme = g_settings.getColorScheme('battle/player')
        pColor = pColorScheme.getHexStr('unknown')
        if isCurrentPlayer(dbID):
            pColor = pColorScheme.getHexStr('himself')
        else:
            channel = self.channelsStorage.getChannel(self._teamChannel)
            if channel and channel.hasMember(dbID):
                if g_battleContext.isTeamKiller(accID=dbID):
                    pColor = pColorScheme.getHexStr('teamkiller')
                elif g_battleContext.isSquadMan(accID=dbID):
                    pColor = pColorScheme.getHexStr('squadman')
                else:
                    pColor = pColorScheme.getHexStr('teammate')
            elif self._channel.hasMember(dbID):
                pColor = pColorScheme.getHexStr('enemy')
        return (pColor, mColor)

    def _onConnectStateChanged(self, channel):
        if channel.isJoined():
            g_eventBus.handleEvent(MessengerEvent(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, {'settings': BATTLE_CHANNEL.COMMON,
             'controller': self}), scope=EVENT_BUS_SCOPE.BATTLE)


class SquadChannelController(_ChannelController):

    def __init__(self, channel):
        super(SquadChannelController, self).__init__(channel)

    def addMessage(self, message, doFormatting = True):
        isCurrent = isCurrentPlayer(message.originator)
        if doFormatting:
            text = self._format(message, message.data)
        else:
            text = message.data
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onBattleChatMessage(text, isCurrent)
        if self._view:
            self._view.addMessage(text, isCurrentPlayer=isCurrent)
        return True

    def getFullPlayerName(self, chatAction):
        pName = None
        try:
            pName = i18n.encodeUtf8(chatAction.originatorNickName)
        except UnicodeError:
            LOG_ERROR('Can not encode nick name', chatAction)

        return g_battleContext.getFullPlayerName(accID=chatAction.originator, pName=pName)

    def getMessageColors(self, message):
        dbID = message.originator
        mColor = g_settings.getColorScheme('battle/message').getHexStr('squad')
        pColorScheme = g_settings.getColorScheme('battle/player')
        pColor = pColorScheme.getHexStr('squadman')
        if isCurrentPlayer(dbID):
            pColor = pColorScheme.getHexStr('himself')
        elif g_battleContext.isTeamKiller(accID=dbID):
            pColor = pColorScheme.getHexStr('teamkiller')
        return (pColor, mColor)

    def _onConnectStateChanged(self, channel):
        if channel.isJoined():
            g_eventBus.handleEvent(MessengerEvent(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, {'settings': BATTLE_CHANNEL.SQUAD,
             'controller': self}), scope=EVENT_BUS_SCOPE.BATTLE)

    def isBattleChatEnabled(self):
        return True


def addDefMessage(message):
    mColor = g_settings.getColorScheme('battle/message').getHexStr('unknown')
    pColor = g_settings.getColorScheme('battle/player').getHexStr('unknown')
    return g_settings.battle.messageFormat % {'playerColor': pColor,
     'playerName': unicode(g_battleContext.getFullPlayerName(accID=message.originator), 'utf-8', errors='ignore'),
     'messageColor': mColor,
     'messageText': message.data}
