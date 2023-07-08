# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/resource_well.py
import json
from functools import partial
import typing
import AccountCommands
from gui.resource_well.resource_well_constants import RESOURCE_WELL_PDATA_KEY
from shared_utils.account_helpers.diff_utils import synchronizeDicts
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, List, Optional, Tuple

class ResourceWell(object):

    def __init__(self, syncData, commandsProxy):
        self.__cache = {}
        self.__ignore = True
        self.__syncData = syncData
        self.__commandsProxy = commandsProxy

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def getCache(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def synchronize(self, isFullSync, diff):
        if isFullSync and self.__cache:
            self.__cache.clear()
        if RESOURCE_WELL_PDATA_KEY in diff:
            synchronizeDicts(diff[RESOURCE_WELL_PDATA_KEY], self.__cache.setdefault(RESOURCE_WELL_PDATA_KEY, {}))

    def putResources(self, resources, reward, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr)
            else:
                proxy = None
            resourcesStr = json.dumps(resources)
            self.__commandsProxy.perform(AccountCommands.CMD_RESOURCE_WELL_PUT, [reward, resourcesStr], proxy)
            return

    def takeBack(self, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = (lambda requestID, resultID, errorStr, ext={}: callback(resultID)) if callback is not None else None
            self.__commandsProxy.perform(AccountCommands.CMD_RESOURCE_WELL_TAKE, 0, proxy)
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
