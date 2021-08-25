# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_vehicle_marker_view.py
import typing
from collections import defaultdict
import GUI
import Math
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.shared import events, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from helpers import dependency
from helpers.i18n import makeString
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from cgf_components.marker_component import LobbyFlashMarker

class LobbyVehicleMarkerView(LobbyVehicleMarkerViewMeta):
    __loadEvents = (VIEW_ALIAS.LOBBY_STORE,
     VIEW_ALIAS.LOBBY_STORAGE,
     VIEW_ALIAS.LOBBY_TECHTREE,
     VIEW_ALIAS.LOBBY_BARRACKS,
     VIEW_ALIAS.LOBBY_PROFILE,
     VIEW_ALIAS.VEHICLE_COMPARE,
     VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS,
     VIEW_ALIAS.LOBBY_MISSIONS,
     VIEW_ALIAS.LOBBY_STRONGHOLD,
     BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW)
    hangarSpace = dependency.descriptor(IHangarSpace)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, ctx=None):
        super(LobbyVehicleMarkerView, self).__init__(ctx)
        self.__markersCache = defaultdict(lambda : None)
        self.__isMarkerDisabled = False

    def _populate(self):
        super(LobbyVehicleMarkerView, self)._populate()
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroPlatoonTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.addListener(events.ViewEventType.LOAD_VIEW, self.__handleViewLoad, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__handleGuiImplViewLoad, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__onHeroPlatoonTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, self.__onToggleVisibility, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        super(LobbyVehicleMarkerView, self)._dispose()
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self.__onHeroPlatoonTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.HERO_TANK_MARKER, self.__onMarkerDisable, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.removeListener(events.ViewEventType.LOAD_VIEW, self.__handleViewLoad, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__handleGuiImplViewLoad, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__onHeroPlatoonTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, self.__onToggleVisibility, EVENT_BUS_SCOPE.LOBBY)
        self.__destroyAllMarkers()

    def getIsMarkerDisabled(self):
        return self.__isMarkerDisabled

    def __onSpaceDestroy(self, _):
        self.__destroyAllMarkers()

    def __onHeroTankLoaded(self, event):
        vehicle = event.ctx['entity']
        self.__beginCreateVehicleMarker(vehicle)

    def __onPlatoonTankLoaded(self, event):
        vehicle = event.ctx['entity']
        playerName = event.ctx['playerName']
        self.__destroyMarker(vehicle.id)
        self.__createPlatoonMarker(vehicle, playerName)

    def __onHeroPlatoonTankDestroy(self, event):
        vehicle = event.ctx['entity']
        self.__destroyMarker(vehicle.id)

    def addCgfMarker(self, entityId, markerComponent, matrix):
        flashMarker = self.as_createCustomMarkerS(entityId, markerComponent.icon.replace('gui', '..'), makeString(markerComponent.textKey))
        self.__markersCache[entityId] = GUI.WGHangarVehicleMarker()
        self.__markersCache[entityId].setMarker(flashMarker, matrix)
        self.__updateMarkerVisibility(entityId)

    def removeCgfMarker(self, entityId):
        self.__destroyMarker(entityId)

    def __onCameraEntityUpdated(self, event):
        entityId = event.ctx['entityId']
        if self.__isMarkerDisabled or self.__markersCache[entityId] is None:
            return
        else:
            state = event.ctx['state']
            if state == CameraMovementStates.FROM_OBJECT:
                return
            self.__markersCache[entityId].markerSetActive(self.hangarSpace.space.vehicleEntityId == entityId)
            return

    def __onMarkerDisable(self, event):
        self.__isMarkerDisabled = event.ctx['isDisable']
        self.__updateAllMarkersVisibility()

    def __updateMarkerVisibility(self, vehicleId):
        if self.__markersCache[vehicleId] is None:
            return
        else:
            self.__markersCache[vehicleId].markerSetActive(not self.__isMarkerDisabled)
            return

    def __updateAllMarkersVisibility(self):
        for vehicleMarker in self.__markersCache.values():
            if vehicleMarker:
                vehicleMarker.markerSetActive(not self.__isMarkerDisabled)

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

    def __beginCreateVehicleMarker(self, vehicle):
        self.__destroyMarker(vehicle.id)
        self.__createVehicleMarker(vehicle)

    def __createVehicleMarker(self, vehicle):
        vClass, vName, vMatrix = self.__getVehicleInfo(vehicle)
        flashMarker = self.as_createMarkerS(vehicle.id, vClass, vName)
        self.__markersCache[vehicle.id] = GUI.WGHangarVehicleMarker()
        self.__markersCache[vehicle.id].setMarker(flashMarker, vMatrix)
        self.__updateMarkerVisibility(vehicle.id)

    def __createPlatoonMarker(self, vehicle, playerName):
        vClass, _, vMatrix = self.__getVehicleInfo(vehicle)
        flashMarker = self.as_createPlatoonMarkerS(vehicle.id, vClass, playerName)
        self.__markersCache[vehicle.id] = GUI.WGHangarVehicleMarker()
        self.__markersCache[vehicle.id].setMarker(flashMarker, vMatrix)
        self.__updateMarkerVisibility(vehicle.id)

    def __destroyMarker(self, entityId):
        self.as_removeMarkerS(entityId)
        self.__markersCache.pop(entityId, None)
        return

    def __destroyAllMarkers(self):
        for k, marker in self.__markersCache.iteritems():
            self.as_removeMarkerS(k)
            if marker is not None:
                marker.markerSetActive(False)

        self.__markersCache.clear()
        return

    def __handleViewLoad(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.__isMarkerDisabled = False
        elif event.alias in self.__loadEvents:
            self.__isMarkerDisabled = True
        else:
            return
        self.__updateAllMarkersVisibility()

    def __handleGuiImplViewLoad(self, _):
        self.__isMarkerDisabled = True
        self.__updateAllMarkersVisibility()

    def __onToggleVisibility(self, event):
        state = event.ctx.get('state')
        if state is not None and state == HeaderMenuVisibilityState.ALL:
            self.__isMarkerDisabled = False
            self.__updateAllMarkersVisibility()
        return
