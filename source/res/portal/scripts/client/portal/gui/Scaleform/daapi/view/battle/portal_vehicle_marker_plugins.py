# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_vehicle_marker_plugins.py
from battle_royale.gui.Scaleform.daapi.view.battle.markers2d.plugins import BattleRoyaleVehicleMarkerPlugin

class PortalVehicleMarkerPlugin(BattleRoyaleVehicleMarkerPlugin):

    def start(self):
        super(PortalVehicleMarkerPlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded += self.__onVehicleMarkerAdded
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleMarkerAdded -= self.__onVehicleMarkerAdded
        super(PortalVehicleMarkerPlugin, self).stop()
        return

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if not vInfo.isAlive() and vInfo.isBot:
            self._hideVehicleMarker(vInfo.vehicleID)

    def updateVehiclesInfo(self, updated, arenaDP):
        super(PortalVehicleMarkerPlugin, self).updateVehiclesInfo(updated, arenaDP)
        for _, vInfo in updated:
            if not vInfo.isAlive() and vInfo.isBot:
                self._hideVehicleMarker(vInfo.vehicleID)

    def __onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        if not vInfo.isAlive() and vInfo.isBot:
            self._hideVehicleMarker(vInfo.vehicleID)

    def _getMarkerSymbol(self, _):
        pass
