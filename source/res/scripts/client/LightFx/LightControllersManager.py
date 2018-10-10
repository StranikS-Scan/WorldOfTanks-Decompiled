# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LightFx/LightControllersManager.py
from Controllers.HealthController import HealthController
import LightManager

class LightControllersManager(object):

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
