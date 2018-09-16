# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/state_machine/states.py
from collections import namedtuple
from .exceptions import StateError
from .node import Node, NodesVisitor
from .transitions import BaseTransition

class StateFlags(object):
    UNDEFINED = 0
    INITIAL = 1
    FINAL = 4
    SINGULAR = 8
    PARALLEL = 16


def _filterBaseState(child):
    return isinstance(child, BaseState)


def _filterInitialState(child):
    return isinstance(child, BaseState) and child.isInitial()


def _filterBaseTransition(child):
    return isinstance(child, BaseTransition)


class BaseState(Node):
    __slots__ = ('__stateID', '__flags', '__isEntered')

    def __init__(self, stateID='', flags=StateFlags.UNDEFINED):
        super(BaseState, self).__init__()
        self.__stateID = stateID
        self.__flags = flags
        self.__isEntered = False

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__stateID)

    def clear(self):
        self.__isEntered = False
        super(BaseState, self).clear()

    def getStateID(self):
        return self.__stateID

    def isInitial(self):
        return self.__flags & StateFlags.INITIAL > 0

    def isSingular(self):
        return self.__flags & StateFlags.SINGULAR > 0

    def isParallel(self):
        return self.__flags & StateFlags.PARALLEL > 0

    def isFinal(self):
        return self.__flags & StateFlags.FINAL > 0

    def isNative(self):
        return not self.isFinal()

    def isUnion(self):
        return self.isNative() and not self.isParallel() and self.getChildrenStates()

    def isElementary(self):
        return self.isFinal() or self.isNative() and not self.getChildrenStates()

    @staticmethod
    def isMachine():
        return False

    def getMachine(self):
        found = self
        while found is not None:
            if found.isMachine():
                return found
            found = found.getParent()

        return

    def addChildState(self, state):
        if not isinstance(state, BaseState):
            raise StateError('Instance of BaseState class is required')
        if self.isFinal():
            raise StateError('Sub-state can not be added to final state')
        self._addChild(state)

    def removeChildState(self, state):
        if not isinstance(state, BaseState):
            raise StateError('Instance of BaseState class is required')
        if self.isFinal():
            raise StateError('Sub-state can not be removed from final state')
        self._removeChild(state)

    def getChildrenStates(self):
        return self.getChildren(filter_=_filterBaseState)

    def configure(self, *args, **kwargs):
        pass

    def enter(self):
        if self.__isEntered:
            raise StateError('{} is already activated'.format(self))
        self.__isEntered = True
        self._onEntered()

    def exit(self):
        if not self.__isEntered:
            raise StateError('{} is not activated'.format(self))
        self.__isEntered = False
        self._onExited()

    def addChild(self, child):
        raise StateError('Routine is not allowed in {}', self.__class__.__name__)

    def removeChild(self, child):
        raise StateError('Routine is not allowed in {}', self.__class__.__name__)

    def _onEntered(self):
        pass

    def _onExited(self):
        pass


class State(BaseState):
    __slots__ = ()

    def __init__(self, stateID='', flags=StateFlags.SINGULAR):
        super(State, self).__init__(stateID=stateID, flags=flags)

    def getInitial(self):
        children = self.getChildren(filter_=_filterInitialState)
        if not children:
            return None
        else:
            if len(children) > 1:
                raise StateError('State {} should be have one initial state, found {}'.format(self, children))
            return children[0]

    def addTransition(self, transition, target=None):
        if not isinstance(transition, BaseTransition):
            raise StateError('Instance of BaseTransition class is required')
        if target is not None:
            transition.setTarget(target)
        self._addChild(transition)
        return

    def removeTransition(self, transition):
        if not isinstance(transition, BaseTransition):
            raise StateError('Instance of BaseTransition class is required')
        self._removeChild(transition)

    def getTransitions(self):
        return self.getChildren(filter_=_filterBaseTransition)


_SortDirection = namedtuple('_SortDirection', ('ancestor', 'descendant'))
_FROM_ANCESTOR_TO_DESCENDANT = _SortDirection(1, -1)
_FROM_DESCENDANT_TO_ANCESTOR = _SortDirection(-1, 1)

class _StateTogglingSortKey(object):
    __slots__ = ('state', 'direction')

    def __init__(self, state, direction):
        super(_StateTogglingSortKey, self).__init__()
        self.state = state
        self.direction = direction

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __ne__(self, other):
        return self._cmp(other) != 0

    def __hash__(self):
        raise TypeError('hash not implemented')

    def _cmp(self, other):
        if self.state.getParent() == other.state.getParent():
            parent = self.state.getParent()
            return cmp(NodesVisitor.getDescendantIndex(self.state, parent, filter_=_filterBaseState), NodesVisitor.getDescendantIndex(other.state, parent, filter_=_filterBaseState))
        if NodesVisitor.isDescendantOf(self.state, other.state):
            return self.direction.ancestor
        if NodesVisitor.isDescendantOf(other.state, self.state):
            return self.direction.descendant
        lca = NodesVisitor.getLCA([self.state, other.state], upper=self.state.getMachine())
        return cmp(NodesVisitor.getDescendantIndex(self.state, lca, filter_=_filterBaseState), NodesVisitor.getDescendantIndex(other.state, lca, filter_=_filterBaseState))


class StateEnteringSortKey(_StateTogglingSortKey):

    def __init__(self, state):
        super(StateEnteringSortKey, self).__init__(state, _FROM_ANCESTOR_TO_DESCENDANT)


class StateExitingSortKey(_StateTogglingSortKey):

    def __init__(self, state):
        super(StateExitingSortKey, self).__init__(state, _FROM_DESCENDANT_TO_ANCESTOR)
