# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_items_controller.py
import logging
from constants import LOOTBOX_TOKEN_PREFIX
import Event
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IEventItemsController
from helpers import dependency
from gui.ClientUpdateManager import g_clientUpdateManager
_logger = logging.getLogger(__name__)

class EventItemsController(IEventItemsController):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(EventItemsController, self).__init__()
        self.onUpdated = Event.Event()
        self.__enabled = False
        self.__lastSelectedOption = {}

    def init(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def fini(self):
        self.onUpdated.clear()
        self.__lastSelectedOption = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def onLobbyInited(self, _):
        if self.getEventItemsCount():
            fmt = backport.text(R.strings.messenger.serviceChannelMessages.blackMarketItemSysMessage.text())
            SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.BlackMarketItem)

    def setSelectedOption(self, itemType, option):
        self.__lastSelectedOption[itemType] = option

    def getSelectedOption(self, itemType):
        return self.__lastSelectedOption.get(itemType)

    def __onTokensUpdate(self, diff):
        for tokenID in diff:
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                item = self._itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
                itemType = item.getType() if item else None
                if itemType == BLACK_MARKET_ITEM_TYPE:
                    self.onUpdated()

        return

    def isEnabled(self):
        return self.__enabled

    def isDisabled(self):
        return False

    def getOwnedItemsByType(self, itemType=None):
        return self.getEventItemsByType(itemType, True)

    def getEventItemsByType(self, itemType=None, onlyOwned=False):
        if itemType is None:
            return
        else:
            items = self.getAllAvailableEventItems() if onlyOwned else self.getAllEventItems()
            for item in items:
                if item is not None and item.getType() == itemType:
                    return item

            return

    def getItemByID(self, itemId=None, ignoreCount=False):
        if itemId is None:
            return
        else:
            item = self._itemsCache.items.tokens.getLootBoxByTokenID(itemId)
            return item if item is not None and (item.getInventoryCount() > 0 or ignoreCount) else None

    def getAllAvailableEventItems(self):
        result = []
        for _, item in self._itemsCache.items.tokens.getLootBoxes().iteritems():
            if item.isEvent() and item.getInventoryCount() > 0:
                result.append(item)

        return result

    def getAllEventItems(self):
        result = []
        for _, item in self._itemsCache.items.tokens.getLootBoxes().iteritems():
            if item.isEvent():
                result.append(item)

        return result

    def getEventItemsCount(self):
        return sum((item.getInventoryCount() for item in self.getAllEventItems()))

    def getEventItemsCountByType(self, itemType):
        return sum((item.getInventoryCount() for item in self.getAllEventItems() if item.getType() == itemType))

    def getItemTypeByID(self, itemId=None):
        if itemId is None:
            return
        else:
            item = self._itemsCache.items.tokens.getLootBoxByTokenID(itemId)
            return item.getType() if item is not None else None
