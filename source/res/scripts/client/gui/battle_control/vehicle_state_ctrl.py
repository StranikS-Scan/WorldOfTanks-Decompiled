# Embedded file name: scripts/client/gui/battle_control/vehicle_state_ctrl.py
import BigWorld
import Event
import SoundGroups
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, VEHICLE_WAINING_INTERVAL, VEHICLE_UPDATE_INTERVAL
from gui.shared.utils.TimeInterval import TimeInterval
import nations

class _PlayerVehicleUpdater(object):

    def __init__(self):
        super(_PlayerVehicleUpdater, self).__init__()
        self.clear()

    def clear(self):
        self.__speed = 0

    def switch(self, isPlayer):
        if isPlayer:
            self.clear()
            result = self
        else:
            result = _OtherVehicleUpdater()
        return result

    def update(self, vehicleID, _):
        player = BigWorld.player()
        if player is None:
            return
        else:
            states = None
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is not None and vehicle.isStarted:
                speed, _ = player.getOwnVehicleSpeeds()
                speed = int(speed * 3.6)
                if self.__speed != speed:
                    self.__speed = speed
                    states = [(VEHICLE_VIEW_STATE.SPEED, speed)]
            return states


class _OtherVehicleUpdater(object):

    def __init__(self):
        super(_OtherVehicleUpdater, self).__init__()
        self.clear()

    def clear(self):
        self.__speed = 0
        self.__health = 0

    def switch(self, isPlayer):
        if isPlayer:
            result = _PlayerVehicleUpdater()
        else:
            self.clear()
            result = self
        return result

    def update(self, vehicleID, ticker):
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is not None:
            states = []
            health = vehicle.health
            if self.__health != health:
                self.__health = health
                states.append((VEHICLE_VIEW_STATE.HEALTH, health))
            if vehicle.isStarted:
                try:
                    speed = vehicle.filter.speedInfo.value[0]
                    fwdSpeedLimit, bckwdSpeedLimit = vehicle.typeDescriptor.physics['speedLimits']
                    speed = max(min(speed, fwdSpeedLimit), -bckwdSpeedLimit)
                    speed = int(speed * 3.6)
                    if self.__speed != speed:
                        self.__speed = speed
                        states.append((VEHICLE_VIEW_STATE.SPEED, speed))
                except (AttributeError, IndexError, ValueError):
                    LOG_CURRENT_EXCEPTION()
                    LOG_ERROR('Can not update speed. Stop')
                    ticker.stop()

            if not vehicle.isAlive():
                states.append((VEHICLE_VIEW_STATE.DESTROYED, None))
                ticker.stop()
        else:
            states = None
        return states


class VehicleStateController(object):

    def __init__(self):
        super(VehicleStateController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onVehicleStateUpdated = Event.Event(self.__eManager)
        self.onVehicleControlling = Event.Event(self.__eManager)
        self.onPostMortemSwitched = Event.Event(self.__eManager)
        self.onRespawnBaseMoving = Event.Event(self.__eManager)
        self.__waitingTI = TimeInterval(VEHICLE_WAINING_INTERVAL, self, '_waiting')
        self.__updateTI = TimeInterval(VEHICLE_UPDATE_INTERVAL, self, '_update')
        self.__vehicleID = 0
        self.__updater = _PlayerVehicleUpdater()
        self.__isRqToSwitch = False

    def clear(self):
        if self.__waitingTI:
            self.__waitingTI.stop()
            self.__waitingTI = None
        if self.__updateTI:
            self.__updateTI.stop()
            self.__updateTI = None
        self.__vehicleID = 0
        self.__isRqToSwitch = False
        self.__updater = None
        self.__eManager.clear()
        return

    def setPlayerVehicle(self, vehicleID):
        self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.PLAYER_INFO, vehicleID)
        self.__vehicleID = vehicleID
        self.__waitingTI.start()

    def getControllingVehicle(self):
        vehicle = None
        if self.__vehicleID:
            vehicle = BigWorld.entity(self.__vehicleID)
        return vehicle

    def invalidate(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__updateTI.stop()
        self.onVehicleStateUpdated(state, value)

    def switchToPostmortem(self):
        self.__isRqToSwitch = False
        if avatar_getter.getPlayerVehicleID() == self.__vehicleID:
            self.__waitingTI.stop()
            self.__updateTI.stop()
        self.onPostMortemSwitched()

    def switchToAnother(self, vehicleID):
        if self.__vehicleID == vehicleID or vehicleID is None:
            return
        else:
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.SWITCHING, self.__vehicleID)
            if self.__updater:
                self.__updater.clear()
            self.__waitingTI.stop()
            self.__updateTI.stop()
            self.__vehicleID = vehicleID
            self.__isRqToSwitch = True
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.PLAYER_INFO, self.__vehicleID)
            self.__waitingTI.start()
            return

    def movingToRespawn(self):
        self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.SWITCHING, 0)
        self.onRespawnBaseMoving()

    def _waiting(self):
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is not None:
            self.__waitingTI.stop()
            self._setup(vehicle)
        return

    def _update(self):
        states = self.__updater.update(self.__vehicleID, self.__updateTI)
        if states is not None:
            for item in states:
                self.onVehicleStateUpdated(*item)

        return

    def _setup(self, vehicle):
        self.__updater = self.__updater.switch(vehicle.isPlayer)
        if self.__isRqToSwitch:
            nationID = vehicle.typeDescriptor.type.id[0]
            notifications = avatar_getter.getSoundNotifications()
            if notifications:
                notifications.clear()
            SoundGroups.g_instance.soundModes.setCurrentNation(nations.NAMES[nationID])
        self.onVehicleControlling(vehicle)
        if not vehicle.isAlive():
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.DESTROYED, None)
        else:
            self.__updateTI.start()
        return


class VehicleStateReplayRecorder(VehicleStateController):

    def invalidate(self, state, value):
        if state == VEHICLE_VIEW_STATE.CRUISE_MODE:
            import BattleReplay
            BattleReplay.g_replayCtrl.onSetCruiseMode(value)
        super(VehicleStateReplayRecorder, self).invalidate(state, value)


def createCtrl(isReplayRecording):
    if isReplayRecording:
        ctrl = VehicleStateReplayRecorder()
    else:
        ctrl = VehicleStateController()
    return ctrl
