# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/validators.py
from items import ITEM_TYPES, EQUIPMENT_TYPES, vehicles

def isBattleBooster(compDescr):
    itemTypeIdx, _, eqID = vehicles.parseIntCompactDescr(compDescr)
    if itemTypeIdx == ITEM_TYPES.equipment:
        equipment = vehicles.g_cache.equipments().get(eqID)
        if equipment and equipment.equipmentType == EQUIPMENT_TYPES.battleBoosters:
            return True
    return False
