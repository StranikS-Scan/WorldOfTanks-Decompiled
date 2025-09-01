# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/state_machine/observers.py
import typing
from .states import State
from .exceptions import StateError
if typing.TYPE_CHECKING:
    from .events import StateEvent

class BaseStateObserver(object):
    __slots__ = ()

    def clear(self):
        pass

    def isObservingState(self, state):
        raise NotImplementedError

    def onStateChanged(self, state, stateEntered, event=None):
        if stateEntered:
            self.onEnterState(state, event)
        else:
            self.onExitState(state, event)

    def onEnterState(self, state, event):
        pass

    def onExitState(self, state, event):
        pass


class StateIdsObserver(BaseStateObserver):
    __slots__ = ('_stateIDs',)

    def __init__(self, stateIDs):
        super(StateIdsObserver, self).__init__()
        if isinstance(stateIDs, str):
            self._stateIDs = [stateIDs]
        else:
            self._stateIDs = list(stateIDs)

    def getStateIDs(self):
        return self._stateIDs[:]

    def isObservingState(self, state):
        return state.getStateID() in self.getStateIDs()


class StateObserversContainer(BaseStateObserver):
    __slots__ = ('_observers',)

    def __init__(self, *observers):
        super(StateObserversContainer, self).__init__()
        self._observers = []
        for observer in observers:
            self.addObserver(observer)

    def clear(self):
        while self._observers:
            observer = self._observers.pop()
            observer.clear()

    def addObserver(self, observer):
        if not isinstance(observer, BaseStateObserver):
            raise StateError('Instance of StateObserver class is required')
        if observer not in self._observers:
            self._observers.append(observer)

    def removeObserver(self, observer):
        if not isinstance(observer, BaseStateObserver):
            raise StateError('Instance of StateObserver class is required')
        if observer in self._observers:
            self._observers.remove(observer)
        observer.clear()

    def isObservingState(self, state):
        return True

    def onStateChanged(self, state, stateEntered, event=None):
        for observer in self._observers:
            if observer.isObservingState(state):
                observer.onStateChanged(state, stateEntered, event=event)
