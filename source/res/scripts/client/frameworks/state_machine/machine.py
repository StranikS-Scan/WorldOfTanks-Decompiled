# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/state_machine/machine.py
import logging
import operator
from . import states as _states
from .events import StateEvent
from .exceptions import StateMachineError
from .node import NodesVisitor
from .observers import BaseStateObserver
from .observers import StateObserversContainer
from .transitions import BaseTransition
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class StateMachine(_states.State):
    __slots__ = ('__isRunning', '__visitor', '__entered', '__observers')

    def __init__(self, stateID=''):
        super(StateMachine, self).__init__(stateID=stateID)
        self.__isRunning = False
        self.__visitor = NodesVisitor()
        self.__entered = []
        self.__observers = StateObserversContainer()

    @staticmethod
    def isMachine():
        return True

    def start(self, doValidate=True):
        if doValidate:
            _validateMachine(self)
        if self.__isRunning:
            _logger.debug('%r: Machine is already started', self)
            return
        else:
            self.__isRunning = True
            transition = _InitialTransition(target=self.getInitial())
            _logger.debug('%r: Machine is started by %r', self, transition)
            entered = self.__enter((transition,))
            transition.clear()
            self.__notify(entered, True, None)
            self.__tick()
            return

    def stop(self):
        if not self.__isRunning:
            _logger.debug('%r: Machine is not started', self)
            return
        self.__isRunning = False
        self.__observers.clear()
        del self.__entered[:]
        self.clear()
        _logger.debug('%r: Machine is stopped', self)

    def isStateEntered(self, stateID):
        for state in self.__entered:
            if state.getStateID() == stateID:
                return True

        return False

    def addState(self, state):
        self.addChildState(state)

    def removeState(self, state):
        self.removeChildState(state)

    def post(self, event):
        _logger.debug('%r: %r is posted', self, event)
        if not isinstance(event, StateEvent):
            raise StateMachineError('Instance of StateEvent class is required')
        if not self.__isRunning:
            raise StateMachineError('State machine is not running')
        self.__tick(event=event)

    def connect(self, observer):
        self.__observers.addObserver(observer)

    def disconnect(self, observer):
        self.__observers.removeObserver(observer)

    def __tick(self, event=None):
        transitions = self.__select(event)
        if transitions:
            self.__process(transitions, event)

    def __process(self, transitions, event):
        _logger.debug('%r: Start process, enabled transitions = %r', self, transitions)
        _logger.debug('%r: Snapshot before exiting states = %r', self, self.__entered)
        exited = self.__exit(transitions)
        _logger.debug('%r: Snapshot after exiting states = %r', self, self.__entered)
        entered = self.__enter(transitions)
        self.__notify(exited, False, event)
        self.__notify(entered, True, event)
        for state in self.__entered:
            if state.isFinal() and state.getParent() == self:
                self.stop()
                break

        _logger.debug('%r: Snapshot after entering states = %r', self, self.__entered)
        _logger.debug('%r: Stop process', self)

    def __select(self, event):
        result = []
        for state in self.__entered:
            if not state.isElementary() or state.isMachine():
                continue
            states = self.__visitor.getAncestors(state, self.getParent())
            if state.isNative():
                states.insert(0, state)
            transition = self.__execute(states, event)
            if transition is not None and transition not in result:
                result.append(transition)

        return result

    def __execute(self, states, event):
        result = []
        for state in states:
            transitions = state.getTransitions()
            for transition in transitions:
                if transition.execute(event):
                    _logger.debug('%r: %r has execution result is True', self, transition)
                    result.append(transition)

            if result:
                result.sort(key=operator.methodcaller('getPriority'), reverse=True)
                transition = result[0]
                _logger.debug('%r: %r is selected', self, transition)
                return transition

        return None

    def __exit(self, transitions):
        result = []
        for transition in transitions:
            states = transition.getEnabledStates()
            if not states:
                continue
            lca = self.__visitor.getLCA(states, upper=self.getParent())
            for state in self.__entered:
                if self.__visitor.isDescendantOf(state, lca) and state not in result:
                    result.append(state)

        result.sort(key=_states.StateExitingSortKey)
        for state in result:
            _logger.debug('%r: %r is exiting', self, state)
            state.exit()
            self.__entered.remove(state)

        return result

    def __enter(self, transitions):
        result = []
        for transition in transitions:
            states = transition.getEnabledStates()
            if not states:
                continue
            lca = self.__visitor.getLCA(states, upper=self.getParent())
            for state in states[1:]:
                self.__collect(state, lca, result)

        result.sort(key=_states.StateEnteringSortKey)
        for state in result:
            self.__entered.append(state)
            _logger.debug('%r: %r is entering', self, state)
            state.enter()

        return result

    def __collect(self, state, root, accumulation):
        accumulation.append(state)
        if state.isParallel():
            for child in state.getChildrenStates():
                self.__collect(child, state, accumulation)

        if state.isUnion():
            self.__collect(state.getInitial(), state, accumulation)
        ancestors = self.__visitor.getAncestors(state, root)
        for ancestor in ancestors:
            if ancestor.getParent() is None:
                continue
            accumulation.append(ancestor)
            if not ancestor.isParallel():
                continue
            for child in ancestor.getChildrenStates():
                for item in accumulation:
                    if self.__visitor.isDescendantOf(item, child):
                        break
                else:
                    self.__collect(child, ancestor, accumulation)

        return

    def __notify(self, states, flag, event):
        for state in states:
            stateID = state.getStateID()
            if not stateID:
                _logger.warn('%r: %r has no ID, can not notify observers', self, state)
                continue
            self.__observers.onStateChanged(stateID, flag, event=event)


class _InitialTransition(BaseTransition):
    __slots__ = ()

    def __init__(self, target):
        super(_InitialTransition, self).__init__()
        self.setTarget(target)

    def getSource(self):
        return _states.State()

    def execute(self, event):
        return True


def _validateTransitionHasLCA(transition, upper=None):
    states = transition.getEnabledStates()
    if states and NodesVisitor.getLCA(states, upper=upper) is None:
        raise StateMachineError('States have no LCA in transition {}'.format(transition))
    return


def _validateInitialState(state):
    initial = state.getInitial()
    if initial is None:
        raise StateMachineError('{} has no initial state'.format(state))
    return


def _validateState(state, machine):
    if state.isUnion():
        _validateInitialState(state)
    if state.isNative():
        for transition in state.getTransitions():
            _validateTransitionHasLCA(transition, upper=machine.getParent())


def _validateMachine(machine):
    _validateInitialState(machine)
    ids = []
    for state in machine.visitInOrder(lambda item: isinstance(item, _states.State)):
        if state.isMachine():
            continue
        stateID = state.getStateID()
        if stateID:
            if stateID not in ids:
                ids.append(stateID)
            else:
                raise StateMachineError('{} is not unique, each state must have unique ID'.format(state))
            _validateState(state, machine)
