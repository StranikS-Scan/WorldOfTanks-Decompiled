# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/client_update_listener.py
import typing
import Event
from PlayerEvents import g_playerEvents
from account_helpers import AccountSyncData
from helpers import dependency
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from skeletons.connection_mgr import IConnectionManager

class ClientUpdateListener(object):
    __slots__ = ('onDataUpdated', '__data', '__key', '__resetOnDisconnect', '__synced', '__default')
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, key, resetOnDisconnect=True, default=None):
        self.__default = default
        self.__data = self.__default
        self.__synced = False
        self.__key = key
        self.__resetOnDisconnect = resetOnDisconnect
        self.onDataUpdated = Event.Event()

    @property
    def data(self):
        return self.__data

    @property
    def synced(self):
        return self.__synced

    def init(self):
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        if self.__resetOnDisconnect:
            self.__connectionMgr.onDisconnected += self.__onDisconnected

    def destroy(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        if self.__resetOnDisconnect:
            self.__connectionMgr.onDisconnected -= self.__onDisconnected
        self.onDataUpdated.clear()
        self.__data = None
        return

    def reset(self):
        self.__data = self.__default
        self.__synced = False

    def __onClientUpdated(self, diff, *_):
        isFullSync = AccountSyncData.isFullSyncDiff(diff)
        if isFullSync:
            self.reset()
        if self.__key in diff:
            diff = diff[self.__key]
            if isinstance(diff, dict):
                synchronizeDicts(diff, self.__data)
            else:
                self.__data = diff
            self.__synced = True
            self.onDataUpdated(self.__data)

    def __onDisconnected(self):
        self.reset()
