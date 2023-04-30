# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/map_zones/minimap.py
from gui.Scaleform.daapi.view.battle.shared.map_zones.mixins import MapZonesListener
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from helpers import unicodeToStr

class MapZonesEntriesPlugin(common.EntriesPlugin, MapZonesListener):
    MINIMAP_ENTRY_SYMBOL = 'ScenarioMinimapEntry'

    def start(self):
        super(MapZonesEntriesPlugin, self).start()
        mmLayers = self.sessionProvider.arenaVisitor.type.getMinimapLayers()
        if mmLayers:
            for layer in mmLayers:
                self.parentObj.as_setScenarioEventS(layer, self.parentObj.getImagePath(layer))

        mapZones = self.sessionProvider.shared.mapZones
        if mapZones:
            for zoneMarker, matrix in mapZones.getZoneMarkers().itervalues():
                self.__addMarkerToZone(zoneMarker, matrix)

            for transformedZone in mapZones.getTransformedZones().itervalues():
                self.__addTransromedZone(transformedZone)

        self.startListen()

    def stop(self):
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
        self.parentObj.as_clearScenarioEventS(unicodeToStr(zone.minimapLayer))

    def __addTransromedZone(self, zone):
        self.parentObj.as_setScenarioEventVisibleS(unicodeToStr(zone.minimapLayer), True)

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
