# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ResearchPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ResearchPanelMeta(BaseDAAPIComponent):

    def goToResearch(self):
        self._printOverrideError('goToResearch')

    def addVehToCompare(self):
        self._printOverrideError('addVehToCompare')

    def as_updateCurrentVehicleS(self, data):
        """
        :param data: Represented by ResearchPanelVO (AS)
        """
        return self.flashObject.as_updateCurrentVehicle(data) if self._isDAAPIInited() else None

    def as_setEarnedXPS(self, earnedXP):
        return self.flashObject.as_setEarnedXP(earnedXP) if self._isDAAPIInited() else None

    def as_setEliteS(self, isElite):
        return self.flashObject.as_setElite(isElite) if self._isDAAPIInited() else None

    def as_setIGRLabelS(self, visible, value):
        return self.flashObject.as_setIGRLabel(visible, value) if self._isDAAPIInited() else None

    def as_actionIGRDaysLeftS(self, visible, value):
        return self.flashObject.as_actionIGRDaysLeft(visible, value) if self._isDAAPIInited() else None

    def as_setNavigationEnabledS(self, value):
        return self.flashObject.as_setNavigationEnabled(value) if self._isDAAPIInited() else None
