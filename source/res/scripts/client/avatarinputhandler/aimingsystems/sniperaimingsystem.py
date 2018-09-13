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

class SniperAimingSystem(IAimingSystem):
    turretYaw = property(lambda self: self.__idealTurretYaw + self.__oscillator.deviation.x)
    gunPitch = property(lambda self: self.__idealGunPitch + self.__oscillator.deviation.y)
    __CONSTRAINTS_MULTIPLIERS = Vector3(1.0, 1.0, 1.0)
    __activeSystem = None

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
        self.__idealTurretYaw = 0.0
        self.__idealGunPitch = 0.0
        self.__worldYaw = 0.0
        self.__worldPitch = 0.0
        self.__vehicleTypeDescriptor = None
        self.__vehicleMProv = None
        self.__vehiclePrevMat = None
        self.__yprDeviationConstraints = Vector3(math.pi * 2.1, math.pi / 2 * 0.95, 0.0)
        self.__oscillator = Oscillator(1.0, Vector3(0.0, 0.0, 15.0), Vector3(0.0, 0.0, 3.5), self.__yprDeviationConstraints)
        return

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
        self.__vehicleMProv = player.getOwnVehicleMatrix()
        self.__vehiclePrevMat = Matrix(self.__vehicleMProv)
        IAimingSystem.enable(self, targetPos)
        player = BigWorld.player()
        desc = player.vehicleTypeDescriptor
        self.__yawLimits = desc.gun['turretYawLimits']
        self.__idealTurretYaw, self.__idealGunPitch = getShotAngles(desc, player.getOwnVehicleMatrix(), (0, 0), targetPos, False)
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw, self.__idealGunPitch)
        currentGunMat = AimingSystems.getPlayerGunMat(self.__idealTurretYaw, self.__idealGunPitch)
        self.__worldYaw = currentGunMat.yaw
        self.__worldPitch = (targetPos - currentGunMat.translation).pitch
        self._matrix.set(currentGunMat)
        self.__idealTurretYaw, self.__idealGunPitch = self.__worldYawPitchToTurret(self.__worldYaw, self.__worldPitch)
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw, self.__idealGunPitch)
        self.__oscillator.reset()
        SniperAimingSystem.__activeSystem = self

    def disable(self):
        SniperAimingSystem.__activeSystem = None
        return

    def getDesiredShotPoint(self):
        start = self.matrix.translation
        scanDir = self.matrix.applyVector(Vector3(0, 0, 1))
        return AimingSystems.getDesiredShotPoint(start, scanDir)

    def resetIdealDirection(self):
        self.__idealTurretYaw, self.__idealGunPitch = self.__worldYawPitchToTurret(self.__worldYaw, self.__worldPitch)
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw, self.__idealGunPitch)

    def handleMovement(self, dx, dy):
        self.resetIdealDirection()
        self.__idealTurretYaw += dx
        self.__idealGunPitch += dy
        self.__idealTurretYaw, self.__idealGunPitch = self.__clampToLimits(self.__idealTurretYaw, self.__idealGunPitch)
        currentGunMat = AimingSystems.getPlayerGunMat(self.__idealTurretYaw, self.__idealGunPitch)
        self.__worldYaw = currentGunMat.yaw
        self.__worldPitch = currentGunMat.pitch
        self._matrix.set(currentGunMat)
        self.__oscillator.velocity = Vector3(0, 0, 0)

    def __clampToLimits(self, turretYaw, gunPitch):
        if self.__yawLimits is not None:
            turretYaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], turretYaw)
        desc = BigWorld.player().vehicleTypeDescriptor
        pitchLimits = calcPitchLimitsFromDesc(turretYaw, desc.gun['pitchLimits'])
        pitchLimitsMin = pitchLimits[0]
        pitchLimitsMax = pitchLimits[1]
        gunPitch = mathUtils.clamp(pitchLimitsMin, pitchLimitsMax, gunPitch)
        return (turretYaw, gunPitch)

    def __worldYawPitchToTurret(self, worldYaw, worldPitch):
        worldToTurret = Matrix(self.__vehicleMProv)
        worldToTurret.invert()
        worldToTurret.preMultiply(mathUtils.createRotationMatrix((worldYaw, worldPitch, 0)))
        return (worldToTurret.yaw, worldToTurret.pitch)

    def update(self, deltaTime):
        self.__oscillator.constraints = mathUtils.matrixScale(self.__yprDeviationConstraints, SniperAimingSystem.__CONSTRAINTS_MULTIPLIERS)
        vehicleMat = Matrix(self.__vehicleMProv)
        curTurretYaw, curGunPitch = self.__worldYawPitchToTurret(self.__worldYaw, self.__worldPitch)
        yprDelta = Vector3(curTurretYaw - self.__idealTurretYaw, curGunPitch - self.__idealGunPitch, 0)
        self.__oscillator.deviation = yprDelta
        self.__oscillator.update(deltaTime)
        curTurretYaw = self.__idealTurretYaw + self.__oscillator.deviation.x
        curGunPitch = self.__idealGunPitch + self.__oscillator.deviation.y
        curTurretYaw, curGunPitch = self.__clampToLimits(curTurretYaw, curGunPitch)
        yprDelta = Vector3(curTurretYaw - self.__idealTurretYaw, curGunPitch - self.__idealGunPitch, 0)
        self.__oscillator.deviation = yprDelta
        currentGunMat = AimingSystems.getPlayerGunMat(curTurretYaw, curGunPitch)
        self.__worldYaw = currentGunMat.yaw
        self.__worldPitch = currentGunMat.pitch
        self._matrix.set(currentGunMat)
        self.__vehiclePrevMat = vehicleMat
        return 0.0
