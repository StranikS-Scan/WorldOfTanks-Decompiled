# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_bonus_parsers/rotation_parser.py
from gui.impl.lobby.loot_box.loot_box_bonus_parsers.default_parser import parseGroupsBonusInfoSection
from gui.impl.lobby.loot_box.loot_box_helper import BonusInfo
from gui.server_events.bonuses import getNonQuestBonuses
from shared_utils import first

def parseBonusSection(data, rotationLevelCount):
    rotationSlots = [ {} for _ in range(rotationLevelCount) ]
    commonSlot = [ {} for _ in range(rotationLevelCount) ]
    rotationLevels = data.get('rotation', {}).get('groups', [])
    for idLevel, levelConfig in enumerate(rotationLevels):
        for idSlot, slotsData in enumerate(levelConfig.get('allof', {})):
            slotBonusInfo = BonusInfo(*slotsData)
            probability, bonuses, limitIDsMap, isRotationSlot = __parseSlotBonusInfoSection(slotBonusInfo)
            if isRotationSlot:
                rotationSlots[idLevel].setdefault(idSlot, {}).setdefault('probability', probability)
                rotationSlots[idLevel].setdefault(idSlot, {}).setdefault('bonuses', bonuses)
                rotationSlots[idLevel].setdefault(idSlot, {}).setdefault('limitIDsMap', limitIDsMap)
            commonSlot[idLevel].setdefault(idSlot, {}).setdefault('probability', probability)
            commonSlot[idLevel].setdefault(idSlot, {}).setdefault('bonuses', bonuses)
            commonSlot[idLevel].setdefault(idSlot, {}).setdefault('limitIDsMap', limitIDsMap)

    return (rotationSlots, first(commonSlot, default={}))


def __parseSlotBonusInfoSection(slotBonusInfo):
    if slotBonusInfo is not None:
        sectionLimitIDsMap, sectionBonuses, rotationSlot = {}, [], False
        for key, data in slotBonusInfo.subBonusRawData.iteritems():
            if key == 'groups':
                groupsSectionLimitIDsmap, groupsSectionBonuses = parseGroupsBonusInfoSection(data, slotBonusInfo)
                sectionLimitIDsMap = groupsSectionLimitIDsmap
                sectionBonuses.extend(groupsSectionBonuses)
            if key == 'properties':
                rotationSlot |= data.get('mainRotationBranch', False)
            sectionBonuses.extend(getNonQuestBonuses(key, data))

        return (slotBonusInfo.probabilitiesList,
         sectionBonuses,
         sectionLimitIDsMap,
         rotationSlot)
    else:
        return ([0],
         [],
         {},
         False)
