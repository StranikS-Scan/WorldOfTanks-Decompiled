# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/damage_panel.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel
from buffs_helpers import ValueSimpleModifier

class HalloweenDamagePanel(DamagePanel):

    def updateVehicleParams(self, vehicle, _, vehicleID):
        modifiers = BigWorld.entity(vehicleID).hwMaxHealthModifier.modifiers
        if modifiers:
            maxHealth = vehicle.descriptor.maxHealth
            maxHealthModifiers = modifiers.getModifiers('maxHealth')
            newHealth, _ = ValueSimpleModifier(maxHealthModifiers).apply(maxHealth)
            if newHealth is not None:
                maxHealth = newHealth
            self._maxHealth = maxHealth
            self._updateHealth(maxHealth)
        else:
            super(HalloweenDamagePanel, self).updateVehicleParams(vehicle, _, vehicleID)
        return
