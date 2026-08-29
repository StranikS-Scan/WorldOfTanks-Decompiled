# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/AvatarComp7BaseComponent.py
from __future__ import absolute_import
from script_component.DynamicScriptComponent import DynamicScriptComponent

class AvatarComp7BaseComponent(DynamicScriptComponent):

    def chooseVehicleForBan(self, vehicleCD):
        self.cell.chooseVehicleForBan(vehicleCD)

    def confirmBanVehicle(self):
        self.cell.confirmBanVehicle()
