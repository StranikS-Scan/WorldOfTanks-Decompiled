# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleStunArea.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playStunAreaShot

class WTVehicleStunArea(DynamicScriptComponent):

    def set_state(self, prev):
        if self.state == prev:
            return
        if self.state == 1:
            isPC = self.entity.id == BigWorld.player().playerVehicleID
            playStunAreaShot(isPC, self.entity.position)
