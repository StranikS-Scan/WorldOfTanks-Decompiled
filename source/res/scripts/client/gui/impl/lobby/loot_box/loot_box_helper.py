# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import BigWorld
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.notifications import NotificationPriorityLevel

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


def parseOneOfBonusInfoSection(data):
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
                            bonuses.extend(parseGroupsBonusInfoSection(rawData))
                        bonuses.extend(getNonQuestBonuses(k, v))

    return bonuses


def parseAllOfBonusInfoSection(data):
    slots = dict()
    if data:
        for idx, slotsData in enumerate(data):
            probability, bonuses = parseSlotBonusInfoSection(slotsData)
            slots.setdefault(idx, {}).setdefault('probability', probability)
            slots.setdefault(idx, {}).setdefault('bonuses', bonuses)

    return slots


def parseSlotBonusInfoSection(data):
    if isinstance(data, tuple) and len(data) == 4:
        probability, _, _, rawData = data
        bonuses = []
        bonuses.extend(parseGroupsBonusInfoSection(rawData))
        return (probability, bonuses)
    return (0, [])


def parseGroupsBonusInfoSection(data):
    groups = data.get('groups', [])
    bonuses = []
    for groupData in groups:
        bonuses.extend(parseOneOfBonusInfoSection(groupData))

    return bonuses


def parseLimitBoxInfoSection(data):
    return data.get('limits', {}).get('guaranteedBonusLimit', {}).get('guaranteedFrequency', 30)
