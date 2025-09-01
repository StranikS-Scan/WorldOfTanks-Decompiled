# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/chat_cmd_ctrl.py
from gui.battle_control.controllers.chat_cmd_ctrl import ChatCommandsController
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME

class WTChatCommandsController(ChatCommandsController):

    def sendCommandToBase(self, baseIdx, cmdName, baseName=''):
        baseName = ID_TO_BASENAME[baseIdx]
        super(WTChatCommandsController, self).sendCommandToBase(baseIdx, cmdName, baseName)
