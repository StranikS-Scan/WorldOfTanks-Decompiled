# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
import BigWorld
from constants import EventBehaviorConst
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import RespawnableVehicleMarkerPlugin, STUN_STATE, INSPIRED_STATE
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
            player.onBotRolesReceived += self.__showEnemiesMarkers
            player.onBotBehaviorReceived += self.__setBehaviorEffect
        self.__showEnemiesMarkers()
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onBotRolesReceived -= self.__showEnemiesMarkers
            player.onBotBehaviorReceived -= self.__setBehaviorEffect
        super(EventVehicleMarkerPlugin, self).fini()
        return

    def hideMarkerTimer(self, vehicleID, handle, statusID, animated):
        if vehicleID not in self._markers:
            return
        handle = self._markers[vehicleID].getMarkerID()
        super(EventVehicleMarkerPlugin, self).hideMarkerTimer(vehicleID, handle, statusID, animated)
        self._invokeMarker(handle, 'clearStatusTimer', statusID)
        behaviorCtrl = self.sessionProvider.dynamic.behaviorMarker
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehicleID)
        if behaviorCtrl and VEHICLE_STATUS.IS_ALIVE & vInfo.vehicleStatus:
            behaviorCtrl.updateBehaviorMarkerById(vehicleID)

    def _getMarkerName(self):
        return settings.MARKER_SYMBOL_NAME.EVENT_VEHICLE_MARKER

    def _setMarkerInitialState(self, marker, accountDBID=0):
        super(EventVehicleMarkerPlugin, self)._setMarkerInitialState(marker, accountDBID)
        if marker.isActive():
            vehicleID = marker.getVehicleID()
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            self.__showEnemyMarker(vInfo, isDead=False)

    def _updateStatusEffectTimer(self, handle, statusID, leftStunTime, animated):
        if any((marker.getMarkerID() == handle for marker in self._markers.itervalues())):
            super(EventVehicleMarkerPlugin, self)._updateStatusEffectTimer(handle, statusID, leftStunTime, animated)

    def __showEnemyMarker(self, vInfo, isDead=False):
        vehicleID = vInfo.vehicleID
        player = BigWorld.player()
        isEnemy = vInfo.team != player.team
        if vehicleID in self._markers and isEnemy:
            self.__updateVehicleMarker(player, vehicleID, isDead)

    def __showEnemyMarkerByVehID(self, vehicleID):
        player = BigWorld.player()
        vehicle = BigWorld.entities.get(vehicleID, None)
        if vehicleID in self._markers and vehicle:
            self.__updateVehicleMarker(player, vehicleID, not vehicle.isAlive())
        return

    def __showEnemiesMarkers(self):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.__showEnemyMarker(vInfo, isDead=not VEHICLE_STATUS.IS_ALIVE & vInfo.vehicleStatus)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID in self._markers:
            if eventID == _EVENT_ID.VEHICLE_SHOW_MESSAGE:
                handle = self._markers[vehicleID].getMarkerID()
                self.__showActionMassage(handle, *value)
            elif eventID == _EVENT_ID.VEHICLE_DEAD:
                arenaDP = self.sessionProvider.getArenaDP()
                vInfo = arenaDP.getVehicleInfo(vehicleID)
                self.__showEnemyMarker(vInfo, isDead=True)

    def __showActionMassage(self, handle, massage, isAlly):
        self._invokeMarker(handle, 'showActionMessage', massage, isAlly)

    def __setBehaviorEffect(self, vehicleID, behavior=EventBehaviorConst.DEFAULT.value):
        if vehicleID not in self._markers:
            return
        markerID = self._markers[vehicleID].getMarkerID()
        arenaDP = self.sessionProvider.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehicleID)
        updateBehavior = self._updateStatusMarkerState
        panic = behavior.endswith(EventBehaviorConst.PANIC.value)
        rage = behavior.endswith(EventBehaviorConst.RAGE.value)
        if (panic or rage) and VEHICLE_STATUS.IS_ALIVE & vInfo.vehicleStatus:
            if panic:
                updateBehavior(vehicleID, False, markerID, INSPIRED_STATE, EventBehaviorConst.STUN_EFFECT_DURATION.value, True, False)
                updateBehavior(vehicleID, True, markerID, STUN_STATE, EventBehaviorConst.STUN_EFFECT_DURATION.value, True, True)
            else:
                updateBehavior(vehicleID, False, markerID, STUN_STATE, EventBehaviorConst.STUN_EFFECT_DURATION.value, True, False)
                updateBehavior(vehicleID, True, markerID, INSPIRED_STATE, EventBehaviorConst.STUN_EFFECT_DURATION.value, True, True)
        else:
            updateBehavior(vehicleID, False, markerID, INSPIRED_STATE, EventBehaviorConst.STUN_EFFECT_DURATION.value, True, False)
            updateBehavior(vehicleID, False, markerID, STUN_STATE, EventBehaviorConst.STUN_EFFECT_DURATION.value, True, False)

    def __updateVehicleMarker(self, player, vehicleID, isDead):
        markerID = self._markers[vehicleID].getMarkerID()
        botMarkerType = player.getBotMarkerType(vehicleID)
        if botMarkerType:
            self._setMarkerActive(markerID, True)
            if isDead:
                botMarkerType += EventBehaviorConst.DESTROYED_PREFIX.value
                self.__setBehaviorEffect(vehicleID)
            self._invokeMarker(markerID, EventBehaviorConst.SHOW_ENEMY_ROLE_MARKER.value, botMarkerType)
        else:
            self._setMarkerActive(markerID, False)
        behaviorCtrl = self.sessionProvider.dynamic.behaviorMarker
        if behaviorCtrl and not isDead:
            behaviorCtrl.updateBehaviorMarkerById(vehicleID)
