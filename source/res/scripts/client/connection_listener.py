# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/connection_listener.py
import logging
from collections import namedtuple
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
_logger = logging.getLogger(__name__)
Record = namedtuple('Record', ['object',
 'event',
 'once',
 'error',
 'warning'])

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
        self._records = []
        self._connectionMgr.onDisconnected -= self._onDisconnected

    def attachListener(self, obj, event, once, errorText=None, warningText=None):
        self._records.append(Record(obj, event, once, errorText, warningText))

    def detachListener(self, obj, listenTo=ListenTo.All):
        for record in self._getRecordsForObject(obj, listenTo):
            self._records.remove(record)

    def isAttached(self, obj, listenTo):
        return any(self._getRecordsForObject(obj, listenTo))

    def _getRecordsForObject(self, obj, event):
        return [ record for record in self._records if record.object == obj and record.event == event ]

    @staticmethod
    def _hasMethod(obj, method):
        return (hasattr(obj.__class__, method) or hasattr(obj, method)) and callable(getattr(obj, method))

    def _notifyListeners(self, listenTo):
        method = self._map[listenTo]
        detached = []
        try:
            for record in self._records:
                if record.event == listenTo or record.event == ListenTo.All:
                    if self._hasMethod(record.object, method):
                        if record.once:
                            detached.append(record)
                        getattr(record.object, method)()
                    elif record.error:
                        _logger.error(record.error)
                    elif record.warning:
                        _logger.warning(record.warning)

        finally:
            for record in detached:
                self._records.remove(record)

    def _onDisconnected(self):
        self._notifyListeners(ListenTo.onDisconnected)
