# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/loot_boxes_controller.py
import logging
from collections import namedtuple
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import WTLootBoxesViewedKeys
from adisp import process
from gui import SystemMessages
from gui.impl.lobby.wt_event.wt_event_constants import getBonusGroup
from gui.impl.lobby.wt_event.wt_event_vehicle_portal import ReRollButton
from helpers import dependency
from constants import Configs, LOOTBOX_TOKEN_PREFIX
import Event
from gui.shared.money import Money
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor, LootBoxReRollProcessor, LootBoxReRollHistoryProcessor
from gui.shared.utils.requesters.tokens_requester import TOTAL_KEY
from gui.shared.event_dispatcher import showEventPortalAwardsWindow, showVehicleAwardWindow
from gui.server_events.bonuses import splitBonuses
from gui.wt_event.wt_event_helpers import isSpecialVehicleReceived, findSpecialVehicle
from gui.wt_event.wt_event_bonuses_packers import LootBoxAwardsManager
from gui.wt_event.wt_event_simple_bonus_packers import mergeWtBonuses, getWtSplitBonusFunction, getWtBonusGroup
from helpers import server_settings
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import ILootBoxesController, IEventBattlesController, IEntitlementsController
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import findFirst
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_TankLimits = namedtuple('_TankLimits', ('guaranteedAttempts', 'leftAttempts', 'isIgnored'))
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
    __gameCtrl = dependency.descriptor(IEventBattlesController)
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
        self.__isEngineerReroll = False

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

    def getLootBoxesCountByTypeForUI(self, lootBoxType):
        count = self.getLootBoxesCountByType(lootBoxType)
        currentReRollHistory = self.getReRollAttemptsCount(lootBoxType)
        return count if currentReRollHistory == 0 else count - 1

    def getLootBoxByTypeInInventory(self, lootBoxType):
        return findFirst(lambda box: box.getType() == lootBoxType, self.getLootBoxesByType(lootBoxType))

    def hasAccountEnoughReRollAttempts(self, boxType):
        count = self.getReRollAttemptsCount(boxType)
        _logger.debug('Current %s re-roll attempts: %d, ', boxType, count)
        return count + 1 >= self.getReRollMaximumAttempts(boxType)

    def isEngineerReroll(self):
        return self.__isEngineerReroll

    def hasAccountEnoughMoneyForReRoll(self, boxType):
        reRollPrice = self.__getCurrentReRollPrice(boxType)
        priceType = self.getReRollPriceType(boxType)
        money = self.__itemsCache.items.stats.money
        if not money.isDefined() or not priceType or not reRollPrice.isDefined():
            _logger.error('Invalid money %s, priceType %s / %s reRollPrice', repr(money), priceType, repr(reRollPrice))
            return
        shortageTotal = money.getShortage(reRollPrice)
        shortageOfSelectedCurrency = shortageTotal.get(priceType)
        return not shortageOfSelectedCurrency

    def __getSpecificLootBoxConfig(self, boxType):
        config = self.__getLootBoxConfig()
        result = [ dictItems for dictItems in config.values() if dictItems['type'] == boxType ]
        return result[0]

    def __getCurrentReRollPrice(self, boxType):
        specificLootBoxConfig = self.__getSpecificLootBoxConfig(boxType)
        allPrices = specificLootBoxConfig.get('reRoll').get('prices')
        priceType = specificLootBoxConfig.get('reRoll').get('priceType')
        boxTypeAccountCount = self.getReRollAttemptsCount(boxType)
        if boxTypeAccountCount > len(allPrices):
            _logger.error('Asked for more Re-Rolls than allowed')
            return None
        elif boxTypeAccountCount == len(allPrices):
            return None
        else:
            currentPrice = allPrices[boxTypeAccountCount]
            return Money(**{priceType: currentPrice})

    def getLootBoxLimitsInfo(self, lootBoxType):
        guaranteedAttempts = 0
        leftAttempts = 0
        isIgnored = False
        lootBox = self.getLootBoxByTypeInInventory(lootBoxType)
        if lootBox:
            lootBoxConfig = self.__getSpecificLootBoxConfig(lootBoxType)
            guaranteedAttempts = lootBox.getGuaranteedFrequency()
            limitID = lootBox.getGuaranteedFrequencyName()
            ignoredLimit = lootBoxConfig.get('reRoll', {}).get('ignoreLimits', {}).get(limitID, {})
            for tokenName, count in ignoredLimit.iteritems():
                if self.__itemsCache.items.tokens.getTokenCount(tokenName) >= count:
                    isIgnored = True

            attempts = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootBox)
            leftAttempts = max(guaranteedAttempts - attempts, 1)
        return _TankLimits(guaranteedAttempts=guaranteedAttempts, leftAttempts=leftAttempts, isIgnored=isIgnored)

    def getCollectionType(self, itemID):
        return None

    def isCollectionElement(self, itemID, collection):
        for bonus in collection:
            processor = _getBonusProcessor(bonus)
            if processor is None:
                continue
            if processor(itemID, bonus):
                return True

        return False

    @process
    def onPortalOpened(self, boxType, parentWindow, callbackFailure=None):
        result = yield LootBoxReRollHistoryProcessor().request()
        if result is None or not result.success:
            _logger.error('LootBox result is None or returned Failure')
            if callbackFailure:
                callbackFailure()
            return
        elif result.success and result.auxData[boxType]['count'] == 0:
            _logger.debug('We do not have unopened lootBoxes, requesting for a new LootBox rewards')
            self.requestLootBoxReRoll(boxType, parentWindow, callbackFailure=callbackFailure)
            return
        else:
            lastRewardRawData = result.auxData[boxType]['rolledRewards'].values()[-1]
            lastReward = _preprocessReRollAwards(lastRewardRawData)
            if lastReward:
                _logger.debug('We have unopened lootBoxes, display them')
                showEventPortalAwardsWindow(boxType, lastReward, 1, len(lastReward))
            else:
                _logger.error('It has been a problem with opening a latest unopened reward')
            return

    @process
    def requestLootBoxReRoll(self, boxType, parentWindow=None, callback=None, reRollButtonUsed=None, callbackFailure=None):
        boxItem = self.getLootBoxByTypeInInventory(boxType)
        result = yield LootBoxReRollProcessor(boxItem).request()
        self.__isEngineerReroll = reRollButtonUsed and reRollButtonUsed == ReRollButton.REROLL
        if result is None or not result.success:
            if callbackFailure:
                callbackFailure()
            raise SoftException('LootBoxReRollProcessor request return unknown result')
        if result.success:
            rewardsList = result.auxData.get('rewards', [])
            if not rewardsList:
                _logger.error('LootBox is opened, but no rewards has been received.')
                return
            rewards = _preprocessAwards(rewardsList['bonus'] if rewardsList.get('bonus', {}) else [rewardsList])
            openedBoxes = len(rewardsList)
            if isSpecialVehicleReceived(rewards):
                showVehicleAwardWindow(rewards, parent=parentWindow)
                if callback:
                    callback({'awards': rewards})
            elif self.__isStopTokenAmongRewards(rewards, boxType):
                if callback:
                    callback({'awards': rewards})
                showEventPortalAwardsWindow(boxItem.getType(), rewards, 1, openedBoxes, parent=parentWindow)
            else:
                if callback:
                    callback({'awards': rewards})
                showEventPortalAwardsWindow(boxItem.getType(), rewards, 1, openedBoxes, parent=parentWindow)
        return

    @process
    def claimReRolledReward(self, boxType, count=1, parentWindow=None, callbackUpdate=None, callbackFailure=None):
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
                rewardsList = result.auxData.get('bonus', [])
                if not rewardsList:
                    _logger.error('LootBox is opened, but no rewards has been received.')
                    return
                rewards = _preprocessAwards(rewardsList)
                openedBoxes = len(rewardsList)
                if openedBoxes == 1 and isSpecialVehicleReceived(rewards):
                    showVehicleAwardWindow(rewards, parent=parentWindow)
                if callbackUpdate is not None:
                    callbackUpdate()
            else:
                SystemMessages.pushMessage(text=result.userMsg, type=result.sysMsgType)
                if callbackFailure:
                    callbackFailure()
            return

    def getReRollAttemptsCount(self, boxType):
        lootBox = self.getLootBoxByTypeInInventory(boxType)
        return self.__itemsCache.items.tokens.getReRollCount(lootBox)

    def getReRollAttemptsLeft(self, boxType):
        boxTypeAttemptsCount = self.getReRollAttemptsCount(boxType)
        return self.getReRollMaximumAttempts(boxType) - boxTypeAttemptsCount

    def getReRollPrice(self, boxType):
        return self.__getCurrentReRollPrice(boxType)

    def getReRollMaximumAttempts(self, boxType):
        specificLootBoxConfig = self.__getSpecificLootBoxConfig(boxType)
        return specificLootBoxConfig.get('reRoll').get('maxAttempts')

    def getReRollPriceType(self, boxType):
        specificLootBoxConfig = self.__getSpecificLootBoxConfig(boxType)
        return specificLootBoxConfig.get('reRoll').get('priceType')

    def isStopTokenAmongRewardList(self, rewardsList, boxType):
        return self.__isStopTokenAmongRewards(rewardsList, boxType)

    def rewardsHaveCompensationBonus(self, rewards):
        for reward in rewards:
            if reward.getName() == 'vehicles' and self.__getCompensationBonusPrice(reward) != []:
                return True

        return False

    def getSpecialVehicleName(self, bonuses):
        vehicles = [ bonus for bonus in bonuses if bonus.getName() == 'vehicles' ]
        specialVehicle = findSpecialVehicle(vehicles, isVehicleObject=True)
        return specialVehicle

    def getExtraRewards(self, boxType, count=None):
        lootBoxConfig = self.__getSpecificLootBoxConfig(boxType)
        count = count if count is not None else self.getReRollAttemptsCount(boxType)
        return lootBoxConfig.get('reRoll').get('extras').get(count)

    def __getCompensationBonusPrice(self, reward):
        compensationList = reward.getCompensation()
        return compensationList if any((number > 0 for number in compensationList)) else []

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

    def __getStopToken(self, boxType):
        boosLootBoxConfig = self.__getSpecificLootBoxConfig(boxType)
        stopTokenValue = boosLootBoxConfig.get('reRoll').get('stopToken', None)
        return stopTokenValue

    def __isStopTokenAmongRewards(self, rewardsList, boxType):
        stopToken = self.__getStopToken(boxType)
        if stopToken is None:
            return False
        else:
            return [ bonus for bonus in rewardsList if bonus.getValue() == stopToken ] != []


def _convertToBonuses(rewards):
    boxBonuses = BattlePassAwardsManager.composeBonuses([rewards])
    group = {}
    i = 0
    for boxBonus in boxBonuses:
        oldBonusGroup, probability, bonuses = _convertBonusGroup([boxBonus])
        bonusGroup = getBonusGroup(i)
        i += 1
        if bonusGroup is None:
            bonusGroup = oldBonusGroup
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


def _preprocessReRollAwards(awards):
    return _preprocessBonusGroup(awards)


def _preprocessAwards(awards):
    if len(awards) > 1:
        return [ _preprocessBonusGroup(group) for group in awards ]
    return _preprocessBonusGroup(awards)


def _preprocessBonusGroup(awards):
    bonusList = [awards] if not isinstance(awards, list) else awards
    bonuses = LootBoxAwardsManager.composeBonuses(bonusList)
    return LootBoxAwardsManager.processCompensation(bonuses)
