# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/map_zones/mixins.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class MapZonesListener(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def startListen(self):
        mapZones = self._sessionProvider.shared.mapZones
        if mapZones:
            mapZones.onMarkerToZoneAdded += self._onMarkerToZoneAdded
            mapZones.onMarkerFromZoneRemoved += self._onMarkerFromZoneRemoved
            mapZones.onMarkerProgressUpdated += self._onMarkerProgressUpdated
            mapZones.onZoneTransformed += self._onZoneTransformed
            mapZones.onTransformedZoneRemoved += self._onTransformedZoneRemoved

    def stopListen(self):
        mapZones = self._sessionProvider.shared.mapZones
        if mapZones:
            mapZones.onMarkerToZoneAdded -= self._onMarkerToZoneAdded
            mapZones.onMarkerFromZoneRemoved -= self._onMarkerFromZoneRemoved
            mapZones.onMarkerProgressUpdated -= self._onMarkerProgressUpdated
            mapZones.onZoneTransformed -= self._onZoneTransformed
            mapZones.onTransformedZoneRemoved -= self._onTransformedZoneRemoved

    def _onMarkerToZoneAdded(self, zoneMarker, matrix):
        pass

    def _onMarkerFromZoneRemoved(self, zoneMarker):
        pass

    def _onMarkerProgressUpdated(self, zoneMarker):
        pass

    def _onZoneTransformed(self, zone):
        pass

    def _onTransformedZoneRemoved(self, zone):
        pass
