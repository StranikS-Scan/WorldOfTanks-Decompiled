# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/state_machine/observers.py
from .events import StateEvent
from .exceptions import StateError

class BaseStateObserver(object):
    __slots__ = ()

    def clear(self):
        pass

    def getStateIDs(self):
        raise NotImplementedError

    def onStateChanged(self, stateID, flag, event=None):
        raise NotImplementedError


class SingleStateObserver(BaseStateObserver):
    __slots__ = ('_stateID',)

    def __init__(self, stateID):
        super(SingleStateObserver, self).__init__()
        self._stateID = stateID

    def getStateIDs(self):
        return (self._stateID,)

    def onStateChanged(self, stateID, flag, event=None):
        if flag:
            self.onEnterState(event=event)
        else:
            self.onExitState(event=event)

    def onEnterState(self, event=None):
        pass

    def onExitState(self, event=None):
        pass


class MultipleStateObserver(SingleStateObserver):
    __slots__ = ('_stateIDs',)

    def __init__(self, stateIDs):
        super(MultipleStateObserver, self).__init__('')
        self._stateIDs = stateIDs

    def getStateIDs(self):
        return self._stateIDs[:]


class StateObserversContainer(BaseStateObserver):
    __slots__ = ('_stateIDs', '_observers')

    def __init__(self, *observers):
        super(StateObserversContainer, self).__init__()
        self._observers = []
        self._stateIDs = []
        for observer in observers:
            self.addObserver(observer)

    def clear(self):
        while self._observers:
            observer = self._observers.pop()
            observer.clear()

        del self._stateIDs[:]

    def addObserver(self, observer):
        if not isinstance(observer, BaseStateObserver):
            raise StateError('Instance of StateObserver class is required')
        if observer not in self._observers:
            self._observers.append(observer)
        stateIDs = observer.getStateIDs()
        for stateID in stateIDs:
            if stateID not in self._stateIDs:
                self._stateIDs.append(stateID)

    def removeObserver(self, observer):
        if not isinstance(observer, BaseStateObserver):
            raise StateError('Instance of StateObserver class is required')
        if observer in self._observers:
            self._observers.remove(observer)
        stateIDs = observer.getStateIDs()
        for stateID in stateIDs:
            if stateID in self._stateIDs:
                self._stateIDs.remove(stateID)

        observer.clear()

    def getStateIDs(self):
        return self._stateIDs[:]

    def onStateChanged(self, stateID, flag, event=None):
        for observer in self._observers:
            if stateID in observer.getStateIDs():
                observer.onStateChanged(stateID, flag, event=event)
