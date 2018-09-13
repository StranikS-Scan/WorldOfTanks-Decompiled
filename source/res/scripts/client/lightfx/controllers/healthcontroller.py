# Embedded file name: scripts/client/LightFx/Controllers/HealthController.py
from LightFx import LightManager

class HealthController:
    HEALTH_EFFECTS = [(9000, 'Full Health'),
     (0.6, 'Mid Health'),
     (0.3, 'Low Health'),
     (0, 'Dead')]

    def __init__(self, health, maxHealth):
        self.__prevHealth = health
        self.__maxHealth = maxHealth
        self.__prevHealthEffect = self.getHealthEffect(health)
        LightManager.g_instance.startLightEffect(self.__prevHealthEffect)

    def getHealthEffect(self, health):
        durability = health * 1.0 / self.__maxHealth
        healthEffect = ''
        for durabilityEffect in HealthController.HEALTH_EFFECTS:
            if durabilityEffect[0] < durability:
                break
            healthEffect = durabilityEffect[1]

        return healthEffect

    def updateHealth(self, health):
        curHealthEffect = self.getHealthEffect(health)
        if health != self.__prevHealth:
            LightManager.g_instance.stopLightEffect(self.__prevHealthEffect)
            LightManager.g_instance.startLightEffect(curHealthEffect)
        if curHealthEffect == 'Dead' and curHealthEffect != self.__prevHealthEffect:
            LightManager.g_instance.startLightEffect('Death')
        self.__prevHealth = health
        self.__prevHealthEffect = curHealthEffect
