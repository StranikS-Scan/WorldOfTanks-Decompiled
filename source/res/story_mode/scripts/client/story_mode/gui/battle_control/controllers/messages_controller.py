# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/messages_controller.py
import BattleReplay
from gui.battle_control.controllers.msgs_ctrl import BattleMessagesController, BattleMessagesPlayer

class StoryModeBattleMessagesController(BattleMessagesController):

    def showDestructibleEntityDestroyedMessage(self, avatar, destructibleID, attackerID):
        self.onShowDestructibleEntityMessageByCode('BUNKER_DESTROYED', destructibleID, attackerID)


class StoryModeBattleMessagesPlayer(BattleMessagesPlayer):

    def showDestructibleEntityDestroyedMessage(self, avatar, destructibleID, attackerID):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        self.onShowDestructibleEntityMessageByCode('BUNKER_DESTROYED', destructibleID, attackerID)
