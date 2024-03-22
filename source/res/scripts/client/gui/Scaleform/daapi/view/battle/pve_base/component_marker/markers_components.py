# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/component_marker/markers_components.py
import ResMgr
from chat_commands_consts import MarkerType
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import BaseMinimapMarkerComponent, World2DActionMarkerComponent, ComponentBitMask, World2DLocationMarkerComponent
from gui.impl.backport import getIntegralFormat

class PveAttackDirectionComponent(BaseMinimapMarkerComponent):

    @classmethod
    def configReader(cls, section):
        config = super(PveAttackDirectionComponent, cls).configReader(section)
        config.update({'bitmapName': section.readString('bitmapName', ''),
         'isFlipped': section.readBool('isFlipped', False)})
        return config

    def _setupMarker(self, gui, **kwargs):
        super(PveAttackDirectionComponent, self)._setupMarker(gui, **kwargs)
        gui.invoke(self._componentID, 'setArrow', self._config['bitmapName'], self._config['isFlipped'])
        isReconnect = kwargs.get('isReconnect', False)
        if not isReconnect:
            gui.invoke(self._componentID, 'animate')


class PveAttackDirectionMinimapComponent(PveAttackDirectionComponent):

    @property
    def maskType(self):
        return ComponentBitMask.MINIMAP_MARKER


class PveAttackDirectionFullscreenMapComponent(PveAttackDirectionComponent):

    @property
    def maskType(self):
        return ComponentBitMask.FULLSCREEN_MAP_MARKER


class PveFlagMinimapComponent(BaseMinimapMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        isReconnect = kwargs.get('isReconnect', False)
        if not isReconnect:
            gui.invoke(self._componentID, 'animate')

    @property
    def maskType(self):
        return ComponentBitMask.MINIMAP_MARKER


class PveFlagFullscreenMapComponent(BaseMinimapMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        isReconnect = kwargs.get('isReconnect', False)
        if not isReconnect:
            gui.invoke(self._componentID, 'animate')

    @property
    def maskType(self):
        return ComponentBitMask.FULLSCREEN_MAP_MARKER


class PveTargetFlagMinimapComponent(BaseMinimapMarkerComponent):

    @property
    def maskType(self):
        return ComponentBitMask.MINIMAP_MARKER


class PveTargetFlagFullscreenMapComponent(BaseMinimapMarkerComponent):

    @property
    def maskType(self):
        return ComponentBitMask.FULLSCREEN_MAP_MARKER


class PveFlagLocationMarkerComponent(World2DLocationMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        super(PveFlagLocationMarkerComponent, self)._setupMarker(gui, **kwargs)
        gui.invokeMarker(self.componentID, 'stopAnimation')

    @property
    def bcMarkerType(self):
        return MarkerType.NON_INTERACTIVE


class PveFlagVehicleMarkerComponent(World2DActionMarkerComponent):

    def __init__(self, *args, **kwargs):
        super(PveFlagVehicleMarkerComponent, self).__init__(*args, **kwargs)
        self._vehicleMarkerGUI = None
        return

    @classmethod
    def configReader(cls, section):
        config = super(PveFlagVehicleMarkerComponent, cls).configReader(section)
        config.update({'symbolIndex': section.readInt('symbolIndex', 0),
         'symbolOffset': section.readInt('symbolOffset', 0)})
        return config

    def attachGUI(self, guiProvider, **kwargs):
        self._vehicleMarkerGUI = guiProvider.getVehicleMarkerPlugin()
        return super(PveFlagVehicleMarkerComponent, self).attachGUI(guiProvider, **kwargs)

    def update(self, distance, *args, **kwargs):
        super(PveFlagVehicleMarkerComponent, self).update(distance, *args, **kwargs)
        self._updateDistance(distance)

    def clear(self):
        super(PveFlagVehicleMarkerComponent, self).clear()
        self._vehicleMarkerGUI = None
        return

    def _setupMarker(self, gui, **kwargs):
        super(PveFlagVehicleMarkerComponent, self)._setupMarker(gui, **kwargs)
        self._insertSymbol()

    def _deleteMarker(self):
        self._removeSymbol()
        super(PveFlagVehicleMarkerComponent, self)._deleteMarker()

    def _getVehicleMarker(self):
        return self._vehicleMarkerGUI.getVehicleMarker(self._targetID) if self._vehicleMarkerGUI else None

    def _insertSymbol(self):
        vehicleMarker = self._getVehicleMarker()
        if vehicleMarker:
            self._vehicleMarkerGUI.invokeMarker(vehicleMarker.getMarkerID(), 'insertSymbol', self._config['symbol'], self._config['symbolIndex'], self._config['symbolOffset'])
            self._vehicleMarkerGUI.invokeMarker(vehicleMarker.getMarkerID(), 'callInsertedSymbolMethod', self._config['symbol'], 'setMeters', self._METERS_STRING)

    def _removeSymbol(self):
        vehicleMarker = self._getVehicleMarker()
        if vehicleMarker:
            self._vehicleMarkerGUI.invokeMarker(vehicleMarker.getMarkerID(), 'removeSymbol', self._config['symbol'])

    def _updateDistance(self, distance):
        vehicleMarker = self._getVehicleMarker()
        if vehicleMarker:
            self._vehicleMarkerGUI.invokeMarker(vehicleMarker.getMarkerID(), 'callInsertedSymbolMethod', self._config['symbol'], 'setDistance', getIntegralFormat(distance))
