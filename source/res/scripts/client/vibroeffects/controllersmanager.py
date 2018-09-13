# Embedded file name: scripts/client/Vibroeffects/ControllersManager.py
from Controllers.HitController import HitController
from Controllers.DeathController import DeathController
from Controllers.EngineController import EngineController
from Controllers.RammingController import RammingController
from Controllers.SwitchController import SwitchController
from Controllers.TrackBreakingController import TrackBreakingController
from Controllers.ShootingController import ShootingController
from Controllers.OnceController import OnceController
import Vibroeffects.VibroManager as VibroManager

class ControllersManager:

    def __init__(self):
        self.__engineVibrationCtrl = EngineController()
        self.__fireVibrationCtrl = SwitchController('crit_fire_veff')
        self.__trackBreakingVibrationCtrl = TrackBreakingController()
        self.__deathVibrationCtrl = DeathController()
        self.__rammingVibrationCtrl = RammingController()

    def destroy(self):
        self.__engineVibrationCtrl.destroy()
        self.__fireVibrationCtrl.destroy()
        self.__rammingVibrationCtrl.destroy()
        VibroManager.g_instance.stopAllEffects()

    def update(self, vehicle, isLeftTrackBroken, isRightTrackBroken):
        if not VibroManager.g_instance.canWork():
            return
        self.__deathVibrationCtrl.update(vehicle.isAlive())
        self.__updateEngine(vehicle)
        if vehicle.isAlive():
            self.__trackBreakingVibrationCtrl.update(vehicle, isLeftTrackBroken, isRightTrackBroken)
        else:
            self.__fireVibrationCtrl.switch(False)
        VibroManager.g_instance.update()

    def switchFireVibrations(self, enableFire):
        if self.__fireVibrationCtrl is not None:
            self.__fireVibrationCtrl.switch(enableFire)
        return

    def executeRammingVibrations(self, vehicleSpeed, matKind):
        if VibroManager.g_instance.canWork():
            self.__rammingVibrationCtrl.execute(vehicleSpeed, matKind)

    def executeHitVibrations(self, hitEffectCode):
        if VibroManager.g_instance.canWork():
            HitController(hitEffectCode)

    def executeShootingVibrations(self, caliber):
        if VibroManager.g_instance.canWork():
            ShootingController(caliber)

    def executeCriticalHitVibrations(self, vehicle, extrasName):
        if not VibroManager.g_instance.canWork():
            return
        if extrasName == 'gunHealth':
            OnceController('crit_run_veff')
        elif extrasName == 'engineHealth':
            OnceController('crit_engine_veff')
        else:
            for tankman in vehicle.typeDescriptor.type.tankmen:
                if extrasName == tankman.name:
                    OnceController('crit_contusion_veff')
                    break

    def __updateEngine(self, vehicle):
        dirFlags = vehicle.engineMode[1]
        if dirFlags & 4 != 0:
            self.__engineVibrationCtrl.setTurn('left')
        elif dirFlags & 8 != 0:
            self.__engineVibrationCtrl.setTurn('right')
        else:
            self.__engineVibrationCtrl.setTurn('')
        self.__engineVibrationCtrl.update(vehicle)
