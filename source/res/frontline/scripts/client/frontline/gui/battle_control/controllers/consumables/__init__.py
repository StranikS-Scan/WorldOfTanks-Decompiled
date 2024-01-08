# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/battle_control/controllers/consumables/__init__.py
from constants import ARENA_BONUS_TYPE
from frontline.gui.battle_control.controllers.consumables import epic_equipment_ctrl

def registerFLEquipmentController():
    from gui.battle_control.controllers.consumables import extendEquipmentController
    extendEquipmentController({ARENA_BONUS_TYPE.EPIC_BATTLE: epic_equipment_ctrl.EpicEquipmentsController}, {ARENA_BONUS_TYPE.EPIC_BATTLE: epic_equipment_ctrl.EpicReplayEquipmentController})
