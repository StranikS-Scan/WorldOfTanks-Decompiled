# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AccountSyncData.py
# Compiled at: 2011-07-20 01:06:18
import AccountCommands
from SyncController import SyncController
from debug_utils import *

class AccountSyncData(object):

    def __init__(self):
        self.revision = 0
        self.__account = None
        self.__syncController = None
        self.__ignore = True
        self.__isSynchronized = False
        self.__syncID = 0
        self.__subscribers = []
        self.__isFirstSync = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False
        self.__isFirstSync = True
        self._synchronize()

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True
        self.__isSynchronized = False

    def setAccount(self, account):
        self.__account = account
        if self.__syncController is not None:
            self.__syncController.destroy()
            self.__syncController = None
        if account is not None:
            self.__syncController = SyncController(account, self.__sendSyncRequest, self.__onSyncResponse, self.__onSyncComplete)
        return

    def waitForSync(self, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        elif self.__isSynchronized:
            callback(AccountCommands.RES_CACHE)
            return
        else:
            if callback is not None:
                self.__subscribers.append(callback)
            return

    def _synchronize(self):
        if self.__ignore:
            return
        elif self.__isSynchronized:
            return
        else:
            self.__syncController.request(self.__getNextSyncID(), None)
            return

    def _resynchronize(self):
        LOG_MX('resynchronize')
        if self.__ignore:
            return
        else:
            self.__isSynchronized = False
            self.revision = 0
            self.__syncController.request(self.__getNextSyncID(), None)
            return

    def __onSyncResponse(self, syncID, resultID, ext={}):
        if resultID == AccountCommands.RES_NON_PLAYER:
            return
        if syncID != self.__syncID:
            return
        if resultID < 0:
            LOG_ERROR('Data synchronization failed.')
            self._resynchronize()
            return
        if self.revision != ext.get('prevRev', self.revision):
            LOG_ERROR('Incorrect diff received', self.revision, ext['prevRev'])
            self._resynchronize()
            return
        self.revision = ext.get('rev', self.revision)
        self.__isSynchronized = True
        self.__account._update(not self.__isFirstSync, ext)
        self.__isFirstSync = False
        subscribers = self.__subscribers
        self.__subscribers = []
        for callback in subscribers:
            callback(resultID)

    def __onSyncComplete(self, syncID, data):
        if syncID != self.__syncID:
            return
        elif data is None:
            return
        else:
            self.revision = data['rev']
            self.__account._update(False, data)
            self._synchronize()
            return

    def __getNextSyncID(self):
        self.__syncID += 1
        if self.__syncID > 30000:
            self.__syncID = 1
        return self.__syncID

    def __sendSyncRequest(self, id, proxy):
        if self.__ignore:
            return
        first = self.revision >> 32
        second = self.revision & 4294967295L
        self.__account._doCmdInt3(AccountCommands.CMD_SYNC_DATA, first, second, 0, proxy)


def synchronizeDicts(diff, cache):
    for key, value in diff.iteritems():
        if value is None:
            cache.pop(key, None)
        elif isinstance(value, dict):
            synchronizeDicts(value, cache.setdefault(key, {}))
        else:
            cache[key] = value

    return
