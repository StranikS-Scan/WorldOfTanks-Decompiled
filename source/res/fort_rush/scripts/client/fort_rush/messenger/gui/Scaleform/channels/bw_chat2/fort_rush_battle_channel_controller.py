# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/messenger/gui/Scaleform/channels/bw_chat2/fort_rush_battle_channel_controller.py
from __future__ import absolute_import
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from messenger.gui.Scaleform.channels.bw_chat2.battle_controllers import TeamChannelController
from messenger.m_constants import MESSENGER_COMMAND_TYPE
from messenger_common_chat2 import MESSENGER_ACTION_IDS
from gui.impl import backport
from gui.impl.gen import R

class FortRushTeamChannelController(TeamChannelController):
    _BASE_RELATED_COMMANDS_NAME = (BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT, BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT)

    def _formatCommand(self, command):
        isCurrent = False
        if command.getCommandType() == MESSENGER_COMMAND_TYPE.BATTLE:
            avatarSessionID = command.getSenderID()
            isCurrent = command.isSender()
            battleChatCommand = MESSENGER_ACTION_IDS.battleChatCommandFromActionID(command.getID())
            if battleChatCommand.name in self._BASE_RELATED_COMMANDS_NAME:
                commandText = backport.text(R.strings.ext_ingame_gui.chat_shortcuts.dyn(battleChatCommand.msgText)())
            else:
                commandText = command.getCommandText()
            text = self._mBuilder.setColors(avatarSessionID).setName(avatarSessionID).setText(commandText).build()
        else:
            text = command.getCommandText()
        return (isCurrent, text)
