# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/cn_lootbox_controller.py
import typing
import logging
import Event
from adisp import process
from constants import LOOTBOX_TOKEN_PREFIX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getCNLootBoxesUrl
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import showShop
from gui.shared.gui_items.loot_box import CHINA_LOOT_BOXES_CATEGORIES, ChinaLootBoxes
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.server_settings import CN_LOOT_BOXES_EVENT_CONFIG
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import ICNLootBoxesController, IEntitlementsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items.processors.loot_boxes import LootBoxGetInfoProcessor
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox
_logger = logging.getLogger(__name__)
_LOOT_BOX_COUNTER_ENTITLEMENT = 'loot_box_counter'

class CNLootBoxesController(ICNLootBoxesController):
    __slots__ = ('__statusChangeNotifier', '__eventsManager', '__boxesCount', '__isLootBoxesAvailable', '__wasInBattle', '__isActive', '__boxInfo')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __entitlementsController = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        super(CNLootBoxesController, self).__init__()
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.__eventsManager = Event.EventManager()
        self.onStatusChange = Event.Event(self.__eventsManager)
        self.onAvailabilityChange = Event.Event(self.__eventsManager)
        self.onBoxesCountChange = Event.Event(self.__eventsManager)
        self.onWelcomeScreenClosed = Event.Event(self.__eventsManager)
        self.__boxesCount = 0
        self.__boxInfo = {}
        self.__isActive = False
        self.__isLootBoxesAvailable = None
        self.__wasInBattle = False
        return

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__statusChangeNotifier.startNotification()
        self.__boxesCount = self.__getBoxesCount()
        self.__updateBoxInfo()
        isActive = self.isActive()
        if self.__wasInBattle and isActive != self.__isActive:
            self.onStatusChange()
        self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
        self.__isActive = isActive
        self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        self.__wasInBattle = False

    def onAvatarBecomePlayer(self):
        self.__stop()
        self.__isActive = self.isActive()
        self.__wasInBattle = True

    def onDisconnected(self):
        self.__stop()
        self.__isLootBoxesAvailable = None
        return

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

    def getDayLimit(self):
        return self.__getConfig().lootBoxBuyDayLimit

    def getEventActiveTime(self):
        return self.__getConfig().getEventActiveTime()

    def getDayInfoStatistics(self):
        entitlement = self.__entitlementsController.getBalanceEntitlementFromCache(_LOOT_BOX_COUNTER_ENTITLEMENT)
        grantedEntitlements = self.__entitlementsController.getGrantedEntitlementFromCache(_LOOT_BOX_COUNTER_ENTITLEMENT)
        if entitlement is None:
            return 0
        elif entitlement.isExpires():
            return 0
        else:
            granted = grantedEntitlements.getAmount() if grantedEntitlements is not None else 0
            return entitlement.getAmount() + granted

    def getExpiresAtLootBoxBuyCounter(self):
        entitlement = self.__entitlementsController.getBalanceEntitlementFromCache(_LOOT_BOX_COUNTER_ENTITLEMENT)
        return entitlement.getExpiresAtInTimestamp() if entitlement is not None else 0

    def getTimeLeftToResetPurchase(self):
        return max(int(self.getExpiresAtLootBoxBuyCounter() - getServerUTCTime()), 0)

    def openShopPage(self):
        showShop(getCNLootBoxesUrl())

    def getCommonBoxInfo(self):
        if not self.__boxInfo:
            self.__updateBoxInfo()
        return self.__boxInfo.get(ChinaLootBoxes.COMMON, {})

    def getPremiumBoxInfo(self):
        if not self.__boxInfo:
            self.__updateBoxInfo()
        return self.__boxInfo.get(ChinaLootBoxes.PREMIUM, {})

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
        self.__eventsManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__statusChangeNotifier.stopNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__boxesCount = 0
        self.__boxInfo.clear()

    def __onServerSettingsChange(self, settings):
        if CN_LOOT_BOXES_EVENT_CONFIG in settings:
            self.onStatusChange()
            self.__statusChangeNotifier.startNotification()
        if 'isLootBoxesEnabled' in settings:
            self.onAvailabilityChange(self.__isLootBoxesAvailable, self.isLootBoxesAvailable())
            self.__isLootBoxesAvailable = self.isLootBoxesAvailable()
        if 'lootBoxes_config' in settings:
            self.__updateBoxInfo()

    def __onNotifyStatusChange(self):
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
                self.onBoxesCountChange(boxesCount)
            self.__boxesCount = boxesCount
            self.__entitlementsController.updateCache([_LOOT_BOX_COUNTER_ENTITLEMENT])

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
                    boxData['limit'] = self.__parseLimitSection(data.get('config', {}))
                    boxData['slots'] = self.__parseAllOfSection(data.get('allof', {}))
                    boxInfoData[lbType] = boxData

        self.__boxInfo = boxInfoData
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
        if isinstance(data, tuple) and len(data) == 3:
            probability, _, rawData = data
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
                if item and len(item) == 3:
                    _, _, rawData = item
                    if rawData:
                        for k, v in rawData.iteritems():
                            if k == 'groups':
                                bonuses.extend(self.__parseGroupsSection(rawData))
                            bonuses.extend(getNonQuestBonuses(k, v))

        return bonuses
