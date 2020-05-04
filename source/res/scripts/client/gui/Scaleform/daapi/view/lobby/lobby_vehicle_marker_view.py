# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_vehicle_marker_view.py
from collections import defaultdict
from functools import partial
import BigWorld
import GUI
import Math
import constants
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
LOBBY_TYPE = constants.LobbyType

class LobbyVehicleMarkerView(LobbyVehicleMarkerViewMeta):
    __loadEvents = (VIEW_ALIAS.LOBBY_HANGAR,
     VIEW_ALIAS.LOBBY_INVENTORY,
     VIEW_ALIAS.LOBBY_STORE_OLD,
     VIEW_ALIAS.LOBBY_STORE,
     VIEW_ALIAS.LOBBY_STORAGE,
     VIEW_ALIAS.LOBBY_TECHTREE,
     VIEW_ALIAS.LOBBY_BARRACKS,
     VIEW_ALIAS.LOBBY_PROFILE,
     VIEW_ALIAS.VEHICLE_COMPARE,
     VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS,
     VIEW_ALIAS.LOBBY_MISSIONS,
     VIEW_ALIAS.LOBBY_STRONGHOLD,
     events.ViewEventType.LOAD_UB_VIEW)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None):
        super(LobbyVehicleMarkerView, self).__init__(ctx)
        self.__vehicleMarkers = defaultdict(dict)
        self.__vehicles = defaultdict(set)
        self.__areMarkersDisabled = False
        self.__selectedVehicleID = None
        self.__lobbyType = None
        return

    def _populate(self):
        super(LobbyVehicleMarkerView, self)._populate()
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_UPDATED, self.__onHeroTankUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, self.__onLobbyTypeChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        add = g_eventBus.addListener
        for event in self.__loadEvents:
            add(event, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.__destroyAllMarkers()
        super(LobbyVehicleMarkerView, self)._dispose()
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_UPDATED, self.__onHeroTankUpdated, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, self.__onLobbyTypeChanged, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        remove = g_eventBus.removeListener
        for event in self.__loadEvents:
            remove(event, self.__handleViewLoad, scope=EVENT_BUS_SCOPE.LOBBY)

    def __onSpaceDestroy(self, _):
        self.__destroyAllMarkers()

    def __onHeroTankLoaded(self, event):
        vehicle = event.ctx['entity']
        lobbyType = event.ctx['lobbyType']
        self.__beginCreateMarker(vehicle, lobbyType)

    def __onHeroTankUpdated(self, event):
        vehicle = event.ctx['entity']
        lobbyType = event.ctx['lobbyType']
        vClass, vName, _, vMarkerStyleId = self.__getVehicleInfo(vehicle, lobbyType)
        self.as_updateMarkerS(vClass, vName, vehicle.id, vMarkerStyleId)

    def __onHeroTankDestroy(self, event):
        vehicle = event.ctx['entity']
        lobbyType = event.ctx['lobbyType']
        self.__destroyMarker(vehicle, lobbyType)

    def __onCameraEntityUpdated(self, event):
        state = event.ctx['state']
        entityId = event.ctx['entityId']
        alwaysShowMarker = event.ctx.get('alwaysShowMarker', False)
        if state == CameraMovementStates.MOVING_TO_OBJECT:
            self.__selectedVehicleID = entityId if not alwaysShowMarker else None
        elif state == CameraMovementStates.FROM_OBJECT and self.__selectedVehicleID == entityId:
            self.__selectedVehicleID = None
        self.__updateMarkerVisibility()
        return

    def __onMarkerDisable(self, event):
        self.__areMarkersDisabled = event.ctx['isDisable']
        self.__updateMarkerVisibility()

    def __onLobbyTypeChanged(self, event):
        self.__lobbyType = event.ctx['lobbyType']
        self.__updateMarkerVisibility()

    def __updateMarkerVisibility(self):
        for lobbyType, markerGroup in self.__vehicleMarkers.iteritems():
            isGroupShown = not self.__areMarkersDisabled and lobbyType == self.__lobbyType
            for vehicleID, marker in markerGroup.iteritems():
                marker.markerSetActive(isGroupShown and vehicleID != self.__selectedVehicleID)

        for lobbyType, vehicles in self.__vehicles.iteritems():
            isVehicleEnabled = lobbyType == self.__lobbyType
            for vehicle in vehicles:
                vehicle.setEnable(isVehicleEnabled and vehicle.id != self.__selectedVehicleID)

    @staticmethod
    def __getVehicleInfo(vehicle, lobbyType):
        vehicleType = vehicle.typeDescriptor.type
        vClass = getVehicleClassTag(vehicleType.tags)
        defaultName = vehicleType.userString if lobbyType != LOBBY_TYPE.EVENT else vehicleType.shortUserString
        vName = getattr(vehicle, 'name', defaultName)
        vMatrix = LobbyVehicleMarkerView.__getCorrectedHPGuiMatrix(vehicle)
        vMarkerStyleId = vehicle.markerStyleId
        return (vClass,
         vName,
         vMatrix,
         vMarkerStyleId)

    @staticmethod
    def __getCorrectedHPGuiMatrix(vehicle):
        mat = Math.Matrix()
        guiNode = vehicle.model.node('HP_gui')
        localPosition = Math.Vector3(guiNode.localMatrix.translation)
        localPosition.y *= vehicle.markerHeightFactor
        vehicleMatrix = vehicle.model.matrix
        worldPosition = vehicleMatrix.applyPoint(localPosition)
        mat.setTranslate(worldPosition)
        return mat

    def __beginCreateMarker(self, vehicle, lobbyType):
        self.__destroyMarker(vehicle, lobbyType)
        BigWorld.callback(0.0, partial(self.__createMarker, vehicle, lobbyType))

    def __createMarker(self, vehicle, lobbyType):
        vClass, vName, vMatrix, vMarkerStyleId = self.__getVehicleInfo(vehicle, lobbyType)
        flashMarker = self.as_createMarkerS(vClass, vName, vehicle.id, vMarkerStyleId)
        marker = GUI.WGHangarVehicleMarker()
        marker.setMarker(flashMarker, vMatrix)
        self.__vehicleMarkers[lobbyType][vehicle.id] = marker
        self.__vehicles[lobbyType].add(vehicle)
        self.__updateMarkerVisibility()

    def __destroyMarker(self, vehicle, lobbyType):
        vehicleID = vehicle.id
        if vehicleID in self.__vehicleMarkers[lobbyType]:
            self.as_removeMarkerS(vehicleID)
            del self.__vehicleMarkers[lobbyType][vehicleID]
        if vehicle in self.__vehicles[lobbyType]:
            self.__vehicles[lobbyType].remove(vehicle)

    def __destroyAllMarkers(self):
        for markerGroup in self.__vehicleMarkers.values():
            for markerID in markerGroup:
                self.as_removeMarkerS(markerID)

        self.__vehicleMarkers = defaultdict(dict)
        self.__vehicles = defaultdict(set)

    def __handleViewLoad(self, event):
        if event.eventType == VIEW_ALIAS.LOBBY_HANGAR:
            self.__isMarkerDisabled = False
        else:
            self.__isMarkerDisabled = True
        self.__updateMarkerVisibility()
