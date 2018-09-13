# Embedded file name: scripts/client/account_helpers/settings_core/IntUserSettings.py
import AccountCommands
from functools import partial
from debug_utils import *

class IntUserSettings(object):

    def __init__(self):
        self.__proxy = None
        self.__syncData = None
        self.__cache = {}
        return

    def setProxy(self, proxy, syncData):
        self.__proxy = proxy
        self.__syncData = syncData

    def onProxyBecomePlayer(self):
        pass

    def onProxyBecomeNonPlayer(self):
        pass

    def isSynchronized(self):
        return bool(self.__cache)

    def synchronize(self, isFullSync, diff):
        cache = self.__cache
        if isFullSync:
            cache.clear()
        settingsFull = diff.get(('intUserSettings', '_r'), {})
        if settingsFull:
            self.__cache = dict(settingsFull)
        settingsDiff = diff.get('intUserSettings', {})
        if settingsDiff:
            for key, value in settingsDiff.iteritems():
                if value is not None:
                    cache[key] = value
                else:
                    cache.pop(key, None)

        LOG_DEBUG('IntUserSettings synchronize: cache now=%s' % self.__cache)
        return

    def getCache(self, callback = None):
        if self.__syncData:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
        elif callback:
            callback(AccountCommands.RES_NON_PLAYER)

    def get(self, key, callback = None):
        if self.__syncData:
            self.__syncData.waitForSync(partial(self.__onGetResponse, key, callback))
        elif callback:
            callback(AccountCommands.RES_NON_PLAYER)

    def addIntSettings(self, dictIntSettings, callback = None):
        if dictIntSettings:
            arr = []
            for k, v in dictIntSettings.iteritems():
                if isinstance(k, int) and isinstance(v, int):
                    arr.append(k)
                    arr.append(v)
                else:
                    import traceback
                    traceback.print_stack()
                    LOG_ERROR('Bad key:value pair in addIntUserSettings: %r:%r (should be int:int)' % (k, v))
                    return

        else:
            import traceback
            traceback.print_stack()
            LOG_ERROR('Bad dictIntSettings: %r (should be {int:int} dictionary)' % dictIntSettings)
            return
        if callback is not None:
            proxyCallback = lambda requestID, resultID, errorStr, ext = {}: callback(resultID)
        else:
            proxyCallback = None
        if self.__proxy:
            self.__proxy._doCmdIntArr(AccountCommands.CMD_ADD_INT_USER_SETTINGS, arr, proxyCallback)
        elif callback:
            callback(AccountCommands.RES_NON_PLAYER)
        return

    def delIntSettings(self, listIntKeys, callback = None):
        arr = []
        for k in listIntKeys:
            if isinstance(k, int):
                arr.append(k)
            else:
                LOG_ERROR('Bad key in delIntSettings: %r (should be int)' % k)
                return

        if arr:
            if callback is not None:
                proxyCallback = lambda requestID, resultID, errorStr, ext = {}: callback(resultID)
            else:
                proxyCallback = None
            if self.__proxy:
                self.__proxy._doCmdIntArr(AccountCommands.CMD_DEL_INT_USER_SETTINGS, arr, proxyCallback)
            elif callback:
                callback(AccountCommands.RES_NON_PLAYER)
        else:
            LOG_ERROR('Bad delIntSettings arr: %r (should be [int] list)' % arr)
            return
        return

    def __onGetResponse(self, statName, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache.get(statName, None))
            return

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return
