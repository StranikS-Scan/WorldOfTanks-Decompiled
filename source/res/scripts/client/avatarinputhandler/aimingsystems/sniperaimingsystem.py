# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/SniperAimingSystem.py
import BigWorld
import Math
import GUI
from Math import Vector3, Matrix
import math
from AvatarInputHandler import mathUtils
from AvatarInputHandler import AimingSystems
from AvatarInputHandler.AimingSystems import IAimingSystem
from AvatarInputHandler.Oscillator import Oscillator
from gun_rotation_shared import calcPitchLimitsFromDesc
from projectile_trajectory import getShotAngles
from AvatarInputHandler.cameras import readFloat, readVec3, readVec2
_MAX_DEVIATION_DEG = 90.0
_MAX_DEVIATION = math.radians(_MAX_DEVIATION_DEG)

class InputFilter:

    def __init__(self):
        self.__T1 = 0.5
        self.__T2 = 2.2
        self.__T3 = 1.5
        self.__F1 = 0.0
        self.__F2 = 0.0
        self.__delay = 0.0

    def reloadConfig(self, filterSec):
        if filterSec is not None:
            T_Vector = readVec3(filterSec, 'T', (0.0, 0.01, 0.01), (10.0, 10.0, 10.0), (0.0, 2.0, 1.0))
            self.__T1 = T_Vector[0]
            self.__T2 = T_Vector[1]
            self.__T3 = T_Vector[2]
        return

    def resetTimer(self):
        self.__delay = 0.0

    def reset(self, value):
        self.__F1 = self.__F2 = value
        self.__delay = 0.0

    def active(self):
        return self.__delay > 0.0 or math.fabs(self.__F1 - self.__F2) > 0.0001

    def value(self):
        return self.__F2

    def adjust(self, delta):
        self.__F1 += delta
        self.__F2 += delta

    def update(self, input, dt):
        self.__delay += dt
        if self.__delay >= self.__T1:
            self.__F1 += (input - self.__F1) * dt / self.__T2
            self.__F2 += (self.__F1 - self.__F2) * dt / self.__T3
            return self.__F2
        else:
            return self.__F2


class SniperAimingSystem(IAimingSystem):
    turretYaw = property(lambda self: self.__idealYaw + self.__oscillator.deviation.x)
    gunPitch = property(lambda self: self.__idealPitch + self.__oscillator.deviation.y)
    __CONSTRAINTS_MULTIPLIERS = Vector3(1.0, 1.0, 1.0)
    __activeSystem = None
    __FILTER_ENABLED = True

    @staticmethod
    def setStabilizerSettings(useHorizontalStabilizer, useVerticalStabilizer):
        SniperAimingSystem.__CONSTRAINTS_MULTIPLIERS.x = 1.0 if useHorizontalStabilizer else 0.0
        SniperAimingSystem.__CONSTRAINTS_MULTIPLIERS.y = 1.0 if useVerticalStabilizer else 0.0
        if SniperAimingSystem.__activeSystem is not None:
            SniperAimingSystem.__activeSystem.resetIdealDirection()
        return

    @staticmethod
    def getStabilizerSettings():
        return (SniperAimingSystem.__CONSTRAINTS_MULTIPLIERS.x > 0.0, SniperAimingSystem.__CONSTRAINTS_MULTIPLIERS.y > 0.0)

    @staticmethod
    def enableFilter(enable):
        SniperAimingSystem.__FILTER_ENABLED = enable

    def __init__(self, dataSec):
        IAimingSystem.__init__(self)
        self.__idealYaw = 0.0
        self.__idealPitch = 0.0
        self.__g_curPitch = 0.0
        self.__g_curYaw = 0.0
        self.__stailizationLimit = math.radians(60.0)
        self.__vehicleTypeDescriptor = None
        self.__vehicleMProv = None
        self.__vehiclePrevMat = None
        self.__yprDeviationConstraints = Vector3(math.pi * 2.1, math.pi / 2.0 * 0.95, 0.0)
        self.__oscillator = Oscillator(1.0, Vector3(0.0, 0.0, 15.0), Vector3(0.0, 0.0, 3.5), self.__yprDeviationConstraints)
        self.__pitchfilter = InputFilter()
        self.reloadConfig(dataSec)
        self.__pitchCompensating = 0.0
        return

    def reloadConfig(self, dataSec):
        filterSec = dataSec['aimingSystem']
        self.__pitchDeviation = readVec2(filterSec, 'deviation', (-_MAX_DEVIATION_DEG, -_MAX_DEVIATION_DEG), (_MAX_DEVIATION_DEG, _MAX_DEVIATION_DEG), (0.0, 0.0))
        self.__pitchDeviation = (-math.radians(self.__pitchDeviation[1]), -math.radians(self.__pitchDeviation[0]))
        self.__pitchfilter.reloadConfig(filterSec)

    def destroy(self):
        IAimingSystem.destroy(self)
        SniperAimingSystem.__activeSystem = None
        return

    def enableHorizontalStabilizerRuntime(self, enable):
        yawConstraint = math.pi * 2.1 if enable else 0.0
        self.__yprDeviationConstraints.x = yawConstraint

    def enable(self, targetPos):
        player = BigWorld.player()
        self.__vehicleTypeDescriptor = player.vehicleTypeDescriptor
        self.__vehicleMProv = player.getOwnVehicleStabilisedMatrix()
        self.__vehiclePrevMat = Matrix(self.__vehicleMProv)
        IAimingSystem.enable(self, targetPos)
        self.__yawLimits = self.__vehicleTypeDescriptor.gun['turretYawLimits']
        self.__pitchLimits = self.__vehicleTypeDescriptor.gun['pitchLimits']
        self.__idealYaw, self.__idealPitch = AimingSystems.getTurretYawGunPitch(self.__vehicleTypeDescriptor, self.__vehicleMProv, targetPos, True)
        self.__idealYaw, self.__idealPitch = self.__clampToLimits(self.__idealYaw, self.__idealPitch)
        currentGunMat = AimingSystems.getPlayerGunMat(self.__idealYaw, self.__idealPitch)
        self.__g_curYaw = currentGunMat.yaw
        self.__g_curPitch = (targetPos - currentGunMat.translation).pitch
        self._matrix.set(currentGunMat)
        self.__idealYaw, self.__idealPitch = self.__worldYawPitchToTurret(self.__g_curYaw, self.__g_curPitch)
        self.__idealYaw, self.__idealPitch = self.__clampToLimits(self.__idealYaw, self.__idealPitch)
        self.__oscillator.reset()
        self.__pitchfilter.reset(currentGunMat.pitch)
        SniperAimingSystem.__activeSystem = self
        vehicle = player.getVehicleAttached()
        if vehicle is not None:
            if not vehicle.filter.placingOnGround:
                vehicle.filter.calcPlacedMatrix(True)
                self.__baseMatrix = vehicle.filter.placingMatrix
            else:
                self.__baseMatrix = vehicle.matrix
        return

    def disable(self):
        SniperAimingSystem.__activeSystem = None
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if vehicle is not None:
            if not vehicle.filter.placingOnGround:
                vehicle.filter.calcPlacedMatrix(False)
        return

    def getDesiredShotPoint(self):
        start = self._matrix.translation
        scanDir = self._matrix.applyVector(Vector3(0.0, 0.0, 1.0))
        return AimingSystems.getDesiredShotPoint(start, scanDir)

    def resetIdealDirection(self):
        self.__idealYaw, self.__idealPitch = self.__worldYawPitchToTurret(self.__g_curYaw, self.__g_curPitch)
        self.__idealYaw, self.__idealPitch = self.__clampToLimits(self.__idealYaw, self.__idealPitch)
        self.__pitchfilter.reset(self.__g_curPitch)

    def handleMovement(self, dx, dy):
        self.__idealYaw, self.__idealPitch = self.__worldYawPitchToTurret(self.__g_curYaw, self.__pitchfilter.value())
        newPitch = self.__idealPitch + dy
        newYaw = self.__idealYaw + dx
        self.__idealYaw, idealPitch, inLimit, pitchMin, dp = self.__inLimit(self.__idealYaw, newYaw, newPitch)
        newPitch += dp
        if not inLimit:
            d1 = pitchMin - self.__idealPitch
            d2 = pitchMin - newPitch
            if math.fabs(d1) >= math.fabs(d2):
                self.__idealPitch = idealPitch
            currentGunMat = AimingSystems.getPlayerGunMat(self.__idealYaw, self.__idealPitch)
            self.__pitchfilter.adjust(currentGunMat.pitch - self.__pitchfilter.value())
        else:
            currentGunMat = AimingSystems.getPlayerGunMat(self.__idealYaw, idealPitch)
            self.__pitchfilter.reset(currentGunMat.pitch)
        self.__g_curYaw = currentGunMat.yaw
        self.__g_curPitch = currentGunMat.pitch
        self._matrix.set(currentGunMat)
        self.__oscillator.velocity = Vector3(0.0, 0.0, 0.0)
        _, uncompensatedPitch = AimingSystems.getTurretYawGunPitch(self.__vehicleTypeDescriptor, BigWorld.player().getOwnVehicleStabilisedMatrix(), self.getDesiredShotPoint())
        if inLimit:
            self.__pitchCompensating = mathUtils.clamp(math.radians(-2.0), math.radians(2.0), idealPitch - uncompensatedPitch)
        else:
            self.__pitchCompensating = 0.0

    def __clampToLimits(self, turretYaw, gunPitch):
        if self.__yawLimits is not None:
            turretYaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], turretYaw)
        pitchLimits = calcPitchLimitsFromDesc(turretYaw, self.__pitchLimits)
        if SniperAimingSystem.__FILTER_ENABLED:
            pitchLimitsMin = min(pitchLimits[0] + self.__pitchDeviation[0], _MAX_DEVIATION)
            pitchLimitsMax = max(pitchLimits[1] + self.__pitchDeviation[1], -_MAX_DEVIATION)
        else:
            pitchLimitsMin = pitchLimits[0]
            pitchLimitsMax = pitchLimits[1]
        gunPitch = mathUtils.clamp(pitchLimitsMin, pitchLimitsMax + self.__pitchCompensating, gunPitch)
        return (turretYaw, gunPitch)

    def __inLimit(self, prevYaw, newYaw, newPitch):
        if self.__yawLimits is not None:
            prevYaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], prevYaw)
            newYaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], newYaw)
        prevPitchLimits = calcPitchLimitsFromDesc(prevYaw, self.__pitchLimits)
        pitchLimits = calcPitchLimitsFromDesc(newYaw, self.__pitchLimits)
        if SniperAimingSystem.__FILTER_ENABLED:
            pitchLimitsMin = pitchLimits[0] + self.__pitchDeviation[0]
            pitchLimitsMax = pitchLimits[1] + self.__pitchDeviation[1]
            prevLimMin = prevPitchLimits[0] + self.__pitchDeviation[0]
            prevLimMax = prevPitchLimits[1] + self.__pitchDeviation[1]
        else:
            pitchLimitsMin = pitchLimits[0]
            pitchLimitsMax = pitchLimits[1]
            prevLimMin = prevPitchLimits[0]
            prevLimMax = prevPitchLimits[1]
        prevLimitedPitch = mathUtils.clamp(prevLimMin, prevLimMax, newPitch)
        limitedPitch = mathUtils.clamp(pitchLimitsMin, pitchLimitsMax, newPitch)
        dp = limitedPitch - prevLimitedPitch
        return (newYaw,
         limitedPitch,
         pitchLimitsMin <= newPitch <= pitchLimitsMax,
         pitchLimitsMin,
         dp)

    def __worldYawPitchToTurret(self, worldYaw, worldPitch):
        worldToTurret = Matrix(self.__vehicleMProv)
        worldToTurret.invert()
        worldToTurret.preMultiply(mathUtils.createRotationMatrix((worldYaw, worldPitch, 0.0)))
        return (worldToTurret.yaw, worldToTurret.pitch)

    def update(self, deltaTime):
        self.__oscillator.constraints = mathUtils.matrixScale(self.__yprDeviationConstraints, SniperAimingSystem.__CONSTRAINTS_MULTIPLIERS)
        l_curYaw, l_curPitch = self.__worldYawPitchToTurret(self.__g_curYaw, self.__g_curPitch)
        stabilizationOn = math.fabs(self._matrix.roll) < self.__stailizationLimit and SniperAimingSystem.__FILTER_ENABLED
        if stabilizationOn:
            l_curYaw, l_curNewPitch = self.__clampToLimits(l_curYaw, l_curPitch)
        else:
            l_curNewPitch = l_curPitch
        if stabilizationOn:
            newLocal = l_curPitch + (l_curNewPitch - l_curPitch)
            newGunMat = AimingSystems.getPlayerGunMat(l_curYaw, newLocal)
            new__g_curPitch = newGunMat.pitch
            new__g_curPitch = self.__pitchfilter.update(new__g_curPitch, deltaTime)
            globalDelta = new__g_curPitch - self.__g_curPitch
        else:
            globalDelta = l_curNewPitch - self.__idealPitch
        yprDelta = Vector3(l_curYaw - self.__idealYaw, globalDelta, 0.0)
        self.__oscillator.deviation = yprDelta
        self.__oscillator.update(deltaTime)
        l_curYaw = self.__idealYaw + self.__oscillator.deviation.x
        if stabilizationOn:
            l_curPitch = l_curPitch + self.__oscillator.deviation.y
        else:
            l_curPitch = self.__idealPitch + self.__oscillator.deviation.y
        l_curYaw, l_newCurPitch = self.__clampToLimits(l_curYaw, l_curPitch)
        if not stabilizationOn:
            globalDelta = l_newCurPitch - self.__idealPitch
            l_curPitch = l_newCurPitch
        yprDelta = Vector3(l_curYaw - self.__idealYaw, globalDelta, 0.0)
        self.__oscillator.deviation = yprDelta
        currentGunMat = AimingSystems.getPlayerGunMat(l_curYaw, l_curPitch)
        self.__g_curYaw = currentGunMat.yaw
        self.__g_curPitch = currentGunMat.pitch
        self._matrix.set(currentGunMat)
