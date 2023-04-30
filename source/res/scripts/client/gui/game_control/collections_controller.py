# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/collections_controller.py
import logging
import typing
from Event import Event, EventManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COLLECTIONS_SECTION, COLLECTION_WAS_ENABLED
from chat_shared import SYS_MESSAGE_TYPE
from collections_common import CollectionsConfig, g_collectionsRelatedItems, makeCollectionItemEntitlementName, makeCollectionRewardEntitlementName
from constants import Configs
from gui.collection.collections_constants import COLLECTION_ITEM_PREFIX_NAME
from gui.collection.collections_helpers import isItemNew
from gui.collection.entitlements_cache import EntitlementsCache
from helpers import dependency
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from messenger.proto.events import g_messengerEvents
from skeletons.gui.game_control import ICollectionsSystemController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import Dict
_logger = logging.getLogger(__name__)

class CollectionsSystemController(ICollectionsSystemController, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__eventsManager = EventManager()
        self.__entitlementsCache = EntitlementsCache()
        self.onServerSettingsChanged = Event(self.__eventsManager)
        self.onBalanceUpdated = Event(self.__eventsManager)
        self.onAvailabilityChanged = Event(self.__eventsManager)

    def onLobbyInited(self, event):
        self.__updateAvailability()
        if self.isEnabled():
            self.__entitlementsCache.updateAll(self.__onCacheUpdated)
            self.__updateRelatedItems()
        self._subscribe()

    def onDisconnected(self):
        self.__entitlementsCache.clear()
        self.__stop()

    def fini(self):
        self.__eventsManager.clear()
        self.__entitlementsCache.clear()
        self.__stop()

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def getCollection(self, collectionId):
        collection = self.__getConfig().getCollection(collectionId)
        if collection is None:
            _logger.error('Collection with id <%s> does not exist!', collectionId)
        return collection

    def isRelatedEventActive(self, collectionId):
        collection = self.getCollection(collectionId)
        return False if collection is None else collection.isRelatedEventActive

    def getCollectionItem(self, collectionId, itemId):
        collection = self.getCollection(collectionId)
        return collection.items.get(itemId) if collection is not None else None

    def getMaxItemCount(self, collectionId):
        return len(self.getCollection(collectionId).items)

    def getMaxProgressItemCount(self, collectionId):
        return sum((not item.isSpecial for item in self.getCollection(collectionId).items.itervalues()))

    def getNewCollectionItemCount(self, collectionId):
        collection = self.getCollection(collectionId)
        if collection is None:
            _logger.error('Collection with id <%s> does not exist!', collectionId)
            return 0
        else:
            return sum((self.isItemReceived(collectionId, item.itemId) and isItemNew(collectionId, item.itemId) for item in collection.items.itervalues()))

    def getReceivedItemCount(self, collectionId):
        balance = self.__entitlementsCache.getCollectionBalance(collectionId)
        return sum((code.startswith(COLLECTION_ITEM_PREFIX_NAME) for code in balance.iterkeys()))

    def getReceivedProgressItemCount(self, collectionId):
        balance = self.__entitlementsCache.getCollectionBalance(collectionId)
        collection = self.getCollection(collectionId)
        items = set((makeCollectionItemEntitlementName(collectionId, item.itemId) for item in collection.items.itervalues() if not item.isSpecial))
        return len(items.intersection(balance.keys()))

    def isRewardReceived(self, collectionId, requiredCount):
        balance = self.__entitlementsCache.getCollectionBalance(collectionId)
        return makeCollectionRewardEntitlementName(collectionId, requiredCount) in balance

    def isCollectionCompleted(self, collectionId):
        return self.getReceivedItemCount(collectionId) >= self.getMaxItemCount(collectionId)

    def isItemReceived(self, collectionId, itemId):
        return makeCollectionItemEntitlementName(collectionId, itemId) in self.__entitlementsCache.getBalance()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged), (g_messengerEvents.serviceChannel.onChatMessageReceived, self.__onChatMessageReceived))

    def __getRawConfig(self):
        return self.__getConfig().getRawData()

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().collectionsConfig

    def __stop(self):
        self._unsubscribe()

    @serverSettingsChangeListener(Configs.COLLECTIONS_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.__updateRelatedItems()
        self.__updateAvailability()
        self.onServerSettingsChanged()

    def __onChatMessageReceived(self, *ctx):
        _, message = ctx
        if self.isEnabled() and message.type == SYS_MESSAGE_TYPE.collectionEntitlementReceived.index():
            entitlementCode = message.data.get('entitlementName', '')
            self.__entitlementsCache.update(entitlementCode, self.__onCacheUpdated)

    def __onCacheUpdated(self, isSuccess, _):
        if isSuccess:
            self.onBalanceUpdated()

    def __updateRelatedItems(self):
        g_collectionsRelatedItems.setData(self.__getRawConfig())

    def __updateAvailability(self):
        if self.isEnabled() != self.__getWasEnabled():
            self.onAvailabilityChanged(self.isEnabled())
        self.__updateWasEnabled()

    def __getWasEnabled(self):
        settings = AccountSettings.getUIFlag(COLLECTIONS_SECTION)
        return settings.get(COLLECTION_WAS_ENABLED, self.isEnabled())

    def __updateWasEnabled(self):
        settings = AccountSettings.getUIFlag(COLLECTIONS_SECTION)
        settings[COLLECTION_WAS_ENABLED] = self.isEnabled()
        AccountSettings.setUIFlag(COLLECTIONS_SECTION, settings)
