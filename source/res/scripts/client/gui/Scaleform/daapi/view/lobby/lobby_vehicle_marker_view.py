# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/lobby_vehicle_marker_view.py
import logging
import typing
from collections import defaultdict
import GUI
import Math
from gui.Scaleform.daapi.view.meta.LobbyVehicleMarkerViewMeta import LobbyVehicleMarkerViewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.shared import events, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared.utils import IHangarSpace
from frameworks.wulf.gui_constants import WindowLayer
from frameworks.wulf import WindowStatus
from gui.impl.pub.pop_over_window import PopOverWindow
if typing.TYPE_CHECKING:
    from cgf_components.marker_component import LobbyFlashMarker
    from gui.shared.events import HasCtxEvent
_logger = logging.getLogger(__name__)

class LobbyVehicleMarkerView(LobbyVehicleMarkerViewMeta):
    __LAYERS_WITHOUT_MARKERS = {WindowLayer.FULLSCREEN_WINDOW,
     WindowLayer.OVERLAY,
     WindowLayer.SUB_VIEW,
     WindowLayer.TOP_SUB_VIEW}
    hangarSpace = dependency.descriptor(IHangarSpace)
    guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, ctx=None):
        super(LobbyVehicleMarkerView, self).__init__(ctx)
        self.__markersCache = defaultdict(lambda : None)
        self.__isMarkerDisabled = False

    def _populate(self):
        super(LobbyVehicleMarkerView, self)._populate()
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self._onHeroPlatoonTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self._onPlatoonTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self._onHeroPlatoonTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.LobbyMarkersManagerEvent.ON_MARKER_ADDED, self.__onCgfMarkerAdded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.LobbyMarkersManagerEvent.ON_MARKER_REMOVED, self.__removeCgfMarker, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.LobbyMarkersManagerEvent.ON_MARKER_RESPONSE, self.__cgfMarkerInitResponse, EVENT_BUS_SCOPE.LOBBY)
        self.guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        self.fireEvent(events.LobbyMarkersManagerEvent(events.LobbyMarkersManagerEvent.ON_MARKER_REQUEST, ctx={'requesterId': id(self)}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        super(LobbyVehicleMarkerView, self)._dispose()
        self.removeListener(events.LobbyMarkersManagerEvent.ON_MARKER_RESPONSE, self.__cgfMarkerInitResponse, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.LobbyMarkersManagerEvent.ON_MARKER_REMOVED, self.__removeCgfMarker, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.LobbyMarkersManagerEvent.ON_MARKER_ADDED, self.__onCgfMarkerAdded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated, EVENT_BUS_SCOPE.DEFAULT)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, self._onHeroTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self._onPlatoonTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self._onHeroPlatoonTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        self.__destroyAllMarkers()

    def __onSpaceDestroy(self, _):
        self.__destroyAllMarkers()

    def __onHeroTankLoaded(self, event):
        vehicle = event.ctx['entity']
        self.__beginCreateVehicleMarker(vehicle)

    def _onHeroTankDestroy(self, event):
        vehicle = event.ctx['entity']
        _logger.info('destroy vehicle marker %s', vehicle.id)
        self.__destroyMarker(vehicle.id)

    def _onPlatoonTankLoaded(self, event):
        vehicle = event.ctx['entity']
        playerName = event.ctx['playerName']
        self.__destroyMarker(vehicle.id)
        self.__createPlatoonMarker(vehicle, playerName)

    def _onHeroPlatoonTankDestroy(self, event):
        vehicle = event.ctx['entity']
        _logger.info('destroy platoon vehicle marker %s', vehicle.id)
        self.__destroyMarker(vehicle.id)

    def __onCgfMarkerAdded(self, event):
        self.__addCgfMarker(event.ctx['markerId'], event.ctx['flashMarkerComponent'], event.ctx['matrix'])

    def __addCgfMarker(self, markerId, markerComponent, matrix):
        flashMarker = markerComponent(self, markerId, markerComponent)
        _logger.info('cgf marker created %s', flashMarker)
        self.__markersCache[markerId] = GUI.HangarVehicleMarker()
        self.__markersCache[markerId].setMarker(flashMarker, matrix)
        self.__updateMarkerVisibility(markerId)

    def __removeCgfMarker(self, event):
        markerId = event.ctx['markerId']
        _logger.info('remove cgf marker %s', markerId)
        self.__destroyMarker(markerId)

    def __cgfMarkerInitResponse(self, event):
        if id(self) == event.ctx['requesterId']:
            for markerData in event.ctx['markers']:
                markerId = markerData['markerId']
                if markerId not in self.__markersCache:
                    self.__addCgfMarker(markerId, markerData['flashMarkerComponent'], markerData['matrix'])

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

    def _canShowMarkers(self):
        windowsManager = self.guiLoader.windowsManager
        windows = windowsManager.findWindows(lambda w: w.layer in self.__LAYERS_WITHOUT_MARKERS and not isinstance(w, PopOverWindow))
        hangarIsExist = len(windowsManager.findWindows(lambda w: isinstance(w, SFWindow) and w.loadParams.viewKey.alias == VIEW_ALIAS.LOBBY_HANGAR)) > 0
        return len(windows) == 1 and hangarIsExist

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
        if hasattr(vehicle, 'markerHeightFactor'):
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
        _logger.info('create vehicle marker %s %s', vehicle.id, vName)
        flashMarker = self.as_createMarkerS(vehicle.id, vClass, vName)
        self.__markersCache[vehicle.id] = GUI.HangarVehicleMarker()
        self.__markersCache[vehicle.id].setMarker(flashMarker, vMatrix)
        self.__updateMarkerVisibility(vehicle.id)

    def __createPlatoonMarker(self, vehicle, playerName):
        vClass, vName, vMatrix = self.__getVehicleInfo(vehicle)
        _logger.info('create platoon vehicle marker %s %s', vehicle.id, vName)
        flashMarker = self.as_createPlatoonMarkerS(vehicle.id, vClass, playerName)
        self.__markersCache[vehicle.id] = GUI.HangarVehicleMarker()
        self.__markersCache[vehicle.id].setMarker(flashMarker, vMatrix)
        self.__updateMarkerVisibility(vehicle.id)

    def __destroyMarker(self, entityId):
        self.as_removeMarkerS(entityId)
        marker = self.__markersCache.pop(entityId, None)
        if marker is not None:
            marker.markerSetActive(False)
        return

    def __destroyAllMarkers(self):
        if self.__markersCache:
            _logger.info('destroy all hangar vehicle markers')
        for k, marker in self.__markersCache.iteritems():
            self.as_removeMarkerS(k)
            if marker is not None:
                marker.markerSetActive(False)

        self.__markersCache.clear()
        return

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        if newStatus in (WindowStatus.LOADING, WindowStatus.DESTROYED):
            self.__isMarkerDisabled = not self._canShowMarkers()
            self.__updateAllMarkersVisibility()
