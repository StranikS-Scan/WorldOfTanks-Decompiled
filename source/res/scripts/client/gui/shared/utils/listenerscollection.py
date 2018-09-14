# Embedded file name: scripts/client/gui/shared/utils/ListenersCollection.py
from debug_utils import LOG_ERROR, LOG_DEBUG

class ListenersCollection(object):

    def __init__(self):
        super(ListenersCollection, self).__init__()
        self._listeners = []
        self._clazz = None
        return

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
        return iter(self._listeners)

    def _setListenerClass(self, listenerClass):
        self._clazz = listenerClass

    def _invokeListeners(self, event, *args, **kwargs):
        LOG_DEBUG(event, args, kwargs)
        for listener in self._listeners[:]:
            notifier = getattr(listener, event)
            if notifier and callable(notifier):
                notifier(*args, **kwargs)
            else:
                LOG_ERROR('Listener method not found', listener, event)
