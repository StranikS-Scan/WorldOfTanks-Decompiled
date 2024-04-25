# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/diorama_vehicle_marker_view.py
import GUI
import Math
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LobbyVehicleMarkerView
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from historical_battles.gui.impl.lobby.widgets.frontman_widget import FrontmanRoleIDToRole
from historical_battles.gui.shared.hb_events import DioramaVehicleEvent
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.shared.utils import IHangarSpace

class DioramaVehicleMarkerView(LobbyVehicleMarkerView):
    __MARKER_POSITION_Y = 3.8
    _gameEventController = dependency.descriptor(IGameEventController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def _populate(self):
        super(DioramaVehicleMarkerView, self)._populate()
        self.addListener(DioramaVehicleEvent.ON_HB_TANK_LOADED, self.__onHBTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(DioramaVehicleEvent.ON_HB_TANK_DESTROY, self.__onHBTankDestroy, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(DioramaVehicleEvent.ON_HB_TANK_DESTROY, self.__onHBTankDestroy, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(DioramaVehicleEvent.ON_HB_TANK_LOADED, self.__onHBTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        super(DioramaVehicleMarkerView, self)._dispose()

    def _canShowMarkers(self):
        windowsManager = self.guiLoader.windowsManager
        hsInited = self.__hangarSpace.inited
        if hsInited and self._gameEventController and self._gameEventController.isHistoricalBattlesMode():
            layersWithoutMarkers = windowsManager.findWindows(lambda w: w.layer in super(DioramaVehicleMarkerView, self)._LAYERS_WITHOUT_MARKERS)
            layersWithMarkers = windowsManager.findWindows(lambda w: isinstance(w, SFWindow) and w.loadParams.viewKey.alias == VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW)
            return layersWithoutMarkers and layersWithMarkers
        return super(DioramaVehicleMarkerView, self)._canShowMarkers()

    def __onHBTankLoaded(self, event):
        ctx = event.ctx
        vehicle = ctx['entity']
        self._LobbyVehicleMarkerView__destroyMarker(vehicle.id)
        self.__createHBVehicleMarker(vehicle, ctx)

    def __onHBTankDestroy(self, event):
        vehicle = event.ctx['entity']
        self._LobbyVehicleMarkerView__destroyMarker(vehicle.id)

    def __createHBVehicleMarker(self, vehicle, ctx):
        vClass, vName, vMatrix = self.__getHBVehicleInfo(vehicle)
        playerName = ctx['name']
        clanName = ctx['clan']
        roleId = ctx['roleId']
        isInBattle = ctx['inBattle']
        if isInBattle:
            vNameFull = backport.text(R.strings.hb_lobby.status.inBattle())
            vClass = None
        elif roleId is not None:
            roleName = FrontmanRoleIDToRole.get(roleId, None)
            textId = R.strings.hb_lobby.role.dyn(roleName.value)
            roleTxt = backport.text(textId())
            vNameFull = roleTxt + ', ' + vName
        else:
            vNameFull = vName
        flashMarker = self.as_createHBMarkerS(vehicle.id, vClass, vNameFull, playerName, clanName)
        markersCache = self._LobbyVehicleMarkerView__markersCache
        markersCache[vehicle.id] = GUI.WGHangarVehicleMarker()
        markersCache[vehicle.id].setMarker(flashMarker, vMatrix)
        self._LobbyVehicleMarkerView__updateMarkerVisibility(vehicle.id)
        return

    @staticmethod
    def __getHBVehicleInfo(vehicle):
        vehicleType = vehicle.typeDescriptor.type
        vClass = getVehicleClassTag(vehicleType.tags)
        vName = vehicleType.userString
        vMatrix = DioramaVehicleMarkerView.__getCorrectedHBMarkerMatrix(vehicle)
        return (vClass, vName, vMatrix)

    @staticmethod
    def __getCorrectedHBMarkerMatrix(vehicle):
        guiNode = vehicle.model.node('HP_gui')
        localPosition = Math.Vector3(guiNode.localMatrix.translation)
        localPosition.y = DioramaVehicleMarkerView.__MARKER_POSITION_Y
        mat = Math.Matrix(vehicle.matrix)
        pos = mat.applyPoint(localPosition)
        mat.setTranslate(pos)
        return mat
