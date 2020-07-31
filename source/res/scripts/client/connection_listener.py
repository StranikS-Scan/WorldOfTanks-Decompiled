# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/connection_listener.py
import logging
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
_logger = logging.getLogger(__name__)
_OBJECT = 0
_EVENT = 1
_ONCE = 2
_ERROR = 3
_WARNING = 4

class ListenTo(object):
    All = 0
    onDisconnected = 1


class ConnectionListenerMeta(type):
    __singleton = None

    @property
    def instance(cls):
        if not cls.__singleton:
            cls.__singleton = ConnectionListener()
        return cls.__singleton


class ConnectionListener(object):
    __metaclass__ = ConnectionListenerMeta
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _records = []
    _map = {ListenTo.onDisconnected: '_onClientDisconnected'}

    def __init__(self):
        self._connectionMgr.onDisconnected += self._onDisconnected

    def __del__(self):
        self._connectionMgr.onDisconnected -= self._onDisconnected

    def attachListener(self, obj, event, once, errorText=None, warningText=None):
        self._records.append((obj,
         event,
         once,
         errorText,
         warningText))

    def detachListener(self, obj, listenTo=ListenTo.All):
        detach = [ record for record in self._records if self._isAttached(record[_OBJECT], record[_EVENT]) ]
        for record in detach:
            self._records.remove(record)

    def _isAttached(self, obj, listenTo):
        return any([ record for record in self._records if record[_OBJECT] == obj and record[_EVENT] in [listenTo, ListenTo.All] ])

    def _hasMethod(self, obj, method):
        return hasattr(obj.__class__, method) and callable(getattr(obj.__class__, method))

    def _notifyListeners(self, listenTo):
        method = self._map[listenTo]
        for record in self._records:
            if record[_EVENT] == listenTo:
                if record[_ONCE]:
                    self.detachListener(record[_OBJECT], listenTo)
                if self._hasMethod(record[_OBJECT], method):
                    getattr(record[_OBJECT], method)()
                elif record[_ERROR]:
                    _logger.error(record[_ERROR])
                elif record[_WARNING]:
                    _logger.warning(record[_WARNING])

    def _onDisconnected(self):
        self._notifyListeners(ListenTo.onDisconnected)
