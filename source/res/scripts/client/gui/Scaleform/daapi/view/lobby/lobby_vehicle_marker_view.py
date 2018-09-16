# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_vehicle_marker_view.py
import BigWorld
import GUI
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.HangarSpace import g_hangarSpace
from hangar_camera_common import CameraRelatedEvents, CameraMovementStates

class LobbyVehicleMarkerView(LobbyVehicleMarkerViewMeta):

    def __init__(self, ctx=None):
        super(LobbyVehicleMarkerView, self).__init__(ctx)
        self.__vehicleMarker = None
        self.__vEntityId = None
        return

    def _populate(self):
        super(LobbyVehicleMarkerView, self)._populate()
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        g_hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def _dispose(self):
        super(LobbyVehicleMarkerView, self)._dispose()
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.__vehicleMarker = None
        self.__vEntityId = None
        return

    def __onSpaceDestroy(self, _):
        self.__destroyMarker()

    def __destroyMarker(self):
        self.as_removeMarkerS()
        self.__vehicleMarker = None
        return

    def __onHeroTankLoaded(self, event):
        vehicle = event.ctx['entity']
        self.__createMarker(vehicle)

    def __onHeroTankDestroy(self, *_):
        self.__destroyMarker()
        self.__vEntityId = None
        return

    def __onCameraEntityUpdated(self, event):
        if self.__vehicleMarker is None:
            return
        else:
            state = event.ctx['state']
            if state == CameraMovementStates.FROM_OBJECT:
                return
            self.__vehicleMarker.markerSetActive(g_hangarSpace.space.vehicleEntityId == event.ctx['entityId'])
            return

    def __onVehicleLoading(self, event):
        if self.__vEntityId != event.ctx.get('vEntityId'):
            return
        if event.ctx.get('started'):
            self.__destroyMarker()
        else:
            vehicle = BigWorld.entities.get(self.__vEntityId)
            self.__createMarker(vehicle)

    @staticmethod
    def __getVehicleInfo(vehicle):
        vehicleType = vehicle.typeDescriptor.type
        vClass = getVehicleClassTag(vehicleType.tags)
        vName = vehicleType.userString
        vMatrix = vehicle.model.node('HP_gui')
        return (vClass, vName, vMatrix)

    def __createMarker(self, vehicle):
        vClass, vName, vMatrix = self.__getVehicleInfo(vehicle)
        self.as_removeMarkerS()
        flashMarker = self.as_createMarkerS(vClass, vName)
        self.__vehicleMarker = GUI.WGHangarVehicleMarker()
        self.__vehicleMarker.setMarker(flashMarker, vMatrix)
        self.__vEntityId = vehicle.id
