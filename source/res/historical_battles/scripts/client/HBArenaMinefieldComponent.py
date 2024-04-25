# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBArenaMinefieldComponent.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MarkersManagerEvent
from items import vehicles
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class HBArenaMinefieldComponent(BigWorld.DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HBArenaMinefieldComponent, self).__init__()
        self._equipment = None
        self._position = None
        self._direction = None
        return

    def showMarker(self, equipmentID, position, direction):
        self._equipment = vehicles.g_cache.equipments()[equipmentID]
        self._position = position
        self._direction = direction
        if self._isMarkersManagerReady:
            self._showMarker()
        else:
            g_eventBus.addListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)

    @property
    def _isMarkersManagerReady(self):
        return self.sessionProvider.shared.areaMarker._gui.getMarkers2DPlugin()

    def _onMarkersCreated(self, event):
        g_eventBus.removeListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self._showMarker()

    def _showMarker(self):
        equipmentsCtrl = self.sessionProvider.shared.equipments
        if equipmentsCtrl:
            equipmentsCtrl.showMarker(self._equipment, self._position, self._direction, self._equipment.markerLifetime)
