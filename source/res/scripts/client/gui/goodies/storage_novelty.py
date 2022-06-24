# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/storage_novelty.py
import Event
from account_helpers.AccountSettings import AccountSettings, DEMOUNT_KIT_SEEN, RECERTIFICATION_FORM_SEEN
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.storage_novelty import IStorageNovelty
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache

class StorageNovelty(IStorageNovelty):
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.onUpdated = Event.Event()
        self.__showNovelty = 0

    @property
    def __noveltyData(self):
        return [{'f': self.__goodiesCache.getDemountKit,
          'seen': DEMOUNT_KIT_SEEN}, {'f': self.__goodiesCache.getRecertificationForms,
          'seen': RECERTIFICATION_FORM_SEEN}]

    def init(self):
        g_clientUpdateManager.addCallbacks({'goodies': self.__onGoodiesUpdated})
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        self.__resolveNovelty()

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync

    def setAsSeen(self, item):
        if self.noveltyCount:
            AccountSettings.setCounters(item, True)
            self.__resolveNovelty()

    @property
    def noveltyCount(self):
        return self.__showNovelty

    def __onGoodiesUpdated(self, *_):
        self.__resolveNovelty()

    @staticmethod
    def getItemsStatus(args):
        items = args['f'](REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT | REQ_CRITERIA.DEMOUNT_KIT.IS_ENABLED)
        return not AccountSettings.getCounters(args['seen']) and items is not None and len(items)

    @property
    def showNovelty(self):
        return self.__showNovelty

    def __resolveNovelty(self):
        showNovelty = 0
        for item in self.__noveltyData:
            if self.getItemsStatus(item):
                showNovelty += 1

        if showNovelty != self.__showNovelty:
            self.__showNovelty = showNovelty
            self.onUpdated()

    def __onCacheResync(self, *_):
        self.__resolveNovelty()
