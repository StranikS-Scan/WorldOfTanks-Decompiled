# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_area_vehicle_marker_ctrl.py
import logging
from functools import partial
import Event
import BigWorld
import Math
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.event.markers import MarkerFactory, EventAreaPointUIMarkerController
from constants import MarkerTypes
_logger = logging.getLogger(__name__)
_RADIUS = 5
_DELTA = 0.007

class EventAreaVehicleMarkersController(IArenaVehiclesController, GameEventGetterMixin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        GameEventGetterMixin.__init__(self)
        self._uiAreaVehicleMarkerController = EventAreaPointUIMarkerController()
        self.__eManager = Event.EventManager()
        self.onMiniMapUpdatedByPosition = Event.Event(self.__eManager)
        self.__isAddedMarkersList = []
        self.__callbackIds = {}
        self.__callbackInterpolationIds = {}
        self._areaVehicleMarkersDict = {}
        self.__prevPositions = {}

    def startControl(self, battleCtx, arenaVisitor):
        self.getAreaVehicleMarker.onUpdated += self.__updateAreaVehicleMarker

    def stopControl(self):
        self.getAreaVehicleMarker.onUpdated -= self.__updateAreaVehicleMarker
        for markerId in self.__callbackIds:
            self.__delCallBackById(markerId, self.__callbackIds)

        for markerId in self.__callbackInterpolationIds:
            self.__delCallBackById(markerId, self.__callbackInterpolationIds)

        self.__callbackIds = {}
        self._areaVehicleMarkersDict = {}
        self.__isAddedMarkersList = []

    def getControllerID(self):
        return BATTLE_CTRL_ID.AREA_VEHICLE_MARKER

    def spaceLoadCompleted(self):
        self._uiAreaVehicleMarkerController.init()

    def __updateAreaVehicleMarker(self):
        self._areaVehicleMarkersDict = markersDict = self.getAreaVehicleMarker.getParams()
        callbackIds = self.__callbackIds
        callbackInterpolationIds = self.__callbackInterpolationIds
        delCallback = self.__delCallBackById
        for markerId in markersDict.keys():
            vehicle = BigWorld.entities.get(markerId)
            data = markersDict[markerId]
            if not data['isAlive']:
                self.__removeMarker(markerId)
                delCallback(markerId, callbackInterpolationIds)
                delCallback(markerId, callbackIds)
                continue
            if vehicle:
                delCallback(markerId, callbackInterpolationIds)
                if data['showInAoI']:
                    if markerId not in callbackIds or callbackIds[markerId] is None:
                        callbackIds[markerId] = BigWorld.callback(0.0, partial(self.__updateAreaVehicleMarkerLocal, markerId))
                else:
                    self.__removeMarker(markerId)
            delCallback(markerId, callbackIds)
            if markerId not in callbackInterpolationIds or callbackInterpolationIds[markerId] is None:
                callbackInterpolationIds[markerId] = BigWorld.callback(0.0, partial(self.__updateAreaVehicleMarkerServer, markerId))

        return

    def __updateAreaVehicleMarkerLocal(self, markerId):
        self.__callbackIds[markerId] = None
        vehicle = BigWorld.entities.get(markerId, None)
        isAlive = vehicle is not None and vehicle.isAlive()
        if isAlive:
            position = vehicle.position
            self.__updateMarker(markerId, isAlive, position)
            self.__prevPositions[markerId] = Math.Vector3(position)
            self.__callbackIds[markerId] = BigWorld.callback(0.0, partial(self.__updateAreaVehicleMarkerLocal, markerId))
        else:
            self.__updateAreaVehicleMarker()
        return

    def __updateAreaVehicleMarkerServer(self, markerId):
        self.__callbackInterpolationIds[markerId] = None
        data = self._areaVehicleMarkersDict.get(markerId, None)
        if not data:
            return
        else:
            updateMarker = self.__updateMarker
            prevPositions = self.__prevPositions
            if markerId not in self.__isAddedMarkersList:
                updateMarker(markerId, data['isAlive'], data['position'])
                prevPositions[markerId] = Math.Vector3(data['position'])
            else:
                direction = data['position'] - prevPositions[markerId]
                curDistance = direction.length
                speed = data['speed'] if data['speed'] > 0 else data['rspeed']
                if curDistance > 0:
                    direction.normalise()
                    position = prevPositions[markerId] + speed * _DELTA * direction
                    updateMarker(markerId, data['isAlive'], position)
                    prevPositions[markerId] = Math.Vector3(position)
            self.__callbackInterpolationIds[markerId] = BigWorld.callback(0.0, partial(self.__updateAreaVehicleMarkerServer, markerId))
            return

    def __delCallBackById(self, markerId, source):
        callbackId = source.get(markerId, None)
        if callbackId is not None:
            BigWorld.cancelCallback(callbackId)
            source[markerId] = None
        return

    def __createMarker(self, markerId, position):
        self.__isAddedMarkersList.append(markerId)
        markerType = self.__getMarkerType(markerId)
        marker = MarkerFactory.createDynMarker(position, _RADIUS, markerType, isVisible=True)
        self._uiAreaVehicleMarkerController.addMarker(markerId, marker, _RADIUS)
        self._uiAreaVehicleMarkerController.showMarkersByObjId(markerId)
        self.onMiniMapUpdatedByPosition(markerId, position, True, markerType)

    def __removeMarker(self, markerId):
        if markerId in self.__isAddedMarkersList:
            self._uiAreaVehicleMarkerController.removeMarkerByObjId(markerId)
            self.onMiniMapUpdatedByPosition(markerId, None, False)
            self.__isAddedMarkersList.remove(markerId)
        return

    def __updateMarkerPosition(self, markerId, position):
        self._uiAreaVehicleMarkerController.updateMarkersPositionByObjId(markerId, position)
        self.onMiniMapUpdatedByPosition(markerId, position, True, self.__getMarkerType(markerId))

    def __updateMarker(self, markerId, isAlive, position):
        if not isAlive:
            self.__removeMarker(markerId)
            return
        if markerId not in self.__isAddedMarkersList:
            self.__createMarker(markerId, position)
        else:
            self.__updateMarkerPosition(markerId, position)

    def __getMarkerType(self, markerId):
        markerType = self._areaVehicleMarkersDict[markerId]['waveMarker']
        return markerType if markerType is not None else MarkerTypes.DEFAULT
