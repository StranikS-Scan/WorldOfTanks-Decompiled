# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_vehicle_marker_view.py
from collections import defaultdict
from functools import partial
import BigWorld
import GUI
import Math
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.shared import events, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class LobbyVehicleMarkerView(LobbyVehicleMarkerViewMeta):
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
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, self.__onLobbyTypeChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.addListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def _dispose(self):
        self.__destroyAllMarkers()
        super(LobbyVehicleMarkerView, self)._dispose()
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, self.__onLobbyTypeChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy

    def __onSpaceDestroy(self, _):
        self.__destroyAllMarkers()

    def __onHeroTankLoaded(self, event):
        vehicle = event.ctx['entity']
        lobbyType = event.ctx['lobbyType']
        self.__beginCreateMarker(vehicle, lobbyType)

    def __onHeroTankDestroy(self, event):
        vehicle = event.ctx['entity']
        lobbyType = event.ctx['lobbyType']
        self.__destroyMarker(vehicle, lobbyType)

    def __onCameraEntityUpdated(self, event):
        state = event.ctx['state']
        entityId = event.ctx['entityId']
        if state == CameraMovementStates.MOVING_TO_OBJECT:
            self.__selectedVehicleID = entityId
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
                vehicle.enable(isVehicleEnabled)

    @staticmethod
    def __getVehicleInfo(vehicle, lobbyType):
        vehicleType = vehicle.typeDescriptor.type
        vClass = getVehicleClassTag(vehicleType.tags)
        vName = vehicleType.userString if lobbyType != 'event' else vehicleType.shortUserString
        vMatrix = LobbyVehicleMarkerView.__getCorrectedHPGuiMatrix(vehicle)
        return (vClass, vName, vMatrix)

    @staticmethod
    def __getCorrectedHPGuiMatrix(vehicle):
        mat = Math.Matrix()
        guiNode = vehicle.model.node('HP_gui')
        localPosition = Math.Vector3(guiNode.localMatrix.translation)
        localPosition.y *= vehicle.markerHeightFactor if hasattr(vehicle, 'markerHeightFactor') else 1.0
        rootNodeMatrix = Math.Matrix(vehicle.model.node(''))
        worldPosition = rootNodeMatrix.applyPoint(localPosition)
        mat.setTranslate(worldPosition)
        return mat

    def __beginCreateMarker(self, vehicle, lobbyType):
        self.__destroyMarker(vehicle, lobbyType)
        BigWorld.callback(0.0, partial(self.__createMarker, vehicle, lobbyType))

    def __createMarker(self, vehicle, lobbyType):
        vClass, vName, vMatrix = self.__getVehicleInfo(vehicle, lobbyType)
        flashMarker = self.as_createMarkerS(vClass, vName, vehicle.id)
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
