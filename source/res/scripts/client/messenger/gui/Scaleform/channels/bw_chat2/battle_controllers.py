# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/channels/bw_chat2/battle_controllers.py
import functools
import BigWorld
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.battle_control.arena_info.arena_vos import EPIC_BATTLE_KEYS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from helpers import dependency
from helpers import i18n
from messenger.ext import isBattleChatEnabled
from messenger.ext.player_helpers import isCurrentPlayer
from messenger.formatters import chat_message
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.gui.Scaleform.channels.layout import BattleLayout
from messenger.m_constants import CLIENT_ERROR_ID
from messenger.m_constants import PROTO_TYPE, MESSENGER_COMMAND_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_errors import ClientError
from messenger_common_chat2 import MESSENGER_LIMITS
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException

class _check_arena_in_waiting(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not self.sessionProvider.arenaVisitor.isArenaInWaiting():
                func(*args, **kwargs)
            else:
                g_messengerEvents.onErrorReceived(ClientError(CLIENT_ERROR_ID.WAITING_BEFORE_START))

        return wrapper


class _ChannelController(BattleLayout):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, channel, messageBuilder, isSecondaryChannelCtrl=False):
        super(_ChannelController, self).__init__(channel, messageBuilder, isSecondaryChannelCtrl)
        self.activate()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto(self):
        return None

    def getSettings(self):
        return self._channel.getProtoData().settings

    def filterMessage(self, cmd):
        return True

    def clear(self):
        if not self._isSecondaryChannelCtrl:
            self._channel.setJoined(False)
        super(_ChannelController, self).clear()

    def activate(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.BATTLE_CHANNEL_CTRL_INITED, {'controller': self}), scope=EVENT_BUS_SCOPE.BATTLE)

    def canSendMessage(self):
        if not self.isEnabled():
            return (False, '')
        return (False, getBroadcastIsInCoolDownMessage(MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC)) if self.proto.arenaChat.isBroadcastInCooldown() else (True, '')

    def _formatMessage(self, message, doFormatting=True):
        avatarSessionID = message.avatarSessionID
        isCurrent = isCurrentPlayer(avatarSessionID)
        return (isCurrent, message.text) if not doFormatting else (isCurrent, self._mBuilder.setColors(avatarSessionID).setName(avatarSessionID, message.accountName).setText(message.text).build())

    def _formatCommand(self, command):
        raise SoftException('This method should not be reached in this context')


class TeamChannelController(_ChannelController):

    def __init__(self, channel):
        super(TeamChannelController, self).__init__(channel, chat_message.TeamMessageBuilder())

    @_check_arena_in_waiting()
    def sendCommand(self, command):
        self.proto.battleCmd.send(command)

    def filterMessage(self, cmd):
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is None:
            return True
        else:
            senderVehicleID = arenaDP.getVehIDBySessionID(cmd.getSenderID())
            return not arenaDP.isPlayerObserver() or senderVehicleID == BigWorld.player().playerVehicleID or arenaDP.isAlly(senderVehicleID)

    @_check_arena_in_waiting()
    def _broadcast(self, message):
        self.proto.arenaChat.broadcast(message, 0)

    def isEnabled(self):
        result = super(TeamChannelController, self).isEnabled()
        arenaDP = self.sessionProvider.getArenaDP()
        arenaVisitor = self.sessionProvider.arenaVisitor
        hasAnyTeammates = arenaDP.getAlliesVehiclesNumber() > 1
        isObserver = arenaDP.isPlayerObserver()
        isBattleRoyale = arenaVisitor.gui.isBattleRoyale()
        return result and (hasAnyTeammates or isObserver) and (not isBattleRoyale or arenaDP.getVehicleInfo().squadIndex == 0)

    def _formatCommand(self, command):
        isCurrent = False
        if command.getCommandType() == MESSENGER_COMMAND_TYPE.BATTLE:
            avatarSessionID = command.getSenderID()
            isCurrent = command.isSender()
            text = self._mBuilder.setColors(avatarSessionID).setName(avatarSessionID).setText(command.getCommandText()).build()
        else:
            text = command.getCommandText()
        return (isCurrent, text)


_EPIC_MINIMAP_ZOOM_MODE_SCALE = 500
_NONCAPTURED_BASES_FOR_LANE_DICT = {1: {1: 4,
     2: 1},
 2: {1: 5,
     2: 2},
 3: {1: 6,
     2: 3}}

class EpicTeamChannelController(TeamChannelController):

    def __getNameSuffix(self, avatarSessionID):
        suffix = ''
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return suffix
        else:
            destructibleEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
            if destructibleEntityComp is None:
                LOG_ERROR('Expected DestructibleEntityComponent not present!')
                return suffix
            senderVID = self.sessionProvider.getCtx().getVehIDBySessionID(avatarSessionID)
            adp = self.sessionProvider.getArenaDP()
            vo = adp.getVehicleStats(senderVID)
            sectorID = vo.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PHYSICAL_SECTOR)
            lane = vo.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PLAYER_GROUP)
            hqActive = False
            hqs = destructibleEntityComp.destructibleEntities
            if hqs:
                hqActive = hqs[hqs.keys()[0]].isActive
            nonCapturedBases = sectorBaseComp.getNumNonCapturedBasesByLane(lane)
            if 0 < sectorID < 7:
                suffix = 0 < lane < 4 and '&lt;' + i18n.makeString(EPIC_BATTLE.ZONE_ZONE_TEXT) + ' ' + ID_TO_BASENAME[sectorID] + '&gt;'
            elif nonCapturedBases == 0 or hqActive and sectorID > 6:
                suffix = '&lt;' + i18n.makeString(EPIC_BATTLE.ZONE_HEADQUARTERS_TEXT) + '&gt;'
            return suffix

    def _formatMessage(self, message, doFormatting=True):
        avatarSessionID = message.avatarSessionID
        isCurrent = isCurrentPlayer(avatarSessionID)
        if not doFormatting:
            return (isCurrent, message.text)
        suffix = self.__getNameSuffix(avatarSessionID)
        return (isCurrent, self._mBuilder.setColors(avatarSessionID).setName(avatarSessionID, message.accountName, suffix=suffix).setText(message.text).build())

    def _formatCommand(self, command):
        isCurrent = False
        if command.getCommandType() == MESSENGER_COMMAND_TYPE.BATTLE:
            avatarSessionID = command.getSenderID()
            isCurrent = command.isSender()
            suffix = self.__getNameSuffix(avatarSessionID)
            text = self._mBuilder.setColors(avatarSessionID).setName(avatarSessionID, suffix=suffix).setText(command.getCommandText()).build()
        else:
            text = command.getCommandText()
        return (isCurrent, text)


class CommonChannelController(_ChannelController):

    def __init__(self, channel):
        super(CommonChannelController, self).__init__(channel, chat_message.CommonMessageBuilder())

    def isEnabled(self):
        return isBattleChatEnabled(True)

    @_check_arena_in_waiting()
    def _broadcast(self, message):
        self.proto.arenaChat.broadcast(message, 1)


class SquadChannelController(_ChannelController):

    def __init__(self, channel):
        super(SquadChannelController, self).__init__(channel, chat_message.SquadMessageBuilder(), True)

    def isEnabled(self):
        return self.proto.unitChat.isInited()

    def setView(self, view):
        super(SquadChannelController, self).setView(view)
        self.proto.unitChat.addHistory()

    def canSendMessage(self):
        if not self.isEnabled():
            return (False, '')
        return (False, getBroadcastIsInCoolDownMessage(MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC)) if self.proto.unitChat.isBroadcastInCooldown() else (True, '')

    def _broadcast(self, message):
        self.proto.unitChat.broadcast(message, 1)
