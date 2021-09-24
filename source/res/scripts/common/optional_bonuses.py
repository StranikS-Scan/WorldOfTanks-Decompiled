# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/optional_bonuses.py
import random
import copy
import time
from typing import Optional, Dict
from account_shared import getCustomizationItem
from soft_exception import SoftException
from items import tankmen
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from battle_pass_common import NON_VEH_CD

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
        subvalue = copy.deepcopy(subvalue)
        subvalue['value'] *= count
        if 'boundToCurrentVehicle' in subvalue:
            subvalue['vehTypeCompDescr'] = vehTypeCompDescr
        customizations.append(subvalue)


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
    total[key] = value


def __mergeBattlePassPoints(total, key, value, isLeaf=False, count=1, *args):
    defaultBattlePassPoints = {'vehicles': {NON_VEH_CD: 0}}
    seasonID = value.get('seasonID')
    if seasonID:
        defaultBattlePassPoints['seasonID'] = seasonID
    battlePass = total.setdefault(key, defaultBattlePassPoints)
    battlePass['vehicles'][NON_VEH_CD] += value.get('vehicles', {}).get(NON_VEH_CD, 0) * count


BONUS_MERGERS = {'credits': __mergeValue,
 'gold': __mergeValue,
 'xp': __mergeValue,
 'crystal': __mergeValue,
 'eventCoin': __mergeValue,
 'bpcoin': __mergeValue,
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
 'rankedDailyBattles': __mergeValue,
 'rankedBonusBattles': __mergeValue,
 'dogTagComponents': __mergeDogTag,
 'battlePassPoints': __mergeBattlePassPoints,
 'meta': lambda *args, **kwargs: None}
ITEM_INVENTORY_CHECKERS = {'vehicles': lambda account, key: account._inventory.getVehicleInvID(key) != 0,
 'customizations': lambda account, key: account._customizations20.getItems((key,), 0)[key] > 0,
 'tokens': lambda account, key: account._quests.hasToken(key)}

def getProbableBonuses(bonusType, value):
    if bonusType == 'allof':
        bonusData = value[0]
        probability, bonuses = bonusData[0], bonusData[3]
        return (probability, [bonuses] if bonuses is not None else [])
    elif bonusType == 'oneof':
        return (None, [ bonus for _, _, _, bonus in value[1] ])
    else:
        return (None, [])


class BonusItemsCache(object):

    def __init__(self, account, cache=None):
        self.__account = account
        self.__cache = cache or {}

    def getRawData(self):
        return self.__cache

    def onItemAccepted(self, itemName, itemKey):
        cache = self.__cache.setdefault(itemName, {})
        state = cache.get(itemKey, None)
        if state is not None:
            wasInInventory, wasAccepted = state
        else:
            wasInInventory = ITEM_INVENTORY_CHECKERS[itemName](self.__account, itemKey)
        cache[itemKey] = (wasInInventory, True)
        return

    def isItemExists(self, itemName, itemKey):
        cache = self.__cache.setdefault(itemName, {})
        state = cache.get(itemKey, None)
        if state is not None:
            wasInInventory, wasAccepted = state
        else:
            wasInInventory = ITEM_INVENTORY_CHECKERS[itemName](self.__account, itemKey)
            wasAccepted = False
            cache[itemKey] = (wasInInventory, wasAccepted)
        return wasInInventory or wasAccepted

    def getFinalizedCache(self):
        result = {}
        for bonus, checks in self.__cache.iteritems():
            bonusResult = result.setdefault(bonus, {})
            for key, (wasInInventory, wasAccepted) in checks.iteritems():
                bonusResult[key] = (wasInInventory or wasAccepted, False)

        return result

    @staticmethod
    def isInventoryChanged(account, itemsCache):
        for bonus, checks in itemsCache.iteritems():
            checker = ITEM_INVENTORY_CHECKERS[bonus]
            for key, (state, _) in checks.iteritems():
                if checker(account, key) != state:
                    return True

        return False


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

    def isAcceptable(self, bonusNode, checkInventory=True):
        if self.isLimitReached(bonusNode):
            return False
        return False if checkInventory and self.isBonusExists(bonusNode) else True

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
        for itemType in ('vehicles', 'tokens'):
            if itemType in bonusNode:
                for itemID in bonusNode[itemType].iterkeys():
                    cache.onItemAccepted(itemType, itemID)

        if 'customizations' in bonusNode:
            for customization in bonusNode['customizations']:
                c11nItem = getCustomizationItem(customization['custType'], customization['id'])[0]
                cache.onItemAccepted('customizations', c11nItem.compactDescr)

    def isBonusExists(self, bonusNode):
        cache = self.__bonusCache
        for itemType in ('vehicles', 'tokens'):
            if itemType in bonusNode:
                for itemID in bonusNode[itemType].iterkeys():
                    if cache.isItemExists(itemType, itemID):
                        return True

        if 'customizations' in bonusNode:
            for customization in bonusNode['customizations']:
                c11nItem = getCustomizationItem(customization['custType'], customization['id'])[0]
                if cache.isItemExists('customizations', c11nItem.compactDescr):
                    return True

        return False

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
            altList = list(enumerate(bonusNodes))
            random.shuffle(altList)
            for i, (_1, _2, _3, bonusValue) in altList:
                if i != selectedIdx:
                    isCompensation = bonusValue.get('properties', {}).get('compensation', False)
                    if isCompensation and isAcceptable(bonusValue):
                        selectedIdx = i
                        selectedValue = bonusValue
                        break
            else:
                shouldCompensated = selectedValue.get('properties', {}).get('shouldCompensated', False)
                if not isAcceptable(selectedValue, False) or shouldCompensated:
                    for i in xrange(len(bonusNodes)):
                        self.__trackChoice(False)

                    return

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

    def __init__(self):
        super(StripVisitor, self).__init__(self.ValuesMerger(), tuple())

    def onOneOf(self, storage, values):
        strippedValues = []
        _, values = values
        for probability, bonusProbability, refGlobalID, bonusValue in values:
            stippedValue = {}
            probability = bonusValue.get('properties', {}).get('userProbability', None)
            self._walkSubsection(stippedValue, bonusValue)
            strippedValues.append((probability,
             -1,
             None,
             stippedValue))

        storage['oneof'] = (None, strippedValues)
        return

    def onAllOf(self, storage, values):
        strippedValues = []
        for probability, bonusProbability, refGlobalID, bonusValue in values:
            stippedValue = {}
            probability = bonusValue.get('properties', {}).get('userProbability', None)
            self._walkSubsection(stippedValue, bonusValue)
            strippedValues.append((probability,
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
