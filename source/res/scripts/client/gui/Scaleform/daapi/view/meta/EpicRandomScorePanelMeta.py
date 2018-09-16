# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicRandomScorePanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicRandomScorePanelMeta(BaseDAAPIComponent):

    def as_setTeamHealthPercentagesS(self, team1, team2):
        return self.flashObject.as_setTeamHealthPercentages(team1, team2) if self._isDAAPIInited() else None
