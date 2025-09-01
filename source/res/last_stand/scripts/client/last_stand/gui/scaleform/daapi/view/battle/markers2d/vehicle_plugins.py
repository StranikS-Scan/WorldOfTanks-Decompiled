# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/markers2d/vehicle_plugins.py
from gui.battle_control.battle_constants import MARKER_HIT_EVENTS
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.impl.gen import R
from gui.impl import backport
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID, FEEDBACK_EVENT_ID
from last_stand.gui.ls_vehicle_role_helper import getVehicleRole
from last_stand_common.last_stand_constants import LS_ROLE_PREFIX
from LSTeamInfoStatsComponent import LSTeamInfoStatsComponent
VEHICLE_MARKER = 'LSVehicleMarkerUI'

class LSVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):
    ICON_HIT_BLOCKED = 'hit_blocked'
    IGNORE_FEEDBACKS = MARKER_HIT_EVENTS.union({FEEDBACK_EVENT_ID.VEHICLE_STUN})

    def init(self, *args):
        super(LSVehicleMarkerPlugin, self).init()
        lsBattleGuiCtrl = self.lsBattleGuiCtrl
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onVehicleBuffIconAdded += self.__onVehicleBuffIconAdded
            lsBattleGuiCtrl.onVehicleInvulnerabilityChanged += self.__onVehicleInvulnerabilityChanged

    def fini(self):
        lsBattleGuiCtrl = self.lsBattleGuiCtrl
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onVehicleBuffIconAdded -= self.__onVehicleBuffIconAdded
            lsBattleGuiCtrl.onVehicleInvulnerabilityChanged -= self.__onVehicleInvulnerabilityChanged
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

            if self.lsBattleGuiCtrl.isVehicleInvulnerable(vID):
                self.__onVehicleInvulnerabilityChanged(vID, True)

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if self.lsBattleGuiCtrl.isVehicleInvulnerable(vehicleID) and eventID in self.IGNORE_FEEDBACKS:
            return
        if eventID == FEEDBACK_EVENT_ID.LS_NO_HIT and vehicleID in self._markers:
            newState, _, _, isFrequent = self._getHitStateVO(eventID, vehicleID)
            stateText = backport.text(R.strings.last_stand_battle.hitMarker.useless())
            iconAnimation = self.ICON_HIT_BLOCKED
            marker = self._markers[vehicleID]
            handle = marker.getMarkerID()
            self._updateMarkerState(handle, newState, False, stateText, iconAnimation, isFrequent)
        else:
            super(LSVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)

    def __onVehicleBuffIconAdded(self, vehicleId, icon):
        marker = self._markers.get(vehicleId)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'showEnemyBuff', icon)
        return

    def __onVehicleInvulnerabilityChanged(self, vehicleID, isInvulnerable):
        marker = self._markers.get(vehicleID)
        if marker is not None:
            isHPVisible = not isInvulnerable
            self._invokeMarker(marker.getMarkerID(), 'setHealthBarMode', isHPVisible)
        return
