# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/world_markers_controllers.py
import BigWorld
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import MARKER_SYMBOL_NAME

class WorldMarkersPlugin(MarkerPlugin):

    def __init__(self, parentObj):
        super(WorldMarkersPlugin, self).__init__(parentObj)
        self._markersIdByEventMarkerId = {}

    def start(self):
        self._fireUIComponentLifetimeEvent(BATTLE_VIEW_ALIASES.MARKERS_2D, self)

    def stop(self):
        self._fireUIComponentLifetimeEvent(BATTLE_VIEW_ALIASES.MARKERS_2D, None)
        return

    def addStaticObject(self, eventMarkerId, position):
        if eventMarkerId not in self._markersIdByEventMarkerId:
            markerId = self._createMarkerWithPosition(MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER, position, active=True)
            self._markersIdByEventMarkerId[eventMarkerId] = markerId
            return True
        return False

    def delStaticObject(self, eventMarkerId):
        self._delMarker(eventMarkerId)

    def setupStaticObject(self, eventMarkerId, shape, minDistance, maxDistance, distance, color):
        self._setupMarker(eventMarkerId, shape, minDistance, maxDistance, distance, color)

    def setDistanceToObject(self, eventMarkerId, distance):
        markerId = self._markersIdByEventMarkerId.get(eventMarkerId)
        if markerId is not None:
            self._invokeMarker(markerId, 'setDistance', distance)
        return

    def addNonStaticObject(self, eventMarkerId, entityId):
        if eventMarkerId in self._markersIdByEventMarkerId:
            return False
        matrix = BigWorld.entities[entityId].matrix
        markerId = self._createMarkerWithMatrix(MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER, matrix, active=True)
        self._markersIdByEventMarkerId[eventMarkerId] = markerId
        return True

    def setupNonStaticObject(self, objectID, shape, minDistance, maxDistance, distance, color):
        self._setupMarker(objectID, shape, minDistance, maxDistance, distance, color)

    def delNonStaticObject(self, eventMarkerId):
        self._delMarker(eventMarkerId)

    def _setupMarker(self, eventMarkerId, shape, minDistance, maxDistance, distance, color):
        markerId = self._markersIdByEventMarkerId.get(eventMarkerId)
        if markerId is not None:
            self._invokeMarker(markerId, 'init', shape, minDistance, maxDistance, distance, backport.text(R.strings.ingame_gui.marker.meters()), color)
        return

    def _delMarker(self, eventMarkerId):
        markerId = self._markersIdByEventMarkerId.pop(eventMarkerId, None)
        if markerId is not None:
            self._destroyMarker(markerId)
            return True
        else:
            return False

    @staticmethod
    def _fireUIComponentLifetimeEvent(alias, component):
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.WORLD_MARKERS_COMPONENT_LIFETIME, {'alias': alias,
         'component': component}), scope=EVENT_BUS_SCOPE.BATTLE)
