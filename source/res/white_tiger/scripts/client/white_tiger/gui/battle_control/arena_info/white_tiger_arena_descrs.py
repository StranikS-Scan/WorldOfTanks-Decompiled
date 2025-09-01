# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/arena_info/white_tiger_arena_descrs.py
import BattleReplay
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription
from gui.impl import backport
from white_tiger.gui.wt_event_helpers import isBossTeam
from gui.impl.gen import R

class WhiteTigerArenaDescription(ArenaWithLabelDescription):

    def getDescriptionString(self, isInBattle=True):
        return backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger())

    def getWinString(self, isInBattle=True):
        return backport.text(R.strings.white_tiger_battle_hints.loading.winText.boss()) if isBossTeam(self._team) else backport.text(R.strings.white_tiger_battle_hints.loading.winText.hunters())

    def getTeamName(self, team):
        return backport.text(R.strings.white_tiger_battle.stats.team.boss()) if isBossTeam(team) else backport.text(R.strings.white_tiger_battle.stats.team.hunters())

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying
