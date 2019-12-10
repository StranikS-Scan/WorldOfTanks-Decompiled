# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_vehicle_marker_view.py
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
        self.__vehicleMarker = None
        self.__isMarkerDisabled = False
        return

    def _populate(self):
        super(LobbyVehicleMarkerView, self)._populate()
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LABEL_UPDATE_REQUIRED, self.__onHeroTankLabelUpdateRequested, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def _dispose(self):
        super(LobbyVehicleMarkerView, self)._dispose()
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LABEL_UPDATE_REQUIRED, self.__onHeroTankLabelUpdateRequested, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.__vehicleMarker = None
        return

    def __onSpaceDestroy(self, _):
        self.__destroyMarker()

    def __onHeroTankLoaded(self, event):
        vehicle = event.ctx['entity']
        self.__beginCreateMarker(vehicle)

    def __onHeroTankLabelUpdateRequested(self, event):
        vehicle = event.ctx['entity']
        self.__beginCreateMarker(vehicle)

    def __onHeroTankDestroy(self, *_):
        self.__destroyMarker()

    def __onCameraEntityUpdated(self, event):
        if self.__isMarkerDisabled or self.__vehicleMarker is None:
            return
        else:
            state = event.ctx['state']
            if state == CameraMovementStates.FROM_OBJECT:
                return
            self.__vehicleMarker.markerSetActive(self.hangarSpace.space.vehicleEntityId == event.ctx['entityId'])
            return

    def __onMarkerDisable(self, event):
        self.__isMarkerDisabled = event.ctx['isDisable']
        self.__updateMarkerVisibility()

    def __updateMarkerVisibility(self):
        if self.__vehicleMarker is None:
            return
        else:
            self.__vehicleMarker.markerSetActive(not self.__isMarkerDisabled)
            return

    @staticmethod
    def __getVehicleInfo(vehicle):
        vehicleType = vehicle.typeDescriptor.type
        vClass = getVehicleClassTag(vehicleType.tags)
        vName = vehicleType.userString
        vMatrix = LobbyVehicleMarkerView.__getCorrectedHPGuiMatrix(vehicle)
        return (vClass, vName, vMatrix)

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

    def __beginCreateMarker(self, vehicle):
        self.__destroyMarker()
        self.__createMarker(vehicle)

    def __createMarker(self, vehicle):
        if vehicle and vehicle.typeDescriptor:
            vClass, vName, vMatrix = self.__getVehicleInfo(vehicle)
            flashMarker = self.as_createMarkerS(vClass, vName)
            self.__vehicleMarker = GUI.WGHangarVehicleMarker()
            self.__vehicleMarker.setMarker(flashMarker, vMatrix)
        self.__updateMarkerVisibility()

    def __destroyMarker(self):
        self.as_removeMarkerS()
        self.__vehicleMarker = None
        return
