# Embedded file name: scripts/client/messenger/proto/bw/battle_chat_cmd.py
from chat_shared import CHAT_COMMANDS
from debug_utils import LOG_ERROR
from gui.arena_info import getPlayerVehicleID
from helpers import i18n
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto.bw.wrappers import ChatActionWrapper
from messenger.proto.entities import ReceivedChatCommand
from messenger.proto.entities import SendChatCommand
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
    return ReceivedChatCommandDecorator(commandData, getPlayerVehicleID())


def getMinimapCellName(cellIdx):
    from gui.WindowsManager import g_windowsManager
    battleWindow = g_windowsManager.battleWindow
    if battleWindow:
        cellName = battleWindow.minimap.getCellName(cellIdx)
    else:
        cellName = 'N/A'
    return cellName


class SendChatCommandDecorator(SendChatCommand):
    __slots__ = ('_command', '_params')

    def __init__(self, command, first = 0, second = 0):
        super(SendChatCommandDecorator, self).__init__()
        self._command = command
        self._params = {'int64Arg': first,
         'int16Arg': second}

    def getProtoType(self):
        return PROTO_TYPE.BW

    def getCommand(self):
        return self._command

    def getParams(self):
        return self._params

    def setFirstParam(self, value):
        self._params['int64Arg'] = value

    def setSecondParam(self, value):
        self._params['int16Arg'] = value


class ReceivedChatCommandDecorator(ReceivedChatCommand):
    __slots__ = ('_chatAction', '_playerVehID', '__publicArgumentCmdFormatters')

    def __init__(self, commandData, playerVehID):
        super(ReceivedChatCommandDecorator, self).__init__()
        self._chatAction = ChatActionWrapper(**dict(commandData))
        self._playerVehID = playerVehID
        self.__publicArgumentCmdFormatters = (self._reloadingGunFormatter, self._reloadingCassetteFormatter, self._reloadingGunReadyFormatter)

    def getID(self):
        return self._chatAction.channel

    def getProtoType(self):
        return PROTO_TYPE.BW

    def getProtoData(self):
        return self._chatAction

    def getCommandText(self):
        index = self.getCommandIndex()
        command = CHAT_COMMANDS[index]
        if command is None:
            LOG_ERROR('Chat command not found', self._chatAction)
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
        return self._chatAction.originator

    def getCommandIndex(self):
        return self._chatAction.data[0]

    def getFirstTargetID(self):
        data = self._chatAction.data
        if len(data) > 1:
            return data[1]
        return 0

    def getReloadingTime(self):
        data = self._chatAction.data
        if len(data) > 1:
            return data[1]
        return 0

    def getAmmoQuantityInCassete(self):
        data = self._chatAction.data
        if len(data) > 1:
            return data[1]
        return 0

    def getAmmoQuantityLeft(self):
        data = self._chatAction.data
        if len(data) > 2:
            return data[2]
        return 0

    def getSecondTargetID(self):
        data = self._chatAction.data
        if len(data) > 2:
            return data[2]
        return 0

    def getVehMarker(self, mode = None, vehicle = None):
        command = CHAT_COMMANDS[self.getCommandIndex()]
        result = ''
        if command is None:
            LOG_ERROR('Chat command not found', self._chatAction)
        else:
            result = command.get('vehMarker', defval='')
        if vehicle:
            mode = 'SPG' if 'SPG' in vehicle.vehicleType.tags else ''
        if mode:
            result = '{0:>s}{1:>s}'.format(result, mode)
        return result

    def getVehMarkers(self, vehicle = None):
        mode = ''
        if vehicle:
            mode = 'SPG' if 'SPG' in vehicle.vehicleType.tags else ''
        return (self.getVehMarker(mode=mode), 'attackSender{0:>s}'.format(mode))

    def getSoundEventName(self):
        return 'chat_shortcut_common_fx'

    def isIgnored(self):
        user = storage_getter('users')().getUser(self.getSenderID())
        if user:
            return user.isIgnored()
        return False

    def isPrivate(self):
        return self.getCommandIndex() in _PRIVATE_ADR_CMD_INDEXES

    def isPublic(self):
        return self.getCommandIndex() in _PUBLIC_ADR_CMD_INDEXES or self.getCommandIndex() in _PUBLIC_ARGUMENT_CMD_INDEXES

    def isReceiver(self):
        return self.getFirstTargetID() == self._playerVehID

    def isSender(self):
        user = storage_getter('users')().getUser(self.getSenderID())
        if user:
            return user.isCurrentPlayer()
        return False

    def showMarkerForReceiver(self):
        return self.getCommandIndex() in _SHOW_MARKER_FOR_RECEIVER_CMD_INDEXES

    def _makeMinimapCommandMessage(self, command):
        return i18n.makeString(command.msgText, getMinimapCellName(self.getSecondTargetID()))

    def _makeTargetedCommandMessage(self, command):
        from gui.BattleContext import g_battleContext
        target = g_battleContext.getFullPlayerName(vID=self.getFirstTargetID())
        text = command.msgText
        if self.isReceiver():
            target = g_settings.battle.targetFormat % {'target': target}
        return i18n.makeString(text, target)

    def _reloadingCassetteFormatter(self, command):
        reloadingTime = self.getReloadingTime()
        ammoQuantityLeft = self.getAmmoQuantityLeft()
        text = command.msgText
        return i18n.makeString(text, rTime=reloadingTime, ammoQuantityLeft=ammoQuantityLeft)

    def _reloadingGunFormatter(self, command):
        reloadingTime = self.getReloadingTime()
        text = command.msgText
        return i18n.makeString(text, rTime=reloadingTime)

    def _reloadingGunReadyFormatter(self, command):
        ammoInCassete = self.getAmmoQuantityInCassete()
        text = command.msgText
        return i18n.makeString(text, ammoInCassete=ammoInCassete)
