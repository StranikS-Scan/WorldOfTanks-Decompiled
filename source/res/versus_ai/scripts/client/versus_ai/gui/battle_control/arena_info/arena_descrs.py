# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/battle_control/arena_info/arena_descrs.py
import BattleReplay
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription

class VersusAIArenaDescription(ArenaWithLabelDescription):

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying
