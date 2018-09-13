# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchPanelMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ResearchPanelMeta(DAAPIModule):

    def goToResearch(self):
        self._printOverrideError('goToResearch')

    def as_setEarnedXPS(self, earnedXP):
        if self._isDAAPIInited():
            return self.flashObject.as_setEarnedXP(earnedXP)

    def as_setEliteS(self, isElite):
        if self._isDAAPIInited():
            return self.flashObject.as_setElite(isElite)
