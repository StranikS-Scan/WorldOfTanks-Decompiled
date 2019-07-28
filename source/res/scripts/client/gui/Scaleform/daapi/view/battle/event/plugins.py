# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from helpers import isPlayerAvatar

class EventVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):

    def init(self, *args):
        super(EventVehicleMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onDamageByVehTypeChanged += self.__onDamageByVehTypeChanged
        self.__onDamageByVehTypeChanged()
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onDamageByVehTypeChanged -= self.__onDamageByVehTypeChanged
        super(EventVehicleMarkerPlugin, self).fini()
        return

    def _getMarkerName(self):
        return settings.MARKER_SYMBOL_NAME.EVENT_VEHICLE_MARKER

    def _setMarkerInitialState(self, marker, accountDBID=0):
        super(EventVehicleMarkerPlugin, self)._setMarkerInitialState(marker, accountDBID)
        if marker.isActive():
            vehicleID = marker.getVehicleID()
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            self.__showEnemyDamageMark(vInfo)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == _EVENT_ID.VEHICLE_SHOW_MESSAGE and vehicleID in self._markers:
            handle = self._markers[vehicleID].getMarkerID()
            self.__showActionMassage(handle, *value)

    def __showActionMassage(self, handle, massage, isAlly):
        self._invokeMarker(handle, 'showActionMessage', massage, isAlly)

    def __showEnemyDamageMark(self, vInfo):
        vehicleID = vInfo.vehicleID
        player = BigWorld.player()
        damage = player.damageByVehType.get(vInfo.vehicleType.compactDescr, 1)
        isEnemy = vInfo.team != player.team
        if vehicleID in self._markers and isEnemy:
            handle = self._markers[vehicleID].getMarkerID()
            self._invokeMarker(handle, 'showEnemyDamageMark', damage)

    def __onDamageByVehTypeChanged(self):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.__showEnemyDamageMark(vInfo)
