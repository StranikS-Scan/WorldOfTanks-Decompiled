# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_area_point_marker_ctrl.py
import logging
from functools import partial
import BigWorld
import Event
from constants import EventMarkerBlinkingParams
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.event.markers import MarkerFactory, EventAreaPointUIMarkerController
from constants import MarkerTypes
_logger = logging.getLogger(__name__)
_DEF_RADIUS = 0

class EventAreaPointMarkersController(IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self._uiAreaPointMarkerController = EventAreaPointUIMarkerController()
        self.__eManager = Event.EventManager()
        self.onMiniMapUpdated = Event.Event(self.__eManager)
        self.onStopBlinking = Event.Event(self.__eManager)
        self.__gameEventStorage = None
        self.__areaPointMarkers = []
        self.__isAddedMarkersList = {}
        self.__blinkingCallback = {}
        return

    def startControl(self, battleCtx, arenaVisitor):
        self.__gameEventStorage = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'gameEventComponent', None)
        if self.__gameEventStorage:
            self.__gameEventStorage.getAreaPointMarker().onUpdated += self.__updateAreaPointMarker
        if hasattr(BigWorld.player(), 'arenaExtraData'):
            if 'markers' in BigWorld.player().arenaExtraData:
                self.__areaPointMarkers = BigWorld.player().arenaExtraData['markers']
        return

    def stopControl(self):
        if self.__gameEventStorage:
            self.__gameEventStorage.getAreaPointMarker().onUpdated -= self.__updateAreaPointMarker
        self.__areaPointMarkers = []
        self.__isAddedMarkersList = {}
        for callbackId in self.__blinkingCallback.itervalues():
            BigWorld.cancelCallback(callbackId)

        self.__blinkingCallback = {}

    def getControllerID(self):
        return BATTLE_CTRL_ID.AREA_POINT

    def spaceLoadCompleted(self):
        self.__isAddedMarkersList = {}
        self.__updateAreaPointMarker()
        self._uiAreaPointMarkerController.init()

    def __updateAreaPointMarker(self):
        if not self.__gameEventStorage:
            return
        areaPointMarkersFromScenario = self.__gameEventStorage.getAreaPointMarker().getParams()
        markerList = self.__isAddedMarkersList
        for markerData in self.__areaPointMarkers:
            markerId = markerData['name']
            if markerId not in areaPointMarkersFromScenario:
                continue
            if areaPointMarkersFromScenario[markerId]['show']:
                matrix = markerData['matrix']
                markerType = areaPointMarkersFromScenario[markerId].get('markerType', MarkerTypes.DEFAULT)
                if markerId in markerList and markerList[markerId] != markerType:
                    self.__delMarkerPoint(markerId)
                if markerId not in markerList:
                    self.__addMarkerPoint(markerId, markerType, matrix)
            if markerId in markerList:
                self.__delMarkerPoint(markerId)

    def __addMarkerPoint(self, markerId, markerType, matrix):
        self.__isAddedMarkersList[markerId] = markerType
        blinking = markerType not in MarkerTypes.NO_BLINKING_MARKER_LIST
        self.onMiniMapUpdated(markerId, matrix, True, markerType, blinking=blinking)
        blinkingDuration = self.__getDuration(markerType)
        if markerType in MarkerTypes.ONLY_MINI_MAP_MARKER_LIST:
            if blinking:
                self.__blinkingCallback[markerId] = BigWorld.callback(blinkingDuration, partial(self.__stopBlinking, markerId))
            return
        marker = MarkerFactory.createMarker(matrix.applyToOrigin(), _DEF_RADIUS, markerType, isVisible=True)
        ctrl = self._uiAreaPointMarkerController
        if ctrl:
            ctrl.addMarker(markerId, marker, _DEF_RADIUS)
            ctrl.showMarkersByObjId(markerId)
            if markerType not in MarkerTypes.NO_BLINKING_MARKER_LIST:
                ctrl.blinkingByObjId(markerId, speed=EventMarkerBlinkingParams.BLINKING_SPEED_CUSTOM_MARKER_MS.value, show=True)
                if markerId in self.__blinkingCallback:
                    BigWorld.cancelCallback(self.__blinkingCallback[markerId])
                self.__blinkingCallback[markerId] = BigWorld.callback(blinkingDuration, partial(self.__stopBlinking, markerId))

    def __delMarkerPoint(self, markerId):
        self._uiAreaPointMarkerController.removeMarkerByObjId(markerId)
        self.onMiniMapUpdated(markerId, None, False)
        del self.__isAddedMarkersList[markerId]
        return

    def __stopBlinking(self, markerId):
        if markerId in self.__blinkingCallback:
            del self.__blinkingCallback[markerId]
            self._uiAreaPointMarkerController.blinkingByObjId(markerId, show=False)
            self.onStopBlinking(markerId)

    def __getDuration(self, markerType):
        return EventMarkerBlinkingParams.BLINKING_DURATION_ARROW_MARKER.value if markerType in MarkerTypes.ARROW_MINI_MAP_MARKER_LIST else EventMarkerBlinkingParams.BLINKING_DURATION_CUSTOM_MARKER.value
