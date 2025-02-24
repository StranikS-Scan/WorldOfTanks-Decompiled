# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/easy_tank_equip/constants.py
from enum import Enum
from items import ITEM_TYPE_NAMES, ITEM_TYPES
FEATURE = 'easy_tank_equip'

class EasyTankEquipLogActions(str, Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'
    SWITCH_PRESET = 'switch_preset'
    SWAP_SLOTS = 'swap_slots'


class EasyTankEquipLogItems(str, Enum):
    MAIN_VIEW = 'easy_tank_equip_view'
    APPLY_BUTTON = 'apply_button'
    CANCEL_BUTTON = 'cancel_button'
    CREW = ITEM_TYPE_NAMES[ITEM_TYPES.tankman]
    OPT_DEVICES = ITEM_TYPE_NAMES[ITEM_TYPES.optionalDevice]
    SHELLS = ITEM_TYPE_NAMES[ITEM_TYPES.shell]
    CONSUMABLES = ITEM_TYPE_NAMES[ITEM_TYPES.equipment]
    STYLES = ITEM_TYPE_NAMES[ITEM_TYPES.customizationItem]


class EasyTankEquipSwapInitiators(str, Enum):
    DRAG_AND_DROP = 'drag_and_drop'
    SWAP_BUTTON = 'swap_button'
