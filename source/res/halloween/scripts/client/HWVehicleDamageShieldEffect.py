# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleDamageShieldEffect.py
import BigWorld
from items import vehicles
from HWVehicleEffect import HWVehicleEffect

class HWVehicleDamageShieldEffect(HWVehicleEffect):

    def __init__(self):
        self.ownerType = self.OwnerType.SELF
        self.specialId = 0
        super(HWVehicleDamageShieldEffect, self).__init__()

    def set_isRespawn(self, prev):
        self._waitAppearanceReady = self.entity.id == BigWorld.player().playerVehicleID and self.isRespawn

    def _getEffectData(self, isSpecial=False):
        equipment = vehicles.g_cache.equipments()[self.eqId]
        return equipment.respawnEffects if self.isRespawn else equipment.baseEffects

    def _onAppearanceReady(self):
        vehicle = self.entity
        appearance = vehicle.appearance
        if appearance is None or not appearance.isConstructed:
            return
        elif vehicle.health <= 0:
            return
        else:
            self._waitAppearanceReady = False
            self._activate(self.startTime)
            return
