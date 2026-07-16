# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/controllers/chat_cmd_ctrl.py
from __future__ import absolute_import
import BigWorld
import CommandMapping
from gui.battle_control.controllers.chat_cmd_ctrl import ChatCommandsController
from helpers import dependency
from last_stand.skeletons.ls_controller import ILSController
from last_stand_common.last_stand_constants import LS_BATTLE_CHAT_COMMANDS

class LSChatCommandsController(ChatCommandsController):
    _lsCtrl = dependency.descriptor(ILSController)

    def handleContexChatCommand(self, key):
        if BigWorld.target() is None and self._lsCtrl.getModeSettings().isObeliskRadialMenuEnabled:
            cmdMap = CommandMapping.g_instance
            if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_THANKYOU, key):
                self.handleChatCommand(LS_BATTLE_CHAT_COMMANDS.LS_OBELISK)
                return
            if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE, key):
                self.handleChatCommand(LS_BATTLE_CHAT_COMMANDS.LS_OBELISK_HELP)
                return
        super(LSChatCommandsController, self).handleContexChatCommand(key)
        return
