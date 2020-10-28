# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_vehicle_marker_view.py
import GUI
import Math
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.shared import events, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from HalloweenHangarTank import HalloweenHangarTank
from gui.impl import backport
from gui.impl.gen import R

class LobbyVehicleMarkerView(LobbyVehicleMarkerViewMeta):
    __loadEvents = (VIEW_ALIAS.LOBBY_STORE,
     VIEW_ALIAS.LOBBY_STORAGE,
     VIEW_ALIAS.LOBBY_TECHTREE,
     VIEW_ALIAS.LOBBY_BARRACKS,
     VIEW_ALIAS.LOBBY_PROFILE,
     VIEW_ALIAS.VEHICLE_COMPARE,
     VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS,
     VIEW_ALIAS.LOBBY_MISSIONS,
     VIEW_ALIAS.LOBBY_STRONGHOLD)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctx=None):
        super(LobbyVehicleMarkerView, self).__init__(ctx)
        self.__vehicleMarkers = {}
        self.__isMarkerDisabled = False
        self.__selectedVehicleID = None
        return

    def _populate(self):
        super(LobbyVehicleMarkerView, self)._populate()
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HALLOWEEN_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HALLOWEEN_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.addListener(events.ViewEventType.LOAD_VIEW, self.__handleViewLoad, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__handleGuiImplViewLoad, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.__destroyAllMarkers()
        super(LobbyVehicleMarkerView, self)._dispose()
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HALLOWEEN_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HALLOWEEN_TANK_DESTROY, self.__onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.removeListener(events.ViewEventType.LOAD_VIEW, self.__handleViewLoad, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__handleGuiImplViewLoad, EVENT_BUS_SCOPE.LOBBY)

    def getIsMarkerDisabled(self):
        return self.__isMarkerDisabled

    def __onSpaceDestroy(self, _):
        self.__destroyAllMarkers()

    def __onHeroTankLoaded(self, event):
        vehicle = event.ctx['entity']
        self.__beginCreateMarker(vehicle)

    def __onHeroTankDestroy(self, event):
        vehicle = event.ctx['entity']
        self.__destroyMarker(vehicle)

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
        self.__isMarkerDisabled = event.ctx['isDisable']
        self.__updateMarkerVisibility()

    def __updateMarkerVisibility(self):
        for vehicleID, marker in self.__vehicleMarkers.iteritems():
            marker.markerSetActive(not self.__isMarkerDisabled and vehicleID != self.__selectedVehicleID)

    @staticmethod
    def __getVehicleInfo(vehicle):
        isHalloween = isinstance(vehicle, HalloweenHangarTank)
        vehicleType = vehicle.typeDescriptor.type
        vClass = getVehicleClassTag(vehicleType.tags) if not isHalloween else ''
        vName = vehicleType.userString if not isHalloween else backport.text(R.strings.event.tradeStyles.skinName(), name=vehicleType.shortUserString)
        vMatrix = LobbyVehicleMarkerView.__getCorrectedHPGuiMatrix(vehicle) if not isHalloween else LobbyVehicleMarkerView.__getHWVehicleGuiMatrix(vehicle)
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

    @staticmethod
    def __getHWVehicleGuiMatrix(hwVehicle):
        mat = Math.Matrix()
        guiNode = hwVehicle.model.node('HP_gui')
        localPosition = Math.Vector3(guiNode.initialLocalMatrix.translation)
        localPosition.y *= hwVehicle.markerHeightFactor
        vehicleMatrix = Math.Matrix(hwVehicle.matrix)
        worldPosition = vehicleMatrix.applyPoint(localPosition)
        mat.setTranslate(worldPosition)
        return mat

    def __beginCreateMarker(self, vehicle):
        self.__destroyMarker(vehicle)
        self.__createMarker(vehicle)

    def __createMarker(self, vehicle):
        vClass, vName, vMatrix, vMarkerStyleId = self.__getVehicleInfo(vehicle)
        flashMarker = self.as_createMarkerS(vClass, vName, vehicle.id, vMarkerStyleId)
        marker = GUI.WGHangarVehicleMarker()
        marker.setMarker(flashMarker, vMatrix)
        self.__vehicleMarkers[vehicle.id] = marker
        self.__updateMarkerVisibility()

    def __destroyMarker(self, vehicle):
        vehicleID = vehicle.id
        if vehicleID in self.__vehicleMarkers:
            self.as_removeMarkerS(vehicleID)
            del self.__vehicleMarkers[vehicleID]

    def __destroyAllMarkers(self):
        for markerID in self.__vehicleMarkers:
            self.as_removeMarkerS(markerID)

        self.__vehicleMarkers.clear()

    def __handleViewLoad(self, event):
        if event.alias in (VIEW_ALIAS.LOBBY_HANGAR, VIEW_ALIAS.EVENT_STYLES_PREVIEW):
            self.__isMarkerDisabled = False
        elif event.alias in self.__loadEvents:
            self.__isMarkerDisabled = True
        else:
            return
        self.__updateMarkerVisibility()

    def __handleGuiImplViewLoad(self, _):
        self.__isMarkerDisabled = True
        self.__updateMarkerVisibility()
