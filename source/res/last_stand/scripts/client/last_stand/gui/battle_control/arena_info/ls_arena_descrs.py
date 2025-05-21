# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/arena_info/ls_arena_descrs.py
import BattleReplay
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription

class LSArenaDescription(ArenaWithLabelDescription):

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying

    def getArenaBonusType(self):
        return self._visitor.getArenaBonusType()
