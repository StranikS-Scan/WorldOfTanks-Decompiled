# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/game_control/gui_lootboxes_controller.py
import logging
import typing
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_LOOT_BOXES, LOOT_BOXES_COUNT, LOOT_BOXES_LAST_ADDED_ID
from adisp import adisp_process
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from constants import LOOTBOX_TOKEN_PREFIX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.impl.lobby.loot_box.loot_box_bonus_parsers.default_parser import parseLimitBoxInfoSection, parseAllOfBonusInfoSection
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.server_events.bonuses import mergeBonuses
from gui.shared.event_dispatcher import showShop
from gui.shared.gui_items.loot_box import EVENT_LOOT_BOXES_CATEGORY, EventLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxGetInfoProcessor
from gui_lootboxes.gui.bonuses.bonuses_order_config import readConfig, BONUSES_CONFIG_PATH_LIST
from gui_lootboxes.gui.storage_context.hangar_optimizer import HangarOptimizer
from helpers import dependency
from helpers.server_settings import GUI_LOOT_BOXES_CONFIG
from shared_utils import nextTick, findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGuiLootBoxesController, ISteamCompletionController, ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
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
    __slots__ = ('__em', '__boxesCount', '__isLootBoxesAvailable', '__isActive', '__boxInfo', '__bonusesConfig', '__hangarOptimizer')
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
        self.onBoxesUpdate = Event.Event(self.__em)
        self.onBoxInfoUpdated = Event.Event(self.__em)
        self.__bonusesConfig = None
        self.__boxesCount = 0
        self.__boxInfo = {}
        self.__isLootBoxesAvailable = False
        self.__isActive = False
        self.__boxCountToGuaranteedBonus = 0
        self.__settings = _SettingsMgr()
        self.__isFirstStorageEnter = True
        self.__hangarOptimizer = HangarOptimizer()
        self.__shopWindowHandler = {}
        return

    @property
    def isConsumesEntitlements(self):
        return False

    @property
    def boxCountToGuaranteedBonus(self):
        return self.__boxCountToGuaranteedBonus

    def onLobbyInited(self, event):
        if self.__bonusesConfig is None:
            self.__bonusesConfig = readConfig(BONUSES_CONFIG_PATH_LIST)
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        g_clientUpdateManager.addCallbacks({'lootBoxes': self.__onBoxesUpdate})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__limitedUIController.startObserve(LuiRules.GUI_LOOTBOXES_ENTRY_POINT, self.__onStatusChange)
        self.__boxesCount = self.__getBoxesCount()
        self.__updateBoxInfo()
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

    def getGuaranteedBonusLimit(self, boxType):
        return self.getBoxInfo(boxType).get('limit', 0)

    def openShop(self, lootboxID=None):
        if self.isBuyAvailable():
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootboxID)) if lootboxID else None
            handler = self.__shopWindowHandler.get(lootBox.getCategory(), None) if lootBox else None
            if handler:
                handler()
            else:
                showShop(getShopURL() + self.__getConfig().getShopCategoryUrl())
        return

    def getBoxInfo(self, boxType):
        if not self.__boxInfo:
            self.__updateBoxInfo()
        return self.__boxInfo.get(boxType, {})

    def getStoreInfo(self, category=EVENT_LOOT_BOXES_CATEGORY):
        return {lb.getType():lb for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == category}

    def getBoxesIDs(self, category=EVENT_LOOT_BOXES_CATEGORY):
        return set((lb.getID() for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == category))

    def getBoxesCount(self):
        return self.__boxesCount

    def getBoxesInfo(self):
        if not self.__boxInfo:
            self.__updateBoxInfo()
        return self.__boxInfo

    def getVehicleLevels(self, boxType):
        boxInfo = self.getBoxInfo(boxType)
        levels = set()
        for slot in boxInfo.get('slots', {}).itervalues():
            bonuses = mergeBonuses([ bonus for bonus in slot.get('bonuses', []) if bonus.getName() == 'vehicles' ])
            for vehicleBonus in bonuses:
                for vehicle in vehicleBonus.getValue().iterkeys():
                    levels.add(self.__itemsCache.items.getItemByCD(vehicle).level)

        return levels

    def getBonusesOrder(self, category=None):
        return self.__bonusesConfig.orders.get(category, self.__bonusesConfig.defaultOrder)

    def getHangarOptimizer(self):
        return self.__hangarOptimizer

    def addShopWindowHandler(self, keyHandler, handler):
        if keyHandler and handler:
            self.__shopWindowHandler[keyHandler] = handler

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getGuiLootBoxesConfig()

    def __stop(self):
        self.__hangarOptimizer.clear()
        self.__em.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__boxesCount = 0
        self.__boxInfo.clear()
        self.__limitedUIController.stopObserve(LuiRules.GUI_LOOTBOXES_ENTRY_POINT, self.__onStatusChange)

    def __onServerSettingsChange(self, settings):
        if 'isLootBoxesEnabled' in settings:
            self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
            self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        if GUI_LOOT_BOXES_CONFIG in settings:
            self.onStatusChange()
            self.__isActive = self.isEnabled()
        if 'lootBoxes_config' in settings:
            self.__updateBoxInfo()
            boxesCount = self.__getBoxesCount()
            self.onBoxesCountChange(boxesCount, self.__boxesCount)
            self.__boxesCount = boxesCount

    def __getBoxesCount(self):
        return sum((lb.getInventoryCount() for lb in self.__itemsCache.items.tokens.getLootBoxes().values()))

    def __onTokensUpdate(self, diff):
        if any((token.startswith(LOOTBOX_TOKEN_PREFIX) for token in diff.iterkeys())):
            boxesCount = self.__getBoxesCount()
            self.onBoxesCountChange(boxesCount, self.__boxesCount)
            self.__boxesCount = boxesCount
            self.__updateLastAddedLootBox()
            self.__hadLootBoxesTokens(hasTokens=True)

    def __onBoxesUpdate(self, diff):
        boxId = self.__boxInfo.get(EventLootBoxes.PREMIUM, {}).get('id')
        guaranteedBonusLimit = self.__boxInfo.get(EventLootBoxes.PREMIUM, {}).get('limit')
        boxHistoryData = diff.get('history', {}).get(boxId)
        if boxHistoryData:
            _, bonusData, _ = boxHistoryData
            _, opened, _ = bonusData.get('guaranteedBonusLimit', (0, 0, 0))
            self.__boxCountToGuaranteedBonus = guaranteedBonusLimit - opened
            self.onBoxesUpdate()

    def __updateLastAddedLootBox(self):
        lootBoxIdToCount = self.getSetting(LOOT_BOXES_COUNT) or {}
        lootBoxes = self.__itemsCache.items.tokens.getLootBoxes().values()
        boxToStore = findFirst(lambda lootBox: lootBoxIdToCount.get(lootBox.getID(), 0) < lootBox.getInventoryCount(), sorted(lootBoxes))
        if boxToStore is not None:
            self.setSetting(LOOT_BOXES_LAST_ADDED_ID, boxToStore.getID())
        lootBoxIdToCountStore = {lootBox.getID():lootBox.getInventoryCount() for lootBox in lootBoxes if lootBox.getInventoryCount() > 0}
        self.setSetting(LOOT_BOXES_COUNT, lootBoxIdToCountStore)
        return

    def __updateBoxCountToGuaranteedBonus(self):
        opened = 0
        guaranteedBonusLimit = self.__boxInfo.get(EventLootBoxes.PREMIUM, {}).get('limit', 0)
        boxHistoryData = self.__boxInfo.get(EventLootBoxes.PREMIUM, {}).get('history')
        if boxHistoryData:
            _, bonusData, _ = boxHistoryData
            if bonusData is not None:
                _, opened, _ = bonusData.get('guaranteedBonusLimit', (0, 0, 0))
        self.__boxCountToGuaranteedBonus = guaranteedBonusLimit - opened
        return

    @nextTick
    @adisp_process
    def __updateBoxInfo(self):
        boxes = [ lb for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == EVENT_LOOT_BOXES_CATEGORY ]
        boxInfoData = {}
        result = None
        if boxes:
            result = yield LootBoxGetInfoProcessor(boxes).request()
        if result and result.success and result.auxData:
            for lootBoxID, lootBoxData in result.auxData.iteritems():
                if lootBoxID in self.getBoxesIDs():
                    boxData = dict()
                    data = lootBoxData.get('bonus', {})
                    lbType = lootBoxData['type']
                    boxData['id'] = lootBoxID
                    boxData['limit'] = parseLimitBoxInfoSection(lootBoxData.get('config', {}))
                    boxData['slots'] = parseAllOfBonusInfoSection(data.get('allof', {}))
                    boxData['history'] = lootBoxData.get('history', (0, None, 0))
                    boxInfoData[lbType] = boxData

        self.__boxInfo = boxInfoData
        self.onBoxInfoUpdated()
        self.__updateBoxCountToGuaranteedBonus()
        return

    def __onStatusChange(self, *_):
        self.onStatusChange()

    def __hadLootBoxesTokens(self, hasTokens=False):
        uiStorage = self.__settingsCore.serverSettings.getUIStorage2()
        isEntryPointEnabled = uiStorage.get(UI_STORAGE_KEYS.GUI_LOOTBOXES_ENTRY_POINT)
        if not isEntryPointEnabled:
            tokens = self.__itemsCache.items.tokens.getTokens()
            if hasTokens or any((token for token in tokens if token.startswith(LOOTBOX_TOKEN_PREFIX))):
                self.__settingsCore.serverSettings.saveInUIStorage2({UI_STORAGE_KEYS.GUI_LOOTBOXES_ENTRY_POINT: True})
