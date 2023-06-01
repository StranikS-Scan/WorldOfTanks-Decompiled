# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/base.py
import time
import typing
from frameworks.state_machine import State, StateFlags, StateEvent
from helpers.CallbackDelayer import CallbackDelayer
from gui.game_loading import loggers
if typing.TYPE_CHECKING:
    from frameworks.state_machine import StateMachine
    from gui.game_loading.resources.base import BaseResources
    from gui.game_loading.resources.models import BaseResourceModel
_logger = loggers.getStatesLogger()

class BaseState(State):
    __slots__ = ('_entered',)

    def __init__(self, stateID, flags=StateFlags.UNDEFINED):
        super(BaseState, self).__init__(stateID=stateID, flags=flags)
        self._entered = False

    @property
    def isEntered(self):
        return self._entered

    def _onEntered(self):
        super(BaseState, self)._onEntered()
        self._entered = True

    def _onExited(self):
        self._entered = False
        super(BaseState, self)._onExited()


class BaseTickingState(BaseState):
    __slots__ = ('_isSelfTicking', '_stopped', '_ticker', '_nextTickTime', '_onCompleteEvent', '_stepNumber')

    def __init__(self, stateID, flags=StateFlags.UNDEFINED, isSelfTicking=False, onCompleteEvent=None):
        super(BaseTickingState, self).__init__(stateID, flags=flags)
        self._isSelfTicking = isSelfTicking
        self._nextTickTime = 0
        self._onCompleteEvent = onCompleteEvent or StateEvent()
        self._stopped = True
        self._ticker = None
        self._stepNumber = 0
        return

    def clear(self):
        self._stop()
        self._entered = False
        super(BaseTickingState, self).clear()
        _logger.debug('[%s] cleared.', self)

    def manualTick(self, stepNumber=0):
        if self._stopped or not self._entered:
            return
        self._stepNumber = stepNumber
        self._runTick()

    def _start(self, *args, **kwargs):
        if not self._entered:
            _logger.debug('[%s] can not start not entered state.', self)
            return
        elif not self._stopped:
            _logger.debug('[%s] already started.', self)
            return
        else:
            self._stopped = False
            nextTickDelay = self._runTick()
            if nextTickDelay is None:
                return
            self._startTicker(nextTickDelay)
            _logger.debug('[%s] started.', self)
            return

    def _stop(self, *args, **kwargs):
        self._stopTicker()
        self._nextTickTime = 0
        self._stopped = True
        _logger.debug('[%s] stopped.', self)

    def _runTick(self):
        if self._nextTickTime > 0:
            waitingTime = self._nextTickTime - time.time()
            if waitingTime > 0:
                return waitingTime
        nextTickDelay = self._task()
        isStateComplete = nextTickDelay is None or nextTickDelay < 0
        if isStateComplete:
            self._stop()
            machine = self.getMachine()
            if machine is not None:
                _logger.debug('[%s] complete, sending notification to state machine.', self)
                machine.post(self._onCompleteEvent)
            else:
                _logger.debug('[%s] not registered in state machine.', self)
            return
        else:
            self._nextTickTime = time.time() + nextTickDelay
            return nextTickDelay

    def _onEntered(self):
        super(BaseTickingState, self)._onEntered()
        self._start()

    def _onExited(self):
        self._stop()
        super(BaseTickingState, self)._onExited()

    def _startTicker(self, delay):
        if self._isSelfTicking and self._ticker is None and delay >= 0:
            self._ticker = CallbackDelayer()
            self._ticker.delayCallback(delay, self._runTick)
            _logger.debug('[%s] ticker started.', self)
        return

    def _stopTicker(self):
        if self._ticker is not None:
            self._ticker.destroy()
            self._ticker = None
            _logger.debug('[%s] ticker stopped.', self)
        return

    def _task(self):
        raise NotImplementedError


class BaseViewResourcesTickingState(BaseTickingState):
    __slots__ = ('_resources',)

    def __init__(self, stateID, resources, flags=StateFlags.UNDEFINED, isSelfTicking=False, onCompleteEvent=None):
        super(BaseViewResourcesTickingState, self).__init__(stateID=stateID, flags=flags, isSelfTicking=isSelfTicking, onCompleteEvent=onCompleteEvent)
        self._resources = resources

    def _onExited(self):
        self._resources.reset()
        super(BaseViewResourcesTickingState, self)._onExited()

    def _task(self):
        resource = self._resources.get()
        if not resource:
            return None
        else:
            self._view(resource)
            return resource.minShowTimeSec

    def _view(self, resource):
        raise NotImplementedError


class BaseGroupTickingStates(BaseState):
    __slots__ = ()

    def manualTick(self, stepNumber=0):
        for state in self.getChildrenStates():
            if isinstance(state, (BaseTickingState, BaseGroupTickingStates)) and state.isEntered:
                state.manualTick(stepNumber)
