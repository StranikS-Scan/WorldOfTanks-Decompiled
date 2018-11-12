# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicRespawnViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicRespawnViewMeta(BaseDAAPIComponent):

    def onLaneSelected(self, laneID):
        self._printOverrideError('onLaneSelected')

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

    def as_setSelectedLaneS(self, laneId):
        return self.flashObject.as_setSelectedLane(laneId) if self._isDAAPIInited() else None

    def as_setLaneStateS(self, laneId, value, blockReasonText):
        return self.flashObject.as_setLaneState(laneId, value, blockReasonText) if self._isDAAPIInited() else None

    def as_setMapDimensionsS(self, mapWidth, mapHeight):
        return self.flashObject.as_setMapDimensions(mapWidth, mapHeight) if self._isDAAPIInited() else None

    def as_setRespawnLocationsS(self, respawnLocationData):
        return self.flashObject.as_setRespawnLocations(respawnLocationData) if self._isDAAPIInited() else None
