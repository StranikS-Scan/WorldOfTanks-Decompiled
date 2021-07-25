# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicRespawnViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicRespawnViewMeta(BaseDAAPIComponent):

    def onLocationSelected(self, pointIdx):
        self._printOverrideError('onLocationSelected')

    def onRespawnBtnClick(self):
        self._printOverrideError('onRespawnBtnClick')

    def onDeploymentReady(self):
        self._printOverrideError('onDeploymentReady')

    def as_updateTimerS(self, timeIsOver, mainTimer):
        return self.flashObject.as_updateTimer(timeIsOver, mainTimer) if self._isDAAPIInited() else None

    def as_updateAutoTimerS(self, timeIsOver, mainTimer):
        return self.flashObject.as_updateAutoTimer(timeIsOver, mainTimer) if self._isDAAPIInited() else None

    def as_resetRespawnStateS(self):
        return self.flashObject.as_resetRespawnState() if self._isDAAPIInited() else None

    def as_setSelectedLocationS(self, pointIdx):
        return self.flashObject.as_setSelectedLocation(pointIdx) if self._isDAAPIInited() else None

    def as_setLaneStateS(self, laneId, value, blockReasonText):
        return self.flashObject.as_setLaneState(laneId, value, blockReasonText) if self._isDAAPIInited() else None

    def as_setMapDimensionsS(self, mapWidth, mapHeight):
        return self.flashObject.as_setMapDimensions(mapWidth, mapHeight) if self._isDAAPIInited() else None

    def as_setRespawnLocationsS(self, locations):
        return self.flashObject.as_setRespawnLocations(locations) if self._isDAAPIInited() else None

    def as_handleAsReplayS(self):
        return self.flashObject.as_handleAsReplay() if self._isDAAPIInited() else None
