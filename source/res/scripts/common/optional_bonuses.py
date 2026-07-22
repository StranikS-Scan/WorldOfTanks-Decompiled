# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/optional_bonuses.py
import copy
import random
import time
import typing
from account_shared import getCustomizationItem
from battle_pass_common import NON_VEH_CD
from debug_utils import LOG_WARNING
from dog_tags_common.components_config import componentConfigAdapter
from soft_exception import SoftException
from copy import deepcopy
from WeakMethod import WeakMethodProxy
if typing.TYPE_CHECKING:
    from typing import Dict, Optional

def _packTrack(track):
    result = []
    if not track:
        return None
    else:
        curByte = curPos = 0
        for flag in track:
            if flag:
                curByte |= 1 << curPos
            curPos += 1
            if curPos > 7:
                result.append(curByte)
                curByte = curPos = 0

        result.append(curByte)
        result = ''.join(('{:02x}'.format(x) for x in bytearray(result)))
        return result


def _trackIterator(packedTrack):
    for curByte in bytearray.fromhex(packedTrack):
        for i in xrange(8):
            result = bool(curByte & 1 << i)
            yield result


def __mergeValue(total, key, value, isLeaf=False, count=1, *args):
    total[key] = total.get(key, 0) + count * value


def __mergeFactor(total, key, value, isLeaf, count=1, *args):
    if isLeaf:
        total[key] = total.get(key, 0) + count * (max(value, 1) - 1)
    else:
        total[key] = total.get(key, 0) + count * value


def __mergeItems(total, key, value, isLeaf=False, count=1, *args):
    items = total.setdefault(key, {})
    for itemCompDescr, itemCount in value.iteritems():
        items[itemCompDescr] = items.get(itemCompDescr, 0) + count * itemCount


def __mergeList(total, key, value, count):
    items = total.setdefault(key, [])
    items.extend((value if isinstance(value, list) else [value]) * count)


def __mergeVehicles(total, key, value, isLeaf, count, *args):
    __mergeList(total, key, value, count)


def __mergeTankmen(total, key, value, isLeaf, count, *args):
    __mergeList(total, key, value, count)


def __mergeCustomizations(total, key, value, isLeaf, count, vehTypeCompDescr):
    customizations = total.setdefault(key, [])
    for subvalue in value:
        currentValue = __findCustomization(customizations, subvalue)
        if currentValue is not None:
            currentValue['value'] += subvalue['value'] * count
        subvalue = copy.deepcopy(subvalue)
        subvalue['value'] *= count
        if 'boundToCurrentVehicle' in subvalue:
            subvalue['vehTypeCompDescr'] = vehTypeCompDescr
        customizations.append(subvalue)

    return


def __findCustomization(customizations, value):
    for customization in customizations:
        if all([ customization.get(param) == value.get(param) for param in ('custType', 'id', 'vehTypeCompDescr') ]):
            return customization

    return None


def __mergeCrewSkins(total, key, value, isLeaf, count, *args):
    __mergeList(total, key, value, count)


def __mergeTokens(total, key, value, isLeaf=False, count=1, *args):
    totalTokens = total.setdefault(key, {})
    for tokenID, tokenData in value.iteritems():
        total = totalTokens.setdefault(tokenID, {'count': 0,
         'expires': {},
         'limit': 0})
        total['count'] += count * tokenData.get('count', 1)
        if not total['expires']:
            total['expires'] = tokenData['expires']
        if 'limit' in tokenData:
            total['limit'] = tokenData['limit'] if total['limit'] == 0 else max(total['limit'], tokenData['limit'])
        extItems = tokenData.get('extItems', None)
        if extItems:
            __mergeList(total, 'extItems', extItems, 1)

    return


def __mergeGoodies(total, key, value, isLeaf=False, count=1, *args):
    totalGoodies = total.setdefault(key, {})
    for goodieID, goodieData in value.iteritems():
        total = totalGoodies.setdefault(goodieID, {'count': 0,
         'expires': {},
         'limit': 0})
        total['count'] += count * goodieData.get('count', 1)
        if not total['expires'] and 'expires' in goodieData:
            total['expires'] = goodieData['expires']
        if 'limit' in goodieData:
            total['limit'] = goodieData['limit'] if total['limit'] == 0 else max(total['limit'], goodieData['limit'])


def __mergeEntitlements(total, key, value, isLeaf=False, count=1, *args):
    totalEntitlements = total.setdefault(key, {})
    for entitlementCode, entitlementData in value.iteritems():
        total = totalEntitlements.setdefault(entitlementCode, {'count': 0})
        total['count'] += count * entitlementData.get('count', 1)
        if 'expires' not in total and 'expires' in entitlementData:
            total['expires'] = entitlementData['expires']


def __mergeEntitlementList(total, key, value, isLeaf=False, count=1, *args):
    entitlementList = total.setdefault(key, {})
    entitlementList.setdefault('items', []).extend(value.get('items', []) * count)


def __mergeCurrencies(total, key, value, isLeaf=False, count=1, *args):
    totalCurrency = total.setdefault(key, {})
    for currencyCode, currencyData in value.iteritems():
        total = totalCurrency.setdefault(currencyCode, {'count': 0})
        total['count'] += count * currencyData.get('count', 1)


def __mergeDossier(total, key, value, isLeaf=False, count=1, *args):
    totalDossiers = total.setdefault(key, {})
    for _dossierType, changes in value.iteritems():
        totalDossier = totalDossiers.setdefault(_dossierType, {})
        duplicatedkeys = not isinstance(changes, dict)
        it = changes if duplicatedkeys else changes.iteritems()
        for record, data in it:
            block, name = record
            try:
                record = (block, int(name))
            except:
                pass

            total = totalDossier.setdefault(record, {'value': 0,
             'unique': False,
             'type': 'add'})
            dataValue = data['value']
            if isinstance(dataValue, basestring):
                if dataValue == 'timestamp':
                    total['value'] = int(time.time())
            else:
                total['value'] += dataValue * count
            total['unique'] = data['unique']
            total['type'] = data['type']
            if 'actualValue' in data:
                total['actualValue'] = data['actualValue']


def __mergeBlueprints(total, key, value, isLeaf=False, count=1, *args):
    totalBlueprints = total.setdefault(key, {})
    for fragmentCD, fragmentData in value.iteritems():
        totalBlueprints.setdefault(fragmentCD, 0)
        totalBlueprints[fragmentCD] += count * fragmentData


def __mergeEnhancements(total, key, value, isLeaf=False, count=1, *args):
    enhancementsTotal = total.setdefault(key, {})
    for enhancementID, enhancementData in value.iteritems():
        enhancementMerged = enhancementsTotal.setdefault(enhancementID, {})
        enhancementMerged.update({'count': enhancementMerged.get('count', 0) + enhancementData.get('count', 0) * count,
         'wipe': enhancementMerged.get('wipe', False) or enhancementData.get('wipe', False)})


def __mergeDogTag(total, key, value, isLeaf=False, count=1, *args):
    dogTags = total.setdefault(key, [])
    dogTags.extend(value)
    dogTags.sort(key=lambda v: componentConfigAdapter.getComponentById(v['id']).viewType.value)


def __mergeBattlePassPoints(total, key, value, isLeaf=False, count=1, *args):
    defaultBattlePassPoints = {'vehicles': {NON_VEH_CD: 0}}
    seasonID = value.get('seasonID')
    chapterID = value.get('chapterID')
    if seasonID:
        defaultBattlePassPoints['seasonID'] = seasonID
    if chapterID:
        defaultBattlePassPoints['chapterID'] = chapterID
    battlePass = total.setdefault(key, defaultBattlePassPoints)
    battlePass['vehicles'][NON_VEH_CD] += value.get('vehicles', {}).get(NON_VEH_CD, 0) * count


def __mergeFreePremiumCrew(total, key, value, isLeaf=False, count=1, *args):
    freePremiumCrewBonus = total.setdefault(key, {})
    for vehLevel, freePremiumCrewCount in value.iteritems():
        freePremiumCrewBonus.setdefault(vehLevel, 0)
        freePremiumCrewBonus[vehLevel] += freePremiumCrewCount * count


def __mergeMeta(total, key, value, isLeaf=False, count=1, *args):
    total[key] = value


def __mergeNoviceReset(total, key, value, isLeaf=False, count=1, *args):
    total[key] = value


def __mergeDailyQuestReroll(total, key, value, isLeaf, count, *args):
    total.setdefault(key, set()).update(value)


def __mergeParagonsUnlocks(total, key, value, isLeaf, count, *args):
    total.setdefault(key, {})
    total[key].setdefault('ids', set()).update(value.get('ids', set()))


def __mergePreferredMapSlots(total, key, value, isLeaf, count, *args):
    preferredMapSlots = total.setdefault(key, {})
    for slotID, slotDurationDays in value.iteritems():
        preferredMapSlots.setdefault(slotID, 0)
        preferredMapSlots[slotID] += count * slotDurationDays


BONUS_MERGERS = {'credits': __mergeValue,
 'gold': __mergeValue,
 'xp': __mergeValue,
 'crystal': __mergeValue,
 'eventCoin': __mergeValue,
 'bpcoin': __mergeValue,
 'equipCoin': __mergeValue,
 'freeXP': __mergeValue,
 'tankmenXP': __mergeValue,
 'vehicleXP': __mergeValue,
 'creditsFactor': __mergeFactor,
 'xpFactor': __mergeFactor,
 'freeXPFactor': __mergeFactor,
 'tankmenXPFactor': __mergeFactor,
 'vehicleXPFactor': __mergeFactor,
 'items': __mergeItems,
 'vehicles': __mergeVehicles,
 'slots': __mergeValue,
 'berths': __mergeValue,
 'premium': __mergeValue,
 'premium_plus': __mergeValue,
 'premium_vip': __mergeValue,
 'tokens': __mergeTokens,
 'goodies': __mergeGoodies,
 'dossier': __mergeDossier,
 'tankmen': __mergeTankmen,
 'customizations': __mergeCustomizations,
 'crewSkins': __mergeCrewSkins,
 'blueprintsAny': __mergeItems,
 'blueprints': __mergeBlueprints,
 'enhancements': __mergeEnhancements,
 'entitlements': __mergeEntitlements,
 'entitlementList': __mergeEntitlementList,
 'currencies': __mergeCurrencies,
 'rankedDailyBattles': __mergeValue,
 'rankedBonusBattles': __mergeValue,
 'dogTagComponents': __mergeDogTag,
 'battlePassPoints': __mergeBattlePassPoints,
 'freePremiumCrew': __mergeFreePremiumCrew,
 'meta': __mergeMeta,
 'dailyQuestReroll': __mergeDailyQuestReroll,
 'noviceReset': __mergeNoviceReset,
 'paragonsUnlocks': __mergeParagonsUnlocks,
 'preferredMapSlots': __mergePreferredMapSlots}

def _vehiclesInventoryChecker(account, key):
    invId = account._inventory.getVehicleInvID(key)
    return not account._rent.isVehicleRented(invId) or account._recycleBin.availableRestoreVehicle(key) if invId != 0 else account._recycleBin.availableRestoreVehicle(key)


ITEM_INVENTORY_CHECKERS = {'vehicles': _vehiclesInventoryChecker,
 'customizations': lambda account, key: account._customizations20.getItems((key,), 0)[key] > 0,
 'tokens': lambda account, key: account._quests.hasToken(key)}
RENT_ITEM_INVENTORY_CHECKERS = {'vehicles': lambda account, key: account._rent.isVehicleRented(account._inventory.getVehicleInvID(key))}

def __vehiclesExistanceChecker(bonusValue, cache):
    for itemID, itemData in bonusValue.iteritems():
        if cache.isItemExists('vehicles', itemID, bool(itemData.get('rent', None))):
            return True

    return False


def __tokensExistanceChecker(bonusValue, cache):
    for itemID in bonusValue.iterkeys():
        if cache.isItemExists('tokens', itemID):
            return True

    return False


def __customizationsExistanceChecker(bonusValue, cache):
    for customization in bonusValue:
        c11nItem = getCustomizationItem(customization['custType'], customization['id'])[0]
        if cache.isItemExists('customizations', c11nItem.compactDescr):
            return True

    return False


UNIQUE_BONUSES_EXISTANCE_CHECKERS = {'vehicles': __vehiclesExistanceChecker,
 'tokens': __tokensExistanceChecker,
 'customizations': __customizationsExistanceChecker}

def __vehiclesCacheUpdater(bonusValue, cache):
    for itemID, itemData in bonusValue.iteritems():
        cache.onItemAccepted('vehicles', itemID, bool(itemData.get('rent', None)))

    return


def __tokensCacheUpdater(bonusValue, cache):
    for itemID in bonusValue.iterkeys():
        cache.onItemAccepted('tokens', itemID)


def __customizationsCacheUpdater(bonusValue, cache):
    for customization in bonusValue:
        c11nItem = getCustomizationItem(customization['custType'], customization['id'])[0]
        cache.onItemAccepted('customizations', c11nItem.compactDescr)


UNIQUE_BONUSES_CACHE_UPDATERS = {'vehicles': __vehiclesCacheUpdater,
 'tokens': __tokensCacheUpdater,
 'customizations': __customizationsCacheUpdater}

class BonusItemsCache(object):

    def __init__(self, account, cache=None):
        self.__account = account
        self.__cache = cache or {}

    def getRawData(self):
        return self.__cache

    def onItemAccepted(self, itemName, itemKey, isRent=False):
        cache = self.__cache.setdefault(itemName, {})
        state = cache.setdefault(itemKey, {}).get(isRent, None)
        if state is not None:
            wasInInventory, wasAccepted = state
        else:
            wasInInventory = (RENT_ITEM_INVENTORY_CHECKERS if isRent else ITEM_INVENTORY_CHECKERS)[itemName](self.__account, itemKey)
        cache[itemKey][isRent] = (wasInInventory, True)
        return

    def isItemExists(self, itemName, itemKey, isRent=False):
        cache = self.__cache.setdefault(itemName, {})
        state = cache.setdefault(itemKey, {}).get(isRent, None)
        if state is not None:
            wasInInventory, wasAccepted = state
        else:
            wasInInventory = (RENT_ITEM_INVENTORY_CHECKERS if isRent else ITEM_INVENTORY_CHECKERS)[itemName](self.__account, itemKey)
            wasAccepted = False
            cache[itemKey][isRent] = (wasInInventory, wasAccepted)
        if isRent and itemName in ITEM_INVENTORY_CHECKERS and cache[itemKey].get(False, None) is None:
            cache[itemKey][False] = (ITEM_INVENTORY_CHECKERS[itemName](self.__account, itemKey), False)
        return wasInInventory or wasAccepted or isRent and any((state for state in cache[itemKey].get(False, ())))

    def getFinalizedCache(self):
        result = {}
        for bonus, checks in self.__cache.iteritems():
            bonusResult = result.setdefault(bonus, {})
            for key, keyData in checks.iteritems():
                keyResult = bonusResult.setdefault(key, {})
                for flag, (wasInInventory, wasAccepted) in keyData.iteritems():
                    keyResult[flag] = (wasInInventory or wasAccepted, False)

        return result

    @staticmethod
    def isInventoryChanged(account, itemsCache):
        for bonus, checks in itemsCache.iteritems():
            checker = ITEM_INVENTORY_CHECKERS[bonus]
            for key, keyData in checks.iteritems():
                if False in keyData and checker(account, key) != keyData[False][0]:
                    return True

        return False


DEEP_CHECKERS = {'groups': lambda nodeAcceptor, bonusNode, checkInventory, depthLevel: all((nodeAcceptor.depthCheck(subBonusNode, checkInventory, depthLevel) for subBonusNode in bonusNode)),
 'allof': lambda nodeAcceptor, bonusNode, checkInventory, depthLevel: all((nodeAcceptor.isAcceptable(subBonusNode[-1], False, depthLevel - 1) for subBonusNode in bonusNode)),
 'oneof': lambda nodeAcceptor, bonusNode, checkInventory, depthLevel: any((nodeAcceptor.isAcceptable(subBonusNode[-1], checkInventory, depthLevel - 1) for subBonusNode in bonusNode[-1]))}

class BonusNodeAcceptor(object):

    def __init__(self, account, bonusConfig=None, counters=None, bonusCache=None, probabilityStage=0, rotationLevel=0, logTracker=None, shouldResetUsedLimits=True):
        self.__account = account
        self.__limitsConfig = bonusConfig.get('limits', None) if bonusConfig else None
        self.__maxStage = bonusConfig.get('probabilityStageCount', 1) - 1 if bonusConfig else 0
        self.__useBonusProbability = bonusConfig.get('useBonusProbability', False) if bonusConfig else False
        self.__locals = None
        self.__cooldowns = None
        self.__uses = None
        self.__shouldVisitNodes = None
        self.__bonusCache = bonusCache or BonusItemsCache(account)
        probabilityStage = min(probabilityStage, self.__maxStage)
        self.__probabilitiesStage = [probabilityStage, probabilityStage]
        self.__bonusProbabilityUses = None
        self.__shouldUseBonusProbability = False
        self.__isMaxStageReached = self.__maxStage <= probabilityStage
        self.__logTracker = logTracker
        self.__usedLimits = set()
        self.__shouldResetUsedLimits = shouldResetUsedLimits
        self.__maxRotationLevel = bonusConfig.get('rotationLevelCount', 1) - 1 if bonusConfig else 0
        rotationLevel = min(rotationLevel, self.__maxRotationLevel)
        self.__rotationsLevel = [rotationLevel, rotationLevel]
        self.currentLimitsID = set()
        self.__initCounters(counters or {})
        self._bonusTrack = []
        return

    def __initCounters(self, counters):
        if self.__limitsConfig:
            self.__uses = uses = {}
            self.__cooldowns = cooldowns = {}
            self.__locals = {}
            self.__bonusProbabilityUses = bonusProbabilityUses = {}
            for limitID, config in self.__limitsConfig.iteritems():
                if 'guaranteedFrequency' in config or 'maxFrequency' in config or 'useBonusProbabilityAfter' in config:
                    cooldowns[limitID], uses[limitID], bonusProbabilityUses[limitID] = counters.get(limitID, (0, 0, 0))

    def getCounters(self):
        if not self.__limitsConfig:
            return None
        else:
            result = {}
            cooldowns = self.__cooldowns
            uses = self.__uses
            bonusProbabilityUses = self.__bonusProbabilityUses
            for limitID, config in self.__limitsConfig.iteritems():
                if 'guaranteedFrequency' in config or 'maxFrequency' in config or 'useBonusProbabilityAfter' in config:
                    result[limitID] = (cooldowns[limitID], uses[limitID], bonusProbabilityUses[limitID])

            return result or None

    def setCounters(self, counters):
        for limitID, counterTuple in counters.iteritems():
            self.__cooldowns[limitID], self.__uses[limitID], self.__bonusProbabilityUses[limitID] = counterTuple

    def getBonusCache(self):
        return self.__bonusCache

    def isAcceptable(self, bonusNode, checkInventory=True, depthLevel=None):
        if self.isLimitReached(bonusNode):
            return False
        return False if checkInventory and self.isBonusExists(bonusNode) else self.depthCheck(bonusNode, checkInventory, depthLevel)

    def getNodesForVisit(self, ids):
        return self.__shouldVisitNodes.intersection(ids) if ids and self.__shouldVisitNodes else None

    def isLimitReached(self, bonusNode):
        if not self.__limitsConfig:
            return False
        limitID = bonusNode.get('properties', {}).get('limitID', None)
        if not limitID:
            return False
        elif self.__locals.get(limitID, 1) <= 0:
            return True
        else:
            return True if self.__cooldowns.get(limitID, 0) > 0 else False

    def updateBonusCache(self, bonusNode):
        cache = self.__bonusCache
        for itemType, updater in UNIQUE_BONUSES_CACHE_UPDATERS.iteritems():
            if itemType in bonusNode:
                updater(bonusNode[itemType], cache)

    def isBonusExists(self, bonusNode):
        cache = self.__bonusCache
        for itemType, checker in UNIQUE_BONUSES_EXISTANCE_CHECKERS.iteritems():
            if itemType in bonusNode:
                if checker(bonusNode[itemType], cache):
                    return True

        return False

    def depthCheck(self, bonusNode, checkInventory, depthLevel=None):
        currentDepthLevel = bonusNode.get('properties', {}).get('depthLevel', 0) if depthLevel is None else depthLevel
        return True if currentDepthLevel <= 0 else all((DEEP_CHECKERS[bonusNodeName](self, bonusNodeValue, checkInventory, currentDepthLevel) for bonusNodeName, bonusNodeValue in bonusNode.iteritems() if bonusNodeName in DEEP_CHECKERS))

    def getProbabilityStages(self):
        return self.__probabilitiesStage

    def setModifiedProbabilityStage(self, probabilitiesStage):
        self.__probabilitiesStage[1] = probabilitiesStage

    def getCurrentProbabilityStage(self):
        return self.__probabilitiesStage[0]

    def __increaseProbabilityStage(self):
        if self.__probabilitiesStage[1] < self.__maxStage:
            self.__probabilitiesStage[1] += 1

    def __updateProbabilityStages(self):
        self.__probabilitiesStage[0] = self.__probabilitiesStage[1]

    def __resetFlags(self):
        if not self.__isMaxStageReached or self.__shouldUseBonusProbability:
            self.__isMaxStageReached = self.__probabilitiesStage[1] >= self.__maxStage
            self.__shouldUseBonusProbability = False

    def getUseBonusProbability(self):
        return self.__shouldUseBonusProbability

    def getStagesInfo(self):
        return tuple(self.getProbabilityStages() + [self.__maxStage + 1])

    def getUsedLimits(self):
        return self.__usedLimits

    def getLoggingInfo(self):
        if self.__logTracker is None:
            return
        else:
            beginStage, endStage, stagesCount = self.getStagesInfo()
            usedLimits = self.getUsedLimits()
            rotationLevel = self.getCurrentRotationLevel()
            return self.__logTracker.generateInfo(beginStage, endStage, stagesCount, usedLimits, rotationLevel)

    def accept(self, bonusNode):
        if bonusNode.get('properties', {}).get('probabilityStageDependence', False):
            self.__increaseProbabilityStage()
        limitID = bonusNode.get('properties', {}).get('limitID', None)
        if limitID:
            limitConfig = self.__limitsConfig[limitID]
            if not limitConfig.get('countDuplicates', True) and self.isBonusExists(bonusNode):
                return
            if limitID in self.__locals:
                self.__locals[limitID] -= 1
            if limitID in self.__cooldowns:
                self.__cooldowns[limitID] = limitConfig.get('maxFrequency', 0)
            if limitID in self.__uses:
                self.__uses[limitID] = 0
            if limitID in self.__bonusProbabilityUses and not self.__isMaxStageReached:
                self.__bonusProbabilityUses[limitID] = 0
        self.updateBonusCache(bonusNode)
        return

    def reuse(self):
        self.__updateProbabilityStages()
        self.__resetFlags()
        self.__updateRotationLevel()
        if not self.__limitsConfig:
            return
        else:
            self.__locals = locals = {}
            cooldowns = self.__cooldowns
            uses = self.__uses
            self.__shouldVisitNodes = set([])
            bonusProbabilityUses = self.__bonusProbabilityUses
            if self.__shouldResetUsedLimits:
                self.__usedLimits = set()
            for limitID, limitConfig in self.__limitsConfig.iteritems():
                bonusLimit = limitConfig.get('bonusLimit', None)
                if bonusLimit is not None:
                    locals[limitID] = bonusLimit
                cooldown = limitConfig.get('maxFrequency', None)
                if cooldown is not None:
                    cooldowns[limitID] -= 1
                guaranteedFrequency = limitConfig.get('guaranteedFrequency', None)
                if guaranteedFrequency is not None:
                    uses[limitID] += 1
                    if uses[limitID] >= guaranteedFrequency:
                        self.__shouldVisitNodes.add(limitID)
                        self.__usedLimits.add(limitID)
                bonusProbabilityAfter = limitConfig.get('useBonusProbabilityAfter', None)
                if bonusProbabilityAfter is not None and not self.__isMaxStageReached and self.__useBonusProbability:
                    bonusProbabilityUses[limitID] += 1
                    if bonusProbabilityUses[limitID] > bonusProbabilityAfter:
                        self.__shouldUseBonusProbability = True
                        self.__usedLimits.add(limitID)

            return

    def isOverStage(self, bonusNode):
        return False if self.isBonusExists(bonusNode) else self.rotationCheck(bonusNode)

    def isMaxRotationLevel(self):
        return self.__rotationsLevel[1] == self.__maxRotationLevel

    def rotationCheck(self, bonusNode):
        rotationCheck = self.rotationCheck
        isOverStage = self.isOverStage
        getDict = bonusNode.get
        val = getDict('groups')
        if val is not None:
            for sub in val:
                if rotationCheck(sub):
                    break
            else:
                return False

        val = getDict('allof')
        if val is not None:
            for _, _, _, sub in val:
                if isOverStage(sub):
                    break
            else:
                return False

        val = getDict('oneof')
        if val is not None:
            for _, _, _, sub in val[1]:
                if isOverStage(sub):
                    break
            else:
                return False

        return True

    def increaseRotationLevel(self):
        if self.__rotationsLevel[1] < self.__maxRotationLevel:
            self.__rotationsLevel[1] += 1
            return
        LOG_WARNING('The rotation level cannot be increased above the maximum, accountID: %d' % self.__account.id)

    def getCurrentRotationLevel(self):
        return self.__rotationsLevel[0]

    def getRotationLevels(self):
        return self.__rotationsLevel

    def setModifiedRotationLevel(self, rotationLevel):
        if rotationLevel <= self.__maxRotationLevel:
            self.__rotationsLevel[1] = rotationLevel
            return
        LOG_WARNING('The rotation level cannot be set above the maximum, accountID: %d' % self.__account.id)

    def isRotation(self):
        return bool(self.__maxRotationLevel)

    def __updateRotationLevel(self):
        self.__rotationsLevel[0] = self.__rotationsLevel[1]

    def reInitCounters(self, bonusConfig):
        self.__limitsConfig = bonusConfig.get('limits', None) if bonusConfig else None
        if self.__limitsConfig:
            cooldowns = {}
            uses = {}
            bonusProbabilityUses = {}
            for limitID, config in self.__limitsConfig.iteritems():
                if 'guaranteedFrequency' in config or 'maxFrequency' in config or 'useBonusProbabilityAfter' in config:
                    cooldowns[limitID], uses[limitID], bonusProbabilityUses[limitID] = self.__cooldowns.get(limitID, 0), self.__uses.get(limitID, 0), self.__bonusProbabilityUses.get(limitID, 0)

            self.__cooldowns = cooldowns
            self.__uses = uses
            self.__bonusProbabilityUses = bonusProbabilityUses
        else:
            self.__cooldowns = None
            self.__uses = None
            self.__bonusProbabilityUses = None
        return

    def trackChoice(self, choice):
        self._bonusTrack.append(choice)

    def getBonusTrack(self):
        return _packTrack(self._bonusTrack)


class NodeVisitor(object):
    SKIP_KEYS = frozenset(('config', 'properties', 'needsExpansion'))

    def __init__(self, mergers, args):
        self._mergers = mergers
        self._mergersArgs = args
        self._handlers = {}
        self.registerHandler('oneof', self.onOneOf)
        self.registerHandler('allof', self.onAllOf)
        self.registerHandler('groups', self.onGroup)
        self.registerHandler('rotation', self.onRotations)

    def onOneOf(self, storage, values):
        raise NotImplementedError()

    def onAllOf(self, storage, values):
        raise NotImplementedError()

    def onGroup(self, storage, values):
        raise NotImplementedError()

    def onRotations(self, storage, values):
        raise NotImplementedError()

    def onMergeValue(self, storage, name, value, isLeaf):
        self._mergers[name](storage, name, value, isLeaf, *self._mergersArgs)

    def _beforeWalk(self, storage, bonusSection):
        return bonusSection

    def _afterWalk(self, storage, bonusSection):
        pass

    def registerHandler(self, key, func):
        self._handlers[key] = WeakMethodProxy(func)

    def _walkSubsection(self, storage, bonusSection):
        result = {}
        SKIP_KEYS = self.SKIP_KEYS
        onMergeValue = self.onMergeValue
        for bonusName, bonusValue in bonusSection.iteritems():
            handler = self._handlers.get(bonusName)
            if handler is not None:
                handler(result, bonusValue)
            if bonusName in SKIP_KEYS:
                continue
            onMergeValue(result, bonusName, bonusValue, True)

        for name, value in result.iteritems():
            onMergeValue(storage, name, value, False)

        return

    def walkBonuses(self, bonusSection, storage=None):
        result = storage if storage is not None else {}
        bonusSection = self._beforeWalk(result, bonusSection)
        self._walkSubsection(result, bonusSection)
        self._afterWalk(result, bonusSection)
        return result


class TrackVisitor(NodeVisitor):

    def __init__(self, track, *args):
        super(TrackVisitor, self).__init__(BONUS_MERGERS, args)
        self.__track = _trackIterator(track)

    def onOneOf(self, storage, values):
        for probability, bonusProbability, limitIDs, bonusValue in values[1]:
            if next(self.__track):
                self._walkSubsection(storage, bonusValue)
                return

    def onRotations(self, storage, values):
        values = values['groups']
        for bonusValue in values:
            if next(self.__track):
                self._walkSubsection(storage, bonusValue)
                break

    def onAllOf(self, storage, values):
        for probability, bonusProbability, refGlobalID, bonusValue in values:
            if next(self.__track):
                self._walkSubsection(storage, bonusValue)

    def onGroup(self, storage, values):
        for bonusValue in values:
            self._walkSubsection(storage, bonusValue)


class ProbabilityVisitor(NodeVisitor):

    def __init__(self, nodeAcceptor, *args):
        super(ProbabilityVisitor, self).__init__(BONUS_MERGERS, args)
        self.__nodeAcceptor = nodeAcceptor
        self.__preVisitor = PreVisitor(nodeAcceptor)

    def onOneOf(self, storage, values):
        rand = random.random()
        limitIDs, bonusNodes = values
        acceptor = self.__nodeAcceptor
        shouldVisitNodes = acceptor.getNodesForVisit(limitIDs)
        probablitiesStage = acceptor.getCurrentProbabilityStage()
        useBonusProbability = acceptor.getUseBonusProbability()
        if shouldVisitNodes:
            check = lambda _, nodeLimitIDs: nodeLimitIDs and nodeLimitIDs.intersection(shouldVisitNodes)
        else:
            check = lambda probability, _: probability > rand
        for i, (probabilities, bonusProbability, nodeLimitIDs, bonusValue) in enumerate(bonusNodes):
            probability = probabilities[probablitiesStage]
            if check(bonusProbability if useBonusProbability else probability, nodeLimitIDs):
                selectedIdx = i
                selectedValue = bonusValue
                break
        else:
            raise SoftException('Unreachable code, oneof probability bug %s' % bonusNodes)

        isAcceptable = acceptor.isAcceptable
        if not isAcceptable(selectedValue):
            availableBonusNodes = []
            sumOfAvailableProbabilities = 0
            sumOfPreviousProbabilities = 0
            for index, (probabilities, bonusProbability, _, bonusValue) in enumerate(bonusNodes):
                ownProbability = bonusProbability if useBonusProbability else probabilities[probablitiesStage]
                ownProbability, sumOfPreviousProbabilities = ownProbability - sumOfPreviousProbabilities, ownProbability
                if index != selectedIdx and bonusValue.get('properties', {}).get('compensation', False) and isAcceptable(bonusValue):
                    sumOfAvailableProbabilities += ownProbability
                    availableBonusNodes.append((index, ownProbability, bonusValue))

            if not availableBonusNodes:
                shouldCompensated = selectedValue.get('properties', {}).get('shouldCompensated', False)
                if not isAcceptable(selectedValue, False) or shouldCompensated:
                    for i in xrange(len(bonusNodes)):
                        self.__nodeAcceptor.trackChoice(False)

                    return
            elif len(availableBonusNodes) == 1:
                selectedIdx, _, selectedValue = availableBonusNodes[0]
            else:
                randomValue = random.random() * sumOfAvailableProbabilities
                sumOfPreviousProbabilities = 0
                for bonusNode in availableBonusNodes:
                    sumOfPreviousProbabilities += bonusNode[1]
                    if randomValue < sumOfPreviousProbabilities:
                        selectedIdx, _, selectedValue = bonusNode
                        break
                else:
                    raise SoftException('Unreachable code, oneof probability bug, random value: {}, available bonus nodes: {}'.format(randomValue, availableBonusNodes))

        for i in xrange(selectedIdx):
            self.__nodeAcceptor.trackChoice(False)

        self.__nodeAcceptor.trackChoice(True)
        acceptor.accept(selectedValue)
        self._walkSubsection(storage, selectedValue)

    def onAllOf(self, storage, values):
        acceptor = self.__nodeAcceptor
        probabilityStage = acceptor.getCurrentProbabilityStage()
        useBonusProbability = acceptor.getUseBonusProbability()
        for probabilities, bonusProbability, nodeLimitIDs, bonusValue in values:
            probability = bonusProbability if useBonusProbability else probabilities[probabilityStage]
            shouldVisitNodes = acceptor.getNodesForVisit(nodeLimitIDs)
            if shouldVisitNodes or probability > random.random() and acceptor.isAcceptable(bonusValue, False):
                self.__nodeAcceptor.trackChoice(True)
                self.__nodeAcceptor.accept(bonusValue)
                self._walkSubsection(storage, bonusValue)
            self.__nodeAcceptor.trackChoice(False)

    def onGroup(self, storage, values):
        for bonusValue in values:
            self._walkSubsection(storage, bonusValue)

    def onRotations(self, storage, values):
        pass

    def _beforeWalk(self, storage, bonusSection):
        bonusSection = self._preVisitorWalkBonuses(bonusSection)
        acceptor = self.__nodeAcceptor
        acceptor.reuse()
        return bonusSection

    def _preVisitorWalkBonuses(self, bonusSection):
        return self.__preVisitor.walkBonuses(bonusSection) if self.__nodeAcceptor.isRotation() else bonusSection


class StripVisitor(NodeVisitor):
    NON_STRIPPED_PROPERTIES = ('mainRotationBranch',)

    class ValuesMerger:

        def __getitem__(self, item):
            return self.copyMerger

        @staticmethod
        def copyMerger(storage, name, value, isLeaf):
            storage[name] = value

    def __init__(self, needProbabilitiesInfo=False, requiredLimitIds=None):
        super(StripVisitor, self).__init__(self.ValuesMerger(), tuple())
        self.__needProbabilitiesInfo = needProbabilitiesInfo
        self.__requiredLimitIds = requiredLimitIds
        self.registerHandler('properties', self.onProperties)

    def onRotations(self, storage, values):
        strippedValue = {}
        self._walkSubsection(strippedValue, values)
        storage['rotation'] = strippedValue

    def onProperties(self, storage, values):
        strippedProperties = {prop:values[prop] for prop in self.NON_STRIPPED_PROPERTIES if prop in values}
        if strippedProperties:
            storage['properties'] = strippedProperties

    def onOneOf(self, storage, values):
        strippedValues = []
        _, values = values
        needProbabilitiesInfo = self.__needProbabilitiesInfo
        requiredLimitIds = self.__requiredLimitIds
        for probability, bonusProbability, refGlobalID, bonusValue in values:
            if bonusValue.get('properties', {}).get('surprise', False):
                continue
            strippedValue = {}
            self._walkSubsection(strippedValue, bonusValue)
            strippedValues.append((probability if needProbabilitiesInfo else [-1],
             -1,
             refGlobalID.intersection(requiredLimitIds) if refGlobalID and requiredLimitIds else None,
             strippedValue))

        storage['oneof'] = (None, strippedValues)
        return

    def onAllOf(self, storage, values):
        strippedValues = []
        needProbabilitiesInfo = self.__needProbabilitiesInfo
        requiredLimitIds = self.__requiredLimitIds
        for probability, bonusProbability, refGlobalID, bonusValue in values:
            if bonusValue.get('properties', {}).get('surprise', False):
                continue
            strippedValue = {}
            self._walkSubsection(strippedValue, bonusValue)
            strippedValues.append((probability if needProbabilitiesInfo else [-1],
             -1,
             refGlobalID.intersection(requiredLimitIds) if refGlobalID and requiredLimitIds else None,
             strippedValue))

        storage['allof'] = strippedValues
        return

    def onGroup(self, storage, values):
        strippedValues = []
        for bonusValue in values:
            strippedValue = {}
            self._walkSubsection(strippedValue, bonusValue)
            strippedValues.append(strippedValue)

        storage['groups'] = strippedValues


class PreVisitor(NodeVisitor):

    class ValuesMerger:

        def __getitem__(self, item):
            return self.copyMerger

        @staticmethod
        def copyMerger(storage, name, value, isLeaf):
            storage[name] = value

    def __init__(self, nodeAcceptor):
        super(PreVisitor, self).__init__(self.ValuesMerger(), tuple())
        self.__nodeAcceptor = nodeAcceptor
        self.registerHandler('config', self.onConfig)
        self.registerHandler('properties', self.onProperties)
        self.__handlersSet = set(self._handlers)

    def _afterWalk(self, storage, bonusSection):
        self._stripConfig(storage)

    def _stripConfig(self, result):
        if self.__nodeAcceptor.currentLimitsID:
            limit = result['config']['limits']
            result['config']['limits'] = {key:limit[key] for key in self.__nodeAcceptor.currentLimitsID}
        self.__nodeAcceptor.reInitCounters(result['config'])

    def onProperties(self, storage, values):
        limitID = values.get('limitID')
        if limitID:
            self.__nodeAcceptor.currentLimitsID.update({limitID})
        storage['properties'] = values

    def onRotations(self, storage, values):
        values = values['groups']
        acceptor = self.__nodeAcceptor
        rotationLevel = self.__nodeAcceptor.getCurrentRotationLevel()
        if rotationLevel > 0:
            for _ in xrange(rotationLevel):
                acceptor.trackChoice(False)

        rotationBonus = {}
        for idx in xrange(rotationLevel, len(values)):
            try:
                rotationBonus.clear()
                acceptor.currentLimitsID.clear()
                self._walkSubsection(rotationBonus, values[idx])
                acceptor.trackChoice(True)
                break
            except NeedIncreaseRotationLevel:
                acceptor.trackChoice(False)
                acceptor.increaseRotationLevel()

        else:
            raise SoftException('Unreachable code, rotation level bug %s' % values)

        if not rotationBonus:
            raise SoftException('Current rotation is empty, rotationLevels: {}, rotation: {}'.format(acceptor.getRotationLevels(), values))
        storage.update(rotationBonus)

    def onOneOf(self, storage, values):
        limitIDs, values = values
        oneofValues = []
        for probabilities, bonusProbability, nodeLimitIDs, bonusValue in values:
            if bonusValue.get('properties', {}).get('mainRotationBranch', False):
                if not self.__nodeAcceptor.isMaxRotationLevel():
                    if not self.__nodeAcceptor.isOverStage(bonusValue):
                        raise NeedIncreaseRotationLevel()
                oneofStorage = {}
                self.__handlersSet.isdisjoint(bonusValue) or self._walkSubsection(oneofStorage, bonusValue)
            oneofValues.append((probabilities,
             bonusProbability,
             nodeLimitIDs,
             oneofStorage or bonusValue))

        storage['oneof'] = (limitIDs, oneofValues)

    def onAllOf(self, storage, values):
        allOfValues = []
        for probabilities, bonusProbability, nodeLimitIDs, bonusValue in values:
            if bonusValue.get('properties', {}).get('mainRotationBranch', False):
                if not self.__nodeAcceptor.isMaxRotationLevel():
                    if not self.__nodeAcceptor.isOverStage(bonusValue):
                        raise NeedIncreaseRotationLevel()
                allOfstorage = {}
                self.__handlersSet.isdisjoint(bonusValue) or self._walkSubsection(allOfstorage, bonusValue)
            allOfValues.append((probabilities,
             bonusProbability,
             nodeLimitIDs,
             allOfstorage or bonusValue))

        storage['allof'] = allOfValues

    def onGroup(self, storage, values):
        groupValues = []
        for bonusValue in values:
            if bonusValue.get('properties', {}).get('mainRotationBranch', False):
                if not self.__nodeAcceptor.isMaxRotationLevel():
                    raise self.__nodeAcceptor.isOverStage(bonusValue) or NeedIncreaseRotationLevel()
            groupStorage = {}
            self._walkSubsection(groupStorage, bonusValue)
            groupValues.append(groupStorage)

        storage['groups'] = groupValues

    def onConfig(self, storage, values):
        storage['config'] = deepcopy(values)


class NeedIncreaseRotationLevel(SoftException):
    pass
