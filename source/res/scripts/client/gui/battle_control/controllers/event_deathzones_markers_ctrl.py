# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_deathzones_markers_ctrl.py
import logging
from Math import Vector3
from PlayerEvents import g_playerEvents
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.Scaleform.daapi.view.battle.event.markers import MarkerFactory, EventDeathZonesUIMarkerController
from constants import MarkerTypes
_logger = logging.getLogger(__name__)
_VISIBILITY_RADIUS = 50

class EventDeathZonesMarkersController(IArenaVehiclesController):

    def __init__(self):
        super(EventDeathZonesMarkersController, self).__init__()
        self._uiEventDeathZonesMarkersController = EventDeathZonesUIMarkerController()
        self._markers = {}

    def startControl(self, battleCtx, arenaVisitor):
        g_playerEvents.onDeathZoneActivated += self._onDeathZoneActivated
        g_playerEvents.onDeathZoneDeactivated += self._onDeathZoneDeactivated

    def stopControl(self):
        g_playerEvents.onDeathZoneActivated -= self._onDeathZoneActivated
        g_playerEvents.onDeathZoneDeactivated -= self._onDeathZoneDeactivated
        self._markers = {}

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_DEATHZONES_MARKERS

    def spaceLoadCompleted(self):
        self._uiEventDeathZonesMarkersController.init()

    def _onDeathZoneActivated(self, zone):
        self._addMarker(zone.zoneId, Vector3())
        self._uiEventDeathZonesMarkersController.registerZone(zone)

    def _onDeathZoneDeactivated(self, zoneId):
        self._destroyMarker(zoneId)

    def _addMarker(self, zoneId, position):
        if zoneId in self._markers:
            return
        marker = MarkerFactory.createDynMarker(position, _VISIBILITY_RADIUS, MarkerTypes.EVENT_DEATHZONE, showIndicator=False)
        self._uiEventDeathZonesMarkersController.addMarker(zoneId, marker, _VISIBILITY_RADIUS)
        self._markers[zoneId] = marker

    def _destroyMarker(self, zoneId):
        self._markers.pop(zoneId)
        self._uiEventDeathZonesMarkersController.removeMarkerByObjId(zoneId)
