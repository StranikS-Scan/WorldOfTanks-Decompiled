# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/comp7/entitlements_cache.py
from adisp import adisp_process, adisp_async
from comp7_common import SEASON_POINTS_ENTITLEMENTS
from gui.entitlements.entitlements_requester import EntitlementsRequester

class EntitlementsCache(object):
    __slots__ = ('__cache', '__requester', '__isSynced')
    __COMP7_CLIENT_ENTITLEMENTS = SEASON_POINTS_ENTITLEMENTS

    def __init__(self):
        self.__cache = {}
        self.__requester = EntitlementsRequester()
        self.__isSynced = False

    @property
    def isSynced(self):
        return self.__isSynced

    def getEntitlementCount(self, entitlementCode):
        return self.__cache.get(entitlementCode, {}).get('amount', 0)

    def reset(self):
        self.__cache = {}
        self.__requester.clear()
        self.__isSynced = False

    def clear(self):
        self.__cache = {}
        self.__requester.clear()
        self.__requester = None
        return

    @adisp_process
    def makePreload(self):
        yield self.__updateByCodes(self.__COMP7_CLIENT_ENTITLEMENTS)

    @adisp_process
    def reloadSeasonPoints(self, callback=None):
        result = yield self.__updateByCodes(SEASON_POINTS_ENTITLEMENTS)
        callback(result)

    @adisp_async
    @adisp_process
    def __updateByCodes(self, codesList, callback):
        self.__isSynced = False
        self.__isSynced, result = yield self.__requester.requestByCodes(codesList)
        self.__cache.update(result)
        callback(self.__isSynced)
