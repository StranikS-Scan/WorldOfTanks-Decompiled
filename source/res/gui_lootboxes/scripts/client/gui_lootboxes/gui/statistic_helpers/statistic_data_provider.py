# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/statistic_helpers/statistic_data_provider.py
import weakref
from collections import defaultdict
import typing
import Event
from constants import VERY_BIG_TIME
from debug_utils import LOG_WARNING
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from helpers.time_utils import getServerUTCTime
from lootboxes_common import mergeDiffStat
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from th_async import th_async, th_await, await_callback
if typing.TYPE_CHECKING:
    from typing import Dict

@replace_none_kwargs(itemsCache=IItemsCache)
def makeDefaultData(lbId, itemsCache=None):
    lootBox = itemsCache.items.tokens.getLootBoxByID(int(lbId))
    expires = lootBox.getAutoOpenTime() or VERY_BIG_TIME
    return {'expires': expires,
     'ver': 0,
     'stat': {}}


class LootBoxStatFetcher(object):

    def __init__(self, storage):
        self._storage = storage

    def requestData(self, callback):
        raise NotImplementedError

    def onAccountBecomePlayer(self):
        raise NotImplementedError

    def onAccountBecomeNonPlayer(self):
        raise NotImplementedError

    def processResult(self, *args, **kwargs):
        raise NotImplementedError

    def onServerSettingsChanged(self, diff):
        raise NotImplementedError


class StatisticDataCache(object):
    _providers = {}
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__cacheStat = defaultdict(lambda : {'expires': 0,
         'ver': 0,
         'stat': {}})
        self.__isFirstSync = True
        self.__em = Event.EventManager()
        self.onBaseStatCollect = Event.Event(self.__em)

    @property
    def allCacheStat(self):
        res = []
        for data in self.__cacheStat.values():
            if data['expires'] > getServerUTCTime():
                res.append(data['stat'])

        return res

    @property
    def expiresInfo(self):
        res = {}
        for lbID, data in self.__cacheStat.iteritems():
            if data['expires'] > getServerUTCTime():
                res[lbID] = data['expires']

        return res

    def getStatByLootboxID(self, lootboxID):
        if lootboxID in self.__cacheStat:
            data = self.__cacheStat[lootboxID]
            if data['expires'] > getServerUTCTime():
                return data['stat']
        return {}

    def getVersionByLootboxID(self, lootboxID=None):
        return self.__cacheStat[lootboxID]['ver'] if lootboxID is not None and lootboxID in self.__cacheStat else sum((stat.get('ver', 0) for stat in self.__cacheStat.values()))

    def canApplySnapshot(self, boxID, startVer):
        return self.__cacheStat[boxID]['ver'] == startVer if boxID in self.__cacheStat else None

    def applyOpenResult(self, lootboxID, result, count):
        if lootboxID not in self.__cacheStat:
            self.__cacheStat[lootboxID] = makeDefaultData(lootboxID)
        lootboxStat = self.__cacheStat[lootboxID]
        for diff in result:
            mergeDiffStat(lootboxStat['stat'], diff)

        lootboxStat['ver'] += count

    @th_async
    def requestBaseStat(self):
        if not self.__lobbyContext.getServerSettings().getLootBoxStatisticsConfig().get('enabled'):
            return
        futures = [ await_callback(lambda callback, p=prov: p.requestData(lambda *a: (p.processResult(*a), callback(*a))))() for prov in self._providers.values() ]
        if not futures:
            return
        for fut in futures:
            yield th_await(fut)

        self.onBaseStatCollect()

    def onAccountBecomePlayer(self):
        for provider in self._providers.values():
            provider.onAccountBecomePlayer()

        if self.__isFirstSync:
            self.requestBaseStat()
            self.__isFirstSync = False

    def onAccountBecomeNonPlayer(self):
        for provider in self._providers.values():
            provider.onAccountBecomeNonPlayer()

    def onServerSettingsChanged(self, diff):
        for provider in self._providers.values():
            provider.onServerSettingsChanged(diff)

    def onDisconnected(self):
        self.__clear()

    def registerProvider(self, key, provider):
        if key not in self._providers:
            self._providers[key] = provider(weakref.proxy(self))
        else:
            LOG_WARNING('Provider: {} is already registered'.format(key))

    def fillCache(self, statData):
        for lbID, data in statData.iteritems():
            lootboxInfo = self.__cacheStat[lbID]
            lootboxInfo['expires'] = data[0]
            lootboxInfo['ver'] = data[1]
            lootboxInfo['stat'] = data[2]

    def __clear(self):
        self.__cacheStat.clear()
        self.__isFirstSync = True

    def fini(self):
        self.__clear()
        self.__em.clear()
