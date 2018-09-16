# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TeamBasesPanelMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TeamBasesPanelMeta(BaseDAAPIComponent):

    def as_addS(self, barId, sortWeight, colorType, title, points, captureTime, vehiclesCount):
        return self.flashObject.as_add(barId, sortWeight, colorType, title, points, captureTime, vehiclesCount) if self._isDAAPIInited() else None

    def as_removeS(self, id):
        return self.flashObject.as_remove(id) if self._isDAAPIInited() else None

    def as_stopCaptureS(self, id, points):
        return self.flashObject.as_stopCapture(id, points) if self._isDAAPIInited() else None

    def as_updateCaptureDataS(self, id, points, rate, captureTime, vehiclesCount, captureString):
        return self.flashObject.as_updateCaptureData(id, points, rate, captureTime, vehiclesCount, captureString) if self._isDAAPIInited() else None

    def as_setCapturedS(self, id, title):
        return self.flashObject.as_setCaptured(id, title) if self._isDAAPIInited() else None

    def as_setOffsetForEnemyPointsS(self):
        return self.flashObject.as_setOffsetForEnemyPoints() if self._isDAAPIInited() else None

    def as_clearS(self):
        return self.flashObject.as_clear() if self._isDAAPIInited() else None
