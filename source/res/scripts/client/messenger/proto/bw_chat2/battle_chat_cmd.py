# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/battle_chat_cmd.py
import struct
import Math
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from helpers import dependency
from helpers import i18n
from messenger import g_settings
from messenger.ext.channel_num_gen import getClientID4BattleChannel
from messenger.m_constants import PROTO_TYPE, BATTLE_CHANNEL
from messenger.proto.entities import OutChatCommand, ReceivedBattleChatCommand
from messenger.proto.interfaces import IBattleCommandFactory
from messenger_common_chat2 import BATTLE_CHAT_COMMANDS_BY_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from messenger_common_chat2 import messageArgs, BATTLE_CHAT_COMMANDS
from skeletons.gui.battle_session import IBattleSessionProvider
AUTOCOMMIT_COMMAND_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
 BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.GOING_THERE,
 BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE)
LOCATION_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA,
 BATTLE_CHAT_COMMAND_NAMES.GOING_THERE,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
 BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT,
 BATTLE_CHAT_COMMAND_NAMES.VEHICLE_SPOTPOINT,
 BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT,
 BATTLE_CHAT_COMMAND_NAMES.NAVIGATION_POINT)
EPIC_GLOBAL_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_SAVE_TANKS_ATK,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_TIME_ATK,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_HQ_ATK,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_TIME_DEF,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_SAVE_TANKS_DEF,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_HQ_DEF,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_WEST,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_CENTER,
 BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_EAST)
TARGETED_VEHICLE_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
 BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.THANKS,
 BATTLE_CHAT_COMMAND_NAMES.REPLY,
 BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY,
 BATTLE_CHAT_COMMAND_NAMES.CLEAR_CHAT_COMMANDS,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7_EX)
BASE_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE)
OBJECTIVE_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE,
 BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE,
 BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE)
_PUBLIC_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.CONFIRM,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_UNAVAILABLE,
 BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_CASSETE,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY_CASSETE,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7,
 BATTLE_CHAT_COMMAND_NAMES.VEHICLE_SPOTPOINT,
 BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT,
 BATTLE_CHAT_COMMAND_NAMES.NAVIGATION_POINT)
_PRIVATE_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
 BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.THANKS,
 BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6_EX,
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7_EX)
_SHOW_MARKER_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY)
_ENEMY_TARGET_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG, BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY, BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY)
_MINIMAP_CMD_NAMES = ('ATTENTIONTOCELL',)
_SPG_AIM_CMD_NAMES = (BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA, BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG)
_VEHICLE_COMMAND_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_UNAVAILABLE,
 BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_CASSETE,
 BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY_CASSETE,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
 BATTLE_CHAT_COMMAND_NAMES.THANKS,
 BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.CONFIRM)
_MUTE_MESSAGE_NAMES = (BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,)
_TEMPORARY_STICKY_NAMES = (BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
 BATTLE_CHAT_COMMAND_NAMES.THANKS,
 BATTLE_CHAT_COMMAND_NAMES.CONFIRM,
 BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT,
 BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
 BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA,
 BATTLE_CHAT_COMMAND_NAMES.VEHICLE_SPOTPOINT,
 BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT,
 BATTLE_CHAT_COMMAND_NAMES.NAVIGATION_POINT)
_TARGETED_CMD_IDS = []
_PUBLIC_CMD_IDS = []
_PRIVATE_CMD_IDS = []
_SHOW_MARKER_CMD_IDS = []
_ENEMY_TARGET_CMD_IDS = []
_MINIMAP_CMD_IDS = []
_SPG_AIM_CMD_IDS = []
_OBJECTIVE_CMD_IDS = []
_BASE_CMD_IDS = []
_GLOBAL_MESSAGE_IDS = []
_REPLY_ID = 0
_CANCEL_REPLY_ID = 0
_CLEAR_CHAT_COMMANDS_ID = 0
_SUPPORTING_ALLY_ID = 0
_BASE_COMMAND_IDS = []
_LOCATION_COMMAND_IDS = []
_VEHICLE_COMMAND_IDS = []
_AUTOCOMMIT_COMMAND_IDS = []
_MUTED_MESSAGE_IDS = []
_TEMPORARY_STICKY_IDS = []
for cmd in BATTLE_CHAT_COMMANDS:
    cmdID = cmd.id
    cmdName = cmd.name
    if cmdName in TARGETED_VEHICLE_CMD_NAMES:
        _TARGETED_CMD_IDS.append(cmdID)
    if cmdName in _SHOW_MARKER_CMD_NAMES:
        _SHOW_MARKER_CMD_IDS.append(cmdID)
    if cmdName in _ENEMY_TARGET_CMD_NAMES:
        _ENEMY_TARGET_CMD_IDS.append(cmdID)
    if cmdName in _PUBLIC_CMD_NAMES:
        _PUBLIC_CMD_IDS.append(cmdID)
    elif cmdName in _PRIVATE_CMD_NAMES:
        _PRIVATE_CMD_IDS.append(cmdID)
    if cmdName in _MINIMAP_CMD_NAMES:
        _MINIMAP_CMD_IDS.append(cmdID)
    if cmdName in _SPG_AIM_CMD_NAMES:
        _SPG_AIM_CMD_IDS.append(cmdID)
    if cmdName in LOCATION_CMD_NAMES:
        _LOCATION_COMMAND_IDS.append(cmdID)
    if cmdName in BASE_CMD_NAMES:
        _BASE_COMMAND_IDS.append(cmdID)
    if cmdName in _VEHICLE_COMMAND_NAMES:
        _VEHICLE_COMMAND_IDS.append(cmdID)
    if cmdName in AUTOCOMMIT_COMMAND_NAMES:
        _AUTOCOMMIT_COMMAND_IDS.append(cmdID)
    if cmdName in _MUTE_MESSAGE_NAMES:
        _MUTED_MESSAGE_IDS.append(cmdID)
    if cmdName == BATTLE_CHAT_COMMAND_NAMES.REPLY:
        _REPLY_ID = cmdID
    if cmdName == BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY:
        _CANCEL_REPLY_ID = cmdID
    if cmdName == BATTLE_CHAT_COMMAND_NAMES.CLEAR_CHAT_COMMANDS:
        _CLEAR_CHAT_COMMANDS_ID = cmdID
    if cmdName == BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY:
        _SUPPORTING_ALLY_ID = cmdID
    if cmdName in OBJECTIVE_CMD_NAMES:
        _OBJECTIVE_CMD_IDS.append(cmdID)
    if cmdName in BASE_CMD_NAMES:
        _BASE_CMD_IDS.append(cmdID)
    if cmdName in EPIC_GLOBAL_CMD_NAMES:
        _GLOBAL_MESSAGE_IDS.append(cmdID)
    if cmdName in _TEMPORARY_STICKY_NAMES:
        _TEMPORARY_STICKY_IDS.append(cmdID)

class _OutCmdDecorator(OutChatCommand):
    __slots__ = ('_name',)

    def __init__(self, name, args=None):
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

    def isServerCommand(self):
        return False


class _ReceivedCmdDecorator(ReceivedBattleChatCommand):
    __slots__ = ('_commandID', '__isSilentMode')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, commandID, args):
        super(_ReceivedCmdDecorator, self).__init__(args, getClientID4BattleChannel(BATTLE_CHANNEL.TEAM.name))
        self._commandID = commandID
        self.__isSilentMode = False

    def getID(self):
        return self._commandID

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def getCommandText(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        if not command:
            LOG_ERROR('Command is not found', self._commandID)
            return u''
        else:
            i18nKey = I18N_INGAME_GUI.chat_shortcuts(command.msgText)
            i18nArguments = {}
            if i18nKey is not None:
                if self.isOnMinimap():
                    if self.isSPGAimCommand():
                        reloadTime = self._protoData['floatArg1']
                        if reloadTime > 0:
                            i18nArguments['reloadTime'] = reloadTime
                            i18nKey += '_reloading'
                elif self.hasTarget():
                    i18nArguments['target'] = self._getTarget()
                    if self.isSPGAimCommand():
                        reloadTime = self._protoData['floatArg1']
                        if reloadTime > 0:
                            i18nArguments['reloadTime'] = reloadTime
                            i18nKey += '_reloading'
                        elif reloadTime < 0:
                            i18nKey += '_empty'
                elif self.isBaseRelatedCommand():
                    strArg = self._protoData['strArg1']
                    if strArg != '':
                        i18nArguments['strArg1'] = strArg
                        i18nKey += '_numbered'
                elif self.isLocationRelatedCommand():
                    if self.isSPGAimCommand():
                        reloadTime = self._protoData['floatArg1']
                        if reloadTime > 0:
                            i18nArguments['reloadTime'] = reloadTime
                            i18nKey += '_reloading'
                        elif reloadTime < 0:
                            i18nKey += '_empty'
                    mapsCtrl = self.sessionProvider.dynamic.maps
                    if mapsCtrl and mapsCtrl.hasMinimapGrid():
                        cellId = mapsCtrl.getMinimapCellIdByPosition(self.getMarkedPosition())
                        if cellId is None:
                            cellId = self.getFirstTargetID()
                        i18nKey += '_gridInfo'
                        i18nArguments['gridId'] = mapsCtrl.getMinimapCellNameById(cellId)
                else:
                    i18nArguments = self._protoData
                text = i18n.makeString(i18nKey, **i18nArguments)
            else:
                text = command.msgText
            return unicode(text, 'utf-8', errors='ignore')

    def getSenderID(self):
        return self.sessionProvider.getArenaDP().getSessionIDByVehID(self._protoData['int64Arg1'])

    def getFirstTargetID(self):
        return self._protoData['int32Arg1']

    def getSecondTargetID(self):
        return self._protoData['floatArg1']

    def getCommandData(self):
        return self._protoData

    def getCellIndex(self):
        return self.getFirstTargetID() if self.isOnMinimap() else 0

    def isSPGAimCommand(self):
        return self._commandID in _SPG_AIM_CMD_IDS

    def getMarkedPosition(self):
        x, y, z = struct.unpack('<fff', self._protoData['strArg2'])
        return Math.Vector3(x, y, z)

    def getMarkedObjective(self):
        return self._protoData['int32Arg1']

    def getMarkedBase(self):
        return self._protoData['int32Arg1']

    def getRepliedToChatCommand(self):
        return self._protoData['strArg1']

    def isOnMinimap(self):
        return self._commandID in _MINIMAP_CMD_IDS

    def isReply(self):
        return self._commandID == _REPLY_ID

    def isCancelReply(self):
        return self._commandID == _CANCEL_REPLY_ID

    def isClearChatCommand(self):
        return self._commandID == _CLEAR_CHAT_COMMANDS_ID

    def isServerCommand(self):
        return self.sessionProvider.arenaVisitor.getArenaUniqueID() == self._protoData['int64Arg1']

    def isMarkedObjective(self):
        return self._commandID in _OBJECTIVE_CMD_IDS

    def isLocationRelatedCommand(self):
        return self._commandID in _LOCATION_COMMAND_IDS

    def isBaseRelatedCommand(self):
        return self._commandID in _BASE_COMMAND_IDS

    def isVehicleRelatedCommand(self):
        return self._commandID in _VEHICLE_COMMAND_IDS

    def hasNoChatMessage(self):
        if self._commandID == _SUPPORTING_ALLY_ID and (self.isSender() or self.isReceiver()):
            return False
        else:
            command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
            if not command:
                LOG_ERROR('Command is not found', self._commandID)
                return False
            return command.msgText is None or self._commandID == _SUPPORTING_ALLY_ID

    def isEpicGlobalMessage(self):
        return self._commandID in _GLOBAL_MESSAGE_IDS

    def hasTarget(self):
        return self._commandID in _TARGETED_CMD_IDS

    def isAutoCommit(self):
        return self._commandID in _AUTOCOMMIT_COMMAND_IDS

    def isPrivate(self):
        return self._commandID in _PRIVATE_CMD_IDS

    def isPublic(self):
        return self._commandID in _PUBLIC_CMD_IDS

    def showMarkerForReceiver(self):
        return self._commandID in _SHOW_MARKER_CMD_IDS

    def isReceiver(self):
        return self.getFirstTargetID() == self.sessionProvider.getArenaDP().getPlayerVehicleID()

    def isMsgOnMarker(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        return command is not None and command.msgOnMarker is not None

    def messageOnMarker(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        i18nKey = I18N_INGAME_GUI.chat_shortcuts(command.msgOnMarker)
        if i18nKey is not None:
            text = i18n.makeString(i18nKey)
        else:
            text = command.msgOnMarker
        return unicode(text, 'utf-8', errors='ignore')

    def isMuteTypeMessage(self):
        return self._commandID in _MUTED_MESSAGE_IDS

    def isTemporarySticky(self):
        return self._commandID in _TEMPORARY_STICKY_IDS

    def setSilentMode(self, mode):
        self.__isSilentMode = mode

    def isInSilentMode(self):
        return self.__isSilentMode

    def _getTarget(self):
        target = self.sessionProvider.getCtx().getPlayerFullName(vID=self.getFirstTargetID())
        if self.isReceiver():
            target = g_settings.battle.targetFormat % {'target': target}
        return target

    def _getCommandVehMarker(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        result = ''
        if not command:
            LOG_ERROR('Command is not found', self._commandID)
        elif command.vehMarker is not None:
            result = command.vehMarker
        return result

    def _getCommandSenderVehMarker(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        result = ''
        if not command:
            LOG_ERROR('Command is not found', self._commandID)
        elif command.senderVehMarker is not None:
            result = command.senderVehMarker
        return result

    def _getSoundNotification(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        if not command:
            LOG_ERROR('Command is not found', self._commandID)
            return ''
        return command.soundNotification


class BattleCommandFactory(IBattleCommandFactory):

    @staticmethod
    def createByAction(actionID, args):
        return _ReceivedCmdDecorator(actionID, args)

    def createSPGAimTargetCommand(self, targetID, reloadTime):
        return _OutCmdDecorator(BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG, messageArgs(int32Arg1=targetID, floatArg1=reloadTime))

    def createByName(self, name):
        decorator = None
        if name in BATTLE_CHAT_COMMANDS_BY_NAMES:
            decorator = _OutCmdDecorator(name)
        return decorator

    def createByGlobalMsgName(self, actionID, baseName=''):
        decorator = None
        if _GLOBAL_MESSAGE_IDS:
            decorator = _OutCmdDecorator(actionID, messageArgs(strArg1=baseName))
        return decorator

    def createByNameTarget(self, name, targetID):
        decorator = None
        if name in BATTLE_CHAT_COMMANDS_BY_NAMES:
            decorator = _OutCmdDecorator(name, messageArgs(int32Arg1=targetID))
        return decorator

    def createByPosition(self, position, name, reloadTime=0.0):
        decorator = None
        if name in BATTLE_CHAT_COMMANDS_BY_NAMES:
            record = struct.pack('<fff', position.x, position.y, position.z)
            msgArgs = messageArgs(strArg2=record)
            if reloadTime != 0.0:
                msgArgs = messageArgs(floatArg1=reloadTime, strArg2=record)
            decorator = _OutCmdDecorator(name, msgArgs)
        return decorator

    def createByObjectiveIndex(self, idx, isAtk, commandName):
        decorator = None
        if _OBJECTIVE_CMD_IDS:
            decorator = _OutCmdDecorator(commandName, messageArgs(int32Arg1=idx))
        return decorator

    def createByBaseIndexAndName(self, baseIdx, commandName, baseName):
        decorator = None
        if commandName in BASE_CMD_NAMES:
            decorator = _OutCmdDecorator(commandName, messageArgs(int32Arg1=baseIdx, strArg1=baseName))
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
        elif quantity <= 0:
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

    def createReplyByName(self, replyID, replyType, replierID):
        return _OutCmdDecorator(BATTLE_CHAT_COMMAND_NAMES.REPLY, messageArgs(int32Arg1=replyID, int64Arg1=replierID, strArg1=replyType))

    def createCancelReplyByName(self, targetIDOfReply, replyAction, replierID):
        return _OutCmdDecorator(BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY, messageArgs(int32Arg1=targetIDOfReply, int64Arg1=replierID, strArg1=replyAction))

    def createClearChatCommandsFromTarget(self, targetID, targetMarkerType):
        return _OutCmdDecorator(BATTLE_CHAT_COMMAND_NAMES.CLEAR_CHAT_COMMANDS, messageArgs(int32Arg1=targetID, strArg1=targetMarkerType))

    def getEnemyTargetCommandsIDs(self):
        return _ENEMY_TARGET_CMD_IDS
