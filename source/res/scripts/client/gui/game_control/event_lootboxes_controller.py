# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_lootboxes_controller.py
import logging
import typing
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EVENT_LOOT_BOXES, LOOT_BOXES, LOOT_BOXES_EVENT_UNIQUE_ID, LOOT_BOXES_WAS_FINISHED, LOOT_BOXES_WAS_STARTED
from adisp import adisp_process
from constants import IS_CHINA, LOOTBOX_TOKEN_PREFIX
from debug_utils import deprecated
from gui import GUI_SETTINGS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getEventLootBoxesUrl
from gui.entitlements.entitlement_common import LOOT_BOX_COUNTER_ENTITLEMENT
from gui.game_control.links import URLMacros
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses
from gui.shared.event_dispatcher import showShop
from gui.shared.gui_items.loot_box import EVENT_LOOT_BOXES_CATEGORY, EventLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxGetInfoProcessor
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.server_settings import EVENT_LOOT_BOXES_CONFIG
from helpers.time_utils import getServerUTCTime
from shared_utils import nextTick
from skeletons.gui.game_control import IEventLootBoxesController, IEntitlementsController, IExternalLinksController, ISteamCompletionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Any
_logger = logging.getLogger(__name__)

class _SettingsMgr(object):
    __eventLootBoxes = dependency.descriptor(IEventLootBoxesController)
    __category = {EVENT_LOOT_BOXES_CATEGORY: EVENT_LOOT_BOXES}

    def getSetting(self, category, setting):
        return (AccountSettings.getSettings(LOOT_BOXES) or {}).get(self.__category[category], {}).get(setting)

    def setSetting(self, category, setting, newValue):
        if setting == LOOT_BOXES_EVENT_UNIQUE_ID:
            raise SoftException('You cannot change the "LOOT_BOXES_EVENT_UNIQUE_ID" manually')
        settings = AccountSettings.getSettings(LOOT_BOXES) or {}
        categorySettings = settings.get(self.__category[category], {})
        oldValue = categorySettings.get(setting)
        settingsChanged = False
        if oldValue != newValue:
            categorySettings[setting] = newValue
            settings[self.__category[category]] = categorySettings
            settingsChanged = True
        if settingsChanged:
            AccountSettings.setSettings(LOOT_BOXES, settings)

    def update(self):
        settings = AccountSettings.getSettings(LOOT_BOXES) or {}
        settingsChanged = False
        for category, data in settings.iteritems():
            oldUniqueID = (data or {}).get(LOOT_BOXES_EVENT_UNIQUE_ID)
            newUniqueID = self.__generateUniqueID(category)
            if oldUniqueID != newUniqueID:
                categoryDefaults = (AccountSettings.getSettingsDefault(LOOT_BOXES) or {}).get(category, {})
                categoryDefaults[LOOT_BOXES_EVENT_UNIQUE_ID] = newUniqueID
                settings[category].update(categoryDefaults)
                settingsChanged = True

        if settingsChanged:
            AccountSettings.setSettings(LOOT_BOXES, settings)

    def __generateUniqueID(self, category):
        return hash('_'.join((category, '_'.join((str(lbID) for lbID in self.__eventLootBoxes.getBoxesIDs(category))))))


class EventLootBoxesController(IEventLootBoxesController):
    __slots__ = ('__statusChangeNotifier', '__em', '__boxesCount', '__isLootBoxesAvailable', '__isActive', '__boxInfo')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __entitlements = dependency.descriptor(IEntitlementsController)
    __steam = dependency.descriptor(ISteamCompletionController)

    def __init__(self):
        super(EventLootBoxesController, self).__init__()
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.__em = Event.EventManager()
        self.onStatusChange = Event.Event(self.__em)
        self.onAvailabilityChange = Event.Event(self.__em)
        self.onBoxesCountChange = Event.Event(self.__em)
        self.onIntroShownChanged = Event.Event(self.__em)
        self.onBoxesUpdate = Event.Event(self.__em)
        self.onBoxInfoUpdated = Event.Event(self.__em)
        self.__boxesCount = 0
        self.__boxInfo = {}
        self.__isLootBoxesAvailable = False
        self.__isActive = False
        self.__boxCountToGuaranteedBonus = 0
        self.__settings = _SettingsMgr()

    @property
    def isConsumesEntitlements(self):
        return self.isLootBoxesAvailable() and self.isActive()

    @property
    def boxCountToGuaranteedBonus(self):
        return self.__boxCountToGuaranteedBonus

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        g_clientUpdateManager.addCallbacks({'lootBoxes': self.__onBoxesUpdate})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__statusChangeNotifier.startNotification()
        self.__boxesCount = self.__getBoxesCount()
        self.__updateBoxInfo()
        self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        self.__isActive = self.isActive()
        self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
        self.__settings.update()

    def getSetting(self, category, setting):
        return self.__settings.getSetting(category, setting)

    def setSetting(self, category, setting, value):
        self.__settings.setSetting(category, setting, value)

    def onAvatarBecomePlayer(self):
        self.__stop()
        self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        self.__isActive = self.isActive()

    def onDisconnected(self):
        self.__stop()
        self.__isLootBoxesAvailable = False
        self.__isActive = False

    def fini(self):
        self.__stop()
        super(EventLootBoxesController, self).fini()

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def isActive(self):
        if self.isEnabled():
            currentRegionalTime = getServerUTCTime()
            eventActiveTime = self.__getConfig().getEventActiveTime()
            return eventActiveTime[0] <= currentRegionalTime < eventActiveTime[1]
        return False

    def isLootBoxesAvailable(self):
        return self.__lobbyContext.getServerSettings().isLootBoxesEnabled()

    def isBuyAvailable(self):
        return self.isLootBoxesAvailable() and self.__entitlements.isCacheInited() and self.getDayInfoStatistics() < self.getDayLimit()

    def isLootBoxesWasStarted(self):
        return self.getSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_WAS_STARTED)

    def isLootBoxesWasFinished(self):
        return self.getSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_WAS_FINISHED)

    def useExternalShop(self):
        return IS_CHINA

    def setIntroWasShown(self, value):
        self.setSetting(EVENT_LOOT_BOXES_CATEGORY, LOOT_BOXES_WAS_STARTED, value)
        self.onIntroShownChanged(wasShown=value)

    def getDayLimit(self):
        return self.__getConfig().lootBoxBuyDayLimit

    def getGuaranteedBonusLimit(self, boxType):
        return self.getBoxInfo(boxType).get('limit', 0)

    def getEventActiveTime(self):
        return self.__getConfig().getEventActiveTime()

    def getDayInfoStatistics(self):
        entitlement = self.__entitlements.getBalanceEntitlementFromCache(LOOT_BOX_COUNTER_ENTITLEMENT)
        grantedEntitlements = self.__entitlements.getGrantedEntitlementFromCache(LOOT_BOX_COUNTER_ENTITLEMENT)
        if entitlement is None:
            return 0
        elif entitlement.isExpires():
            return 0
        else:
            granted = grantedEntitlements.getAmount() if grantedEntitlements is not None else 0
            return entitlement.getAmount() + granted

    def getExpiresAtLootBoxBuyCounter(self):
        entitlement = self.__entitlements.getBalanceEntitlementFromCache(LOOT_BOX_COUNTER_ENTITLEMENT)
        return entitlement.getExpiresAtInTimestamp() if entitlement is not None else 0

    def getTimeLeftToResetPurchase(self):
        return max(int(self.getExpiresAtLootBoxBuyCounter() - getServerUTCTime()), 0)

    @adisp_process
    def openShop(self):
        if self.useExternalShop():
            urlParser = URLMacros(allowedMacroses=['DB_ID'])
            path = GUI_SETTINGS.lootBoxes.get('categoryURL')
            url = yield urlParser.parse(GUI_SETTINGS.checkAndReplaceWebShopMacros(path))
            dependency.instance(IExternalLinksController).open(url)
        else:
            showShop(getEventLootBoxesUrl())

    def getCommonBoxInfo(self):
        return self.getBoxInfo(EventLootBoxes.COMMON)

    def getPremiumBoxInfo(self):
        return self.getBoxInfo(EventLootBoxes.PREMIUM)

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

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getEventLootBoxesConfig()

    def __stop(self):
        self.__em.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__statusChangeNotifier.stopNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__boxesCount = 0
        self.__boxInfo.clear()

    def __onServerSettingsChange(self, settings):
        if self.isLootBoxesAvailable() and self.isActive() and not (self.__isLootBoxesAvailable and self.__isActive):
            self.__entitlements.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])
        if 'isLootBoxesEnabled' in settings:
            self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
            self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        if EVENT_LOOT_BOXES_CONFIG in settings:
            self.onStatusChange()
            self.__isActive = self.isActive()
            self.__statusChangeNotifier.startNotification()
        if 'lootBoxes_config' in settings:
            self.__updateBoxInfo()

    def __onNotifyStatusChange(self):
        if self.isLootBoxesAvailable() and self.isActive() and not self.__isActive:
            self.__entitlements.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])
            self.__isActive = self.isActive()
        self.onStatusChange()

    def __getTimeToStatusChange(self):
        if self.isEnabled():
            startTime, finishTime = self.__getConfig().getEventActiveTime()
            currentTime = getServerUTCTime()
            if startTime >= getServerUTCTime():
                return startTime - currentTime
            if currentTime <= finishTime:
                return finishTime - currentTime

    def __getBoxesCount(self):
        return sum((lb.getInventoryCount() for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == EVENT_LOOT_BOXES_CATEGORY))

    def __onTokensUpdate(self, diff):
        if any((token.startswith(LOOTBOX_TOKEN_PREFIX) for token in diff.iterkeys())):
            boxesCount = self.__getBoxesCount()
            if boxesCount != self.__boxesCount:
                self.onBoxesCountChange(boxesCount, self.__boxesCount)
            if self.isLootBoxesAvailable() and self.isActive() and boxesCount > self.__boxesCount:
                self.__entitlements.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])
            self.__boxesCount = boxesCount

    def __onBoxesUpdate(self, diff):
        boxId = self.__boxInfo.get(EventLootBoxes.PREMIUM, {}).get('id')
        guaranteedBonusLimit = self.__boxInfo.get(EventLootBoxes.PREMIUM, {}).get('limit')
        boxHistoryData = diff.get('history', {}).get(boxId)
        if boxHistoryData:
            _, bonusData, _ = boxHistoryData
            _, opened, _ = bonusData.get('guaranteedBonusLimit', (0, 0, 0))
            self.__boxCountToGuaranteedBonus = guaranteedBonusLimit - opened
            self.onBoxesUpdate()

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
    @deprecated
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
                    boxData['limit'] = self.__parseLimitSection(lootBoxData.get('config', {}))
                    boxData['slots'] = self.__parseAllOfSection(data.get('allof', {}))
                    boxData['history'] = lootBoxData.get('history', (0, None, 0))
                    boxInfoData[lbType] = boxData

        self.__boxInfo = boxInfoData
        self.onBoxInfoUpdated()
        self.__updateBoxCountToGuaranteedBonus()
        return

    def __parseLimitSection(self, data):
        return data.get('limits', {}).get('guaranteedBonusLimit', {}).get('guaranteedFrequency', 30)

    def __parseAllOfSection(self, data):
        slots = dict()
        if data:
            for idx, slotsData in enumerate(data):
                probability, bonuses = self.__parseSlotSection(slotsData)
                slots.setdefault(idx, {}).setdefault('probability', probability)
                slots.setdefault(idx, {}).setdefault('bonuses', bonuses)

        return slots

    def __parseSlotSection(self, data):
        if isinstance(data, tuple) and len(data) == 4:
            probability, _, _, rawData = data
            bonuses = []
            bonuses.extend(self.__parseGroupsSection(rawData))
            return (probability, bonuses)
        return (0, [])

    def __parseGroupsSection(self, data):
        groups = data.get('groups', [])
        bonuses = []
        for groupData in groups:
            bonuses.extend(self.__parseOneOfSection(groupData))

        return bonuses

    def __parseOneOfSection(self, data):
        oneOf = data.get('oneof', ())
        bonuses = []
        if oneOf and len(oneOf) == 2:
            _, items = oneOf
            for item in items:
                if item and len(item) == 4:
                    _, _, _, rawData = item
                    if rawData:
                        for k, v in rawData.iteritems():
                            if k == 'groups':
                                bonuses.extend(self.__parseGroupsSection(rawData))
                            bonuses.extend(getNonQuestBonuses(k, v))

        return bonuses
