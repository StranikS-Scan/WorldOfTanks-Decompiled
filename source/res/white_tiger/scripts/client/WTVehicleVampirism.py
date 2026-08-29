# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleVampirism.py
import BigWorld
from vehicle_systems.model_assembler import loadAppearancePrefab
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playVampirismRepair

class WTVehicleVampirism(DynamicScriptComponent):

    def __init__(self):
        super(WTVehicleVampirism, self).__init__()
        self.__prefabPath = None
        return

    def set_equipmentID(self, _):
        equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        self.__prefabPath = equipment.usagePrefab

    def onHeal(self):
        self.__loadPrefab()

    def _onAvatarReady(self):
        self.set_equipmentID(None)
        return

    def __loadPrefab(self):
        appearance = self.entity.appearance
        if appearance and appearance.isConstructed and self.__prefabPath:
            loadAppearancePrefab(self.__prefabPath, appearance, self.__onLoaded)

    def __onLoaded(self, _):
        if self.entity.id == BigWorld.player().playerVehicleID:
            playVampirismRepair(self.entity.position)
