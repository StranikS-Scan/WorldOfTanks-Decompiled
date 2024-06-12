# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_bonus_parsers/default_parser.py
from gui.impl.lobby.loot_box.loot_box_helper import BonusInfo, OneOfBonusInfo
from gui.server_events.bonuses import getNonQuestBonuses

def parseAllOfBonusInfoSection(data):
    slots = dict()
    if data:
        for idx, slotsData in enumerate(data):
            slotBonusInfo = BonusInfo(*slotsData)
            probability, bonuses, limitIDsMap = __parseSlotBonusInfoSection(slotBonusInfo)
            slots.setdefault(idx, {}).setdefault('probability', probability)
            slots.setdefault(idx, {}).setdefault('bonuses', bonuses)
            slots.setdefault(idx, {}).setdefault('limitIDsMap', limitIDsMap)

    return slots


def parseLimitBoxInfoSection(data):
    return data.get('limits', {}).get('guaranteedBonusLimit', {}).get('guaranteedFrequency', 30)


def __parseSlotBonusInfoSection(slotBonusInfo):
    if slotBonusInfo is not None:
        sectionLimitIDsMap, sectionBonuses = {}, []
        for key, data in slotBonusInfo.subBonusRawData.iteritems():
            if key == 'groups':
                groupsSectionLimitIDsmap, groupsSectionBonuses = __parseGroupsBonusInfoSection(data, slotBonusInfo)
                sectionLimitIDsMap = groupsSectionLimitIDsmap
                sectionBonuses.extend(groupsSectionBonuses)
            sectionBonuses.extend(getNonQuestBonuses(key, data))

        return (slotBonusInfo.probabilitiesList, sectionBonuses, sectionLimitIDsMap)
    else:
        return (0, [], {})


def __parseGroupsBonusInfoSection(groups, slotBonusInfo):
    limitIDsMap = dict()
    bonuses = []
    for groupData in groups:
        oneOfBonusInfo = OneOfBonusInfo(*groupData.get('oneof', ([], {})))
        sectionLimitIDsMap, sectionBonuses = __parseOneOfBonusInfoSection(oneOfBonusInfo)
        __updateLimitIDsMap(limitIDsMap, slotBonusInfo, sectionLimitIDsMap, sectionBonuses)
        bonuses.extend(sectionBonuses)

    return (limitIDsMap, bonuses)


def __parseOneOfBonusInfoSection(oneOfBonusInfo):
    limitIDsMap = dict()
    bonuses = []
    if oneOfBonusInfo is None:
        return (limitIDsMap, bonuses)
    else:
        for item in oneOfBonusInfo.subBonusRawData:
            bonusInfo = BonusInfo(*item)
            if bonusInfo and bonusInfo.subBonusRawData:
                for k, v in bonusInfo.subBonusRawData.iteritems():
                    if k == 'groups':
                        sectionLimitIDsMap, sectionBonuses = __parseGroupsBonusInfoSection(v, bonusInfo)
                        __updateLimitIDsMap(limitIDsMap, bonusInfo, sectionLimitIDsMap, sectionBonuses)
                        bonuses.extend(sectionBonuses)
                    sectionBonuses = getNonQuestBonuses(k, v)
                    __updateLimitIDsMap(limitIDsMap, bonusInfo, {}, sectionBonuses)
                    bonuses.extend(sectionBonuses)

        return (limitIDsMap, bonuses)


def __updateLimitIDsMap(resultLimitIDsMap, parentNodeBonusInfo, childLimitIDsMap, childBonuses):
    for childLimitID, childLimitBonuses in childLimitIDsMap.iteritems():
        resultLimitIDsMap.setdefault(childLimitID, []).extend(childLimitBonuses)

    if parentNodeBonusInfo.limitIDs:
        for limitID in parentNodeBonusInfo.limitIDs:
            if limitID not in childLimitIDsMap:
                resultLimitIDsMap.setdefault(limitID, []).extend(childBonuses)
