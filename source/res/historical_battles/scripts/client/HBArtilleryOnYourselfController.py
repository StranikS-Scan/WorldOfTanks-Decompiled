# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBArtilleryOnYourselfController.py
import BigWorld
from script_component.ScriptComponent import ScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES

class HBArtilleryOnYourselfController(ScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def activate(self, _):
        player = BigWorld.player()
        if player is not None:
            chatCommands = self.sessionProvider.shared.chatCommands
            if chatCommands is not None:
                chatCommands.handleChatCommand(BATTLE_CHAT_COMMAND_NAMES.HB_ARTILLERY_ON_YOURSELF, targetID=-1)
        return
