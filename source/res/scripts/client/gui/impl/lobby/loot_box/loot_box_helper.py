# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
from collections import namedtuple
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.gui.shared import IItemsCache
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isAllVehiclesObtainedInSlot(slot, itemsCache=None):
    inventoryVehicles = itemsCache.items.inventory.getIventoryVehiclesCDs()
    for bonus in slot['bonuses']:
        if bonus.getName() == 'vehicles':
            if any((i[0].intCD not in inventoryVehicles for i in bonus.getVehicles())):
                return False

    return True
