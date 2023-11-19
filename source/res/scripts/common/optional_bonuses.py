# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/optional_bonuses.py
import copy
import random
import time
import typing
from account_shared import getCustomizationItem
from battle_pass_common import NON_VEH_CD
from dog_tags_common.components_config import componentConfigAdapter
from soft_exception import SoftException
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
 'noviceReset': __mergeNoviceReset}
ITEM_INVENTORY_CHECKERS = {'vehicles': lambda account, key: account._inventory.getVehicleInvID(key) != 0 and not account._rent.isVehicleRented(account._inventory.getVehicleInvID(key)),
 'customizations': lambda account, key: account._customizations20.getItems((key,), 0)[key] > 0,
 'tokens': lambda account, key: account._quests.hasToken(key)}
RENT_ITEM_INVENTORY_CHECKERS = {'vehicles': lambda account, key: account._rent.isVehicleRented(account._inventory.getVehicleInvID(key))}

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

    def __init__(self, account, bonusConfig=None, counters=None, bonusCache=None, probabilityStage=0, logTracker=None, shouldResetUsedLimits=True):
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
        self.__initCounters(counters or {})
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
        if 'vehicles' in bonusNode:
            for itemID, itemData in bonusNode['vehicles'].iteritems():
                cache.onItemAccepted('vehicles', itemID, bool(itemData.get('rent', None)))

        if 'tokens' in bonusNode:
            for itemID in bonusNode['tokens'].iterkeys():
                cache.onItemAccepted('tokens', itemID)

        if 'customizations' in bonusNode:
            for customization in bonusNode['customizations']:
                c11nItem = getCustomizationItem(customization['custType'], customization['id'])[0]
                cache.onItemAccepted('customizations', c11nItem.compactDescr)

        return

    def isBonusExists(self, bonusNode):
        cache = self.__bonusCache
        if 'vehicles' in bonusNode:
            for itemID, itemData in bonusNode['vehicles'].iteritems():
                if cache.isItemExists('vehicles', itemID, bool(itemData.get('rent', None))):
                    return True

        if 'tokens' in bonusNode:
            for itemID, itemData in bonusNode['tokens'].iteritems():
                if cache.isItemExists('tokens', itemID):
                    return True

        if 'customizations' in bonusNode:
            for customization in bonusNode['customizations']:
                c11nItem = getCustomizationItem(customization['custType'], customization['id'])[0]
                if cache.isItemExists('customizations', c11nItem.compactDescr):
                    return True

        return False

    def depthCheck(self, bonusNode, checkInventory, depthLevel=None):
        currentDepthLevel = bonusNode.get('properties', {}).get('depthLevel', 0) if depthLevel is None else depthLevel
        return True if currentDepthLevel <= 0 else all((DEEP_CHECKERS[bonusNodeName](self, bonusNodeValue, checkInventory, currentDepthLevel) for bonusNodeName, bonusNodeValue in bonusNode.iteritems() if bonusNodeName in DEEP_CHECKERS))

    def getProbabilityStages(self):
        return self.__probabilitiesStage

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
            return self.__logTracker.generateInfo(beginStage, endStage, stagesCount, usedLimits)

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


class NodeVisitor(object):

    def __init__(self, mergers, args):
        self._mergers = mergers
        self._mergersArgs = args

    def onOneOf(self, storage, values):
        raise NotImplementedError()

    def onAllOf(self, storage, values):
        raise NotImplementedError()

    def onGroup(self, storage, values):
        raise NotImplementedError()

    def onMergeValue(self, storage, name, value, isLeaf):
        self._mergers[name](storage, name, value, isLeaf, *self._mergersArgs)

    def beforeWalk(self, storage, bonusSection):
        pass

    def _walkSubsection(self, storage, bonusSection):
        result = {}
        for bonusName, bonusValue in bonusSection.iteritems():
            if bonusName == 'oneof':
                self.onOneOf(result, bonusValue)
            if bonusName == 'allof':
                self.onAllOf(result, bonusValue)
            if bonusName == 'groups':
                self.onGroup(result, bonusValue)
            if bonusName in ('config', 'properties', 'needsExpansion'):
                continue
            self.onMergeValue(result, bonusName, bonusValue, True)

        for name, value in result.iteritems():
            self.onMergeValue(storage, name, value, False)

    def walkBonuses(self, bonusSection, storage=None):
        result = storage if storage is not None else {}
        self.beforeWalk(result, bonusSection)
        self._walkSubsection(result, bonusSection)
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
        self.__bonusTrack = []
        self.__nodeAcceptor = nodeAcceptor

    def getBonusTrack(self):
        return _packTrack(self.__bonusTrack)

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
            previousOwnProbability = 0.0
            canUsePrevInsteadOfZeroProbability = False
            for index, (probabilities, bonusProbability, _, bonusValue) in enumerate(bonusNodes):
                ownProbability = bonusProbability if useBonusProbability else probabilities[probablitiesStage]
                if ownProbability != 0.0:
                    ownProbability, sumOfPreviousProbabilities = ownProbability - sumOfPreviousProbabilities, ownProbability
                if ownProbability != 0.0:
                    canUsePrevInsteadOfZeroProbability = True
                    previousOwnProbability = ownProbability
                    probability = ownProbability
                elif canUsePrevInsteadOfZeroProbability and previousOwnProbability != 0.0:
                    probability = previousOwnProbability
                else:
                    continue
                if index != selectedIdx and bonusValue.get('properties', {}).get('compensation', False) and isAcceptable(bonusValue):
                    sumOfAvailableProbabilities += probability
                    availableBonusNodes.append((index, probability, bonusValue))
                    canUsePrevInsteadOfZeroProbability = False

            if not availableBonusNodes:
                shouldCompensated = selectedValue.get('properties', {}).get('shouldCompensated', False)
                if not isAcceptable(selectedValue, False) or shouldCompensated:
                    for i in xrange(len(bonusNodes)):
                        self.__trackChoice(False)

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
            self.__trackChoice(False)

        self.__trackChoice(True)
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
                self.__trackChoice(True)
                self.__nodeAcceptor.accept(bonusValue)
                self._walkSubsection(storage, bonusValue)
            self.__trackChoice(False)

    def onGroup(self, storage, values):
        for bonusValue in values:
            self._walkSubsection(storage, bonusValue)

    def beforeWalk(self, storage, bonusSection):
        acceptor = self.__nodeAcceptor
        acceptor.reuse()

    def __trackChoice(self, choice):
        self.__bonusTrack.append(choice)


class StripVisitor(NodeVisitor):

    class ValuesMerger:

        def __getitem__(self, item):
            return self.copyMerger

        @staticmethod
        def copyMerger(storage, name, value, isLeaf):
            storage[name] = value

    def __init__(self, needProbabilitiesInfo=False):
        self.__needProbabilitiesInfo = needProbabilitiesInfo
        super(StripVisitor, self).__init__(self.ValuesMerger(), tuple())

    def onOneOf(self, storage, values):
        strippedValues = []
        _, values = values
        needProbabilitiesInfo = self.__needProbabilitiesInfo
        for probability, bonusProbability, refGlobalID, bonusValue in values:
            stippedValue = {}
            self._walkSubsection(stippedValue, bonusValue)
            strippedValues.append(([probability if needProbabilitiesInfo else -1],
             -1,
             None,
             stippedValue))

        storage['oneof'] = (None, strippedValues)
        return

    def onAllOf(self, storage, values):
        strippedValues = []
        needProbabilitiesInfo = self.__needProbabilitiesInfo
        for probability, bonusProbability, refGlobalID, bonusValue in values:
            stippedValue = {}
            self._walkSubsection(stippedValue, bonusValue)
            strippedValues.append(([probability if needProbabilitiesInfo else -1],
             -1,
             None,
             stippedValue))

        storage['allof'] = strippedValues
        return

    def onGroup(self, storage, values):
        strippedValues = []
        for bonusValue in values:
            stippedValue = {}
            self._walkSubsection(stippedValue, bonusValue)
            strippedValues.append(stippedValue)

        storage['groups'] = strippedValues
