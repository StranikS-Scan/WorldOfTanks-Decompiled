# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballScorePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FootballScorePanelMeta(BaseDAAPIComponent):

    def as_setTeamScoresS(self, team1, team2):
        return self.flashObject.as_setTeamScores(team1, team2) if self._isDAAPIInited() else None
