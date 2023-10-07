# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/damage_panel.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel
from buffs_helpers import ValueSimpleModifier
from gui.Scaleform.daapi.view.battle.shared.formatters import formatHealthProgress, normalizeHealthPercent

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

    def _updateMaxHealth(self):
        prebattleCtrl = self.sessionProvider.shared.prebattleSetups
        if prebattleCtrl is not None:
            prebattleMaxHealth = 0
            vehicleMaxHealth = 0
            prebattleVehicle = prebattleCtrl.getPrebattleSetupsVehicle()
            if prebattleVehicle is not None:
                prebattleMaxHealth = prebattleVehicle.descriptor.maxHealth
            vehicle = self._getControllingVehicle()
            if vehicle is not None:
                vehicleMaxHealth = vehicle.maxHealth
            return max(prebattleMaxHealth, vehicleMaxHealth)
        else:
            return 0

    def _updateHealth(self, health):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            vehicle = ctrl.getControllingVehicle()
            self._maxHealth = vehicle.maxHealth
        if self._maxHealth > 0:
            healthStr = formatHealthProgress(health, self._maxHealth)
            healthProgress = normalizeHealthPercent(health, self._maxHealth)
            self.as_updateHealthS(healthStr, healthProgress)
        return
