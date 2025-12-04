# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TankRamAbilityEquipment.py
from AbilityEquipment import AbilityEquipment
from PlayerEvents import g_playerEvents

class TankRamAbilityEquipment(AbilityEquipment):

    def showCollisionEffectWithOtherVehicle(self, selfPtForEffects, isAlly):
        g_playerEvents.onCollisionWithOtherAliveVehicle(selfPtForEffects, isAlly)
