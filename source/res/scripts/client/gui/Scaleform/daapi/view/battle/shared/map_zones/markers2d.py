# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/map_zones/markers2d.py
import logging
import Math
import typing
from gui.Scaleform.daapi.view.battle.shared.map_zones.mixins import MapZonesListener
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
_logger = logging.getLogger(__name__)
_MS_MARKER_MIN_SCALE = 60.0
_MS_MARKER_BOUNDS = Math.Vector4(30, 30, 90, -15)
_MS_MARKER_INNER_BOUNDS = Math.Vector4(15, 15, 70, -35)
_MS_MARKER_CULL_DISTANCE = 1800
_MS_MARKER_BOUNDS_MIN_SCALE = Math.Vector2(1.0, 0.8)

class MapZonesPlugin(plugins.MarkerPlugin, MapZonesListener):
    MINIMAP_ENTRY_SYMBOL = 'ScenarioMarkerUI'

    def __init__(self, parentObj):
        super(MapZonesPlugin, self).__init__(parentObj)
        self.__markers = {}

    def start(self):
        super(MapZonesPlugin, self).start()
        mapZones = self.sessionProvider.shared.mapZones
        if mapZones:
            for zoneMarker, matrix in mapZones.getZoneMarkers().itervalues():
                if zoneMarker.isVisibleOn3DScene:
                    self.__addMarkerToZone(zoneMarker, matrix)

        self.startListen()

    def stop(self):
        self.stopListen()
        self.__destroyMarkers()
        super(MapZonesPlugin, self).stop()

    def _onMarkerToZoneAdded(self, zoneMarker, matrix):
        if zoneMarker.isVisibleOn3DScene:
            self.__addMarkerToZone(zoneMarker, matrix)

    def _onMarkerFromZoneRemoved(self, zoneMarker):
        if zoneMarker.isVisibleOn3DScene:
            self.__removeMarkerFromZone(zoneMarker)

    def _onMarkerProgressUpdated(self, zoneMarker):
        if zoneMarker.isVisibleOn3DScene:
            self.__updateProgress(zoneMarker)

    def __addMarkerToZone(self, zoneMarker, matrix):
        self.__markers[zoneMarker.id] = markerID = self._createMarkerWithMatrix(symbol=self.MINIMAP_ENTRY_SYMBOL, matrixProvider=matrix)
        self._setMarkerRenderInfo(markerID, _MS_MARKER_MIN_SCALE, _MS_MARKER_BOUNDS, _MS_MARKER_INNER_BOUNDS, _MS_MARKER_CULL_DISTANCE, _MS_MARKER_BOUNDS_MIN_SCALE)
        self.__updateProgress(zoneMarker)

    def __removeMarkerFromZone(self, zoneMarker):
        markerID = self.__markers.pop(zoneMarker.id, None)
        if markerID is not None:
            self._destroyMarker(markerID)
        return

    def __updateProgress(self, zoneMarker):
        zoneMarkerID = zoneMarker.id
        if zoneMarkerID in self.__markers:
            markerID = self.__markers[zoneMarkerID]
            self._invokeMarker(markerID, 'setProgress', zoneMarker.markerProgress)
        else:
            _logger.error('ZoneMarker not found, id: %s', zoneMarkerID)

    def __destroyMarkers(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()
