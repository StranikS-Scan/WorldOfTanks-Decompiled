# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/base/stamper.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.gift_system.hubs.subsystems import BaseHubSubsystem
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from helpers.server_settings import GiftEventConfig

class IGiftEventStamper(BaseHubSubsystem):

    def isBalanceAvailable(self):
        raise NotImplementedError

    def wasBalanceAvailable(self):
        raise NotImplementedError

    def getStampCount(self, stampName):
        raise NotImplementedError


class GiftEventBaseStamper(IGiftEventStamper):
    __slots__ = ('__updateCallback', '__isBalanceAvailable', '__wasBalanceAvailable')
    _STAMPS = set()
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, eventSettings, updateCallback):
        super(GiftEventBaseStamper, self).__init__(eventSettings)
        self.__updateCallback = updateCallback
        self.__isBalanceAvailable = self.__wasBalanceAvailable = False
        self.__initBalanceWatchers()
        g_clientUpdateManager.addCallbacks({'cache.mayConsumeWalletResources': self.__updateBalanceAvailability,
         'cache.entitlements': self.__updateBalanceContent})

    def destroy(self):
        self.__itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__updateCallback = None
        return

    def isBalanceAvailable(self):
        return self.__isBalanceAvailable

    def wasBalanceAvailable(self):
        return self.__wasBalanceAvailable

    def getStampCount(self, stampName):
        return self.__itemsCache.items.stats.entitlements.get(stampName, 0)

    def _isNotificationsEnabled(self):
        return self._settings.isEnabled

    def __initBalanceWatchers(self):
        if not self.__itemsCache.isSynced():
            self.__itemsCache.onSyncCompleted += self.__onItemsSyncCompleted
            return
        self.__onItemsSyncCompleted()

    def __onItemsSyncCompleted(self, *_):
        mayConsumeWalletResources = self.__itemsCache.items.stats.mayConsumeWalletResources
        self.__isBalanceAvailable = self.__wasBalanceAvailable = mayConsumeWalletResources
        self.__itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted
        self.__notifyGiftEventHub()

    def __notifyGiftEventHub(self):
        if self._isNotificationsEnabled():
            self.__updateCallback()

    def __updateBalanceAvailability(self, isAvailable):
        if self.__isBalanceAvailable != isAvailable:
            self.__isBalanceAvailable = isAvailable
            self.__wasBalanceAvailable = self.__wasBalanceAvailable or isAvailable
            self.__notifyGiftEventHub()

    def __updateBalanceContent(self, entitlementsData):
        if self._STAMPS & set(entitlementsData.keys()):
            self.__notifyGiftEventHub()
