# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/vehicle_state_ctrl.py
import math
import weakref
import BigWorld
import Event
import SoundGroups
import nations
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, VEHICLE_WAINING_INTERVAL, VEHICLE_UPDATE_INTERVAL
from gui.shared.utils.TimeInterval import TimeInterval
_RPM_DELTA_THRESHOLD = 0.01
_STOPPED_ENGINE_GEAR = 127
_VEHICLE_ANIM_DURATION = 0.5
_RPM_SHIFT = 0.3
_RPM_MAX_VALUE = 1.0
_RPM_SHIFT_FACTOR = 1.0 - _RPM_SHIFT / _RPM_MAX_VALUE

class _StateHandler(object):
    """
    The class determines a high-level interface and provides the base logic to track vehicle state
    changes and to emit appropriate events. The class must be used as a parent class for all custom
    handlers and must not be instantiated directly.
    The main goal of a custom state handler is to encapsulate logic of state change processing.
    The custom events are used by _VehicleUpdater to track states changes in the same way and to
    fire appropriate events periodically. For details please see _VehicleUpdater class description.
    """
    __slots__ = ('__updater',)

    def __init__(self, updater):
        """
        Constructor.
        Just stores a weakref to the updater (parent maintaining this handler). The updater is
        used in order to provide API to send vehicle state changes events directly from a custom
        handler.
        
        :param updater: An instance of _VehicleUpdater class, that creates this handler.
        """
        super(_StateHandler, self).__init__()
        self.__updater = weakref.proxy(updater)

    def clear(self):
        """
        Clears internal state and frees resources. The method is invoked when the _VehicleUpdater
        is cleared.
        :return:
        """
        self.__updater = None
        return

    def handleStateChange(self, state, value):
        """
        Represents a hook to catch states changes before the vehicle state controller propagates
        them to subscribers. Through this method it is possible to prohibit delivering of state
        changes to subscribers by the controller and to get full control over state change
        processing.
        
        :param state: A state listed within VEHICLE_VIEW_STATE
        :param value: State value
        :return: True if the event should not be sent to subscribers by the vehicle state controller.
                False, otherwise.
        """
        return False

    def onVehicleStateUpdated(self, state, value):
        """
        The helper method that can be used to notify subscribers about a change of vehicle's state.
        
        :param state: A state listed within VEHICLE_VIEW_STATE
        :param value: State value.
        """
        self.__updater.onVehicleStateUpdated(state, value)

    def _invalidate(self, vehicle):
        """
        The derived classes should override this method to determine actual vehicle state and
        to expose them to updater. The method is invoked by the updater through equal time
        intervals. Thus by overriding this method you can notify subscribers about state changes
        through equal time intervals. To get full control over state changes, it is required to
        override handleStateChange and this method.
        
        :param vehicle: A reference to Vehicle(BW entity) object.
        :return: A list of (state, value) tuples (states changes)
        """
        pass

    def __call__(self, vehicle):
        return self._invalidate(vehicle)


class _RpmStateHandler(_StateHandler):
    """
    The class that encapsulates logic of processing state of tachometer indicator
    (VEHICLE_VIEW_STATE.RPM).
    Right now, rpm value is available only for users own vehicle. For all other vehicles the rpm is
    determined based on the current gear and vehicle speed. To improve performance, the appropriate
    event is caught and sent directly through equal time intervals. Also introduced such concept as
    'rpm threshold'. The main goal of the rpm threshold is to avoid redundant UI updates.
    """
    __slots__ = ('__rpm', '__visibleRpm', '__simMode', '__speedLimits')

    def __init__(self, updater, vehicle):
        """
        Constructor.
        
        :param updater: An instance of _VehicleUpdater class(handler's parent)
        :param vehicle: Vehicle to be tracked.
        :return:
        """
        super(_RpmStateHandler, self).__init__(updater)
        self.__rpm = 0
        self.__visibleRpm = 0
        self.__simMode = not vehicle.isPlayerVehicle
        self.__speedLimits = vehicle.typeDescriptor.physics['speedLimits']

    def clear(self):
        """
        Clears internal state and frees resources.
        """
        self.__rpm = 0
        self.__visibleRpm = 0
        self.__simMode = False
        self.__speedLimits = None
        return

    def handleStateChange(self, state, value):
        """
        Tracks RPM changes and stores them.
        
        :param state: A state listed within VEHICLE_VIEW_STATE
        :param value: State value.
        :return: True for VEHICLE_VIEW_STATE.RPM state changes and False for all others.
        """
        if state == VEHICLE_VIEW_STATE.RPM:
            self.__rpm = value
            return True
        return False

    def _invalidate(self, vehicle):
        """
        Determines whether rpm change is bigger than the threshold since the last update (in other
        words, compares the visible value with the current value).
        
        :param vehicle: A reference to Vehicle(BW entity) object.
        :return: Not empty list if the change is bigger than threshold.
        """
        states = []
        if self.__simMode:
            self.__simRpm(vehicle)
        scaledRmp = self.__scaleRmp(self.__rpm, vehicle)
        if abs(scaledRmp - self.__visibleRpm) > _RPM_DELTA_THRESHOLD:
            self.__visibleRpm = scaledRmp
            states.append((VEHICLE_VIEW_STATE.RPM, self.__visibleRpm))
        return states

    def __simRpm(self, vehicle):
        """
        Updates current rpm based on vehicle's speed and the current gear. Used algorithm from
        engine_states.py (see refresh method)
        
        :param vehicle: A reference to Vehicle(BW entity) object.
        """
        try:
            vehicleSpeed = vehicle.filter.speedInfo.value[0]
            speedRangePerGear = (self.__speedLimits[0] + self.__speedLimits[1]) / 3.0
        except (AttributeError, IndexError, ValueError):
            LOG_CURRENT_EXCEPTION()
            return

        gearNum = math.ceil(math.floor(math.fabs(vehicleSpeed) * 50.0) / 50.0 / speedRangePerGear)
        if gearNum:
            self.__rpm = math.fabs(1.0 + (vehicleSpeed - gearNum * speedRangePerGear) / speedRangePerGear)
        else:
            self.__rpm = 0.0

    def __scaleRmp(self, rpm, vehicle):
        """
        Calculates a new value for shifted rpm scale (In moving, rpm scale is shifted from
        0.0-1.2 to 0.3-1.2).
        
        :param rpm: True rpm value to be converted.
        :param vehicle: A reference to Vehicle(BW entity) object.
        """
        return _RPM_SHIFT + rpm * _RPM_SHIFT_FACTOR if vehicle.appearance.gear > 0 and rpm < _RPM_MAX_VALUE else rpm


class _EngineStateHandler(_StateHandler):
    """
    The class provides logic to track engine state changes and vehicle movement changes.
    All logic is based on changes of the current gear.
    """
    __slots__ = ('__weakref__', '__gear', '__vehMoveAnimTimer', '__engineStartAnimTimer')

    def __init__(self, updater, vehicle):
        """
        Constructor. Initializes internal variables based on vehicle state.
        
        :param updater: An instance of _VehicleUpdater class, that creates this handler.
        :param vehicle: Vehicle to be tracked.
        :return:
        """
        super(_EngineStateHandler, self).__init__(updater)
        self.__gear = vehicle.appearance.gear if vehicle is not None else _STOPPED_ENGINE_GEAR
        self.__vehMoveAnimTimer = TimeInterval(_VEHICLE_ANIM_DURATION, self, '_stopVehMoveAnim')
        self.__engineStartAnimTimer = TimeInterval(_VEHICLE_ANIM_DURATION, self, '_stopEngineStartAnim')
        return

    def clear(self):
        """
        Resets internal variables.
        """
        self.__gear = _STOPPED_ENGINE_GEAR
        self._stopVehMoveAnim()
        self._stopEngineStartAnim()

    def _invalidate(self, vehicle):
        """
        The method determines whether one of the following events has occurred and exposes the
        appropriate state change to the updater:
            1. Vehicle starts moving.
            2. Engine is started.
        By these events, appropriate animations are run on UI. To stop animations appropriate state
        change event is sent in _VEHICLE_ANIM_DURATION time. Note that animation duration depends
        on sound effect (track length). But right now there is no way to determine effect duration.
        Therefore for all vehicles the same constant is used.
        
        :param vehicle: A reference to the tracked vehicle(BW entity).
        :return: The state change if any. Otherwise an empty list.
        """
        states = []
        gear = vehicle.appearance.gear
        if self.__gear != gear:
            if not self.__gear and gear > 0:
                if not self.__vehMoveAnimTimer.isStarted():
                    states.append((VEHICLE_VIEW_STATE.VEHICLE_MOVEMENT_STATE, True))
                    self.__vehMoveAnimTimer.start()
            elif self.__gear == _STOPPED_ENGINE_GEAR and gear >= 0:
                if not self.__engineStartAnimTimer.isStarted():
                    states.append((VEHICLE_VIEW_STATE.VEHICLE_ENGINE_STATE, True))
                    self.__engineStartAnimTimer.start()
            elif self.__gear > 0 and not self.__gear:
                pass
            elif self.__gear >= 0 and gear == _STOPPED_ENGINE_GEAR:
                pass
            self.__gear = gear
        return states

    def _stopVehMoveAnim(self):
        """
        Stops 'vehicle start' animation by sending the appropriate event.
        """
        if self.__vehMoveAnimTimer.isStarted():
            self.__vehMoveAnimTimer.stop()
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.VEHICLE_MOVEMENT_STATE, False)

    def _stopEngineStartAnim(self):
        """
        Stops 'engine start' animation by sending the appropriate event.
        """
        if self.__engineStartAnimTimer.isStarted():
            self.__engineStartAnimTimer.stop()
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.VEHICLE_ENGINE_STATE, False)


class _SpeedStateHandler(_StateHandler):
    """
    The class encapsulates logic of tracking of vehicle speed changes (current speed and
    max speed).
    """
    __slots__ = ('__speed', '__maxSpeed', '__isOwnVehicle')

    def __init__(self, updater, isOwnVehicle):
        """
        Constructor. Initializes internal variables.
        
        :param updater: An instance of _VehicleUpdater class, that creates this handler.
        :param isOwnVehicle: Indicates whether the tracked vehicle is user's vehicle.
        """
        super(_SpeedStateHandler, self).__init__(updater)
        self.__speed = 0
        self.__maxSpeed = 0
        self.__isOwnVehicle = isOwnVehicle

    def clear(self):
        """
        Resets internal variables.
        """
        self.__speed = 0
        self.__maxSpeed = 0
        self.__isOwnVehicle = False

    def _invalidate(self, vehicle):
        """
        Determines whether the current speed or max speed is changed form the last update and
        exposes the appropriate event(s) to the updater.
        Note that to determine the current speed two different algorithm are used depending on
        whether the current tracked vehicle is own vehicle.
        
        :param vehicle: A reference to the tracked vehicle(BW entity).
        :return: States changes if any. Otherwise an empty list.
        """
        fwdSpeedLimit, bckwdSpeedLimit = vehicle.typeDescriptor.physics['speedLimits']
        if self.__isOwnVehicle:
            player = BigWorld.player()
            if player is None:
                return ()
            speed, _ = player.getOwnVehicleSpeeds()
        else:
            try:
                speed = vehicle.filter.speedInfo.value[0]
            except (AttributeError, IndexError, ValueError):
                LOG_CURRENT_EXCEPTION()
                return ()

            speed = max(min(speed, fwdSpeedLimit), -bckwdSpeedLimit)
        speed = self._formatSpeed(speed)
        states = []
        if self.__speed != speed:
            self.__speed = speed
            states.append((VEHICLE_VIEW_STATE.SPEED, speed))
        maxSpeed = self._formatSpeed(-bckwdSpeedLimit if speed < 0 else fwdSpeedLimit)
        if maxSpeed != self.__maxSpeed:
            self.__maxSpeed = maxSpeed
            states.append((VEHICLE_VIEW_STATE.MAX_SPEED, maxSpeed))
        return states

    @staticmethod
    def _formatSpeed(speed):
        """
        # Converts m/sec to km/h.
        :param speed: Speed in m/sec
        :return: Speed in km/h
        """
        return int(speed * 3.6)


class _HealthStateHandler(_StateHandler):
    """
    The class encapsulates logic of tracking of vehicle health changes.
    """
    __slots__ = '__health'

    def __init__(self, updater):
        """
        Constructor. Initializes internal variables.
        
        :param updater: An instance of _VehicleUpdater class, that creates this handler.
        """
        super(_HealthStateHandler, self).__init__(updater)
        self.__health = 0

    def clear(self):
        """
        Resets internal variables.
        """
        self.__health = 0

    def _invalidate(self, vehicle):
        """
        Determines whether vehicle health is changed form the last update and exposes the
        VEHICLE_VIEW_STATE.HEALTH state change event to the updater.
        
        :param vehicle: A reference to the tracked vehicle(BW entity).
        :return: State change or an empty list.
        """
        states = []
        health = vehicle.health
        if self.__health != health:
            self.__health = health
            states.append((VEHICLE_VIEW_STATE.HEALTH, health))
        return states


class _VehicleUpdater(object):
    """
    The class implements logic for tracking changes of vehicle parameters in equal time intervals.
    It encapsulates different algorithms of tracking based on vehicle type. The inner logic is
    based on the custom state handlers (classes derived from _StateHandler).
    """

    def __init__(self, vehCtrl, vehicleID):
        """
        Constructor. Initializes internal variables.
        
        :param vehCtrl: Reference to vehicle state controller owning this updater.
        :param vehicleID: Unique identifier of vehicle to be tracked
        """
        super(_VehicleUpdater, self).__init__()
        self.__handlers = None
        self.__ctrl = weakref.proxy(vehCtrl)
        self.__vehicleID = vehicleID
        self.__updateTI = None
        self._setUpHandlers()
        return

    def handleStateChange(self, state, value):
        """
        Represents a hook to catch states changes before the vehicle state controller propagates
        them to subscribers. Redirects the call to each handler to perform required logic.
        
        :param state: A state listed within VEHICLE_VIEW_STATE
        :param value: State value
        :return: True if any handler returns True. Otherwise - False.
        """
        isStateHandled = False
        for handler in self.__handlers:
            isStateHandled |= handler.handleStateChange(state, value)

        return isStateHandled

    def switch(self, vehicleID):
        """
        Switches the updater to another vehicle: reset internal states and handlers.
        
        :param vehicleID: Unique identifier of a new vehicle that will be tracked
        """
        self.clear()
        self.__vehicleID = vehicleID
        self._setUpHandlers()
        return self

    def start(self):
        """
        Sets up and starts the timer to invalidate handlers.
        """
        if self.__updateTI is None:
            self.__updateTI = TimeInterval(VEHICLE_UPDATE_INTERVAL, self, '_update')
        self.__updateTI.start()
        return

    def stop(self):
        """
        Stops and clears running timer (if any).
        """
        if self.__updateTI is not None:
            self.__updateTI.stop()
            self.__updateTI = None
        return

    def clear(self):
        """
        Clears internal variables and stops timer.
        """
        self.stop()
        if self.__handlers is not None:
            for handler in self.__handlers:
                handler.clear()

            self.__handlers = None
        self.__vehicleID = None
        return

    def onVehicleStateUpdated(self, state, value):
        """
        The helper method to provide handler ability to notify subscribers about changes of
        vehicle's states through the vehicle state controller.
        
        :param state: A state listed within VEHICLE_VIEW_STATE
        :param value: State value.
        """
        self.__ctrl.onVehicleStateUpdated(state, value)

    def _update(self):
        """
        Callback on timer tick event. Initiates invalidation of all handlers, get all states
        changes and redirects them to the vehicle state controller by emitting appropriate events.
        """
        states = []
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is not None and vehicle.isStarted:
            if not vehicle.isAlive():
                states.append((VEHICLE_VIEW_STATE.DESTROYED, None))
                self.stop()
            else:
                for handler in self.__handlers:
                    newStates = handler(vehicle)
                    states.extend(newStates)

        for item in states:
            self.onVehicleStateUpdated(*item)

        return

    def _setUpHandlers(self):
        """
        Determines a list of handlers based on vehicle type and sets up them.
        """
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is not None:
            isPlayerVehicle = vehicle.isPlayerVehicle
            if isPlayerVehicle:
                self.__handlers = (_SpeedStateHandler(self, True), _RpmStateHandler(self, vehicle), _EngineStateHandler(self, vehicle))
            else:
                self.__handlers = (_HealthStateHandler(self),
                 _SpeedStateHandler(self, False),
                 _RpmStateHandler(self, vehicle),
                 _EngineStateHandler(self, vehicle))
        return


class VehicleStateController(object):
    """
    Class of controller that tracks specified vehicle on arena. At any time there is only one
    instance of this class. When player's own vehicle is destroyed, controller can track other
    vehicles on player's team.
    The main goal of the controller to combine all knowledge about vehicle state changes and to
    notify subscribers about that through appropriate events. The controller declares public
    interface to know about changes. Triggers call these method to notify the controller about
    specific changes that occur outside client. Also there is a list of changes that are triggered
    directly by the controller via the updater. The updater tracks those parameters on which there
    are no outside triggers or when required to control triggering frequency.
    """

    def __init__(self):
        """
        Constructor. Initializes internal variables.
        """
        super(VehicleStateController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onVehicleStateUpdated = Event.Event(self.__eManager)
        self.onVehicleControlling = Event.Event(self.__eManager)
        self.onPostMortemSwitched = Event.Event(self.__eManager)
        self.onRespawnBaseMoving = Event.Event(self.__eManager)
        self.__waitingTI = TimeInterval(VEHICLE_WAINING_INTERVAL, self, '_waiting')
        self.__vehicleID = 0
        self.__updater = None
        self.__isRqToSwitch = False
        return

    def clear(self):
        """
        Clears internal variables and stops timers.
        :return:
        """
        if self.__waitingTI:
            self.__waitingTI.stop()
            self.__waitingTI = None
        if self.__updater is not None:
            self.__updater.clear()
            self.__updater = None
        self.__vehicleID = 0
        self.__isRqToSwitch = False
        self.__eManager.clear()
        return

    def setPlayerVehicle(self, vehicleID):
        """
        Sets ID of player's own vehicle.
        
        :param vehicleID: ID of vehicle entity
        """
        self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.PLAYER_INFO, vehicleID)
        self.__vehicleID = vehicleID
        self.__updater = _VehicleUpdater(self, self.__vehicleID)
        self.__waitingTI.start()

    def getControllingVehicle(self):
        """
        Gets entity of vehicle that is controlling.
        
        :return: entity of vehicle or None
        """
        vehicle = None
        if self.__vehicleID:
            vehicle = BigWorld.entity(self.__vehicleID)
        return vehicle

    def invalidate(self, state, value, vehicleID=0):
        """
        Invalidates vehicle sates. The method should be invoked by vehicle state change trigger.
        
        :param state: A state listed within VEHICLE_VIEW_STATE
        :param value: New state value
        :param vehicleID: ID of vehicle for which the given state is changed.
        """
        if vehicleID != 0 and vehicleID != self.__vehicleID:
            return
        else:
            isStateChangeHandled = False
            if self.__updater is not None:
                isStateChangeHandled = self.__updater.handleStateChange(state, value)
            if not isStateChangeHandled:
                self.onVehicleStateUpdated(state, value)
            return

    def switchToPostmortem(self):
        """
        Switches to postmortem mode.
        """
        self.__isRqToSwitch = False
        if avatar_getter.getPlayerVehicleID() == self.__vehicleID:
            self.__waitingTI.stop()
            if self.__updater is not None:
                self.__updater.stop()
        self.onPostMortemSwitched()
        return

    def switchToAnother(self, vehicleID):
        """
        Switches to another vehicle.
        
        :param vehicleID: ID of a new vehicle to be tracked.
        """
        if self.__vehicleID == vehicleID or vehicleID is None:
            return
        else:
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.SWITCHING, self.__vehicleID)
            self.__waitingTI.stop()
            if self.__updater:
                self.__updater.stop()
            self.__vehicleID = vehicleID
            self.__isRqToSwitch = True
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.PLAYER_INFO, self.__vehicleID)
            self.__waitingTI.start()
            return

    def movingToRespawn(self):
        """
        Emits the appropriate event and state change event. The method should be called
        when the vehicle is moved to respawn.
        :return:
        """
        self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.SWITCHING, 0)
        self.onRespawnBaseMoving()

    def _waiting(self):
        """
        Callback to be invoked when the waiting timer is elapsed. Starts the updater when the
        avatar has been switched to the required vehicle.
        """
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is not None:
            self.__waitingTI.stop()
            self._setup(vehicle)
        return

    def _setup(self, vehicle):
        """
        Set up the updater and other properties
        :param vehicle: Vehicle entity.
        """
        if self.__updater is not None:
            self.__updater = self.__updater.switch(self.__vehicleID)
        if self.__isRqToSwitch:
            nationID = vehicle.typeDescriptor.type.id[0]
            notifications = avatar_getter.getSoundNotifications()
            if notifications is not None:
                notifications.clear()
            SoundGroups.g_instance.soundModes.setCurrentNation(nations.NAMES[nationID])
        self.onVehicleControlling(vehicle)
        if not vehicle.isAlive():
            self.onVehicleStateUpdated(VEHICLE_VIEW_STATE.DESTROYED, None)
        elif self.__updater is not None:
            self.__updater.start()
        return


class VehicleStateReplayRecorder(VehicleStateController):
    """
    Class of controller extends VehicleStateController. It stores cruise mode to replay.
    """

    def invalidate(self, state, value, vehicleID=0):
        if state == VEHICLE_VIEW_STATE.CRUISE_MODE:
            import BattleReplay
            BattleReplay.g_replayCtrl.onSetCruiseMode(value)
        super(VehicleStateReplayRecorder, self).invalidate(state, value, vehicleID)


def createCtrl(isReplayRecording):
    """
    Creates instance of vehicle controller.
    :param isReplayRecording:
    :return: instance of VehicleStateController based on the given flag.
    """
    if isReplayRecording:
        ctrl = VehicleStateReplayRecorder()
    else:
        ctrl = VehicleStateController()
    return ctrl
