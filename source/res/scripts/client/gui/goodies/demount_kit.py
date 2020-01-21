# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/demount_kit.py
import Event
from account_helpers.AccountSettings import AccountSettings, DEMOUNT_KIT_SEEN
from goodies.goodie_constants import DEMOUNT_KIT_ID
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.demount_kit import IDemountKitNovelty
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache

def isDemountKitApplicableTo(module):
    if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and not module.isRemovable and not module.isDeluxe():
        goodiesCache = dependency.instance(IGoodiesCache)
        demountKit = goodiesCache.getDemountKit(DEMOUNT_KIT_ID)
        return demountKit and demountKit.enabled
    return False


class DemountKitNovelty(IDemountKitNovelty):
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.onUpdated = Event.Event()
        self.__showNovelty = False

    def init(self):
        g_clientUpdateManager.addCallbacks({'goodies': self.__onGoodiesUpdated})
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        self.__resolveNovelty()

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync

    def setAsSeen(self):
        AccountSettings.setCounters(DEMOUNT_KIT_SEEN, True)
        self.__resolveNovelty()

    @property
    def showNovelty(self):
        return self.__showNovelty

    @property
    def noveltyCount(self):
        return 1 if self.showNovelty else 0

    def __onGoodiesUpdated(self, *_):
        self.__resolveNovelty()

    def __resolveNovelty(self):
        showNovelty = not AccountSettings.getCounters(DEMOUNT_KIT_SEEN) and len(self.__goodiesCache.getDemountKits(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT | REQ_CRITERIA.DEMOUNT_KIT.IS_ENABLED)) > 0
        if showNovelty != self.__showNovelty:
            self.__showNovelty = showNovelty
            self.onUpdated()

    def __onCacheResync(self, *_):
        self.__resolveNovelty()
