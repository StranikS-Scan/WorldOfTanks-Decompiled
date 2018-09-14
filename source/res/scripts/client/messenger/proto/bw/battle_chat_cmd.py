# Embedded file name: scripts/client/messenger/proto/bw/battle_chat_cmd.py
from chat_shared import CHAT_COMMANDS
from debug_utils import LOG_ERROR
from helpers import i18n
from messenger import g_settings
from messenger.ext import getMinimapCellName
from messenger.m_constants import PROTO_TYPE
from messenger.proto.bw.find_criteria import BWBattleTeamChannelFindCriteria
from messenger.proto.bw.wrappers import ChatActionWrapper
from messenger.proto.entities import ReceivedBattleChatCommand
from messenger.proto.entities import OutChatCommand
from messenger.proto.interfaces import IBattleCommandFactory
from messenger.storage import storage_getter
_PUBLIC_ADR_CMD_INDEXES = (CHAT_COMMANDS.ATTACKENEMY.index(),
 CHAT_COMMANDS.SUPPORTMEWITHFIRE.index(),
 CHAT_COMMANDS.POSITIVE.index(),
 CHAT_COMMANDS.NEGATIVE.index(),
 CHAT_COMMANDS.RELOADING_READY.index(),
 CHAT_COMMANDS.RELOADING_UNAVAILABLE.index(),
 CHAT_COMMANDS.HELPME.index())
_PUBLIC_ARGUMENT_CMD_INDEXES = (CHAT_COMMANDS.RELOADINGGUN.index(), CHAT_COMMANDS.RELOADING_CASSETE.index(), CHAT_COMMANDS.RELOADING_READY_CASSETE.index())
_PRIVATE_ADR_CMD_INDEXES = (CHAT_COMMANDS.TURNBACK.index(),
 CHAT_COMMANDS.FOLLOWME.index(),
 CHAT_COMMANDS.HELPMEEX.index(),
 CHAT_COMMANDS.STOP.index())
_VEHICLE_TARGET_CMD_INDEXES = (CHAT_COMMANDS.ATTACKENEMY.index(),
 CHAT_COMMANDS.TURNBACK.index(),
 CHAT_COMMANDS.FOLLOWME.index(),
 CHAT_COMMANDS.HELPMEEX.index(),
 CHAT_COMMANDS.SUPPORTMEWITHFIRE.index(),
 CHAT_COMMANDS.STOP.index())
_SHOW_MARKER_FOR_RECEIVER_CMD_INDEXES = (CHAT_COMMANDS.ATTACKENEMY.index(), CHAT_COMMANDS.SUPPORTMEWITHFIRE.index())

def makeDecorator(commandData):
    from gui.battle_control import avatar_getter
    return _ReceivedCmdDecorator(commandData, avatar_getter.getPlayerVehicleID())


class _SendCmdDecorator(OutChatCommand):
    __slots__ = ('_command', '_params')

    def __init__(self, command, first = 0, second = 0):
        super(_SendCmdDecorator, self).__init__({'int64Arg': first,
         'int16Arg': second})
        self._command = command

    def getID(self):
        return self._command.index()

    def getProtoType(self):
        return PROTO_TYPE.BW

    def getCommand(self):
        return self._command


class _ReceivedCmdDecorator(ReceivedBattleChatCommand):
    __slots__ = ('_chatAction', '_playerVehID', '__publicArgumentCmdFormatters')

    def __init__(self, commandData, playerVehID):
        super(_ReceivedCmdDecorator, self).__init__(ChatActionWrapper(**dict(commandData)))
        self._protoData = ChatActionWrapper(**dict(commandData))
        self._playerVehID = playerVehID
        self.__publicArgumentCmdFormatters = (self._reloadingGunFormatter, self._reloadingCassetteFormatter, self._reloadingGunReadyFormatter)

    def getID(self):
        return self._protoData.channel

    def getProtoType(self):
        return PROTO_TYPE.BW

    def getCommandText(self):
        index = self.getCommandIndex()
        command = CHAT_COMMANDS[index]
        if command is None:
            LOG_ERROR('Chat command not found', self._protoData)
            return ''
        else:
            if command.argsCnt > 0:
                if index == CHAT_COMMANDS.ATTENTIONTOCELL.index():
                    text = self._makeMinimapCommandMessage(command)
                elif index in _VEHICLE_TARGET_CMD_INDEXES:
                    text = self._makeTargetedCommandMessage(command)
                elif index in _PUBLIC_ARGUMENT_CMD_INDEXES:
                    fmtIndex = _PUBLIC_ARGUMENT_CMD_INDEXES.index(index)
                    formatter = self.__publicArgumentCmdFormatters[fmtIndex]
                    text = formatter(command)
                else:
                    LOG_ERROR('Chat command is not supported', command.name())
                    text = ''
            else:
                text = i18n.makeString(command.msgText)
            return unicode(text, 'utf-8', errors='ignore')

    def getSenderID(self):
        return self._protoData.originator

    def getCommandIndex(self):
        return self._protoData.data[0]

    def getFirstTargetID(self):
        data = self._protoData.data
        if len(data) > 1:
            return data[1]
        return 0

    def getSecondTargetID(self):
        data = self._protoData.data
        if len(data) > 2:
            return data[2]
        return 0

    def getCellIndex(self):
        if self.isOnMinimap():
            return self.getSecondTargetID()
        return 0

    def getReloadingTime(self):
        data = self._protoData.data
        if len(data) > 1:
            return data[1]
        return 0

    def getAmmoQuantityInCassete(self):
        data = self._protoData.data
        if len(data) > 1:
            return data[1]
        return 0

    def getAmmoQuantityLeft(self):
        data = self._protoData.data
        if len(data) > 2:
            return data[2]
        return 0

    def getVehMarker(self, mode = None, vehicle = None):
        command = CHAT_COMMANDS[self.getCommandIndex()]
        result = ''
        if command is None:
            LOG_ERROR('Chat command not found', self._protoData)
        else:
            result = command.get('vehMarker', defval='')
        if vehicle:
            mode = 'SPG' if 'SPG' in vehicle.vehicleType.tags else ''
        if mode:
            result = '{0:>s}{1:>s}'.format(result, mode)
        return result

    def isOnMinimap(self):
        return self.getCommandIndex() == CHAT_COMMANDS.ATTENTIONTOCELL.index()

    def isPrivate(self):
        return self.getCommandIndex() in _PRIVATE_ADR_CMD_INDEXES

    def isPublic(self):
        return self.getCommandIndex() in _PUBLIC_ADR_CMD_INDEXES or self.getCommandIndex() in _PUBLIC_ARGUMENT_CMD_INDEXES

    def isReceiver(self):
        return self.getFirstTargetID() == self._playerVehID

    def showMarkerForReceiver(self):
        return self.getCommandIndex() in _SHOW_MARKER_FOR_RECEIVER_CMD_INDEXES

    def _makeMinimapCommandMessage(self, command):
        return i18n.makeString(command.msgText, cellName=getMinimapCellName(self.getSecondTargetID()))

    def _makeTargetedCommandMessage(self, command):
        from gui.battle_control import g_sessionProvider
        target = g_sessionProvider.getCtx().getFullPlayerName(vID=self.getFirstTargetID())
        text = command.msgText
        if self.isReceiver():
            target = g_settings.battle.targetFormat % {'target': target}
        return i18n.makeString(text, target=target)

    def _reloadingCassetteFormatter(self, command):
        reloadingTime = self.getReloadingTime()
        ammoQuantityLeft = self.getAmmoQuantityLeft()
        text = command.msgText
        return i18n.makeString(text, floatArg1=reloadingTime, int32Arg1=ammoQuantityLeft)

    def _reloadingGunFormatter(self, command):
        reloadingTime = self.getReloadingTime()
        text = command.msgText
        return i18n.makeString(text, floatArg1=reloadingTime)

    def _reloadingGunReadyFormatter(self, command):
        ammoInCassete = self.getAmmoQuantityInCassete()
        text = command.msgText
        return i18n.makeString(text, int32Arg1=ammoInCassete)


class BattleCommandFactory(IBattleCommandFactory):

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    def createByName(self, name):
        command = CHAT_COMMANDS.lookup(name)
        if command is None:
            return
        else:
            return self.__addClientID(_SendCmdDecorator(command))

    def createByNameTarget(self, name, targetID):
        if targetID is None:
            return
        else:
            command = CHAT_COMMANDS.lookup(name)
            if command is None:
                return
            return self.__addClientID(_SendCmdDecorator(command, first=targetID))

    def createByCellIdx(self, cellIdx):
        return self.__addClientID(_SendCmdDecorator(CHAT_COMMANDS.ATTENTIONTOCELL, second=cellIdx))

    def create4Reload(self, isCassetteClip, timeLeft, quantity):
        command = CHAT_COMMANDS.RELOADINGGUN
        first, second = (0, 0)
        if timeLeft > 0:
            first = timeLeft
            if isCassetteClip:
                if quantity > 0:
                    command = CHAT_COMMANDS.RELOADING_CASSETE
                    second = quantity
        elif quantity == 0:
            command = CHAT_COMMANDS.RELOADING_UNAVAILABLE
        elif isCassetteClip:
            command = CHAT_COMMANDS.RELOADING_READY_CASSETE
            first = quantity
        else:
            command = CHAT_COMMANDS.RELOADING_READY
        return self.__addClientID(_SendCmdDecorator(command, first, second))

    def __addClientID(self, decorator):
        channel = self.channelsStorage.getChannelByCriteria(BWBattleTeamChannelFindCriteria())
        if channel:
            decorator.setClientID(channel.getClientID())
        return decorator
