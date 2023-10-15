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
        self._maxHealth = self.__getMaxHealth()

    def _updateHealth(self, health):
        self._maxHealth = self.__getMaxHealth()
        if self._maxHealth > 0:
            healthStr = formatHealthProgress(health, self._maxHealth)
            healthProgress = normalizeHealthPercent(health, self._maxHealth)
            self.as_updateHealthS(healthStr, healthProgress)

    def __getMaxHealth(self):
        maxHealths = [0]
        vehicle = self._getControllingVehicle()
        if vehicle is not None:
            maxHealths.append(vehicle.maxHealth)
        prebattleCtrl = self.sessionProvider.shared.prebattleSetups
        if prebattleCtrl is not None:
            prebattleVehicle = prebattleCtrl.getPrebattleSetupsVehicle()
            if prebattleVehicle is not None:
                maxHealths.append(prebattleVehicle.descriptor.maxHealth)
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP:
            playerVehType = arenaDP.getVehicleInfo(vehicle.id).vehicleType
            maxHealths.append(playerVehType.maxHealth)
        return max(maxHealths)
