# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/markers2d/vehicle_plugins.py
from LSTeamInfoStatsComponent import LSTeamInfoStatsComponent
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from last_stand.gui.ls_vehicle_role_helper import getVehicleRole
from last_stand_common.last_stand_constants import LS_ROLE_PREFIX
VEHICLE_MARKER = 'LSVehicleMarkerUI'

class LSVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):

    def init(self, *args):
        super(LSVehicleMarkerPlugin, self).init()
        lsBattleGuiCtrl = self.lsBattleGuiCtrl
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onVehicleBuffIconAdded += self.__onVehicleBuffIconAdded

    def fini(self):
        lsBattleGuiCtrl = self.lsBattleGuiCtrl
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onVehicleBuffIconAdded -= self.__onVehicleBuffIconAdded
        super(LSVehicleMarkerPlugin, self).fini()

    @property
    def vehicleStats(self):
        return LSTeamInfoStatsComponent.getInstance()

    @property
    def lsBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def _getMarkerSymbol(self, vehicleID):
        return VEHICLE_MARKER

    def _restoreMarker(self, marker, vProxy, vInfo, guiProps):
        super(LSVehicleMarkerPlugin, self)._restoreMarker(marker, vProxy, vInfo, guiProps)
        if not marker.isAlive():
            self._updateMarkerState(marker.getMarkerID(), 'dead', True, '')
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)
            lsBattleGuiCtrl = self.lsBattleGuiCtrl
            if lsBattleGuiCtrl and lsBattleGuiCtrl.isVehicleHidden(vInfo.vehicleID):
                self._hideVehicleMarker(vehicleID=vInfo.vehicleID)

    def _getVehicleClassTag(self, vInfo):
        role = getVehicleRole(vInfo.vehicleType)
        return LS_ROLE_PREFIX + role if role is not None else super(LSVehicleMarkerPlugin, self)._getVehicleClassTag(vInfo)

    def _getVehicleName(self, nameParts, vInfo):
        return vInfo.vehicleType.shortNameWithPrefix if not vInfo.player.isBot else vInfo.vehicleType.name

    def _setMarkerInitialState(self, marker, vInfo):
        super(LSVehicleMarkerPlugin, self)._setMarkerInitialState(marker, vInfo)
        lsBattleGuiCtrl = self.lsBattleGuiCtrl
        if lsBattleGuiCtrl:
            vID = vInfo.vehicleID
            for icon in lsBattleGuiCtrl.vehicleMarkerIcons.get(vID, []):
                self.__onVehicleBuffIconAdded(vID, icon)

    def __onVehicleBuffIconAdded(self, vehicleId, icon):
        marker = self._markers.get(vehicleId)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'showEnemyBuff', icon)
        return
