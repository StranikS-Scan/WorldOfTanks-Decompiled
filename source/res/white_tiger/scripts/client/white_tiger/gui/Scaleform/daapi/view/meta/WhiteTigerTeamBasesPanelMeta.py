# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/meta/WhiteTigerTeamBasesPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.team_bases_panel import TeamBasesPanel

class WhiteTigerTeamBasesPanelMeta(TeamBasesPanel):

    def as_updateCaptureS(self, id, points, rate, captureTime, vehiclesCount, captureString, colorType, locked):
        return self.flashObject.as_updateCapture(id, points, rate, captureTime, vehiclesCount, captureString, colorType, locked) if self._isDAAPIInited() else None
