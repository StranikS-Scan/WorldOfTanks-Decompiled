# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/loot_box_helper.py
from collections import namedtuple
from copy import copy
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.advent_calendar_v2_consts import GUARANTEED_REWARD_GROUP_NAME
Slot = namedtuple('Slot', ('name', 'probability', 'bonuses'))

class LootBoxHelper(object):

    @staticmethod
    def getLootBoxBonuses(data):
        bonuses = []
        bonuses.extend(LootBoxHelper.__parseAllOfSection(data.pop('allof', [])))
        _, guaranteedBonuses = LootBoxHelper.__parseRawData(data)
        if guaranteedBonuses:
            bonuses.append(Slot(name=GUARANTEED_REWARD_GROUP_NAME, bonuses=guaranteedBonuses, probability=1.0))
        LootBoxHelper._plainSlots(bonuses)
        return bonuses

    @staticmethod
    def __parseAllOfSection(data):
        slots = []
        for slotsData in data:
            slots.append(LootBoxHelper.__parseSlotSection(slotsData))

        return slots

    @staticmethod
    def __parseSlotSection(data):
        probability, slotName, bonuses = 0, '', []
        if isinstance(data, tuple) and len(data) == 4:
            probability, _, _, rawData = data
            properties, bonuses = LootBoxHelper.__parseRawData(rawData)
            slotName = _stripSlotName(properties.get('name', ''))
            probability = probability[0]
        return Slot(name=slotName, bonuses=bonuses, probability=probability)

    @staticmethod
    def __parseOneOfSection(data):
        bonuses = []
        if data and len(data) == 2:
            _, items = data
            for item in items:
                slot = LootBoxHelper.__parseSlotSection(item)
                if slot.name:
                    bonuses.append(slot)
                bonuses.extend(slot.bonuses)

        return bonuses

    @staticmethod
    def __parseRawData(rawData):
        bonuses = []
        properties = {}
        for k, v in rawData.iteritems():
            if k == 'properties':
                properties.update(v)
            for b in getNonQuestBonuses(k, v):
                name = b.getName()
                if name == 'oneof':
                    bonuses.extend(LootBoxHelper.__parseOneOfSection(b.getValue()))
                if name == 'ny24Toys':
                    bonuses.extend(_extractNyRandomToy(b.getValue()))
                bonuses.append(b)

        return (properties, bonuses)

    @staticmethod
    def _plainSlots(slots):
        for slot in copy(slots):
            innerSlots = []
            for b in copy(slot.bonuses):
                if isinstance(b, Slot):
                    innerSlots.append(b)
                    slot.bonuses.remove(b)

            LootBoxHelper._plainSlots(innerSlots)
            slots.extend(innerSlots)
            if not slot.bonuses:
                slots.remove(slot)


def _extractNyRandomToy(rawData):
    bonuses = []
    for bonusValue in rawData.itervalues():
        for toyId, count in bonusValue.iteritems():
            bonuses.extend(getNonQuestBonuses('randomNy24Toy', count, ctx={'toyId': toyId}))

    return bonuses


def _stripSlotName(name):
    return name.replace('slot_', '')
