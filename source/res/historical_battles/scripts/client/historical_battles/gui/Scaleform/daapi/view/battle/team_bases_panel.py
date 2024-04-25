# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/team_bases_panel.py
from gui.Scaleform.daapi.view.battle.classic.team_bases_panel import TeamBasesPanel

class HBTeamBasesPanel(TeamBasesPanel):

    def setOffsetForEnemyPoints(self):
        pass

    def setTeamBaseCaptured(self, clientID, playerTeam):
        super(HBTeamBasesPanel, self).setTeamBaseCaptured(clientID, playerTeam)
        self.removeTeamBase(clientID)
