# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import EventBusPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import MARKER_SYMBOL_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions, EventKeys
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS, FEEDBACK_EVENT_ID
from gui.impl import backport
from gui.impl.gen import R

class EventVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):

    def _getMarkerSymbol(self, vehicleID):
        return MARKER_SYMBOL_NAME.EVENT_VEHICLE_MARKER

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        super(EventVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
        if vehicleID not in self._markers:
            return
        markerID = self._markers[vehicleID].getMarkerID()
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_SHOW_MESSAGE:
            self._showActionMessage(markerID, *value)
        elif eventID == FEEDBACK_EVENT_ID.WT_BOMB_CAPTURE:
            self._updateBombMarker(vehicleID, BATTLE_MARKER_STATES.WT_BOMB_CAPTURING_STATE, value)
        elif eventID == FEEDBACK_EVENT_ID.WT_BOMB_DEPLOY:
            self._updateBombMarker(vehicleID, BATTLE_MARKER_STATES.WT_BOMB_INSTALLING_STATE, value)

    def _showActionMessage(self, markerID, message, isAlly):
        self._invokeMarker(markerID, 'showActionMessage', message, isAlly)

    def _updateBombMarker(self, vehicleID, stateID, duration):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive():
            return
        else:
            markerID = self._markers[vehicleID].getMarkerID()
            self._updateMarkerTimer(vehicleID, markerID, duration, stateID, True)
            return

    def _setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        markerID = marker.getMarkerID()
        vType = vInfo.vehicleType
        vehId = vInfo.vehicleID
        if avatar_getter.isVehiclesColorized():
            guiPropsName = 'team{}'.format(vInfo.team)
        else:
            if avatar_getter.isObserver():
                arenaDP = self.sessionProvider.getArenaDP()
                obsVehId = BigWorld.player().observedVehicleID
                if vehId == obsVehId or arenaDP.isSquadMan(vehId, arenaDP.getVehicleInfo(obsVehId).prebattleID):
                    guiProps = PLAYER_GUI_PROPS.squadman
            guiPropsName = guiProps.name()
        if self._isSquadIndicatorEnabled and vInfo.squadIndex:
            squadIndex = vInfo.squadIndex
        else:
            squadIndex = 0
        hunting = VehicleActions.isHunting(vInfo.events)
        classTag = vType.classTag
        if 'event_boss' in vType.tags:
            classTag = 'boss'
        isCarrier = False
        if vInfo.gameModeSpecific.getValue(EventKeys.BOMB_INDEX.value):
            isCarrier = True
        self._invokeMarker(markerID, 'setIsBombCarrier', isCarrier)
        self._invokeMarker(markerID, 'setVehicleInfo', classTag, vType.iconPath, nameParts.vehicleName, vType.level, nameParts.playerFullName, nameParts.playerName, nameParts.clanAbbrev, nameParts.regionCode, vType.maxHealth, guiPropsName, hunting, squadIndex, backport.text(R.strings.ingame_gui.stun.seconds()))
        self._invokeMarker(markerID, 'update')


class EventEventBusPlugin(EventBusPlugin):

    def start(self):
        super(EventEventBusPlugin, self).start()
        spawnCtrl = self.sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onShowSpawnPoints += self._onShowSpawnPoints
            spawnCtrl.onCloseSpawnPoints += self._onCloseSpawnPoints
        return

    def stop(self):
        spawnCtrl = self.sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onShowSpawnPoints -= self._onShowSpawnPoints
            spawnCtrl.onCloseSpawnPoints -= self._onCloseSpawnPoints
        super(EventEventBusPlugin, self).stop()
        return

    def _onShowSpawnPoints(self, *_):
        self._parentObj.setVisible(False)

    def _onCloseSpawnPoints(self, *_):
        self._parentObj.setVisible(True)
