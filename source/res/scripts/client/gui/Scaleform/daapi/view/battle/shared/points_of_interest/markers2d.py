# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/points_of_interest/markers2d.py
import logging
import typing
import Math
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.constants import POI_TYPE_UI_MAPPING, POI_STATUS_UI_MAPPING
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.poi_helpers import getPoiCooldownProgress
from points_of_interest.components import PoiStateComponent, PoiStateUpdateMask
from points_of_interest.mixins import PointsOfInterestListener
from points_of_interest_shared import PoiStatus
if typing.TYPE_CHECKING:
    from helpers.fixed_dict import StatusWithTimeInterval
_logger = logging.getLogger(__name__)
_POI_MARKER_SYMBOL = 'PointOfInterestMarkerUI'
_POI_MARKER_POSITION_OFFSET = Math.Vector3(0.0, 12.0, 0.0)
_POI_MARKER_MIN_SCALE = 53
_POI_MARKER_BOUNDS = Math.Vector4(30, 30, 30, 30)
_POI_MARKER_INNER_BOUNDS = Math.Vector4(17, 17, 18, 18)
_POI_MARKER_CULL_DISTANCE = 1800
_POI_MARKER_BOUNDS_MIN_SCALE = Math.Vector2(1.0, 1.0)

class PointsOfInterestPlugin(plugins.MarkerPlugin, PointsOfInterestListener):

    def __init__(self, parentObj):
        plugins.MarkerPlugin.__init__(self, parentObj)
        PointsOfInterestListener.__init__(self)
        self.__markers = {}

    def start(self):
        super(PointsOfInterestPlugin, self).start()
        self.__initMarkers()
        self._registerPoiListener()

    def stop(self):
        self._unregisterPoiListener()
        self.__destroyMarkers()
        super(PointsOfInterestPlugin, self).stop()

    def onPoiAdded(self, poiState):
        poiID = poiState.id
        poi = self.sessionProvider.dynamic.pointsOfInterest.getPoiEntity(poiID)
        if poi is None:
            _logger.error('Missing PointOfInterest id=%s', poiID)
            return
        else:
            self.__markers[poiID] = markerID = self._createMarkerWithPosition(symbol=_POI_MARKER_SYMBOL, position=poi.position + _POI_MARKER_POSITION_OFFSET, active=self.__isMarkerActive(poiID))
            self._setMarkerRenderInfo(markerID, minScale=_POI_MARKER_MIN_SCALE, offset=_POI_MARKER_BOUNDS, innerOffset=_POI_MARKER_INNER_BOUNDS, cullDistance=_POI_MARKER_CULL_DISTANCE, boundsMinScale=_POI_MARKER_BOUNDS_MIN_SCALE)
            self._setMarkerSticky(markerID, isSticky=False)
            self.__updateType(markerID, poiState)
            self.__updateStatus(markerID, poiState)
            self.__updateProgress(markerID, poiState)
            self.__updateTeam(markerID, poiState)
            if poiState.status.statusID == PoiStatus.COOLDOWN:
                self.__updateCooldownProgress(markerID, poiState)
            return

    def onPoiRemoved(self, poiState):
        markerID = self.__markers.pop(poiState.id, None)
        if markerID is not None:
            self._destroyMarker(markerID)
        return

    def onProcessPoi(self, poiState):
        markerID = self.__markers.get(poiState.id)
        if markerID is None:
            return
        else:
            updatedFields = poiState.updatedFields
            if updatedFields & PoiStateUpdateMask.STATUS:
                self.__updateStatus(markerID, poiState)
            if updatedFields & (PoiStateUpdateMask.STATUS | PoiStateUpdateMask.PROGRESS):
                self.__updateProgress(markerID, poiState)
            if updatedFields & PoiStateUpdateMask.INVADER:
                self.__updateTeam(markerID, poiState)
            if poiState.status.statusID == PoiStatus.COOLDOWN:
                self.__updateCooldownProgress(markerID, poiState)
            return

    def onPoiEntered(self, poiID):
        self.__setPoiMarkerVisibility(poiID, isVisible=False)

    def onPoiLeft(self, poiID):
        self.__setPoiMarkerVisibility(poiID, isVisible=True)

    def __initMarkers(self):
        for poiState in self._poiStateQuery:
            self.onPoiAdded(poiState)

    def __destroyMarkers(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()

    def __updateType(self, markerID, state):
        poiType = POI_TYPE_UI_MAPPING[state.type]
        self._invokeMarker(markerID, 'setType', poiType)

    def __updateStatus(self, markerID, poiState):
        status = poiState.status
        duration = status.endTime - status.startTime
        statusID = POI_STATUS_UI_MAPPING[status.statusID]
        self._invokeMarker(markerID, 'setStatus', statusID, duration)

    def __updateProgress(self, markerID, poiState):
        progress = poiState.progress
        self._invokeMarker(markerID, 'setProgress', progress)

    def __updateTeam(self, markerID, poiState):
        isAlly = bool(poiState.invader)
        self._invokeMarker(markerID, 'setIsAlly', isAlly)

    def __updateCooldownProgress(self, markerID, poiState):
        progress = getPoiCooldownProgress(poiState)
        self._invokeMarker(markerID, 'setProgress', progress)

    def __setPoiMarkerVisibility(self, poiID, isVisible):
        markerID = self.__markers.get(poiID)
        if markerID is not None:
            self._setMarkerActive(markerID, active=isVisible)
        return

    def __isMarkerActive(self, poiID):
        poiVehicleState = self._poiVehicleState
        return False if poiVehicleState is not None and poiVehicleState.id == poiID else True
