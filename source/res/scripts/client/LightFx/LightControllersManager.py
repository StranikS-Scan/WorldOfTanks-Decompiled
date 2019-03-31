# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LightFx/LightControllersManager.py
# Compiled at: 2011-07-13 20:48:05
from Controllers.HealthController import HealthController
import LightManager

class LightControllersManager:

    def __init__(self, vehicle):
        self.__healthController = HealthController(vehicle.health, vehicle.typeDescriptor.maxHealth)

    def destroy(self):
        LightManager.g_instance.setStartupLights()

    def executeShotLight(self):
        LightManager.g_instance.startLightEffect('Shot')

    def executeHitLight(self):
        LightManager.g_instance.startLightEffect('Hit')

    def update(self, vehicle):
        self.__healthController.updateHealth(vehicle.health)
