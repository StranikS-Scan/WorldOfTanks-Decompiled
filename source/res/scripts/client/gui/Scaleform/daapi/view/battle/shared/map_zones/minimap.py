# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/map_zones/minimap.py
import logging
from constants import MinimapLayerType
from gui.Scaleform.daapi.view.battle.shared.map_zones.mixins import MapZonesListener
from gui.Scaleform.daapi.view.battle.shared.minimap import common, settings
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from helpers import unicodeToStr
_logger = logging.getLogger(__name__)
_layerTypesMapping = {MinimapLayerType.BASE: BATTLE_MINIMAP_CONSTS.SCENARIO_EVENT_EFFECT,
 MinimapLayerType.ALERT: BATTLE_MINIMAP_CONSTS.SCENARIO_EVENT_ALERT}

class MapZonesEntriesPlugin(common.EntriesPlugin, MapZonesListener):
    MINIMAP_ENTRY_SYMBOL = 'ScenarioMinimapEntry'

    def __init__(self, parent, clazz=None):
        super(MapZonesEntriesPlugin, self).__init__(parent, clazz)
        self.__mmLayers = self.sessionProvider.arenaVisitor.type.getMinimapLayers() or {}

    def start(self):
        super(MapZonesEntriesPlugin, self).start()
        for layerId, (path, layerType) in self.__mmLayers.iteritems():
            self.parentObj.as_setScenarioEventS(layerId, self.parentObj.getImagePath(path), _layerTypesMapping[layerType])

        mapZones = self.sessionProvider.shared.mapZones
        if mapZones:
            for zoneMarker, matrix in mapZones.getZoneMarkers().itervalues():
                self.__addMarkerToZone(zoneMarker, matrix)

            for transformedZone in mapZones.getTransformedZones().itervalues():
                self.__addTransromedZone(transformedZone)

        self.startListen()

    def stop(self):
        for layerId in self.__mmLayers.iterkeys():
            self.parentObj.as_clearScenarioEventS(layerId)

        self.stopListen()
        super(MapZonesEntriesPlugin, self).stop()

    def _onMarkerToZoneAdded(self, zoneMarker, matrix):
        self.__addMarkerToZone(zoneMarker, matrix)

    def _onMarkerFromZoneRemoved(self, zoneMarker):
        self.__removeMarkerFromZone(zoneMarker)

    def _onMarkerProgressUpdated(self, zoneMarker):
        self.__updateProgress(zoneMarker)

    def _onZoneTransformed(self, zone):
        self.__addTransromedZone(zone)

    def _onTransformedZoneRemoved(self, zone):
        layerId = zone.layerId
        if layerId in self.__mmLayers:
            self.parentObj.as_setScenarioEventVisibleS(unicodeToStr(layerId), False)
        else:
            _logger.error('layerId not found, id: %s', layerId)

    def __addTransromedZone(self, zone):
        layerId = zone.layerId
        if layerId in self.__mmLayers:
            self.parentObj.as_setScenarioEventVisibleS(unicodeToStr(layerId), True)
        else:
            _logger.error('layerId not found, id: %s', layerId)

    def __addMarkerToZone(self, zoneMarker, matrix):
        model = self._addEntryEx(uniqueID=zoneMarker.id, symbol=self.MINIMAP_ENTRY_SYMBOL, container=settings.CONTAINER_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if model:
            self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)
        self.__updateProgress(zoneMarker)

    def __removeMarkerFromZone(self, zoneMarker):
        self._delEntryEx(uniqueID=zoneMarker.id)

    def __updateProgress(self, zoneMarker):
        if zoneMarker and zoneMarker.id in self._entries:
            entryID = self._entries[zoneMarker.id].getID()
            self._invoke(entryID, 'setProgress', zoneMarker.markerProgress)
