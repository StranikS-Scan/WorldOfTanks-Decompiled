# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/br_equipment_ctrl.py
from items import vehicles
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.battle_royale.constants import EQUIPMENT_ORDER

def createEquipmentByName(equipmentName):
    equipmentId = vehicles.g_cache.equipmentIDs()[equipmentName]
    return vehicles.g_cache.equipments()[equipmentId]


class BattleRoyaleEquipmentController(equipment_ctrl.EquipmentsController):
    __slots__ = ()

    def startControl(self, *args):
        self.__applyEmptyItems()

    def clear(self, leave=True):
        super(BattleRoyaleEquipmentController, self).clear(leave)
        if not leave:
            self.__applyEmptyItems()

    def __applyEmptyItems(self):
        for equipmentName in EQUIPMENT_ORDER:
            equipment = createEquipmentByName(equipmentName)
            self.setEquipment(equipment.compactDescr, 0, 0, 0, 0)
