# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_bonus_parsers/rotation_parser.py
from gui.server_events.bonuses import getNonQuestBonuses
from gui.impl.lobby.loot_box.loot_box_helper import BonusInfo

def __allOfParser(bitmask, _, bonusValue, parentLimitIds, bonusLimitIds, ctx):
    bonusInfos = [ BonusInfo(*rawData) for rawData in bonusValue ]
    allChildLimitIds = set().union(*(bonusInfo.limitIDs for bonusInfo in bonusInfos if bonusInfo.limitIDs))
    for bonusInfo in bonusInfos:
        __parseSubsection(bitmask=bitmask & __getProbabilityBitmask(bonusInfo.probabilitiesList[0]), section=bonusInfo.subBonusRawData, parentLimitIds=__makeLimitIdsSet(bonusInfo.limitIDs), bonusLimitIds=bonusLimitIds.union(parentLimitIds - allChildLimitIds), ctx=ctx)


def __oneOfParser(bitmask, _, bonusValue, parentLimitIds, bonusLimitIds, ctx):
    _, rawBonusList = bonusValue
    bonusInfos = [ BonusInfo(*rawData) for rawData in rawBonusList ]
    allChildLimitIds = set().union(*(bonusInfo.limitIDs for bonusInfo in bonusInfos if bonusInfo.limitIDs))
    previousProbabilityList = [0] * ctx['probabilityStageCount']
    for bonusInfo in bonusInfos:
        actualCurrentProbability = [ curr - prev for curr, prev in zip(bonusInfo.probabilitiesList[0], previousProbabilityList) ]
        __parseSubsection(bitmask=bitmask & __getProbabilityBitmask(actualCurrentProbability), section=bonusInfo.subBonusRawData, parentLimitIds=__makeLimitIdsSet(bonusInfo.limitIDs), bonusLimitIds=bonusLimitIds.union(parentLimitIds - allChildLimitIds), ctx=ctx)
        previousProbabilityList = bonusInfo.probabilitiesList[0]


def __groupsParser(bitmask, _, bonusValue, parentLimitIds, bonusLimitIds, ctx):
    for rawData in bonusValue:
        __parseSubsection(bitmask=bitmask, section=rawData, parentLimitIds=parentLimitIds, bonusLimitIds=bonusLimitIds, ctx=ctx)


def __defaultParser(bitmask, bonusType, bonusValue, parentLimitIds, bonusLimitIds, ctx):
    bonuses = getNonQuestBonuses(bonusType, bonusValue)
    limitsToUpdate = bonusLimitIds.union(parentLimitIds)
    if __isEmptySlotsBitmask(bitmask) and bonusType == 'tokens':
        slotSettings = ctx['slotSettings']
        slotGuiParams = slotSettings.setdefault(ctx['slotId'], [])
        slotGuiParams.extend(sum([ bonus.getValue().keys() for bonus in bonuses ], []))
    elif __isCommonSlotsBitmask(bitmask, ctx['probabilityStageCount']):
        commonSlots = ctx['commonSlots']
        slot = commonSlots.setdefault(ctx['slotId'], __getEmptySlotData())
        __extendSlot(slot, bonuses, limitsToUpdate)
    else:
        for rotationId in __iterateBitsPositions(mask=bitmask):
            rotationSlots = ctx['rotationSlots']
            slot = rotationSlots[rotationId].setdefault(ctx['slotId'], __getEmptySlotData())
            __extendSlot(slot, bonuses, limitsToUpdate)


def __extendSlot(slot, bonuses, bonusLimitIds):
    slot['bonuses'].extend(bonuses)
    for bonusLimitId in bonusLimitIds:
        slot['limitIDsMap'].setdefault(bonusLimitId, []).extend(bonuses)


__PARSERS = {'allof': __allOfParser,
 'oneof': __oneOfParser,
 'groups': __groupsParser}

def parseBonusSection(data, probabilityStageCount):
    rotationSlots = [ {} for _ in range(probabilityStageCount) ]
    commonSlot = {}
    slotSettings = {}
    rawSlots = data.get('allof', [])
    for idx, slotsData in enumerate(rawSlots):
        slotBonusInfo = BonusInfo(*slotsData)
        bitmask = __getProbabilityBitmask(slotBonusInfo.probabilitiesList[0])
        ctx = __makeParserContext(idx, rotationSlots, commonSlot, probabilityStageCount, slotSettings)
        __parseSubsection(bitmask=bitmask, section=slotBonusInfo.subBonusRawData, parentLimitIds=__makeLimitIdsSet(slotBonusInfo.limitIDs), bonusLimitIds=set(), ctx=ctx)
        for rotationId in __iterateBitsPositions(bitmask):
            __updateSlotInfo(rotationSlots[rotationId].get(idx), slotBonusInfo.probabilitiesList, slotSettings.get(idx, []))

        __updateSlotInfo(commonSlot.get(idx), slotBonusInfo.probabilitiesList, slotSettings.get(idx, []))

    return (rotationSlots, commonSlot)


def __updateSlotInfo(slot, probabilityList, slotSettings):
    if slot:
        slot['probability'] = probabilityList
        slot['slotSettings'] = slotSettings


def __parseSubsection(bitmask, section, parentLimitIds, bonusLimitIds, ctx):
    for key, data in section.iteritems():
        parser = __PARSERS.get(key, __defaultParser)
        parser(bitmask, key, data, parentLimitIds, bonusLimitIds, ctx)


def __iterateBitsPositions(mask):
    while mask:
        maskWithoutMinBit = mask & mask - 1
        yield (mask - maskWithoutMinBit).bit_length() - 1
        mask = maskWithoutMinBit


def __getProbabilityBitmask(probabilityList):
    return sum((bool(probability) << i for i, probability in enumerate(probabilityList)))


def __isCommonSlotsBitmask(bitmask, probabilityStageCount):
    return bitmask == __getFullBitmask(probabilityStageCount)


def __isEmptySlotsBitmask(bitmask):
    return bitmask == 0


def __getFullBitmask(probabilityStageCount):
    return (1 << probabilityStageCount) - 1


def __getEmptySlotData():
    return {'probability': None,
     'bonuses': [],
     'limitIDsMap': {},
     'slotSettings': {}}


def __makeParserContext(slotId, rotationSlots, commonSlots, probabilityStageCount, slotSettings):
    return {'slotId': slotId,
     'probabilityStageCount': probabilityStageCount,
     'rotationSlots': rotationSlots,
     'commonSlots': commonSlots,
     'slotSettings': slotSettings}


def __makeLimitIdsSet(limitIds):
    return set(limitIds) if limitIds else set()
