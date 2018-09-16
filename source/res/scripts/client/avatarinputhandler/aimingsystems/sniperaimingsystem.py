# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/SniperAimingSystem.py
import math
import BigWorld
import Math
from Math import Vector3, Matrix
from AvatarInputHandler import mathUtils
from AvatarInputHandler import AimingSystems
from AvatarInputHandler.AimingSystems import IAimingSystem
from gun_rotation_shared import calcPitchLimitsFromDesc

class SniperAimingSystem(IAimingSystem):
    turretYaw = property(lambda self: self.__idealTurretYaw + self.__oscillator.deviation.x)
    gunPitch = property(lambda self: self.__idealGunPitch + self.__oscillator.deviation.y)
    __CONSTRAINTS_MULTIPLIERS = Vector3(1.0, 1.0, 1.0)
    __activeSystem = None
    __STABILIZED_CONSTRAINTS = Vector3(math.pi * 2.1, math.pi / 2.0 * 0.95, 0.0)
    __BEYOND_LIMITS_DELAY = 0.5

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

    def __init__(self):
        IAimingSystem.__init__(self)
        self.__zoom = None
        self.__idealTurretYaw = 0.0
        self.__idealGunPitch = 0.0
        self.__worldYaw = 0.0
        self.__worldPitch = 0.0
        self.__vehicleTypeDescriptor = None
        self.__vehicleMProv = None
        self.__yprDeviationConstraints = Vector3(SniperAimingSystem.__STABILIZED_CONSTRAINTS)
        self.__oscillator = Math.PyOscillator(1.0, Vector3(0.0, 0.0, 15.0), Vector3(0.0, 0.0, 3.5), self.__yprDeviationConstraints)
        self.__returningOscillator = Math.PyOscillator(1.0, Vector3(0.0, 15.0, 15.0), Vector3(0.0, 3.5, 3.5), self.__yprDeviationConstraints)
        self.__pitchCompensating = 0.0
        self.__yawLimits = None
        self.__forceFullStabilization = False
        self.__timeBeyondLimits = 0.0
        self.__playerGunMatFunction = AimingSystems.getPlayerGunMat
        return

    def destroy(self):
        IAimingSystem.destroy(self)
        SniperAimingSystem.__activeSystem = None
        return

    def enableHorizontalStabilizerRuntime(self, enable):
        yawConstraint = math.pi * 2.1 if enable else 0.0
        self.__yprDeviationConstraints.x = yawConstraint

    def forceFullStabilization(self, enable):
        self.__forceFullStabilization = enable

    def getPitchLimits(self):
        return self.__vehicleTypeDescriptor.gun.combinedPitchLimits

    def enable(self, targetPos, playerGunMatFunction=AimingSystems.getPlayerGunMat):
        player = BigWorld.player()
        self.__playerGunMatFunction = playerGunMatFunction
        self.__vehicleTypeDescriptor = player.vehicleTypeDescriptor
        self.__vehicleMProv = player.inputHandler.steadyVehicleMatrixCalculator.outputMProv
        IAimingSystem.enable(self, targetPos)
        self.focusOnPos(targetPos)
        self.__oscillator.reset()
        SniperAimingSystem.__activeSystem = self
        self.__timeBeyondLimits = 0.0

    def disable(self):
        SniperAimingSystem.__activeSystem = None
        return

    def focusOnPos(self, preferredPos):
        self.__yawLimits = self.__vehicleTypeDescriptor.gun.turretYawLimits
        if self.__isTurretHasStaticYaw():
            self.__yawLimits = None
        if self.__yawLimits is not None and abs(self.__yawLimits[0] - self.__yawLimits[1]) < 1e-05:
            self.__yawLimits = None
        self.__idealTurretYaw, self.__idealGunPitch = self.__getTurretYawGunPitch(preferredPos, True)
        self.__returningOscillator.reset()
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw, self.__idealGunPitch)
        currentGunMat = self.__getPlayerGunMat(self.__idealTurretYaw, self.__idealGunPitch)
        self.__worldYaw = currentGunMat.yaw
        self.__worldPitch = (preferredPos - currentGunMat.translation).pitch
        self.__idealTurretYaw, self.__idealGunPitch = self.__worldYawPitchToTurret(self.__worldYaw, self.__worldPitch)
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw, self.__idealGunPitch)
        currentGunMat = self.__getPlayerGunMat(self.__idealTurretYaw, self.__idealGunPitch)
        self.__worldYaw = currentGunMat.yaw
        self.__worldPitch = currentGunMat.pitch
        self._matrix.set(currentGunMat)
        return

    def getDesiredShotPoint(self):
        start = self._matrix.translation
        scanDir = self._matrix.applyVector(Vector3(0.0, 0.0, 1.0))
        return AimingSystems.getDesiredShotPoint(start, scanDir)

    def resetIdealDirection(self):
        self.__idealTurretYaw, self.__idealGunPitch = self.__worldYawPitchToTurret(self.__worldYaw, self.__worldPitch)
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw, self.__idealGunPitch)

    def handleMovement(self, dx, dy):
        self.__idealTurretYaw, self.__idealGunPitch = self.__worldYawPitchToTurret(self.__worldYaw, self.__worldPitch)
        pitchExcess = self.__calcPitchExcess(self.__idealTurretYaw + dx, self.__idealGunPitch + dy)
        if pitchExcess * dy < 0:
            dy = 0
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw + dx, self.__idealGunPitch + dy)
        if pitchExcess != 0.0:
            self.__adjustPitchLimitExtension(abs(pitchExcess), True)
        currentGunMat = self.__getPlayerGunMat(self.__idealTurretYaw, self.__idealGunPitch)
        self.__worldYaw = currentGunMat.yaw
        self.__worldPitch = currentGunMat.pitch
        self._matrix.set(currentGunMat)
        self.__oscillator.velocity = Vector3(0.0, 0.0, 0.0)
        self.__returningOscillator.velocity = Vector3(0.0, 0.0, 0.0)
        _, uncompensatedPitch = self.__getTurretYawGunPitch(self.getDesiredShotPoint())
        self.__pitchCompensating = mathUtils.clamp(math.radians(-2.0), math.radians(2.0), self.__idealGunPitch - uncompensatedPitch)
        if abs(self.__pitchCompensating) < 0.01:
            self.__pitchCompensating = 0.0

    def __clampToLimits(self, turretYaw, gunPitch):
        if self.__yawLimits is not None:
            turretYaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], turretYaw)
        pitchLimits = calcPitchLimitsFromDesc(turretYaw, self.getPitchLimits())
        adjustment = max(0, self.__returningOscillator.deviation.y)
        pitchLimits[0] -= adjustment
        pitchLimits[1] += adjustment
        gunPitch = mathUtils.clamp(pitchLimits[0], pitchLimits[1] + self.__pitchCompensating, gunPitch)
        return (turretYaw, gunPitch)

    def __adjustPitchLimitExtension(self, value, shrinkOnly=False):
        if value < 0.0:
            value = 0.0
            self.__returningOscillator.reset()
        if shrinkOnly and value > self.__returningOscillator.constraints.y:
            return
        extension = Math.Vector3(0, value, 0)
        self.__returningOscillator.constraints = extension
        self.__returningOscillator.deviation = extension

    def __calcPitchExcess(self, turretYaw, gunPitch):
        if self.__yawLimits is not None:
            turretYaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], turretYaw)
        pitchLimits = calcPitchLimitsFromDesc(turretYaw, self.getPitchLimits())
        if pitchLimits[0] > gunPitch:
            return pitchLimits[0] - gunPitch
        else:
            return self.__pitchCompensating + pitchLimits[1] - gunPitch if self.__pitchCompensating + pitchLimits[1] < gunPitch else 0.0

    def __worldYawPitchToTurret(self, worldYaw, worldPitch):
        worldToTurret = Matrix(self.__vehicleMProv)
        worldToTurret.invert()
        worldToTurret.preMultiply(mathUtils.createRotationMatrix((worldYaw, worldPitch, 0.0)))
        return (worldToTurret.yaw, worldToTurret.pitch)

    def update(self, deltaTime):
        if self.__forceFullStabilization:
            self.__oscillator.constraints = SniperAimingSystem.__STABILIZED_CONSTRAINTS
        else:
            self.__oscillator.constraints = mathUtils.matrixScale(self.__yprDeviationConstraints, SniperAimingSystem.__CONSTRAINTS_MULTIPLIERS)
        curTurretYaw, curGunPitch = self.__worldYawPitchToTurret(self.__worldYaw, self.__worldPitch)
        yprDelta = Vector3(curTurretYaw - self.__idealTurretYaw, curGunPitch - self.__idealGunPitch, 0.0)
        self.__oscillator.deviation = yprDelta
        self.__oscillator.update(deltaTime)
        curTurretYaw = self.__idealTurretYaw + self.__oscillator.deviation.x
        curGunPitch = self.__idealGunPitch + self.__oscillator.deviation.y
        if self.__returningOscillator.deviation.y <= 0.0:
            self.__returningOscillator.reset()
        pitchOutOfBounds = self.__calcPitchExcess(curTurretYaw, curGunPitch)
        if pitchOutOfBounds != 0.0:
            self.__timeBeyondLimits += deltaTime
            self.__adjustPitchLimitExtension(abs(pitchOutOfBounds))
            if self.__timeBeyondLimits > SniperAimingSystem.__BEYOND_LIMITS_DELAY:
                self.__returningOscillator.update(deltaTime)
        else:
            self.__returningOscillator.reset()
            self.__timeBeyondLimits = 0.0
        curTurretYaw, curGunPitch = self.__clampToLimits(curTurretYaw, curGunPitch)
        yprDelta = Vector3(curTurretYaw - self.__idealTurretYaw, curGunPitch - self.__idealGunPitch, 0.0)
        self.__oscillator.deviation = yprDelta
        currentGunMat = self.__getPlayerGunMat(curTurretYaw, curGunPitch)
        self.__worldYaw = currentGunMat.yaw
        self.__worldPitch = currentGunMat.pitch
        self._matrix.set(currentGunMat)

    def getShotPoint(self):
        return self.getDesiredShotPoint()

    def getZoom(self):
        return self.__zoom

    def overrideZoom(self, zoom):
        self.__zoom = zoom
        return zoom

    def __getPlayerGunMat(self, turretYaw, gunPitch):
        return self.__playerGunMatFunction(turretYaw, gunPitch)

    def __getTurretYawGunPitch(self, targetPos, compensateGravity=False):
        player = BigWorld.player()
        stabilisedMatrix = Math.Matrix(player.inputHandler.steadyVehicleMatrixCalculator.stabilisedMProv)
        turretYaw, gunPitch = AimingSystems.getTurretYawGunPitch(self.__vehicleTypeDescriptor, stabilisedMatrix, targetPos, compensateGravity)
        rotation = mathUtils.createRotationMatrix((turretYaw, gunPitch, 0.0))
        rotation.postMultiply(stabilisedMatrix)
        invertSteady = Math.Matrix(self.__vehicleMProv)
        invertSteady.invert()
        rotation.postMultiply(invertSteady)
        return (rotation.yaw, rotation.pitch)

    def __isTurretHasStaticYaw(self):
        return self.__vehicleTypeDescriptor.gun.staticTurretYaw is not None
