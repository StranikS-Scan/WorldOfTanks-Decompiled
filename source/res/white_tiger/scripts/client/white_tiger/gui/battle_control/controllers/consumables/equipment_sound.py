# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/equipment_sound.py
import SoundGroups
from items import vehicles
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentSound

class WtEquipmentSound(EquipmentSound):

    @staticmethod
    def playPressed(item, result):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            sound = equipment.soundPressedReady if result else equipment.soundPressedNotReady
            if sound is not None:
                SoundGroups.g_instance.playSound2D(sound)
        return

    @staticmethod
    def playCancel(item):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            sound = equipment.soundPressedCancel
            if sound is not None:
                SoundGroups.g_instance.playSound2D(sound)
        return
