# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/loot_box_helper.py
from collections import namedtuple
from copy import copy
from advent_calendar.gui.feature.constants import GUARANTEED_REWARD_GROUP_NAME
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency, int2roman
from items.components.ny_constants import ToyTypes
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.gui.shared import IItemsCache
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
                if name == 'ny25Toys':
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
            bonuses.extend(getNonQuestBonuses('randomNyToy', count, ctx={'toyId': toyId}))

    return bonuses


def _stripSlotName(name):
    return name.replace('slot_', '')


_VEHICLES_TIER_THRESHOLD = 8

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isHighTierBonusVehicle(bonus, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(bonus.getValue().keys()[0])
    return vehicle.level >= _VEHICLES_TIER_THRESHOLD if vehicle else None


def extractCustomizationBonus(bonus):
    value = bonus.getValue()
    if isinstance(value, list):
        value = value[0]
    return bonus.getC11nItem(value)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def extractItemBonus(bonus, itemsCache=None):
    item = itemsCache.items.getItemByCD(bonus.getValue().keys()[0])
    return item.userName if item else ''


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def extractVehicleBonus(bonus, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(bonus.getValue().keys()[0])
    return '{vehName} ({vehLevel})'.format(vehName=vehicle.userName, vehLevel=int2roman(vehicle.level)) if vehicle else ''


_BONUS_TYPE_VALUE_EXTRACTOR = {'items': extractItemBonus,
 'highTierVehicles': extractVehicleBonus,
 'lowTierVehicles': extractVehicleBonus}

def processProbabilityBonuses(probabilityGroups):
    processedBonuses = {}
    for probabilityGroup in probabilityGroups:
        bonusItems = {}
        for bonus in probabilityGroup.bonuses:
            bonusType = bonus.getName()
            if bonusType == 'currencies':
                bonusType = bonus.getCode()
            elif bonusType == 'vehicles':
                bonusType = 'highTierVehicles' if isHighTierBonusVehicle(bonus) else 'lowTierVehicles'
            elif bonusType == 'customizations':
                value = extractCustomizationBonus(bonus)
                if value:
                    bonusType = value.itemTypeName
                    if bonusType == 'style':
                        bonusType += '_3d' if value.is3D else '_2d'
                    bonusItems.setdefault(bonusType, set()).add(value.userName)
                    continue
            elif bonusType == 'randomNyToy':
                toyId = bonus.getContext().get('toyId')
                if toyId is not None and NewYearCurrentToyInfo(toyId).getToyType() == ToyTypes.COLOR_FIR:
                    bonusType = ToyTypes.COLOR_FIR
            bonusItems.setdefault(bonusType, set()).add(_BONUS_TYPE_VALUE_EXTRACTOR.get(bonusType, lambda b: str(b.getValue()))(bonus))

        processedBonuses.setdefault(probabilityGroup.name, {}).setdefault(probabilityGroup.probability, {}).update(bonusItems)

    return processedBonuses
