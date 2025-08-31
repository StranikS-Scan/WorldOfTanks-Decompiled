# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_constants.py
from enum import Enum
from gui.server_events.bonuses import VehiclesBonus, CustomizationsBonus
from shared_utils import CONST_CONTAINER

class VehicleCharacteristics(Enum):
    PROS = 'pros'
    CONS = 'cons'


class BonusGroup(object):
    STYLE_3D = 'style3d'
    LOOTBOX = 'lootbox'
    OTHER = 'other'
    GUARANTEED_ITEMS = 'guaranteed_items'
    CUSTOMIZATION = 'customization'
    VEHICLES = 'vehicles'


class WhiteTigerLootBoxes(CONST_CONTAINER):
    WT_HUNTER = 'wt_hunter'
    WT_BOSS = 'wt_boss'
    WT_TANK = 'wt_tank'


def getBonusGroup(bonuses):
    customizationCount = sum((1 for bonus in bonuses if isinstance(bonus, CustomizationsBonus)))
    if customizationCount > 0:
        return BonusGroup.CUSTOMIZATION
    vehicleCount = sum((1 for bonus in bonuses if isinstance(bonus, VehiclesBonus)))
    return BonusGroup.VEHICLES if vehicleCount > 1 else BonusGroup.GUARANTEED_ITEMS
