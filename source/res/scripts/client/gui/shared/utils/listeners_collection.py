# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/listeners_collection.py
import itertools
from debug_utils import LOG_ERROR, LOG_DEBUG

class IListenersCollection(object):

    def addMutualListeners(self, mutualListeners):
        pass

    def addListener(self, listener):
        pass

    def removeListener(self, listener):
        pass


class ListenersCollection(IListenersCollection):

    def __init__(self):
        super(ListenersCollection, self).__init__()
        self._listeners = []
        self._clazz = None
        self._mutualListeners = None
        self._isSuspended = False
        return

    def clear(self):
        LOG_DEBUG('Listeners collection was cleared: ', self)
        while self._listeners:
            self._listeners.pop()

        self._clazz = None
        self._mutualListeners = None
        return

    def suspend(self):
        LOG_DEBUG('Listeners collection was suspended: ', self)
        self._isSuspended = True

    def resume(self):
        LOG_DEBUG('Listeners collection was resumed: ', self)
        self._isSuspended = False

    def addMutualListeners(self, mutualListeners):
        if isinstance(mutualListeners, ListenersCollection):
            self._mutualListeners = mutualListeners
        else:
            LOG_ERROR('Object is not extend {0:>s}'.format(ListenersCollection.__name__), mutualListeners)

    def addListener(self, listener):
        if isinstance(listener, self._clazz):
            if not self.hasListener(listener):
                self._listeners.append(listener)
            else:
                LOG_ERROR('Listener already added', listener)
        else:
            LOG_ERROR('Object is not extend {0:>s}'.format(self._clazz.__name__), listener)

    def hasListener(self, listener):
        return listener in self._listeners

    def removeListener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)
        else:
            LOG_DEBUG('Listener not found.', listener)

    def getListenersIterator(self):
        return itertools.chain(iter(self._listeners), self._mutualListeners.getListenersIterator()) if self._mutualListeners is not None else iter(self._listeners)

    def _setListenerClass(self, listenerClass):
        self._clazz = listenerClass

    def _invokeListeners(self, event, *args, **kwargs):
        if self._isSuspended:
            return
        LOG_DEBUG(event, args, kwargs)
        for listener in self.getListenersIterator():
            notifier = getattr(listener, event)
            if notifier and callable(notifier):
                notifier(*args, **kwargs)
            LOG_ERROR('Listener method not found', listener, event)
