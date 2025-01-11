# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/game_control/gui_lootboxes_controller.py
import logging
import typing
from gui_lootboxes.gui.bonuses.bonuses_order_config import readConfig, BONUSES_CONFIG_PATH_LIST
from gui_lootboxes.gui.storage_context.hangar_optimizer import HangarOptimizer
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_LOOT_BOXES, LOOT_BOXES_COUNT, LOOT_BOXES_LAST_ADDED_ID
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from constants import Configs
from constants import LOOTBOX_TOKEN_PREFIX, LOOTBOX_KEY_PREFIX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared.event_dispatcher import showShop
from gui.shared.gui_items.loot_box import EVENT_LOOT_BOXES_CATEGORY
from helpers import dependency
from helpers.server_settings import GUI_LOOT_BOXES_CONFIG
from lootboxes_common import makeLBKeyTokenID
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGuiLootBoxesController, ISteamCompletionController, ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.loot_box.loot_box_helper import getKeyByTokenID, getKeyByID, hasInfiniteLootBoxes
if typing.TYPE_CHECKING:
    from typing import Any
_logger = logging.getLogger(__name__)

class _SettingsMgr(object):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def getSetting(self, setting):
        return (AccountSettings.getSettings(GUI_LOOT_BOXES) or {}).get(setting)

    def setSetting(self, setting, newValue):
        settings = AccountSettings.getSettings(GUI_LOOT_BOXES) or {}
        oldValue = settings.get(setting)
        if oldValue != newValue:
            settings[setting] = newValue
            AccountSettings.setSettings(GUI_LOOT_BOXES, settings)


class GuiLootBoxesController(IGuiLootBoxesController):
    __slots__ = ('__em', '__boxesCount', '__isLootBoxesAvailable', '__isActive', '__bonusesConfig', '__hangarOptimizer', '__boxKeysCount')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __steam = dependency.descriptor(ISteamCompletionController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        super(GuiLootBoxesController, self).__init__()
        self.__em = Event.EventManager()
        self.onStatusChange = Event.Event(self.__em)
        self.onAvailabilityChange = Event.Event(self.__em)
        self.onBoxesCountChange = Event.Event(self.__em)
        self.onKeysUpdate = Event.Event(self.__em)
        self.onBoxesHistoryUpdate = Event.Event(self.__em)
        self.onBoxInfoUpdated = Event.Event(self.__em)
        self.__bonusesConfig = None
        self.__boxesCount = 0
        self.__boxKeysCount = 0
        self.__isLootBoxesAvailable = False
        self.__isActive = False
        self.__settings = _SettingsMgr()
        self.__isFirstStorageEnter = True
        self.__hangarOptimizer = HangarOptimizer()
        self.__shopWindowHandler = {}
        return

    @property
    def isConsumesEntitlements(self):
        return False

    def onLobbyInited(self, event):
        if self.__bonusesConfig is None:
            self.__bonusesConfig = readConfig(BONUSES_CONFIG_PATH_LIST)
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        g_clientUpdateManager.addCallbacks({'lootBoxes': self.__onBoxesUpdate})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__limitedUIController.startObserve(LuiRules.GUI_LOOTBOXES_ENTRY_POINT, self.__onStatusChange)
        self.__boxesCount = self.__getBoxesCount()
        self.__boxKeysCount = self.__getBoxKeysCount()
        self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        self.__hadLootBoxesTokens()
        self.__isActive = self.isEnabled()
        self.__isFirstStorageEnter = True
        self.__updateLastAddedLootBox()
        self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
        return

    def getSetting(self, setting):
        return self.__settings.getSetting(setting)

    def setSetting(self, setting, value):
        self.__settings.setSetting(setting, value)

    def onAvatarBecomePlayer(self):
        self.__stop()
        self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        self.__isActive = self.isEnabled()

    def onDisconnected(self):
        self.__stop()
        self.__isLootBoxesAvailable = False
        self.__isActive = False

    def fini(self):
        self.__stop()
        super(GuiLootBoxesController, self).fini()

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def isLootBoxesAvailable(self):
        return self.__lobbyContext.getServerSettings().isLootBoxesEnabled()

    def isBuyAvailable(self):
        return self.__getConfig().isBuyAvailable

    def isFirstStorageEnter(self):
        return self.__isFirstStorageEnter

    def setStorageVisited(self):
        self.__isFirstStorageEnter = False

    def getDayLimit(self):
        return self.__getConfig().lootBoxBuyDayLimit

    def openShop(self, lootboxID=None):
        if self.isBuyAvailable():
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootboxID)) if lootboxID else None
            handler = self.__shopWindowHandler.get(lootBox.getCategory(), None) if lootBox else None
            if handler:
                handler()
            else:
                showShop(getShopURL() + self.__getConfig().getShopCategoryUrl())
        return

    def getStoreInfo(self, category=EVENT_LOOT_BOXES_CATEGORY):
        return {lb.getType():lb for lb in self.getGuiLootBoxes() if lb.getCategory() == category}

    def getBoxesIDs(self, category=EVENT_LOOT_BOXES_CATEGORY):
        return set((lb.getID() for lb in self.getGuiLootBoxes() if lb.getCategory() == category))

    def getBoxesCount(self):
        return self.__boxesCount

    def getBoxKeysCount(self):
        return self.__boxKeysCount

    def getKeyByID(self, keyID):
        return getKeyByID(keyID)

    def getKeyByTokenID(self, tokenID):
        return getKeyByTokenID(tokenID)

    def getBonusesOrder(self, category=None):
        return self.__bonusesConfig.orders.get(category, self.__bonusesConfig.defaultOrder)

    def getHangarOptimizer(self):
        return self.__hangarOptimizer

    def addShopWindowHandler(self, keyHandler, handler):
        if keyHandler and handler:
            self.__shopWindowHandler[keyHandler] = handler

    def hasLootboxKey(self):
        return any((token.startswith(LOOTBOX_KEY_PREFIX) for token in self.__itemsCache.items.tokens.getTokens().iterkeys()))

    def hasInfiniteLootboxes(self):
        return hasInfiniteLootBoxes(itemsCache=self.__itemsCache)

    def getGuiLootBoxes(self):
        return [ lb for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.isVisible() ]

    def getGuiLootBoxByTokenID(self, tokenID):
        lb = self.__itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
        return lb if lb and lb.isVisible() else None

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getGuiLootBoxesConfig()

    def __stop(self):
        self.__hangarOptimizer.clear()
        self.__em.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__boxesCount = 0
        self.__boxKeysCount = 0
        self.__limitedUIController.stopObserve(LuiRules.GUI_LOOTBOXES_ENTRY_POINT, self.__onStatusChange)

    def __onServerSettingsChange(self, settings):
        if 'isLootBoxesEnabled' in settings:
            self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
            self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        if GUI_LOOT_BOXES_CONFIG in settings:
            self.onStatusChange()
            self.__isActive = self.isEnabled()
        if 'lootBoxes_config' in settings:
            self.onBoxInfoUpdated()
            boxesCount = self.__getBoxesCount()
            self.onBoxesCountChange(boxesCount, self.__boxesCount)
            self.__boxesCount = boxesCount
        if Configs.LOOTBOX_KEYS_CONFIG in settings:
            self.__boxKeysCount = self.__getBoxKeysCount()
            self.onKeysUpdate()

    def __getBoxesCount(self):
        return sum((lb.getInventoryCount() for lb in self.getGuiLootBoxes() if not lb.isHiddenCount()))

    def __getBoxKeysCount(self):
        count = 0
        for keyID in self.__lobbyContext.getServerSettings().getLootBoxKeyConfig():
            keyToken = makeLBKeyTokenID(keyID)
            count += self.__itemsCache.items.tokens.getTokenCount(keyToken)

        return count

    def __onTokensUpdate(self, diff):
        if any((token.startswith(LOOTBOX_TOKEN_PREFIX) for token in diff.iterkeys())):
            boxesCount = self.__getBoxesCount()
            self.onBoxesCountChange(boxesCount, self.__boxesCount)
            self.__boxesCount = boxesCount
            self.__updateLastAddedLootBox()
            self.__hadLootBoxesTokens()
        if any((token.startswith(LOOTBOX_KEY_PREFIX) for token in diff.iterkeys())):
            self.__boxKeysCount = self.__getBoxKeysCount()
            self.onKeysUpdate()

    def __onBoxesUpdate(self, diff):
        if 'history' in diff:
            self.onBoxesHistoryUpdate(diff['history'])

    def __updateLastAddedLootBox(self):
        lootBoxIdToCount = self.getSetting(LOOT_BOXES_COUNT) or {}
        lootBoxes = self.getGuiLootBoxes()
        boxToStore = findFirst(lambda lootBox: lootBoxIdToCount.get(lootBox.getID(), 0) < lootBox.getInventoryCount(), sorted(lootBoxes))
        if boxToStore is not None:
            self.setSetting(LOOT_BOXES_LAST_ADDED_ID, boxToStore.getID())
        lootBoxIdToCountStore = {lootBox.getID():lootBox.getInventoryCount() for lootBox in lootBoxes if lootBox.getInventoryCount() > 0}
        self.setSetting(LOOT_BOXES_COUNT, lootBoxIdToCountStore)
        return

    def __onStatusChange(self, *_):
        self.onStatusChange()

    def __hadLootBoxesTokens(self):
        uiStorage = self.__settingsCore.serverSettings.getUIStorage2()
        isEntryPointEnabled = uiStorage.get(UI_STORAGE_KEYS.GUI_LOOTBOXES_ENTRY_POINT)
        if not isEntryPointEnabled and self.__boxesCount > 0:
            self.__settingsCore.serverSettings.saveInUIStorage2({UI_STORAGE_KEYS.GUI_LOOTBOXES_ENTRY_POINT: True})
