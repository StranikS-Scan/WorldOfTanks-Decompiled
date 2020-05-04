# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/battle_chat_cmd.py
import struct
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
import Math
_TARGETED_CMD_NAMES = ('ATTACKENEMY', 'TURNBACK', 'FOLLOWME', 'HELPMEEX', 'SUPPORTMEWITHFIRE', 'STOP', 'EVENT_CHAT_1_EX', 'EVENT_CHAT_2_EX', 'EVENT_CHAT_3_EX', 'EVENT_CHAT_4_EX', 'EVENT_CHAT_5_EX', 'EVENT_CHAT_6_EX', 'EVENT_CHAT_7_EX')
_PUBLIC_CMD_NAMES = ('ATTACKENEMY', 'SUPPORTMEWITHFIRE', 'POSITIVE', 'NEGATIVE', 'RELOADING_READY', 'RELOADING_UNAVAILABLE', 'HELPME', 'RELOADINGGUN', 'RELOADING_CASSETE', 'RELOADING_READY_CASSETE', 'EVENT_CHAT_1', 'EVENT_CHAT_2', 'EVENT_CHAT_3', 'EVENT_CHAT_4', 'EVENT_CHAT_5', 'EVENT_CHAT_6', 'EVENT_CHAT_7')
_PRIVATE_CMD_NAMES = ('TURNBACK', 'FOLLOWME', 'HELPMEEX', 'STOP', 'EVENT_CHAT_1_EX', 'EVENT_CHAT_2_EX', 'EVENT_CHAT_3_EX', 'EVENT_CHAT_4_EX', 'EVENT_CHAT_5_EX', 'EVENT_CHAT_6_EX', 'EVENT_CHAT_7_EX')
_SHOW_MARKER_CMD_NAMES = ('ATTACKENEMY', 'SUPPORTMEWITHFIRE')
_ENEMY_TARGET_CMD_NAMES = ('ATTACKENEMY', 'SUPPORTMEWITHFIRE')
_MINIMAP_CMD_NAMES = ('ATTENTIONTOCELL', 'SPG_AIM_AREA')
_SPG_AIM_CMD_NAMES = ('SPG_AIM_AREA', 'ATTACKENEMY')
_EPIC_GLOBAL_CMD_NAMES = {'EPIC_GLOBAL_SAVETANKS_ATK',
 'EPIC_GLOBAL_SAVETANKS_DEF',
 'EPIC_GLOBAL_TIME_ATK',
 'EPIC_GLOBAL_TIME_DEF',
 'EPIC_GLOBAL_HQ_ATK',
 'EPIC_GLOBAL_HQ_DEF',
 'EPIC_GLOBAL_WEST',
 'EPIC_GLOBAL_CENTER',
 'EPIC_GLOBAL_EAST'}
_TARGETED_CMD_IDS = []
_PUBLIC_CMD_IDS = []
_PRIVATE_CMD_IDS = []
_SHOW_MARKER_CMD_IDS = []
_ENEMY_TARGET_CMD_IDS = []
_MINIMAP_CMD_IDS = []
_SPG_AIM_CMD_IDS = []
_MINIMAP_MARK_POSITION_ID = 0
_MINIMAP_MARK_OBJECTIVE_IDS = []
_MINIMAP_MARK_BASE_IDS = []
_GLOBAL_MESSAGE_IDS = []
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
    if cmdName in _MINIMAP_CMD_NAMES:
        _MINIMAP_CMD_IDS.append(cmdID)
    if cmdName in _SPG_AIM_CMD_NAMES:
        _SPG_AIM_CMD_IDS.append(cmdID)
    if cmdName == 'ATTENTIONTOPOSITION':
        _MINIMAP_MARK_POSITION_ID = cmdID
    if cmdName in ('ATTENTIONTOOBJECTIVE_ATK', 'ATTENTIONTOOBJECTIVE_DEF'):
        _MINIMAP_MARK_OBJECTIVE_IDS.append(cmdID)
    if cmdName in ('ATTENTIONTOBASE_ATK', 'ATTENTIONTOBASE_DEF'):
        _MINIMAP_MARK_BASE_IDS.append(cmdID)
    if cmdName in _EPIC_GLOBAL_CMD_NAMES:
        _GLOBAL_MESSAGE_IDS.append(cmdID)

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


class _ReceivedCmdDecorator(ReceivedBattleChatCommand):
    __slots__ = ('_commandID',)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

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
            return u''
        else:
            i18nKey = I18N_INGAME_GUI.chat_shortcuts(command.msgText)
            i18nArguments = {}
            if i18nKey is not None:
                if self.isOnMinimap():
                    cellIdx = None
                    if self.isSPGAimCommand():
                        try:
                            cellIdx, reloadTime = struct.unpack('<fffif', self._protoData['strArg1'])[3:]
                        except struct.error as e:
                            LOG_ERROR('The following command can not be unpacked: ', e)
                            return

                        if reloadTime > 0:
                            i18nArguments['reloadTime'] = reloadTime
                            i18nKey += '_reloading'
                    i18nArguments['cellName'] = self._getCellName(cellIdx)
                elif self.hasTarget():
                    i18nArguments['target'] = self._getTarget()
                    if self.isSPGAimCommand():
                        reloadTime = self._protoData['floatArg1']
                        if reloadTime > 0:
                            i18nArguments['reloadTime'] = reloadTime
                            i18nKey += '_reloading'
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
        return Math.Vector3(self._protoData['int32Arg1'], 0, self._protoData['floatArg1'])

    def getMarkedObjective(self):
        return self._protoData['int32Arg1']

    def getMarkedBase(self):
        return self._protoData['int32Arg1']

    def getMarkedBaseName(self):
        return self._protoData['strArg1']

    def isOnMinimap(self):
        return self._commandID in _MINIMAP_CMD_IDS

    def isOnEpicBattleMinimap(self):
        cmdArray = [_MINIMAP_MARK_POSITION_ID,
         _MINIMAP_MARK_OBJECTIVE_IDS[0],
         _MINIMAP_MARK_OBJECTIVE_IDS[1],
         _MINIMAP_MARK_BASE_IDS[0],
         _MINIMAP_MARK_BASE_IDS[1]]
        return self._commandID in cmdArray

    def isMarkedPosition(self):
        return self._commandID == _MINIMAP_MARK_POSITION_ID

    def isMarkedObjective(self):
        return self._commandID in _MINIMAP_MARK_OBJECTIVE_IDS

    def isMarkedBase(self):
        return self._commandID in _MINIMAP_MARK_BASE_IDS

    def isEpicGlobalMessage(self):
        return self._commandID in _GLOBAL_MESSAGE_IDS

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

    def _getTarget(self):
        target = self.sessionProvider.getCtx().getPlayerFullName(vID=self.getFirstTargetID())
        if self.isReceiver():
            target = g_settings.battle.targetFormat % {'target': target}
        return target

    def _getCellName(self, cellIdx=None):
        from gui.battle_control import minimap_utils
        return minimap_utils.getCellName(self.getFirstTargetID()) if cellIdx is None else minimap_utils.getCellName(cellIdx)

    def _getCommandVehMarker(self):
        command = _ACTIONS.battleChatCommandFromActionID(self._commandID)
        result = ''
        if not command:
            LOG_ERROR('Command is not found', self._commandID)
        elif command.vehMarker is not None:
            result = command.vehMarker
        return result


class BattleCommandFactory(IBattleCommandFactory):

    @staticmethod
    def createByAction(actionID, args):
        return _ReceivedCmdDecorator(actionID, args)

    def createSPGAimAreaCommand(self, dsp, cellIdx, reloadTime):
        record = struct.pack('<fffif', dsp.x, dsp.y, dsp.z, int(cellIdx), reloadTime)
        return _OutCmdDecorator('SPG_AIM_AREA', messageArgs(strArg1=record))

    def createSPGAimTargetCommand(self, targetID, reloadTime):
        return _OutCmdDecorator('ATTACKENEMY', messageArgs(int32Arg1=targetID, floatArg1=reloadTime))

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

    def createByCellIdx(self, cellIdx):
        return _OutCmdDecorator('ATTENTIONTOCELL', messageArgs(int32Arg1=cellIdx))

    def createByPosition(self, position):
        decorator = None
        if _MINIMAP_MARK_POSITION_ID:
            decorator = _OutCmdDecorator('ATTENTIONTOPOSITION', messageArgs(int32Arg1=position.x, floatArg1=position.z))
        return decorator

    def createByObjectiveIndex(self, idx, isAtk):
        decorator = None
        key = 'ATTENTIONTOOBJECTIVE_ATK' if isAtk else 'ATTENTIONTOOBJECTIVE_DEF'
        if _MINIMAP_MARK_OBJECTIVE_IDS:
            decorator = _OutCmdDecorator(key, messageArgs(int32Arg1=idx))
        return decorator

    def createByBaseIndex(self, idx, name, isAtk):
        decorator = None
        key = 'ATTENTIONTOBASE_ATK' if isAtk else 'ATTENTIONTOBASE_DEF'
        if _MINIMAP_MARK_BASE_IDS:
            decorator = _OutCmdDecorator(key, messageArgs(int32Arg1=idx, strArg1=name))
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
