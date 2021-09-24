# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/loot_boxes_controller.py
import logging
from collections import namedtuple
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import WTLootBoxesViewedKeys
from adisp import process
from gui import SystemMessages
from helpers import dependency
from constants import Configs, LOOTBOX_TOKEN_PREFIX
import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.impl.lobby.wt_event.wt_event_constants import EventCollections
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
from gui.shared.event_dispatcher import showEventPortalAwardsWindow, showVehicleAwardWindow
from gui.server_events.bonuses import splitBonuses
from gui.wt_event.wt_event_helpers import isSpecialVehicleReceived
from gui.wt_event.wt_event_bonuses_packers import LootBoxAwardsManager
from gui.wt_event.wt_event_simple_bonus_packers import mergeWtBonuses, getWtSplitBonusFunction, getWtBonusGroup
from helpers import server_settings
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import ILootBoxesController, IGameEventController, IEntitlementsController
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import findFirst
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_TankLimits = namedtuple('_TankLimits', ('guaranteedAttempts', 'leftAttempts'))
_GroupBonuses = namedtuple('_GroupBonuses', ('probability', 'bonuses'))

def _processCustomizationBonus(intCD, bonus):
    for item in bonus.getCustomizations():
        itemCD = bonus.getC11nItem(item).intCD
        if itemCD == intCD:
            return True

    return False


def _processTmanTokenBonus(token, bonus):
    return token in bonus.getValue()


def _getBonusProcessor(bonus):
    bonusName = bonus.getName()
    if bonusName == 'customizations':
        return _processCustomizationBonus
    else:
        return _processTmanTokenBonus if bonusName == 'tmanToken' else None


class LootBoxesController(ILootBoxesController):
    __gameCtrl = dependency.descriptor(IGameEventController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __entitlementsController = dependency.descriptor(IEntitlementsController)

    def __init__(self):
        super(LootBoxesController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onUpdated = Event.Event(self.__eventManager)
        self.onUpdatedConfig = Event.Event(self.__eventManager)
        self.__lootBoxesConfig = {}
        self.__hunterLastViewedCount = 0
        self.__bossLastViewedCount = 0

    def fini(self):
        self.__clear()
        self.__eventManager.clear()
        self.__eventManager = None
        super(LootBoxesController, self).fini()
        return

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().eventBattlesConfig

    def onLobbyInited(self, event):
        self.__addListeners()
        self.__packLootBoxes()
        if not self.__entitlementsController.isCacheInited:
            self.__updateEntitlementsCache()

    def __updateEntitlementsCache(self):
        if self.__gameCtrl.isAvailable():
            lootBoxCounterEntitlementID = self.getModeSettings().lootBoxCounterEntitlementID
            self.__entitlementsController.updateCache((lootBoxCounterEntitlementID,))

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def onAccountBecomeNonPlayer(self):
        self.__hunterLastViewedCount = 0
        self.__bossLastViewedCount = 0

    def getLootBoxesRewards(self, lootBoxType):
        return self.__lootBoxesConfig.get(lootBoxType, {})

    def getLastViewedCount(self):
        if self.__settingsCore.isReady:
            self.__hunterLastViewedCount = self.__settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, WTLootBoxesViewedKeys.HUNTER_LAST_VIEWED, 0)
            self.__bossLastViewedCount = self.__settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, WTLootBoxesViewedKeys.BOSS_LAST_VIEWED, 0)
            hunterCount = self.getLootBoxesCountByType(EventLootBoxes.WT_HUNTER)
            bossCount = self.getLootBoxesCountByType(EventLootBoxes.WT_BOSS)
            if self.__hunterLastViewedCount > hunterCount:
                self.__hunterLastViewedCount = hunterCount
                self.__saveHunterLastViewedCount()
            if self.__bossLastViewedCount > bossCount:
                self.__bossLastViewedCount = bossCount
                self.__saveBossLastViewedCount()
        return (self.__hunterLastViewedCount, self.__bossLastViewedCount)

    def updateLastViewedCount(self):
        self.__hunterLastViewedCount = self.getLootBoxesCountByType(EventLootBoxes.WT_HUNTER)
        self.__bossLastViewedCount = self.getLootBoxesCountByType(EventLootBoxes.WT_BOSS)
        self.__saveHunterLastViewedCount()
        self.__saveBossLastViewedCount()

    def getLootBoxesByType(self, lootBoxType=None):
        if lootBoxType is None:
            lootBoxTypes = (EventLootBoxes.WT_HUNTER, EventLootBoxes.WT_BOSS)
        else:
            lootBoxTypes = (lootBoxType,)
        return [ lootBox for lootBox in self.__itemsCache.items.tokens.getLootBoxes().itervalues() if lootBox.getType() in lootBoxTypes ]

    def getLootBoxesCountByType(self, lootBoxType):
        itemsByType = self.__itemsCache.items.tokens.getLootBoxesCountByType()
        lootBoxes = itemsByType.get(lootBoxType, {})
        return lootBoxes.get(TOTAL_KEY, 0)

    def getLootBoxByTypeInInventory(self, lootBoxType):
        return findFirst(lambda box: box.getType() == lootBoxType, self.getLootBoxesByType(lootBoxType))

    def getLootBoxLimitsInfo(self, lootBoxType):
        guaranteedAttempts, leftAttempts = (0, 0)
        lootBox = self.getLootBoxByTypeInInventory(lootBoxType)
        if lootBox:
            guaranteedAttempts = lootBox.getGuaranteedFrequency()
            attempts = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootBox)
            leftAttempts = max(guaranteedAttempts - attempts, 1)
        return _TankLimits(guaranteedAttempts=guaranteedAttempts, leftAttempts=leftAttempts)

    def getCollectionType(self, itemID):
        if self.isCollectionElement(itemID, self.__gameCtrl.getHunterCollection()):
            return EventCollections.HUNTER
        else:
            return EventCollections.BOSS if self.isCollectionElement(itemID, self.__gameCtrl.getBossCollection()) else None

    def isCollectionElement(self, itemID, collection):
        for bonus in collection:
            processor = _getBonusProcessor(bonus)
            if processor is None:
                continue
            if processor(itemID, bonus):
                return True

        return False

    @process
    def requestLootBoxOpen(self, boxType, count, parentWindow=None, callbackUpdate=None):
        currentCount = self.getLootBoxesCountByType(boxType)
        if currentCount == 0:
            _logger.error('Invalid lootBox count')
            return
        else:
            boxItem = self.getLootBoxByTypeInInventory(boxType)
            if boxItem is None:
                _logger.error('Invalid lootBox item')
                return
            requestedCount = min(currentCount, count)
            result = yield LootBoxOpenProcessor(boxItem, requestedCount).request()
            if result is None:
                raise SoftException('LootBoxOpenProcessor request return unknown result')
            if result.success:
                rewardsList = result.auxData
                if not rewardsList:
                    _logger.error('LootBox is opened, but no rewards has been received.')
                    return
                rewards = _preprocessAwards(rewardsList)
                openedBoxes = len(rewardsList)
                if openedBoxes == 1 and isSpecialVehicleReceived(rewards):
                    showVehicleAwardWindow(rewards, parent=parentWindow)
                elif callbackUpdate:
                    data = {'awards': rewards,
                     'openedBoxes': openedBoxes}
                    callbackUpdate(data)
                else:
                    showEventPortalAwardsWindow(boxItem.getType(), rewards, count, openedBoxes, parent=parentWindow)
            else:
                SystemMessages.pushMessage(text=result.userMsg, type=result.sysMsgType)
            return

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getLootBoxDailyPurchaseLimit(self):
        return self.getModeSettings().lootBoxDailyPurchaseLimit

    def getPurchasedLootBoxesCount(self):
        lootBoxCounterEntitlementID = self.getModeSettings().lootBoxCounterEntitlementID
        entitlementsController = self.__entitlementsController
        entitlement = entitlementsController.getEntitlementFromCache(lootBoxCounterEntitlementID)
        if entitlement is None or entitlement.isExpired:
            return 0
        else:
            grantedEntitlement = entitlementsController.getGrantedEntitlementFromCache(lootBoxCounterEntitlementID)
            grantedAmount = 0 if grantedEntitlement is None else grantedEntitlement.amount
            return entitlement.amount + grantedAmount

    def getAvailableForPurchaseLootBoxesCount(self):
        lootBoxDailyPurchaseLimit = self.getLootBoxDailyPurchaseLimit()
        purchasedLootBoxesCount = self.getPurchasedLootBoxesCount()
        availableLootBoxesCount = lootBoxDailyPurchaseLimit - purchasedLootBoxesCount
        return availableLootBoxesCount if availableLootBoxesCount > 0 else 0

    def __clear(self):
        if self.__lootBoxesConfig:
            self.__lootBoxesConfig.clear()
        self.__hunterLastViewedCount = 0
        self.__bossLastViewedCount = 0
        self.__removeListeners()

    @server_settings.serverSettingsChangeListener(Configs.LOOTBOX_CONFIG.value)
    def __onServerSettingChanged(self, _):
        self.__lootBoxesConfig.clear()
        self.__packLootBoxes()
        self.onUpdatedConfig()

    def __onTokensUpdate(self, diff):
        hunterCount = self.getLootBoxesCountByType(EventLootBoxes.WT_HUNTER)
        bossCount = self.getLootBoxesCountByType(EventLootBoxes.WT_BOSS)
        if self.__hunterLastViewedCount is None or hunterCount < self.__hunterLastViewedCount:
            self.__hunterLastViewedCount = hunterCount
        if self.__bossLastViewedCount is None or bossCount < self.__bossLastViewedCount:
            self.__bossLastViewedCount = bossCount
        if any([ token.startswith(LOOTBOX_TOKEN_PREFIX) for token in diff ]):
            self.__updateEntitlementsCache()
        self.onUpdated()
        return

    def __getLootBoxConfig(self):
        return self.__lobbyContext.getServerSettings().getLootBoxConfig()

    def __packLootBoxes(self):
        config = self.__getLootBoxConfig()
        if not config:
            return
        else:
            for box in config.itervalues():
                boxType = box.get('type')
                if boxType not in (EventLootBoxes.WT_HUNTER, EventLootBoxes.WT_BOSS) or boxType in self.__lootBoxesConfig:
                    continue
                bonuses = box.get('bonus', {})
                if bonuses is not None:
                    self.__lootBoxesConfig[boxType] = _convertToBonuses(bonuses)

            if not self.__lootBoxesConfig:
                _logger.error('[LootBox] Could not fetch lootBox bonus data for some reason')
            return

    def __saveHunterLastViewedCount(self):
        if self.__settingsCore.isReady:
            self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, {WTLootBoxesViewedKeys.HUNTER_LAST_VIEWED: self.__hunterLastViewedCount})

    def __saveBossLastViewedCount(self):
        if self.__settingsCore.isReady:
            self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, {WTLootBoxesViewedKeys.BOSS_LAST_VIEWED: self.__bossLastViewedCount})


def _convertToBonuses(rewards):
    boxBonuses = BattlePassAwardsManager.composeBonuses([rewards])
    group = {}
    for boxBonus in boxBonuses:
        bonusGroup, probability, bonuses = _convertBonusGroup([boxBonus])
        if bonuses:
            group[bonusGroup] = _GroupBonuses(probability, bonuses)

    return group


def _convertBonusGroup(bonuses):
    probability = None
    hasNewBonuses = True
    while hasNewBonuses:
        hasNewBonuses = False
        flatBonuses = []
        for bonus in bonuses:
            if bonus.getName() == 'groups':
                flatBonuses.extend(LootBoxAwardsManager.composeBonuses(bonus.getValue()))
                hasNewBonuses = True
            if bonus.getName() in ('oneof', 'allof'):
                bonusProbability, clearBonuses = bonus.getOptionalBonusesWithProbability()
                if bonusProbability:
                    probability = bonusProbability[0]
                flatBonuses.extend(clearBonuses)
                hasNewBonuses = True
            flatBonuses.append(bonus)

        bonuses = flatBonuses

    mergedBonuses = mergeWtBonuses(bonuses)
    bonusGroup = getWtBonusGroup(mergedBonuses)
    return (bonusGroup, probability, splitBonuses(mergedBonuses, splitFunc=getWtSplitBonusFunction))


def _preprocessAwards(awards):
    if len(awards) > 1:
        return [ _preprocessBonusGroup(group) for group in awards ]
    return _preprocessBonusGroup(awards)


def _preprocessBonusGroup(awards):
    bonusList = [awards] if not isinstance(awards, list) else awards
    bonuses = LootBoxAwardsManager.composeBonuses(bonusList)
    return LootBoxAwardsManager.processCompensation(bonuses)
