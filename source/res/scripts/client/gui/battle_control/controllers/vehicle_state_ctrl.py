# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicle_state_ctrl.py
from functools import partial
import weakref
import BigWorld
import BattleReplay
import Event
import SoundGroups
import nations
from BattleReplay import CallbackDataNames
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, VEHICLE_WAINING_INTERVAL, VEHICLE_UPDATE_INTERVAL, BATTLE_CTRL_ID, DEVICE_STATE_NORMAL
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.utils.TimeInterval import TimeInterval
from shared_utils import first
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class _StateHandler(object):
    __slots__ = ('__updater',)

    def __init__(self, updater):
        super(_StateHandler, self).__init__()
        self.__updater = weakref.proxy(updater)

    def clear(self):
        self.__updater = None
        return

    def handleStateChange(self, state, value):
        return False

    def notifyStateChanged(self, state, value):
        self.__updater.notifyStateChanged(state, value)

    def _invalidate(self, vehicle):
        pass

    def __call__(self, vehicle):
        return self._invalidate(vehicle)


class _SpeedStateHandler(_StateHandler):
    __slots__ = ('__speed', '__maxSpeed', '__isOwnVehicle')

    def __init__(self, updater, isOwnVehicle):
        super(_SpeedStateHandler, self).__init__(updater)
        self.__speed = 0
        self.__maxSpeed = 0
        self.__isOwnVehicle = isOwnVehicle

    def clear(self):
        self.__speed = 0
        self.__maxSpeed = 0
        self.__isOwnVehicle = False

    def _invalidate(self, vehicle):
        fwdSpeedLimit, bckwdSpeedLimit = vehicle.typeDescriptor.physics['speedLimits']
        if self.__isOwnVehicle:
            player = BigWorld.player()
            if player is None:
                return ()
            if player.isVehicleAlive:
                speed, _ = player.getOwnVehicleSpeeds()
            else:
                speed = 0
        else:
            try:
                speed = vehicle.speedInfo.value[0]
            except (AttributeError, IndexError, ValueError):
                LOG_CURRENT_EXCEPTION()
                return ()

            speed = max(min(speed, fwdSpeedLimit), -bckwdSpeedLimit)
        speed = self._formatSpeed(speed)
        states = []
        if self.__speed != speed:
            self.__speed = speed
            states.append((VEHICLE_VIEW_STATE.SPEED, speed))
        return states

    @staticmethod
    def _formatSpeed(speed):
        return int(speed * 3.6)


class _HealthStateHandler(_StateHandler):
    __slots__ = ('__health',)

    def __init__(self, updater):
        super(_HealthStateHandler, self).__init__(updater)
        self.__health = 0

    def clear(self):
        self.__health = 0

    def _invalidate(self, vehicle):
        states = []
        health = vehicle.health
        if self.__health != health:
            self.__health = health
            states.append((VEHICLE_VIEW_STATE.HEALTH, health))
        return states


class _VehicleUpdater(object):

    def __init__(self, vehCtrl, vehicleID):
        super(_VehicleUpdater, self).__init__()
        self.__isAlive = True
        self.__handlers = None
        self.__ctrl = weakref.proxy(vehCtrl)
        self.__vehicleID = vehicleID
        self.__updateTI = None
        self._setUpHandlers()
        return

    def handleStateChange(self, state, value):
        isStateHandled = False
        for handler in self.__handlers:
            isStateHandled |= handler.handleStateChange(state, value)

        return isStateHandled

    def switch(self, vehicleID):
        self.clear()
        self.__vehicleID = vehicleID
        self._setUpHandlers()
        return self

    def start(self):
        if self.__updateTI is None:
            self.__updateTI = TimeInterval(VEHICLE_UPDATE_INTERVAL, self, '_update')
        self.__updateTI.start()
        return

    def stop(self):
        if self.__updateTI is not None:
            self.__updateTI.stop()
            self.__updateTI = None
        return

    def clear(self):
        self.stop()
        if self.__handlers is not None:
            for handler in self.__handlers:
                handler.clear()

            self.__handlers = None
        self.__vehicleID = None
        self.__isAlive = True
        return

    def updateOnce(self):
        self._update()

    def notifyStateChanged(self, state, value):
        self.__ctrl.notifyStateChanged(state, value)

    def _update(self):
        states = []
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is not None and vehicle.isStarted:
            if not vehicle.isAlive() and self.__isAlive:
                self.__isAlive = False
                if vehicle.health > 0 and not vehicle.isCrewActive:
                    states.append((VEHICLE_VIEW_STATE.CREW_DEACTIVATED, 0))
                else:
                    states.append((VEHICLE_VIEW_STATE.DESTROYED, 0))
            for handler in self.__handlers:
                newStates = handler(vehicle)
                states.extend(newStates)

        for item in states:
            self.notifyStateChanged(*item)

        return

    def _setUpHandlers(self):
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is not None:
            isPlayerVehicle = vehicle.isPlayerVehicle
            if isPlayerVehicle:
                if not vehicle.isAlive():
                    self.__handlers = (_SpeedStateHandler(self, True),)
                else:
                    self.__handlers = (_SpeedStateHandler(self, True),)
            else:
                self.__handlers = (_HealthStateHandler(self), _SpeedStateHandler(self, False))
        return


class VehicleStateController(IBattleController):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VehicleStateController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onVehicleStateUpdated = Event.Event(self.__eManager)
        self.onVehicleControlling = Event.Event(self.__eManager)
        self.onPostMortemSwitched = Event.Event(self.__eManager)
        self.onRespawnBaseMoving = Event.Event(self.__eManager)
        self.onUpdateScenarioTimer = Event.Event(self.__eManager)
        self.__cachedStateValues = {}
        self.__cachedRepairingCallbackID = None
        self.__waitingTI = TimeInterval(VEHICLE_WAINING_INTERVAL, self, '_waiting')
        self.__vehicleID = 0
        self.__updater = None
        self.__isRqToSwitch = False
        self.__isInPostmortem = False
        self.__needInvalidate = False
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.OBSERVED_VEHICLE_STATE

    def startControl(self):
        pass

    def stopControl(self):
        if self.__waitingTI is not None:
            self.__waitingTI.stop()
            self.__waitingTI = None
        if self.__updater is not None:
            self.__updater.clear()
            self.__updater = None
        self.__vehicleID = 0
        self.__isRqToSwitch = False
        self.__isInPostmortem = False
        self.__eManager.clear()
        self.__cachedStateValues.clear()
        if self.__cachedRepairingCallbackID:
            BigWorld.cancelCallback(self.__cachedRepairingCallbackID)
        return

    @property
    def isInPostmortem(self):
        return self.__isInPostmortem

    def setPlayerVehicle(self, vehicleID):
        isEventBattle = self.guiSessionProvider.arenaVisitor.gui.isEventBattle()
        if isEventBattle:
            self.__cachedStateValues.clear()
            self.notifyStateChanged(VEHICLE_VIEW_STATE.SWITCHING, 0)
        self.notifyStateChanged(VEHICLE_VIEW_STATE.PLAYER_INFO, vehicleID)
        self.__vehicleID = vehicleID
        self.__updater = _VehicleUpdater(self, self.__vehicleID)
        self.__waitingTI.start()

    def getControllingVehicle(self):
        vehicle = None
        if self.__vehicleID:
            vehicle = BigWorld.entity(self.__vehicleID)
        return vehicle

    def getControllingVehicleID(self):
        return self.__vehicleID

    def notifyStateChanged(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.DEVICES:
            self.__cachedStateValues.setdefault(stateID, {})
            deviceName = value[0]
            cachedRepairingDeviceName = first(self.__cachedStateValues.get(VEHICLE_VIEW_STATE.REPAIRING, ()))
            if cachedRepairingDeviceName == deviceName and value[2] == DEVICE_STATE_NORMAL:
                self.__cachedStateValues.pop(VEHICLE_VIEW_STATE.REPAIRING)
            self.__cachedStateValues[stateID][deviceName] = value
        else:
            if stateID == VEHICLE_VIEW_STATE.REPAIRING:
                if self.__cachedRepairingCallbackID:
                    BigWorld.cancelCallback(self.__cachedRepairingCallbackID)
                BigWorld.callback(value[2], partial(self.__cachedRepairingCallback, value))
            self.__cachedStateValues[stateID] = value
        self.onVehicleStateUpdated(stateID, value)

    def __cachedRepairingCallback(self, value):
        self.__cachedRepairingCallbackID = None
        if self.__cachedStateValues.get(VEHICLE_VIEW_STATE.REPAIRING) == value:
            self.__cachedStateValues.pop(VEHICLE_VIEW_STATE.REPAIRING)
        return

    def getStateValue(self, stateID):
        if stateID in self.__cachedStateValues:
            if stateID == VEHICLE_VIEW_STATE.DEVICES:
                value = self.__cachedStateValues[stateID].values()
            else:
                value = self.__cachedStateValues[stateID]
            return value
        else:
            return None

    def refreshVehicleStateValue(self, stateID):
        if stateID in self.__cachedStateValues:
            self.onVehicleStateUpdated(stateID, self.__cachedStateValues[stateID])

    def invalidate(self, state, value, vehicleID=0):
        if vehicleID != 0 and vehicleID != self.__vehicleID:
            return
        else:
            isStateChangeHandled = False
            if self.__isRqToSwitch and self.__waitingTI.isStarted():
                self._waiting()
            if self.__updater is not None:
                isStateChangeHandled = self.__updater.handleStateChange(state, value)
            if not isStateChangeHandled:
                self.notifyStateChanged(state, value)
            return

    def switchToPostmortem(self, noRespawnPossible, respawnAvailable):
        self.__isRqToSwitch = False
        if avatar_getter.getPlayerVehicleID() == self.__vehicleID:
            if self.__updater is not None:
                self.__updater.stop()
                self.__updater.updateOnce()
        self.__isInPostmortem = True
        self.onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        return

    def switchToOther(self, vehicleID):
        if vehicleID is None:
            self.notifyStateChanged(VEHICLE_VIEW_STATE.SWITCHING, 0)
            self.__needInvalidate = True
            return
        elif self.__vehicleID == vehicleID and not self.__needInvalidate:
            return
        else:
            self.__needInvalidate = False
            self.notifyStateChanged(VEHICLE_VIEW_STATE.SWITCHING, vehicleID)
            self.__waitingTI.stop()
            if self.__updater:
                self.__updater.stop()
            self.__vehicleID = vehicleID
            self.__isRqToSwitch = True
            self.notifyStateChanged(VEHICLE_VIEW_STATE.PLAYER_INFO, self.__vehicleID)
            self.__cachedStateValues.clear()
            self.__waitingTI.start()
            return

    def movingToRespawn(self):
        self.__isInPostmortem = False
        self.notifyStateChanged(VEHICLE_VIEW_STATE.SWITCHING, 0)
        self.onRespawnBaseMoving()
        self.__cachedStateValues.clear()

    def updateScenarioTimer(self, waitTime, alarmTime, visible):
        self.onUpdateScenarioTimer(waitTime, alarmTime, visible)

    def _waiting(self):
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is not None and vehicle.isStarted:
            self.__waitingTI.stop()
            self._setup(vehicle)
        return

    def _setup(self, vehicle):
        if self.__updater is not None:
            self.__updater = self.__updater.switch(self.__vehicleID)
        if self.__isRqToSwitch:
            nationID = vehicle.typeDescriptor.type.id[0]
            notifications = avatar_getter.getSoundNotifications()
            if notifications is not None and not self.guiSessionProvider.arenaVisitor.gui.isEventBattle():
                notifications.clear()
            SoundGroups.g_instance.soundModes.setCurrentNation(nations.NAMES[nationID])
        self.onVehicleControlling(vehicle)
        if self.__updater is not None:
            self.__updater.start()
        return


class VehicleStateReplayRecorder(VehicleStateController):

    def invalidate(self, state, value, vehicleID=0):
        if state in VEHICLE_VIEW_STATE.CLIENT_ONLY:
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.CLIENT_VEHICLE_STATE_GROUP.format(state), (state, value, vehicleID))
        super(VehicleStateReplayRecorder, self).invalidate(state, value, vehicleID)


class VehicleStateReplayPlayer(VehicleStateController):

    def startControl(self):
        super(VehicleStateReplayPlayer, self).startControl()
        for state in VEHICLE_VIEW_STATE.CLIENT_ONLY:
            BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.CLIENT_VEHICLE_STATE_GROUP.format(state), self.invalidate)

    def stopControl(self):
        for state in VEHICLE_VIEW_STATE.CLIENT_ONLY:
            BattleReplay.g_replayCtrl.delDataCallback(CallbackDataNames.CLIENT_VEHICLE_STATE_GROUP.format(state), self.invalidate)

        super(VehicleStateReplayPlayer, self).stopControl()


def createCtrl(setup):
    if setup.isReplayRecording:
        ctrl = VehicleStateReplayRecorder()
    elif setup.isReplayPlaying:
        ctrl = VehicleStateReplayPlayer()
    else:
        ctrl = VehicleStateController()
    return ctrl
