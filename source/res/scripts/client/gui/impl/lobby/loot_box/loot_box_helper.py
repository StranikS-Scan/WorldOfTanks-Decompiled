# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
from collections import namedtuple
from gui.server_events.bonuses import getNonQuestBonuses
from items.components.crew_books_constants import CREW_BOOK_RARITY
BonusInfo = namedtuple('SlotBonusInfo', ['probabilitiesList',
 'bonusProbability',
 'limitIDs',
 'subBonusRawData'])
OneOfBonusInfo = namedtuple('OneOfBonusInfo', ['limitIDs', 'subBonusRawData'])
_AGGREGATE_BONUS_TYPES = {'crewBooks': (CREW_BOOK_RARITY.CREW_COMMON, CREW_BOOK_RARITY.CREW_RARE)}

def aggregateSimilarBonuses(bonuses):
    masterAggregateBonuses = {}
    result = []
    for bonus in bonuses:
        if bonus.getName() in _AGGREGATE_BONUS_TYPES:
            needToAddBonus = True
            item, count = bonus.getItems()[0]
            type = item.descriptor.type
            if type in _AGGREGATE_BONUS_TYPES[bonus.getName()]:
                if type in masterAggregateBonuses:
                    _, masterCount = masterAggregateBonuses[type].getItems()[0]
                    if count != masterCount:
                        result.append(bonus)
                        continue
                needToAddBonus = type not in masterAggregateBonuses
                masterBonus = masterAggregateBonuses.setdefault(type, bonus)
                masterBonus.getValue()[item.intCD] = count
            if needToAddBonus:
                result.append(bonus)
        if bonus.getName() == 'collectionItem':
            if bonus.getCollectionId() not in masterAggregateBonuses:
                result.append(bonus)
                masterAggregateBonuses[bonus.getCollectionId()] = bonus
        result.append(bonus)

    return result


def parseAllOfBonusInfoSection(data):
    slots = dict()
    if data:
        for idx, slotsData in enumerate(data):
            probability, bonuses = __parseSlotBonusInfoSection(__toNamedTuple(slotsData, BonusInfo))
            slots.setdefault(idx, {}).setdefault('probability', probability)
            slots.setdefault(idx, {}).setdefault('bonuses', bonuses)

    return slots


def parseLimitBoxInfoSection(data):
    return data.get('limits', {}).get('guaranteedBonusLimit', {}).get('guaranteedFrequency', 30)


def __parseSlotBonusInfoSection(slotBonusInfo):
    if slotBonusInfo is not None:
        bonuses = []
        bonuses.extend(__parseGroupsBonusInfoSection(slotBonusInfo.subBonusRawData))
        return (slotBonusInfo.probabilitiesList, bonuses)
    else:
        return (0, [])


def __parseGroupsBonusInfoSection(data):
    groups = data.get('groups', [])
    bonuses = []
    for groupData in groups:
        bonuses.extend(__parseOneOfBonusInfoSection(groupData))

    return bonuses


def __parseOneOfBonusInfoSection(data):
    oneOfBonusInfo = __toNamedTuple(data.get('oneof', ()), OneOfBonusInfo)
    bonuses = []
    if oneOfBonusInfo is None:
        return bonuses
    else:
        for item in oneOfBonusInfo.subBonusRawData:
            bonusInfo = __toNamedTuple(item, BonusInfo)
            if bonusInfo and bonusInfo.subBonusRawData:
                for k, v in bonusInfo.subBonusRawData.iteritems():
                    if k == 'groups':
                        bonuses.extend(__parseGroupsBonusInfoSection(bonusInfo.subBonusRawData))
                    bonuses.extend(getNonQuestBonuses(k, v))

        return bonuses


def __toNamedTuple(data, nameTupleType):
    return nameTupleType._make(data) if isinstance(data, tuple) and len(data) == len(nameTupleType._fields) else None
