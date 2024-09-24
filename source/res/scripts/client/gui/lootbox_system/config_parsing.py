# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/config_parsing.py
from gui.server_events.bonuses import getNonQuestBonuses

def parseAllOfSection(data):
    slots = {}
    if data:
        for idx, slotsData in enumerate(data):
            probability, bonuses = parseSlotSection(slotsData)
            slot = slots.setdefault(idx, {})
            slot.setdefault('probability', probability)
            slot.setdefault('bonuses', bonuses)

    return slots


def parseSlotSection(data):
    if isinstance(data, tuple) and len(data) == 4:
        probability, _, _, rawData = data
        return (probability, parseGroupsSection(rawData))
    return (0, [])


def parseGroupsSection(data):
    groups = data.get('groups', [])
    bonuses = []
    for groupData in groups:
        bonuses.extend(parseOneOfSection(groupData))

    return bonuses


def parseOneOfSection(data):
    oneOf = data.get('oneof', ())
    bonuses = []
    if oneOf and len(oneOf) == 2:
        _, items = oneOf
        for item in items:
            if item and len(item) == 4:
                _, _, _, rawData = item
                if rawData:
                    for k, v in rawData.iteritems():
                        if k == 'groups':
                            bonuses.extend(parseGroupsSection(rawData))
                        bonuses.extend(getNonQuestBonuses(k, v))

    return bonuses
