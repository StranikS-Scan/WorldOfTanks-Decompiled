# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/unit_chat_cmd.py
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI as I18N_INGAME_GUI
from helpers import dependency
from helpers import i18n
from messenger import g_settings
from messenger.ext.channel_num_gen import getClientID4BattleChannel
from messenger.m_constants import PROTO_TYPE, BATTLE_CHANNEL
from messenger.proto.entities import OutChatCommand, ReceivedUnitChatCommand
from messenger.proto.interfaces import IUnitCommandFactory
from messenger_common_chat2 import messageArgs
from messenger_common_chat2 import UNIT_CHAT_COMMANDS, UNIT_CHAT_COMMANDS_BY_NAMES
_MINIMAP_CMD_ID = 0
for cmd in UNIT_CHAT_COMMANDS:
    cmdID = cmd.id
    cmdName = cmd.name
    if cmdName == 'ATTENTIONTOCELL':
        _MINIMAP_CMD_ID = cmdID

class _OutCmdDecorator(OutChatCommand):
    __slots__ = ('_name',)

    def __init__(self, name, args=None):
        super(_OutCmdDecorator, self).__init__(args or messageArgs(), 0)
        self._name = name

    def getID(self):
        return self.getCommand().id

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def getCommand(self):
        return UNIT_CHAT_COMMANDS_BY_NAMES[self._name]


class _ReceivedCmdDecorator(ReceivedUnitChatCommand):
    __slots__ = ('_commandID',)

    def __init__(self, commandID, args):
        super(_ReceivedCmdDecorator, self).__init__(args, 0)
        self._commandID = commandID

    def getID(self):
        return self._commandID

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def getCommandText(self):
        pass

    def getMapPosX(self):
        return self._protoData['int32Arg1']

    def getMapPosY(self):
        return self._protoData['floatArg1']

    def isOnMinimap(self):
        return self._commandID == _MINIMAP_CMD_ID


class UnitCommandFactory(IUnitCommandFactory):

    @staticmethod
    def createByAction(actionID, args):
        return _ReceivedCmdDecorator(actionID, args)

    def createByMapPos(self, x, y):
        decorator = None
        if _MINIMAP_CMD_ID:
            decorator = _OutCmdDecorator('ATTENTIONTOCELL', messageArgs(int32Arg1=x, floatArg1=y))
        return decorator
