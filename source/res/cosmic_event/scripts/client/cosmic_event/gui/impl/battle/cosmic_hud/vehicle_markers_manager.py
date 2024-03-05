# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/battle/cosmic_hud/vehicle_markers_manager.py
import logging
import typing
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.vehicle_marker_model import VehicleMarkerModel
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins, vehicle_plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import CommonMarkerType
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
_logger = logging.getLogger(__name__)

class VehicleMarkersManager(plugins.IMarkersManager):
    _pluginClass = vehicle_plugins.VehicleMarkerPlugin

    def __init__(self, markersArray, markersCtrl):
        self._plugins = []
        self._markers = markersArray
        self._markersCtrl = markersCtrl

    def start(self):
        plugin = self._pluginClass(self)
        self._plugins.append(plugin)
        for p in self._plugins:
            p.init()
            p.start()

        _logger.debug('VehicleMarkersManager: start')

    def stop(self):
        for p in self._plugins:
            p.stop()
            p.fini()

        self._plugins = []
        for markerModel in self._markers:
            self._markersCtrl.remove(markerModel.proxy)

        _logger.debug('VehicleMarkersManager: stop')

    def createMarker(self, symbol, matrixProvider=None, active=True, markerType=CommonMarkerType.VEHICLE):
        _logger.debug('VehicleMarkersManager invoked: createMarker %s', symbol)
        markerModel = VehicleMarkerModel()
        self._markers.addViewModel(markerModel)
        return len(self._markers) - 1

    def invokeMarker(self, markerID, *signature):
        _logger.debug('VehicleMarkersManager invoked: invokeMarker (%s)', str(signature))
        if signature[0] == 'setVehicleInfo':
            self._markers[markerID].setPlayerName(signature[6])

    def setMarkerMatrix(self, markerID, matrix):
        _logger.debug('VehicleMarkersManager invoked: setMarkerMatrix')
        self._markersCtrl.add(self._markers[markerID].proxy, matrix)

    def setMarkerActive(self, markerID, active):
        pass

    def setMarkerLocationOffset(self, markerID, minY, maxY, distForMinY, maxBoost, boostStart):
        pass

    def setMarkerRenderInfo(self, markerID, minScale, offset, innerOffset, cullDistance, boundsMinScale):
        pass

    def setMarkerBoundCheckEnabled(self, markerID, enable):
        pass

    def setMarkerObjectInFocus(self, markerID, isInFocus):
        pass

    def destroyMarker(self, markerID):
        pass

    def setMarkerSticky(self, markerID, isSticky):
        pass

    def _createCanvas(self, arenaVisitor):
        pass

    def _setupPlugins(self, arenaVisitor):
        pass
