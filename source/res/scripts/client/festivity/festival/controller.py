# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/controller.py
import logging
from Event import Event
from PlayerEvents import g_playerEvents
from festivity.base import FestivityQuestsHangarFlag
from festivity.festival.constants import FEST_DATA_SYNC_KEY, FestSyncDataKeys
from festivity.festival.item_info import FestivalItemInfo
from festivity.festival.package_shop import FestivalPackageShop
from festivity.festival.player_card import PlayerCard
from festivity.festival.requester import FestCriteria
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import festival
from items.components.festival_constants import FEST_CONFIG, FEST_ITEM_TYPE, FEST_ITEM_QUALITY
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.festival import IFestivalController
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_RND_HINT_MIN_TICKETS_COUNT = 6
_DEFAULT_QUESTS_FLAG = FestivityQuestsHangarFlag(None, None, None)
_WHERE_EARN_TICKETS_LIMIT = 1
_DEFAULT_CARD_TAB = FEST_ITEM_TYPE.BASIS

class FestivalController(IFestivalController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __bootcampController = dependency.descriptor(IBootcampController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(FestivalController, self).__init__()
        self.__commandProcessor = None
        self.__items = None
        self.__magicBasis = None
        self.__globalPlayerCard = None
        self.__shop = None
        self.__currentCardTabState = _DEFAULT_CARD_TAB
        self.onStateChanged = Event()
        self.onDataUpdated = Event()
        return

    def init(self):
        self.__commandProcessor = dependency.instance(IFestivityFactory).getProcessor()

    def fini(self):
        self.__commandProcessor = None
        self.__shop = None
        return

    def onDisconnected(self):
        self.__currentCardTabState = _DEFAULT_CARD_TAB

    def onLobbyInited(self, event):
        if self.__bootcampController.isInBootcamp():
            return
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def onAvatarBecomePlayer(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged

    def isEnabled(self):
        if self.__bootcampController.isInBootcamp():
            return False
        config = self.__lobbyContext.getServerSettings().getFestivalConfig()
        return config[FEST_CONFIG.FESTIVAL_ENABLED] and config[FEST_CONFIG.PLAYER_CARDS_ENABLED]

    def getHangarQuestsFlagData(self):
        return _DEFAULT_QUESTS_FLAG

    def setCurrentCardTabState(self, tabState):
        self.__currentCardTabState = tabState

    def getCurrentCardTabState(self):
        return self.__currentCardTabState

    def getReceivedItemsCount(self):
        criteria = FestCriteria.INVENTORY | ~FestCriteria.TYPE(FEST_ITEM_TYPE.RANK) | ~FestCriteria.QUALITY(FEST_ITEM_QUALITY.SPECIAL)
        return len(self.getFestivalItems(criteria))

    def getTotalItemsCount(self):
        criteria = ~FestCriteria.TYPE(FEST_ITEM_TYPE.RANK) | ~FestCriteria.QUALITY(FEST_ITEM_QUALITY.SPECIAL)
        return len(self.getFestivalItems(criteria))

    def getTickets(self):
        return self.__itemsCache.items.festivity.getTickets()

    def getPlayerCard(self):
        return PlayerCard(self.__itemsCache.items.festivity.getPlayerCard())

    def getFestivalItems(self, criteria=REQ_CRITERIA.EMPTY):
        result = {}
        for itemID, item in self.__getItems().iteritems():
            if criteria(item):
                result[itemID] = item

        return result

    def getUnseenItems(self, typeName=None):
        criteria = FestCriteria.INVENTORY | FestCriteria.UNSEEN
        if typeName is not None:
            criteria |= FestCriteria.TYPE(typeName)
        return self.getFestivalItems(criteria)

    def markItemsAsSeen(self, itemsIDs):
        self.__commandProcessor.markItemsAsSeen(itemsIDs)

    def getGlobalPlayerCard(self):
        return self.__globalPlayerCard or self.getPlayerCard()

    def setGlobalPlayerCard(self, playerCard):
        self.__globalPlayerCard = playerCard

    def getPackages(self):
        return self.__getShop().getPackages()

    def getPackageByID(self, pkgID):
        return self.__getShop().getPackageByID(pkgID)

    def isCommonItemCollected(self):
        return self.__invCommonItemsCount() == self.getTotalCommonItem()

    def getTotalCommonItem(self):
        return len(self.getCommonItems(FEST_ITEM_TYPE.ANY))

    def getRandomCost(self, randomName):
        randomConfig = self.__lobbyContext.getServerSettings().getFestivalConfig()[FEST_CONFIG.RANDOM_PRICES]
        inventoryMask = self.__itemsCache.items.festivity.getItemsBytes()
        return festival.getRandomCost(randomName, inventoryMask, randomConfig)[0]

    def canBuyAnyRandomPack(self):
        inventoryMask = self.__itemsCache.items.festivity.getItemsBytes()
        return festival.canBuyOneMorePacks(inventoryMask)

    def needToShowWhereEarnTickets(self):
        invCommonItemsCount = len(self.getFestivalItems(FestCriteria.QUALITY(FEST_ITEM_QUALITY.COMMON) | FestCriteria.INVENTORY))
        return invCommonItemsCount <= _WHERE_EARN_TICKETS_LIMIT

    def getCommonItems(self, randomName):
        result = {}
        for itemID, item in self.__getItems().iteritems():
            if item.getType() == FEST_ITEM_TYPE.RANK:
                continue
            if (randomName == FEST_ITEM_TYPE.ANY or item.getType() == randomName) and item.getQuality() in (FEST_ITEM_QUALITY.COMMON, FEST_ITEM_QUALITY.STARTING):
                result[itemID] = item

        return result

    def getMagicBasis(self):
        if self.__magicBasis is None:
            for item in self.__getItems().itervalues():
                if item.getAltResIds():
                    self.__magicBasis = item
                    break

        return self.__magicBasis

    def canShowRandomBtnHint(self):
        return self.getTickets() >= _RND_HINT_MIN_TICKETS_COUNT

    def __onClientUpdated(self, diff, _):
        if FEST_DATA_SYNC_KEY in diff:
            self.onDataUpdated(diff[FEST_DATA_SYNC_KEY].keys())

    def __onServerSettingChanged(self, diff):
        if 'festival_config' in diff:
            festConfig = diff['festival_config']
            updatedKeys = []
            if FEST_CONFIG.PACKAGES in festConfig:
                self.__getShop().update(festConfig[FEST_CONFIG.PACKAGES])
                updatedKeys.append(FestSyncDataKeys.PACKAGES)
            if FEST_CONFIG.RANDOM_PRICES in festConfig:
                updatedKeys.append(FestSyncDataKeys.RANDOM_PRICES)
            if FEST_CONFIG.FESTIVAL_ENABLED in festConfig or FEST_CONFIG.PLAYER_CARDS_ENABLED in festConfig:
                self.onStateChanged()
            if updatedKeys:
                self.onDataUpdated(updatedKeys)

    def __getItems(self):
        if self.__items is None:
            self.__items = {itemID:FestivalItemInfo(itemID) for itemID in festival.g_cache.getCollection()}
        return self.__items

    def __getShop(self):
        if self.__shop is None:
            self.__shop = FestivalPackageShop(self.__lobbyContext.getServerSettings().getFestivalConfig().get(FEST_CONFIG.PACKAGES, {}))
        return self.__shop

    def __invCommonItemsCount(self):
        commonItems = self.getCommonItems(FEST_ITEM_TYPE.ANY)
        return sum((1 for item in commonItems.itervalues() if item.isInInventory()))
