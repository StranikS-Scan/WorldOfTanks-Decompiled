# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/listeners_collection.py
from __future__ import absolute_import
import itertools
import logging
_logger = logging.getLogger(__name__)

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
        _logger.debug('Listeners collection was cleared: %r', self)
        while self._listeners:
            self._listeners.pop()

        self._clazz = None
        self._mutualListeners = None
        return

    def suspend(self):
        _logger.debug('Listeners collection was suspended: %r', self)
        self._isSuspended = True

    def resume(self):
        _logger.debug('Listeners collection was resumed: %r', self)
        self._isSuspended = False

    def addMutualListeners(self, mutualListeners):
        if isinstance(mutualListeners, ListenersCollection):
            self._mutualListeners = mutualListeners
        else:
            _logger.error('Object is not extend {0:>s} %r'.format(ListenersCollection.__name__), mutualListeners)

    def addListener(self, listener):
        if isinstance(listener, self._clazz):
            if not self.hasListener(listener):
                self._listeners.append(listener)
            else:
                _logger.error('Listener already added %r', listener)
        else:
            _logger.error('Object does not extend {0:>s} %r'.format(self._clazz.__name__), listener)

    def hasListener(self, listener):
        return listener in self._listeners

    def removeListener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)
        else:
            _logger.debug('Listener not found %r.', listener)

    def getListenersIterator(self):
        return itertools.chain(iter(self._listeners), self._mutualListeners.getListenersIterator()) if self._mutualListeners is not None else iter(self._listeners)

    def _setListenerClass(self, listenerClass):
        self._clazz = listenerClass

    def _invokeListeners(self, event, *args, **kwargs):
        if self._isSuspended:
            return
        else:
            _logger.debug('%r %r %r', event, args, kwargs)
            for listener in list(self.getListenersIterator()):
                if listener not in self.getListenersIterator():
                    continue
                notifier = getattr(listener, event, None)
                if notifier and callable(notifier):
                    try:
                        notifier(*args, **kwargs)
                    except Exception:
                        _logger.exception('Error while notifying listener %r for event %r', listener, event)

                _logger.error('Listener method not found %r %r', listener, event)

            return
