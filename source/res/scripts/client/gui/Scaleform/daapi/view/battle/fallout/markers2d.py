# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/markers2d.py
import GUI
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.battle_control.battle_constants import GAS_ATTACK_STATE

class FalloutVehicleMarker(markers.VehicleMarker):

    def __init__(self, markerID, vehicleID, vProxy, active=True):
        super(FalloutVehicleMarker, self).__init__(markerID, vehicleID, vProxy, active)
        self._flagBearer = False

    def isFlagBearer(self):
        return self._flagBearer

    def setFlagBearer(self, bearer):
        if self._flagBearer != bearer:
            self._flagBearer = bearer
            return True
        return False


class GasAttackSafeZonePlugin(plugins.MarkerPlugin):

    def __init__(self, parentObj):
        super(GasAttackSafeZonePlugin, self).__init__(parentObj)
        self.__safeZoneMarkerHandle = None
        self.__isMarkerVisible = False
        self.__settings = self.sessionProvider.arenaVisitor.getGasAttackSettings()
        return

    def init(self):
        super(GasAttackSafeZonePlugin, self).init()
        ctrl = self.sessionProvider.dynamic.gasAttack
        if ctrl is not None:
            ctrl.onUpdated += self.__onGasAttackUpdate
        self.__initMarker(self.__settings.position)
        return

    def fini(self):
        self.__settings = None
        ctrl = self.sessionProvider.dynamic.gasAttack
        if ctrl is not None:
            ctrl.onUpdated -= self.__onGasAttackUpdate
        super(GasAttackSafeZonePlugin, self).fini()
        return

    def stop(self):
        self.__delSafeZoneMarker()
        super(GasAttackSafeZonePlugin, self).stop()

    def __updateSafeZoneMarker(self, isVisible):
        if not self.__isMarkerVisible == isVisible:
            self.__isMarkerVisible = isVisible
            self._invokeMarker(self.__safeZoneMarkerHandle, 'update', self.__isMarkerVisible)

    def __initMarker(self, center):
        if self.__safeZoneMarkerHandle is None:
            self.__safeZoneMarkerHandle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.SAFE_ZONE_MARKER, center + settings.MARKER_POSITION_ADJUSTMENT)
        return

    def __delSafeZoneMarker(self):
        if self.__safeZoneMarkerHandle is not None:
            self._destroyMarker(self.__safeZoneMarkerHandle)
            self.__safeZoneMarkerHandle = None
        return

    def __onGasAttackUpdate(self, state):
        self.__updateSafeZoneMarker(state.state in GAS_ATTACK_STATE.VISIBLE)


class FalloutMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(FalloutMarkersManager, self)._setupPlugins(arenaVisitor)
        if arenaVisitor.hasGasAttack():
            setup['safe_zone'] = GasAttackSafeZonePlugin
        return setup
