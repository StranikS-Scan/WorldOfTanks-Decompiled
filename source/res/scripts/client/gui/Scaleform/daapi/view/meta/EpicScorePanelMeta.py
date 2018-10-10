# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicScorePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicScorePanelMeta(BaseDAAPIComponent):

    def as_updateBasesS(self, west, center, east):
        return self.flashObject.as_updateBases(west, center, east) if self._isDAAPIInited() else None

    def as_updateHeadquarterHealthS(self, id, healthInPercent):
        return self.flashObject.as_updateHeadquarterHealth(id, healthInPercent) if self._isDAAPIInited() else None

    def as_headquarterDestroyedS(self, idx):
        return self.flashObject.as_headquarterDestroyed(idx) if self._isDAAPIInited() else None

    def as_updatePointsForBaseS(self, idx, points):
        return self.flashObject.as_updatePointsForBase(idx, points) if self._isDAAPIInited() else None

    def as_setTargetS(self, targetType, targetId):
        return self.flashObject.as_setTarget(targetType, targetId) if self._isDAAPIInited() else None

    def as_setPrebattleTimerS(self, remainingPrebattleTime):
        return self.flashObject.as_setPrebattleTimer(remainingPrebattleTime) if self._isDAAPIInited() else None
