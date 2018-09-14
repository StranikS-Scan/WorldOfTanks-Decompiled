# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/repair_ctrl.py
import weakref
from collections import defaultdict
import BigWorld
import Event
from constants import REPAIR_POINT_ACTION as _ACTION
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, REPAIR_STATE_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.utils.TimeInterval import TimeInterval
_ACTIONS_SOUND_IDS = {_ACTION.COMPLETE_REPAIR: 'point_repair'}
_ACTIONS_NAMES = dict([ (v, k) for k, v in _ACTION.__dict__.iteritems() if not k.startswith('_') ])
_STATE_NAMES = dict([ (v, k) for k, v in REPAIR_STATE_ID.__dict__.iteritems() if not k.startswith('_') ])
_STATE_ID_TO_ACTIONS = {REPAIR_STATE_ID.DISABLED: (_ACTION.BECOME_DISABLED,),
 REPAIR_STATE_ID.READY: (_ACTION.BECOME_READY,),
 REPAIR_STATE_ID.REPAIRING: (_ACTION.START_REPAIR, _ACTION.RESTART_REPAIR),
 REPAIR_STATE_ID.COOLDOWN: (_ACTION.COMPLETE_REPAIR, _ACTION.ENTER_WHILE_CD, _ACTION.ENTER_WHILE_CD)}

def _getActionName(action):
    if action in _ACTIONS_NAMES:
        return '{}::{}'.format(_ACTIONS_NAMES[action], action)
    else:
        return 'N/A'


def _getStateName(stateID):
    if stateID in _STATE_NAMES:
        return _STATE_NAMES[stateID]
    else:
        return 'N/A'


class RepairState(object):
    __slots__ = ('_ctrl', '_stateID', '_pointIndex', '_actions', '_isPlayerInPoint')

    def __init__(self, pointIndex, stateID, *actions):
        super(RepairState, self).__init__()
        self._ctrl = None
        self._pointIndex = pointIndex
        self._stateID = stateID
        self._actions = actions
        self._isPlayerInPoint = False
        return

    def __repr__(self):
        return 'RepairState(state={}, actions={})'.format(_getStateName(self._stateID), map(_getActionName, self._actions))

    def create(self, ctrl):
        if self._stateID != REPAIR_STATE_ID.UNRESOLVED:
            self._ctrl = weakref.proxy(ctrl)
            self._ctrl.onStateCreated(self._pointIndex, self._stateID)

    def destroy(self):
        if self._ctrl is not None:
            self._ctrl.onStateDestroyed(self._pointIndex, self._stateID)
            self._ctrl = None
        return

    def getStateID(self):
        return self._stateID

    def isPlayerInPoint(self):
        return self._isPlayerInPoint

    def hasAction(self, action):
        return action in self._actions

    def setAction(self, action, nextActionTime):
        pass


class TimeTrackState(RepairState):
    __slots__ = ('_timer', '_nextTime', '__weakref__')

    def __init__(self, pointIndex, stateID, *actions):
        super(TimeTrackState, self).__init__(pointIndex, stateID, *actions)
        self._timer = None
        self._nextTime = 0
        return

    def destroy(self):
        self._destroyTimer()
        super(TimeTrackState, self).destroy()

    def setAction(self, action, nextActionTime):
        if action in self._actions:
            self._recreateTimer(nextActionTime)
            self._updateTime()
        else:
            self._destroyTimer()

    def _getTimeLeft(self):
        return max(0, round(self._nextTime - BigWorld.serverTime()))

    def _updateTime(self):
        self._ctrl.onTimerUpdated(self._pointIndex, self._stateID, self._getTimeLeft())

    def _createTimer(self, nextActionTime):
        self._nextTime = nextActionTime
        self._timer = TimeInterval(1, self, '_updateTime')
        self._timer.start()

    def _destroyTimer(self):
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        return

    def _recreateTimer(self, nextActionTime):
        self._destroyTimer()
        self._createTimer(nextActionTime)


class DisabledState(RepairState):
    __slots__ = ()

    def __init__(self, pointIndex):
        super(DisabledState, self).__init__(pointIndex, REPAIR_STATE_ID.DISABLED, _ACTION.BECOME_DISABLED)


class ReadyState(RepairState):
    __slots__ = ()

    def __init__(self, pointIndex):
        super(ReadyState, self).__init__(pointIndex, REPAIR_STATE_ID.READY, _ACTION.BECOME_READY, _ACTION.CANCEL_REPAIR)


class RepairingState(TimeTrackState):
    __slots__ = ()

    def __init__(self, pointIndex):
        super(RepairingState, self).__init__(pointIndex, REPAIR_STATE_ID.REPAIRING, _ACTION.START_REPAIR, _ACTION.RESTART_REPAIR)

    def create(self, ctrl):
        self._isPlayerInPoint = True
        super(RepairingState, self).create(ctrl)


class CooldownState(TimeTrackState):
    __slots__ = ()

    def __init__(self, pointIndex):
        super(CooldownState, self).__init__(pointIndex, REPAIR_STATE_ID.COOLDOWN, _ACTION.COMPLETE_REPAIR, _ACTION.ENTER_WHILE_CD, _ACTION.LEAVE_WHILE_CD)

    def create(self, ctrl):
        self._isPlayerInPoint = True
        super(CooldownState, self).create(ctrl)

    def setAction(self, action, timeLeft):
        if action == _ACTION.ENTER_WHILE_CD:
            self._isPlayerInPoint = True
            self._ctrl.onVehicleEntered(self._pointIndex, self._stateID)
        elif action == _ACTION.LEAVE_WHILE_CD:
            self._isPlayerInPoint = False
            self._ctrl.onVehicleLeft(self._pointIndex, self._stateID)
        if timeLeft:
            super(CooldownState, self).setAction(action, timeLeft)


class RepairPointsStates(defaultdict):

    def __missing__(self, key):
        self[key] = value = RepairState(key, REPAIR_STATE_ID.UNRESOLVED)
        return value


def findState(pointIndex, action):
    """ Tries to find GUI state by server-side action.
    :param pointIndex: integer containing index of point.
    :param action: integer containing one of REPAIR_POINT_ACTION.*.
    :return: instance of RepairState.
    """
    for clazz in (DisabledState,
     ReadyState,
     RepairingState,
     CooldownState):
        state = clazz(pointIndex)
        if state.hasAction(action):
            return state

    return RepairState(pointIndex, REPAIR_STATE_ID.UNRESOLVED, action)


def playSoundByAction(action):
    if action in _ACTIONS_SOUND_IDS:
        nots = getSoundNotifications()
        if nots is not None:
            nots.play(_ACTIONS_SOUND_IDS[action])
    return


class RepairController(IBattleController):
    """ Controller converts server-side action to state that are specific for UI,
    and UI is notified about action by controller's events."""

    def __init__(self):
        super(RepairController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onStateCreated = Event.Event(self.__eManager)
        self.onStateDestroyed = Event.Event(self.__eManager)
        self.onTimerUpdated = Event.Event(self.__eManager)
        self.onVehicleEntered = Event.Event(self.__eManager)
        self.onVehicleLeft = Event.Event(self.__eManager)
        self.__states = RepairPointsStates()

    def getControllerID(self):
        """ Gets unique ID of controller.
        :return: integer.
        """
        return BATTLE_CTRL_ID.REPAIR

    def startControl(self):
        """Start to control states. It's just implementation of interface."""
        pass

    def stopControl(self):
        """Stops to control states."""
        while self.__states:
            _, state = self.__states.popitem()
            state.destroy()

        self.__eManager.clear()
        self.__eManager = None
        return

    def getPointStateID(self, pointIndex):
        """ Gets state ID of desired point.
        :param pointIndex: integer containing index of point.
        :return: one of REPAIR_STATE_ID.*.
        """
        return self.__states[pointIndex].getStateID()

    def getPointsStates(self):
        """ Gets present states of repair points.
        :return: generator.
        """
        for pointIndex, state in self.__states.iteritems():
            yield (pointIndex, state.getStateID(), state.isPlayerInPoint())

    def action(self, repairPointIndex, action, nextActionTime):
        """ Server notifies client that repair point state is changed by action.
        :param repairPointIndex: integer containing index of point.
        :param action: integer containing one of REPAIR_POINT_ACTION.*.
        :param nextActionTime: float containing server-side time when next action will be appear.
        """
        currentState = self.__states[repairPointIndex]
        if not currentState.hasAction(action):
            newState = findState(repairPointIndex, action)
            if newState.getStateID() != currentState.getStateID():
                LOG_DEBUG('State is switched', currentState, newState)
                currentState.destroy()
                newState.create(self)
                newState.setAction(action, nextActionTime)
                self.__states[repairPointIndex] = newState
                playSoundByAction(action)
            else:
                LOG_WARNING('State can not be switched to same one', newState)
        else:
            currentState.setAction(action, nextActionTime)
