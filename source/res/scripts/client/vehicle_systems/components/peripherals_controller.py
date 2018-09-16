# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/peripherals_controller.py
import AuxiliaryFx
from Vibroeffects.ControllersManager import ControllersManager as VibrationControllersManager
from LightFx.LightControllersManager import LightControllersManager as LightFxControllersManager
import LightFx.LightManager
from svarog_script.py_component import Component

class PeripheralsController(Component):

    def __init__(self):
        self.__vibrationsCtrl = None
        self.__lightFxCtrl = None
        self.__auxiliaryFxCtrl = None
        return

    def attachToVehicle(self, vehicle):
        if self.__vibrationsCtrl is None:
            self.__vibrationsCtrl = VibrationControllersManager()
        if LightFx.LightManager.g_instance is not None and LightFx.LightManager.g_instance.isEnabled():
            self.__lightFxCtrl = LightFxControllersManager(vehicle)
        if AuxiliaryFx.g_instance is not None:
            self.__auxiliaryFxCtrl = AuxiliaryFx.g_instance.createFxController(vehicle)
        return

    def destroy(self):
        self.deactivate()

    def activate(self):
        pass

    def deactivate(self):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.destroy()
            self.__vibrationsCtrl = None
        if self.__lightFxCtrl is not None:
            self.__lightFxCtrl.destroy()
            self.__lightFxCtrl = None
        if self.__auxiliaryFxCtrl is not None:
            self.__auxiliaryFxCtrl.destroy()
            self.__auxiliaryFxCtrl = None
        return

    def switchFireVibrations(self, bStart):
        self.__vibrationsCtrl.switchFireVibrations(bStart)

    def executeHitVibrations(self, hitEffectCode):
        self.__vibrationsCtrl.executeHitVibrations(hitEffectCode)

    def executeRammingVibrations(self, vehicle, matKind=None):
        self.__vibrationsCtrl.executeRammingVibrations(vehicle.getSpeed(), matKind)

    def executeShootingVibrations(self, caliber):
        self.__vibrationsCtrl.executeShootingVibrations(caliber)

    def executeCriticalHitVibrations(self, vehicle, extrasName):
        self.__vibrationsCtrl.executeCriticalHitVibrations(vehicle, extrasName)

    def update(self, vehicle, crashedTrackCtrl):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.update(vehicle, crashedTrackCtrl.isLeftTrackBroken(), crashedTrackCtrl.isRightTrackBroken())
        if self.__lightFxCtrl is not None:
            self.__lightFxCtrl.update(vehicle)
        if self.__auxiliaryFxCtrl is not None:
            self.__auxiliaryFxCtrl.update(vehicle)
        return
