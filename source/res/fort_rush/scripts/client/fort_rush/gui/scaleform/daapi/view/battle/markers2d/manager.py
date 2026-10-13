# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/markers2d/manager.py
from __future__ import absolute_import
from fort_rush.gui.fort_rush_gui_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.framework import getSwfExtensionUrl
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_FORT_RUSH_VEHICLE_MARKER = 'FortRushVehicleMarkerUI'

class FortRushVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def start(self):
        super(FortRushVehicleMarkerPlugin, self).start()
        ctrl = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)
        if ctrl is not None:
            ctrl.onVehicleInvulnerabilityChanged += self.__onVehicleInvulnerabilityChanged
        return

    def stop(self):
        ctrl = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)
        if ctrl is not None:
            ctrl.onVehicleInvulnerabilityChanged -= self.__onVehicleInvulnerabilityChanged
        super(FortRushVehicleMarkerPlugin, self).stop()
        return

    def _getMarkerSymbol(self, vehicleID):
        return _FORT_RUSH_VEHICLE_MARKER

    def __onVehicleInvulnerabilityChanged(self, vehicleID, isActive):
        self.__setInvulnerableIconVisible(vehicleID, isActive)

    def _setMarkerInitialState(self, marker, vInfo):
        super(FortRushVehicleMarkerPlugin, self)._setMarkerInitialState(marker, vInfo)
        ctrl = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)
        isInvulnerable = ctrl is not None and ctrl.isVehicleInvulnerable(vInfo.vehicleID)
        self.__setInvulnerableIconVisible(vInfo.vehicleID, isInvulnerable)
        return

    def __setInvulnerableIconVisible(self, vehicleID, isVisible):
        marker = self._markers.get(vehicleID)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'setInvulnerableIconVisible', isVisible)
        return


class FortRushMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = getSwfExtensionUrl('fort_rush', 'fortRushBattleVehicleMarkersApp.swf')

    def _setupPlugins(self, arenaVisitor):
        setup = super(FortRushMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = FortRushVehicleMarkerPlugin
        return setup
