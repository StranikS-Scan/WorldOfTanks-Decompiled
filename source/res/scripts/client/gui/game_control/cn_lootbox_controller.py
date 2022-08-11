# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/cn_lootbox_controller.py
import logging
import typing
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CN_LOOT_BOXES_INTRO_WAS_SHOWN
from adisp import process
from constants import LOOTBOX_TOKEN_PREFIX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.entitlements.entitlement_common import LOOT_BOX_COUNTER_ENTITLEMENT
from gui.game_control.links import URLMacros
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.gui_items.loot_box import CHINA_LOOT_BOXES_CATEGORIES, ChinaLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxGetInfoProcessor
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.server_settings import CN_LOOT_BOXES_EVENT_CONFIG
from helpers.time_utils import getServerUTCTime
from shared_utils import nextTick
from skeletons.gui.game_control import ICNLootBoxesController, IEntitlementsController, IExternalLinksController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox
_logger = logging.getLogger(__name__)

class CNLootBoxesController(ICNLootBoxesController):
    __slots__ = ('__statusChangeNotifier', '__em', '__boxesCount', '__isLootBoxesAvailable', '__isActive', '__boxInfo')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __entitlementsController = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        super(CNLootBoxesController, self).__init__()
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
        super(CNLootBoxesController, self).fini()

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
        return self.isLootBoxesAvailable() and self.__entitlementsController.isCacheInited() and self.getDayInfoStatistics() < self.getDayLimit()

    def isIntroWasShown(self):
        return AccountSettings.getSettings(CN_LOOT_BOXES_INTRO_WAS_SHOWN)

    def setIntroWasShown(self, value):
        AccountSettings.setSettings(CN_LOOT_BOXES_INTRO_WAS_SHOWN, value)
        self.onIntroShownChanged(wasShown=value)

    def getDayLimit(self):
        return self.__getConfig().lootBoxBuyDayLimit

    def getGuaranteedBonusLimit(self, boxType):
        return self.getBoxInfo(boxType).get('limit', 0)

    def getEventActiveTime(self):
        return self.__getConfig().getEventActiveTime()

    def getDayInfoStatistics(self):
        entitlement = self.__entitlementsController.getBalanceEntitlementFromCache(LOOT_BOX_COUNTER_ENTITLEMENT)
        grantedEntitlements = self.__entitlementsController.getGrantedEntitlementFromCache(LOOT_BOX_COUNTER_ENTITLEMENT)
        if entitlement is None:
            return 0
        elif entitlement.isExpires():
            return 0
        else:
            granted = grantedEntitlements.getAmount() if grantedEntitlements is not None else 0
            return entitlement.getAmount() + granted

    def getExpiresAtLootBoxBuyCounter(self):
        entitlement = self.__entitlementsController.getBalanceEntitlementFromCache(LOOT_BOX_COUNTER_ENTITLEMENT)
        return entitlement.getExpiresAtInTimestamp() if entitlement is not None else 0

    def getTimeLeftToResetPurchase(self):
        return max(int(self.getExpiresAtLootBoxBuyCounter() - getServerUTCTime()), 0)

    @process
    def openExternalShopPage(self):
        externalOpener = dependency.instance(IExternalLinksController)
        urlParser = URLMacros(allowedMacroses=['DB_ID'])
        url = yield urlParser.parse(self.__getConfig().externalShopUrl)
        externalOpener.open(url)

    def getCommonBoxInfo(self):
        return self.getBoxInfo(ChinaLootBoxes.COMMON)

    def getPremiumBoxInfo(self):
        return self.getBoxInfo(ChinaLootBoxes.PREMIUM)

    def getBoxInfo(self, boxType):
        if not self.__boxInfo:
            self.__updateBoxInfo()
        return self.__boxInfo.get(boxType, {})

    def getStoreInfo(self):
        return {lb.getType():lb for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == CHINA_LOOT_BOXES_CATEGORIES}

    def getBoxesIDs(self):
        return set((lb.getID() for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == CHINA_LOOT_BOXES_CATEGORIES))

    def getBoxesCount(self):
        return self.__boxesCount

    def getBoxesInfo(self):
        if not self.__boxInfo:
            self.__updateBoxInfo()
        return self.__boxInfo

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getCNLootBoxesEventConfig()

    def __stop(self):
        self.__em.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__statusChangeNotifier.stopNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__boxesCount = 0
        self.__boxInfo.clear()

    def __onServerSettingsChange(self, settings):
        if self.isLootBoxesAvailable() and self.isActive() and not (self.__isLootBoxesAvailable and self.__isActive):
            self.__entitlementsController.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])
        if 'isLootBoxesEnabled' in settings:
            self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
            self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        if CN_LOOT_BOXES_EVENT_CONFIG in settings:
            self.onStatusChange()
            self.__isActive = self.isActive()
            self.__statusChangeNotifier.startNotification()
        if 'lootBoxes_config' in settings:
            self.__updateBoxInfo()

    def __onNotifyStatusChange(self):
        if self.isLootBoxesAvailable() and self.isActive() and not self.__isActive:
            self.__entitlementsController.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])
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
        return sum((lb.getInventoryCount() for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == CHINA_LOOT_BOXES_CATEGORIES))

    def __onTokensUpdate(self, diff):
        if any((token.startswith(LOOTBOX_TOKEN_PREFIX) for token in diff.iterkeys())):
            boxesCount = self.__getBoxesCount()
            if boxesCount != self.__boxesCount:
                self.onBoxesCountChange(boxesCount, self.__boxesCount)
            if self.isLootBoxesAvailable() and self.isActive() and boxesCount > self.__boxesCount:
                self.__entitlementsController.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])
            self.__boxesCount = boxesCount

    def __onBoxesUpdate(self, diff):
        boxId = self.__boxInfo.get(ChinaLootBoxes.PREMIUM, {}).get('id')
        guaranteedBonusLimit = self.__boxInfo.get(ChinaLootBoxes.PREMIUM, {}).get('limit')
        boxHistoryData = diff.get('history', {}).get(boxId)
        if boxHistoryData:
            _, bonusData, _ = boxHistoryData
            _, opened, _ = bonusData.get('guaranteedBonusLimit', (0, 0, 0))
            self.__boxCountToGuaranteedBonus = guaranteedBonusLimit - opened
            self.onBoxesUpdate()

    def __updateBoxCountToGuaranteedBonus(self):
        opened = 0
        guaranteedBonusLimit = self.__boxInfo.get(ChinaLootBoxes.PREMIUM, {}).get('limit', 0)
        boxHistoryData = self.__boxInfo.get(ChinaLootBoxes.PREMIUM, {}).get('history')
        if boxHistoryData:
            _, bonusData, _ = boxHistoryData
            if bonusData is not None:
                _, opened, _ = bonusData.get('guaranteedBonusLimit', (0, 0, 0))
        self.__boxCountToGuaranteedBonus = guaranteedBonusLimit - opened
        return

    @nextTick
    @process
    def __updateBoxInfo(self):
        boxes = [ lb for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == CHINA_LOOT_BOXES_CATEGORIES ]
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
