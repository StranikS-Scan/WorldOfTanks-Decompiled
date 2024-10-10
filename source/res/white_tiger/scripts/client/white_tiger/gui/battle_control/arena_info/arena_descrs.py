# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/arena_info/arena_descrs.py
import BattleReplay
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription
from gui.wt_event.wt_event_helpers import isBossTeam

class WhiteTigerArenaDescription(ArenaWithLabelDescription):

    def getDescriptionString(self, isInBattle=True):
        return backport.text(R.strings.event.loading.battleTypes.wt())

    def getWinString(self, isInBattle=True):
        return backport.text(R.strings.event.loading.winText.boss()) if isBossTeam(self._team) else backport.text(R.strings.event.loading.winText.hunters())

    def getTeamName(self, team):
        return backport.text(R.strings.event.stats.team.boss()) if isBossTeam(team) else backport.text(R.strings.event.stats.team.hunters())

    def isInvitationEnabled(self):
        replayCtrl = BattleReplay.g_replayCtrl
        return not replayCtrl.isPlaying
