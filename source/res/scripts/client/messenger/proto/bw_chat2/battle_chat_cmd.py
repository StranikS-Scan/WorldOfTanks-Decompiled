# Embedded file name: scripts/client/messenger/proto/bw_chat2/battle_chat_cmd.py
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from helpers import i18n
from messenger import g_settings
from messenger.ext import getMinimapCellName
from messenger.ext.channel_num_gen import getClientID4BattleChannel
from messenger.m_constants import PROTO_TYPE, BATTLE_CHANNEL
from messenger.proto.entities import OutChatCommand, ReceivedBattleChatCommand
from messenger.proto.interfaces import IBattleCommandFactory
from messenger_common_chat2 import messageArgs, BATTLE_CHAT_COMMANDS
from messenger_common_chat2 import BATTLE_CHAT_COMMANDS_BY_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
_TARGETED_CMD_NAMES = ('ATTACKENEMY', 'TURNBACK', 'FOLLOWME', 'HELPMEEX', 'SUPPORTMEWITHFIRE', 'STOP')
_PUBLIC_CMD_NAMES = ('ATTACKENEMY', 'SUPPORTMEWITHFIRE', 'POSITIVE', 'NEGATIVE', 'RELOADING_READY', 'RELOADING_UNAVAILABLE', 'HELPME', 'RELOADINGGUN', 'RELOADING_CASSETE', 'RELOADING_READY_CASSETE')
_PRIVATE_CMD_NAMES = ('TURNBACK', 'FOLLOWME', 'HELPMEEX', 'STOP')
_SHOW_MARKER_CMD_NAMES = ('ATTACKENEMY', 'SUPPORTMEWITHFIRE')
_ENEMY_TARGET_CMD_NAMES = ('ATTACKENEMY', 'SUPPORTMEWITHFIRE')
_TARGETED_CMD_IDS = []
_PUBLIC_CMD_IDS = []
_PRIVATE_CMD_IDS = []
_SHOW_MARKER_CMD_IDS = []
_ENEMY_TARGET_CMD_IDS = []
_MINIMAP_CMD_ID = 0
for cmd in BATTLE_CHAT_COMMANDS:
    cmdID = cmd.id
    cmdName = cmd.name
    if cmdName in _TARGETED_CMD_NAMES:
        _TARGETED_CMD_IDS.append(cmdID)
    if cmdName in _SHOW_MARKER_CMD_NAMES:
        _SHOW_MARKER_CMD_IDS.append(cmdID)
    if cmdName in _ENEMY_TARGET_CMD_NAMES:
        _ENEMY_TARGET_CMD_IDS.append(cmdID)
    if cmdName in _PUBLIC_CMD_NAMES:
        _PUBLIC_CMD_IDS.append(cmdID)
    elif cmdName in _PRIVATE_CMD_NAMES:
        _PRIVATE_CMD_IDS.append(cmdID)
    if cmdName == 'ATTENTIONTOCELL':
        _MINIMAP_CMD_ID = cmdID

class _OutCmdDecorator(OutChatCommand):
    __slots__ = ('_name',)

    def __init__(self, name, args = None):
        super(_OutCmdDecorator, self).__init__(args or messageArgs(), getClientID4BattleChannel(BATTLE_CHANNEL.TEAM.name))
        self._name = name

    def getID(self):
        return self.getCommand().id

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def getCommand(self):
        return BATTLE_CHAT_COMMANDS_BY_NAMES[self._name]

    def getTargetID(self):
        return self._protoData['int32Arg1']

    def isEnemyTarget(self):
        return self.getID() in _ENEMY_TARGET_CMD_IDS


class _ReceivedCmdDecorator(ReceivedBattleChatCommand):
    __slots__ = ('_commandID',)

    def __init__(self, commandID, args):
        super(_ReceivedCmdDecorator, self).__init__(args, getClientID4BattleChannel(BATTLE_CHANNEL.TEAM.name))
        self._commandID = commandID

    def getID(self):
        return self._commandID

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def getCommandText(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        if not command:
            LOG_ERROR('Command is not found', self._commandID)
            return ''
        else:
            i18nKey = I18N_INGAME_GUI.chat_shortcuts(command.msgText)
            if i18nKey is not None:
                if self.isOnMinimap():
                    text = i18n.makeString(i18nKey, cellName=self._getCellName())
                elif self.hasTarget():
                    text = i18n.makeString(i18nKey, target=self._getTarget())
                else:
                    text = i18n.makeString(i18nKey, **self._protoData)
            else:
                text = command.msgText
            return text

    def getSenderID(self):
        return self._protoData['int64Arg1']

    def getFirstTargetID(self):
        return self._protoData['int32Arg1']

    def getSecondTargetID(self):
        return self._protoData['floatArg1']

    def getCellIndex(self):
        if self.isOnMinimap():
            return self.getFirstTargetID()
        return 0

    def isOnMinimap(self):
        return self._commandID == _MINIMAP_CMD_ID

    def hasTarget(self):
        return self._commandID in _TARGETED_CMD_IDS

    def isPrivate(self):
        return self._commandID in _PRIVATE_CMD_IDS

    def isPublic(self):
        return self._commandID in _PUBLIC_CMD_IDS

    def showMarkerForReceiver(self):
        return self._commandID in _SHOW_MARKER_CMD_IDS

    def isReceiver(self):
        from gui.battle_control import avatar_getter
        return self.getFirstTargetID() == avatar_getter.getPlayerVehicleID()

    def _getTarget(self):
        from gui.battle_control import g_sessionProvider
        target = g_sessionProvider.getCtx().getFullPlayerName(vID=self.getFirstTargetID())
        if self.isReceiver():
            target = g_settings.battle.targetFormat % {'target': target}
        return target

    def _getCellName(self):
        return getMinimapCellName(self.getFirstTargetID())

    def _getCommandVehMarker(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        result = ''
        if not command:
            LOG_ERROR('Command is not found', self._commandID)
        else:
            result = command.vehMarker
        return result


class BattleCommandFactory(IBattleCommandFactory):

    @staticmethod
    def createByAction(actionID, args):
        return _ReceivedCmdDecorator(actionID, args)

    def createByName(self, name):
        decorator = None
        if name in BATTLE_CHAT_COMMANDS_BY_NAMES:
            decorator = _OutCmdDecorator(name)
        return decorator

    def createByNameTarget(self, name, targetID):
        decorator = None
        if name in BATTLE_CHAT_COMMANDS_BY_NAMES:
            decorator = _OutCmdDecorator(name, messageArgs(int32Arg1=targetID))
        return decorator

    def createByCellIdx(self, cellIdx):
        decorator = None
        if _MINIMAP_CMD_ID:
            decorator = _OutCmdDecorator('ATTENTIONTOCELL', messageArgs(int32Arg1=cellIdx))
        return decorator

    def create4Reload(self, isCassetteClip, timeLeft, quantity):
        name = 'RELOADINGGUN'
        args = None
        if timeLeft > 0:
            floatArg1 = timeLeft
            int32Arg1 = 0
            if isCassetteClip:
                if quantity > 0:
                    name = 'RELOADING_CASSETE'
                    int32Arg1 = quantity
            args = messageArgs(int32Arg1=int32Arg1, floatArg1=floatArg1)
        elif quantity == 0:
            name = 'RELOADING_UNAVAILABLE'
        elif isCassetteClip:
            name = 'RELOADING_READY_CASSETE'
            args = messageArgs(int32Arg1=quantity)
        else:
            name = 'RELOADING_READY'
        if name in BATTLE_CHAT_COMMANDS_BY_NAMES:
            decorator = _OutCmdDecorator(name, args)
        else:
            decorator = None
        return decorator

    def getEnemyTargetCommandsIDs(self):
        return _ENEMY_TARGET_CMD_IDS
