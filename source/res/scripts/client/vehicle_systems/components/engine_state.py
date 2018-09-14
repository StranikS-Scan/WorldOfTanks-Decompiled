# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/engine_state.py
import math
from random import uniform
import BigWorld
from AvatarInputHandler.mathUtils import clamp
from constants import ARENA_PERIOD, VEHICLE_PHYSICS_MODE
from vehicle_systems import assembly_utility
from vehicle_systems.assembly_utility import LinkDescriptor
from Event import Event

class DetailedEngineState(assembly_utility.Component):
    rpm = property(lambda self: self._rpm)
    gearNum = property(lambda self: self._gearNum)
    gearUp = property(lambda self: self._gearUp)
    mode = property(lambda self: self._mode)
    starting = property(lambda self: self.__starting)
    physicLoad = property(lambda self: self._physicLoad)
    relativeSpeed = property(lambda self: self._relativeSpeed)
    engineLoad = property(lambda self: self._engineLoad)
    roughnessValue = property(lambda self: self._roughnessValue)
    relativeRPM = property(lambda self: self._reativelRPM)
    _STOPPED = 0
    _IDLE = 1
    _MEDIUM = 2
    _HIGH = 3

    def __init__(self):
        self._rpm = 0.0
        self._reativelRPM = 0.0
        self._gearNum = 0
        self._mode = DetailedEngineState._STOPPED
        self.__starting = False
        self._gearUp = False
        self._physicLoad = 0.0
        self._relativeSpeed = 0.0
        self._maxClimbAngle = math.radians(20.0)
        self._engineLoad = self._STOPPED
        self._vehicle = None
        self._gearUpCbk = None
        self.__startEngineCbk = None
        self.__prevArenaPeriod = BigWorld.player().arena.period
        self.onEngineStart = Event()
        if self.__prevArenaPeriod == ARENA_PERIOD.BATTLE or self.__prevArenaPeriod == ARENA_PERIOD.PREBATTLE:
            self.__startEngineCbk = BigWorld.callback(0.1, self.__startEngineFunc)
        BigWorld.player().arena.onPeriodChange += self.__arenaPeriodChanged
        return

    def destroy(self):
        BigWorld.player().arena.onPeriodChange -= self.__arenaPeriodChanged
        if self.__startEngineCbk is not None:
            BigWorld.cancelCallback(self.__startEngineCbk)
        self._vehicle = None
        self._gearUpCbk = None
        self.onEngineStart.clear()
        self.onEngineStart = None
        return

    def __arenaPeriodChanged(self, *args):
        period = BigWorld.player().arena.period
        if period != self.__prevArenaPeriod and period == ARENA_PERIOD.PREBATTLE:
            self._mode = DetailedEngineState._STOPPED
            self.__prevArenaPeriod = period
            maxTime = BigWorld.player().arena.periodEndTime - BigWorld.serverTime()
            maxTime = maxTime * 0.7 if maxTime > 0.0 else 1.0
            time = uniform(0.0, maxTime)
            self.__startEngineCbk = BigWorld.callback(time, self.__startEngineFunc)
        elif period == ARENA_PERIOD.BATTLE:
            if self.__startEngineCbk is None and self._mode == DetailedEngineState._STOPPED:
                self.onEngineStart()
            self.__starting = False
        return

    def __startEngineFunc(self):
        self.__startEngineCbk = None
        self.__starting = True
        self._mode = DetailedEngineState._IDLE
        self.onEngineStart()
        return

    def setMode(self, mode):
        if mode > DetailedEngineState._STOPPED:
            if self._mode == DetailedEngineState._STOPPED:
                self.__starting = True
            else:
                self.__starting = False
        else:
            self.__starting = False
        self._mode = mode

    def start(self, vehicle):
        self._vehicle = vehicle
        self._maxClimbAngle = math.acos(self._vehicle.typeDescriptor.physics['minPlaneNormalY'])

    def refresh(self, delta):
        vehicleTypeDescriptor = self._vehicle.typeDescriptor
        vehicleSpeed = self._vehicle.speedInfo.value[0]
        if vehicleSpeed > 0.0:
            self._relativeSpeed = vehicleSpeed / vehicleTypeDescriptor.physics['speedLimits'][0]
        else:
            self._relativeSpeed = vehicleSpeed / vehicleTypeDescriptor.physics['speedLimits'][1]
        self._relativeSpeed = clamp(-1.0, 1.0, self._relativeSpeed)

    def setGearUpCallback(self, gearUpCbk):
        self._gearUpCbk = gearUpCbk

    def delGearUpCallback(self):
        self._gearUpCbk = None
        return


class DetailedEngineStateWWISE(DetailedEngineState):
    rotationSpeed = property(lambda self: self.__rotationSpeed)
    roatationRelSpeed = property(lambda self: self.__roatationRelSpeed)
    gear2 = property(lambda self: self.__gear2)
    gear3 = property(lambda self: self.__gear3)
    rpmPhysicRel = property(lambda self: self.__rpmPhysicRel)
    rpmPhysicAbs = property(lambda self: self.__rpmPhysicAbs)
    _GEAR_DELTA = 0.2
    physicRPMLink = LinkDescriptor()
    physicGearLink = LinkDescriptor()

    def __init__(self):
        super(DetailedEngineStateWWISE, self).__init__()
        self.__rotationSpeed = 0.0
        self.__roatationRelSpeed = 0.0
        self.__prevGearNum = 0
        self.__prevGearNum2 = 0
        self.__gear2 = 0
        self.__gear3 = 0
        self.__rpmPhysicRel = 0.0
        self.__rpmPhysicAbs = 0.0
        self.__newPhysicGear = 0
        self.__prevPitch = 0
        self.__speed = 0.0

    def calculateRPM(self):
        self.__rpmPhysicRel = 0.0 if self.__newPhysicGear == 0 else self.physicRPMLink()
        mi = self._vehicle.typeDescriptor.engine['rpm_min']
        ma = self._vehicle.typeDescriptor.engine['rpm_max']
        self.__rpmPhysicAbs = self.__rpmPhysicRel * (ma - mi) + mi
        self._reativelRPM = self.__rpmPhysicRel

    def calculateGear(self):
        self.__newPhysicGear = self.physicGearLink()

    def refresh(self, delta):
        super(DetailedEngineStateWWISE, self).refresh(delta)
        self.calculateRPM()
        self.calculateGear()
        if not self._vehicle.isPlayerVehicle or self._vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
            speed = self._vehicle.speedInfo.value[0]
            self.__speed = (speed - self.__speed) * 0.2 * delta
            speedRange = self._vehicle.typeDescriptor.physics['speedLimits'][0] + self._vehicle.typeDescriptor.physics['speedLimits'][1]
            speedRangeGear = speedRange / 3
            self._gearNum = math.ceil(math.floor(math.fabs(self.__speed) * 50) / 50 / speedRangeGear)
            if self.__prevGearNum2 != self._gearNum:
                self.__prevGearNum = self.__prevGearNum2
            self._gearUp = self.__prevGearNum2 < self._gearNum and self._engineLoad > self._IDLE
            if self._gearUp and self._gearUpCbk is not None:
                self._gearUpCbk()
            if self._gearNum == 2 and self.__prevGearNum < self._gearNum:
                self.__gear_2 = 100
            else:
                self.__gear_2 = 0
            if self._gearNum == 3 and self.__prevGearNum < self._gearNum:
                self.__gear_3 = 100
            else:
                self.__gear_3 = 0
            self.__prevGearNum2 = self._gearNum
            if self._gearNum != 0 and self._engineLoad > self._IDLE:
                self._reativelRPM = math.fabs(1 + (self.__speed - self._gearNum * speedRangeGear) / speedRangeGear)
                self._reativelRPM = self._reativelRPM * (1.0 - self._GEAR_DELTA * self._gearNum) + self._GEAR_DELTA * self._gearNum
            else:
                self._reativelRPM = 0.0
            self._rpm = self._reativelRPM * 100.0
        else:
            self._gearUp = self.__newPhysicGear > self._gearNum
            if self._gearUp and self._gearUpCbk is not None:
                self._gearUpCbk()
            self._gearNum = self.__newPhysicGear
        self.__rotationSpeed = self._vehicle.speedInfo.value[1]
        self.__roatationRelSpeed = self.__rotationSpeed / self._vehicle.typeDescriptor.physics['rotationSpeedLimit']
        self._engineLoad = 2 if self._mode == 3 else self._mode
        self._roughnessValue = -(self._vehicle.pitch - self.__prevPitch) / delta
        self.__prevPitch = self._vehicle.pitch
        if self._mode >= 2:
            absRelSpeed = abs(self._relativeSpeed)
            if absRelSpeed > 0.01:
                k_mg = -abs(self._vehicle.pitch) / self._maxClimbAngle if self._relativeSpeed * self._vehicle.pitch > 0.0 else abs(self._vehicle.pitch) / self._maxClimbAngle
                self._physicLoad = (1.0 + k_mg) * 0.5
                if self._relativeSpeed > 0.0:
                    speedImpactK = 1.0 / 0.33
                else:
                    speedImpactK = 1.0 / 0.9
                speedImpact = clamp(0.01, 1.0, absRelSpeed * speedImpactK)
                speedImpact = clamp(0.0, 2.0, 1.0 / speedImpact)
                self._physicLoad = clamp(0.0, 1.0, self._physicLoad * speedImpact)
                self._physicLoad += self._roughnessValue if self._roughnessValue > 0 else 0
                self._physicLoad += clamp(0.0, 1.0, absRelSpeed - 0.9)
                self._physicLoad = clamp(0.0, 1.0, self._physicLoad)
                self._physicLoad = max(self._physicLoad, abs(self.__roatationRelSpeed))
            else:
                self._physicLoad = 1.0
        else:
            self._physicLoad = self._mode - 1
        return
