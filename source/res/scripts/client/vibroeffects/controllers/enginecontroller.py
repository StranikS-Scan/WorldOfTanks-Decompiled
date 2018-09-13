# Embedded file name: scripts/client/Vibroeffects/Controllers/EngineController.py
import BigWorld
import Vibroeffects.VibroManager as VibroManager
from debug_utils import *
from OnceController import OnceController
from Vibroeffects.EffectsSettings import EffectsSettings
import time

class EngineController:
    __SWAMP = 0
    __SAND = 1
    __OTHER_TERRAIN = 2

    def __init__(self):
        self.__lastVehicleSpeed = 0
        self.__lastTime = None
        self.__accelerationStartTime = None
        self.__prevEnginePower = 0
        self.__movingEffect = VibroManager.g_instance.getEffect('move_low_veff')
        self.__turnLeftEffect = None
        self.__turnRightEffect = None
        self.__idleEffect = VibroManager.g_instance.getEffect('move_idle_veff')
        self.__accelerationEffect = VibroManager.g_instance.getEffect('move_acceleration_veff')
        self.__brakingEffect = VibroManager.g_instance.getEffect('move_braking_veff')
        getEffect = VibroManager.g_instance.getEffect
        self.__engineEffects = {EngineController.__SWAMP: {2: getEffect('move_swamp_low_veff'),
                                    3: getEffect('move_swamp_high_veff')},
         EngineController.__SAND: {2: getEffect('move_sand_low_veff'),
                                   3: getEffect('move_sand_high_veff')},
         EngineController.__OTHER_TERRAIN: {2: getEffect('move_low_veff'),
                                            3: getEffect('move_high_veff')}}
        self.__turn = ''
        self.__lastTurn = ''
        self.__startupApply()
        return

    def destroy(self):
        self.__turnOffVibrations()

    def setTurn(self, value):
        self.__turn = value

    def __checkAcceleration(self, vehicle):
        totalAccelerationTime = 0 if self.__accelerationStartTime is None else time.time() - self.__accelerationStartTime
        ACC_ENGINE_MODE = 3
        if vehicle.engineMode[0] == ACC_ENGINE_MODE and self.__prevEnginePower != ACC_ENGINE_MODE:
            VibroManager.g_instance.startEffect(self.__accelerationEffect)
            self.__accelerationStartTime = time.time()
        elif vehicle.engineMode[0] != ACC_ENGINE_MODE and self.__prevEnginePower == ACC_ENGINE_MODE or totalAccelerationTime > self.__accelerationEffect.getDuration():
            if self.__accelerationEffect.isRunning():
                VibroManager.g_instance.stopEffect(self.__accelerationEffect)
            if vehicle.engineMode[0] != ACC_ENGINE_MODE:
                self.__accelerationStartTime = None
        curSpeed = vehicle.getSpeed()
        curTime = BigWorld.time()
        deltaT = curTime - self.__lastTime
        acc = (curSpeed - self.__lastVehicleSpeed) / deltaT
        if acc <= EffectsSettings.DecelerationThreshold:
            VibroManager.g_instance.startEffect(self.__brakingEffect)
        else:
            VibroManager.g_instance.stopEffect(self.__brakingEffect)
        self.__lastVehicleSpeed = curSpeed
        self.__lastTime = curTime
        self.__prevEnginePower = vehicle.engineMode[0]
        return

    def update(self, vehicle):
        if self.__lastTime is not None:
            self.__checkAcceleration(vehicle)
        else:
            self.__lastTime = BigWorld.time()
        enginePower = vehicle.engineMode[0]
        if enginePower == 0:
            self.__turnOffVibrations()
        elif enginePower == 1:
            self.__doApplyIdlePower()
        else:
            self.__doApplyNormalPower(vehicle)
        if self.__turn != self.__lastTurn:
            if self.__turn != 'left' and self.__turn != 'right':
                self.__turn = ''
            self.__lastTurn = self.__turn
            self.__doApplyTurn()
        return

    def __turnOffVibrations(self):
        VibroManager.g_instance.stopEffect(self.__movingEffect)
        VibroManager.g_instance.stopEffect(self.__idleEffect)
        VibroManager.g_instance.stopEffect(self.__accelerationEffect)
        VibroManager.g_instance.stopEffect(self.__brakingEffect)

    def __startupApply(self):
        self.__turn = ''
        self.__lastTurn = ''
        self.__turnOffVibrations()

    def __doApplyIdlePower(self):
        VibroManager.g_instance.startEffect(self.__idleEffect)
        VibroManager.g_instance.stopEffect(self.__movingEffect)

    def getMoveEffect(self, vehicle):
        terrainMaterialType = vehicle.appearance.terrainMatKind[0]
        terrainType = EngineController.__OTHER_TERRAIN
        if vehicle.appearance.isInWater or terrainMaterialType in (102,):
            terrainType = EngineController.__SWAMP
        elif terrainMaterialType in (103, 110):
            terrainType = EngineController.__SAND
        return self.__engineEffects[terrainType][vehicle.engineMode[0]]

    def __doApplyNormalPower(self, vehicle):
        oldMoveEffect = self.__movingEffect
        self.__movingEffect = self.getMoveEffect(vehicle)
        if self.__movingEffect != oldMoveEffect:
            VibroManager.g_instance.stopEffect(oldMoveEffect)
        VibroManager.g_instance.startEffect(self.__movingEffect)
        VibroManager.g_instance.stopEffect(self.__idleEffect)

    def __doApplyTurn(self):
        return
        if self.__turn == 'left':
            VibroManager.g_instance.startEffect(self.__turnLeftEffect)
            VibroManager.g_instance.stopEffect(self.__turnRightEffect)
        elif self.__turn == 'right':
            VibroManager.g_instance.startEffect(self.__turnRightEffect)
            VibroManager.g_instance.stopEffect(self.__turnLeftEffect)
        else:
            VibroManager.g_instance.stopEffect(self.__turnLeftEffect)
            VibroManager.g_instance.stopEffect(self.__turnRightEffect)
