# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/ArcadeAimingSystem.py
import BigWorld
import Math
from Math import Vector3, Matrix
import functools
import math
from AvatarInputHandler import mathUtils, AimingSystems, cameras
from AvatarInputHandler.AimingSystems import IAimingSystem
from ProjectileMover import collideDynamic
from debug_utils import LOG_WARNING
import gun_rotation_shared

class ArcadeAimingSystem(IAimingSystem):

    def __setDistanceFromFocus(self, value):
        shotPoint = self.getThirdPersonShotPoint()
        self.__cursor.distanceFromFocus = value
        posOnVehicleProv = self.positionAboveVehicleProv.value
        posOnVehicle = Vector3(posOnVehicleProv.x, posOnVehicleProv.y, posOnVehicleProv.z)
        camPos = self.matrix.translation
        triBase = camPos - posOnVehicle
        pivotToTarget = shotPoint - posOnVehicle
        camPosToTarget = shotPoint - camPos
        if triBase.dot(camPosToTarget) * triBase.dot(pivotToTarget) > 0.0:
            if self.__shotPointCalculator is not None:
                self.__adjustFocus()
            else:
                self.focusOnPos(shotPoint)
        return

    def __setVehicleMProv(self, value):
        self.__vehicleMProv = value
        self.__cursor.base = value

    def __setYaw(self, value):
        self.__cursor.yaw = value
        if self.__cursor.yaw > 2.0 * math.pi:
            self.__cursor.yaw -= 2.0 * math.pi
        elif self.__cursor.yaw < -2.0 * math.pi:
            self.__cursor.yaw += 2.0 * math.pi

    def __setPitch(self, value):
        self.__cursor.pitch = mathUtils.clamp(self.__anglesRange[0], self.__anglesRange[1], value)

    def __setAimMatrix(self, aimMatrix):
        self.__aimMatrix = aimMatrix
        self.__setDistanceFromFocus(self.distanceFromFocus)

    vehicleMProv = property(lambda self: self.__vehicleMProv, __setVehicleMProv)
    positionAboveVehicleProv = property(lambda self: self.__cursor.positionAboveBaseProvider)
    distanceFromFocus = property(lambda self: self.__cursor.distanceFromFocus, __setDistanceFromFocus)
    aimMatrix = property(lambda self: self.__aimMatrix, __setAimMatrix)
    yaw = property(lambda self: self.__cursor.yaw, __setYaw)
    pitch = property(lambda self: self.__cursor.pitch, __setPitch)

    def __init__(self, vehicleMProv, heightAboveTarget, focusRadius, aimMatrix, anglesRange, enableSmartShotPointCalc = True):
        IAimingSystem.__init__(self)
        self.__aimMatrix = aimMatrix
        self.__vehicleMProv = vehicleMProv
        self.__anglesRange = anglesRange
        self.__cursor = BigWorld.ThirdPersonProvider()
        self.__cursor.base = vehicleMProv
        self.__cursor.heightAboveBase = heightAboveTarget
        self.__cursor.focusRadius = focusRadius
        self.__shotPointCalculator = ShotPointCalculatorPlanar() if enableSmartShotPointCalc else None
        return

    def getPivotSettings(self):
        return (self.__cursor.heightAboveBase, self.__cursor.focusRadius)

    def setPivotSettings(self, heightAboveBase, focusRadius):
        self.__cursor.heightAboveBase = heightAboveBase
        self.__cursor.focusRadius = focusRadius

    def destroy(self):
        IAimingSystem.destroy(self)

    def enable(self, targetPos, turretYaw = None, gunPitch = None):
        if targetPos is not None:
            self.focusOnPos(targetPos)
            if turretYaw is not None and gunPitch is not None:
                self.__adjustFocus((turretYaw, gunPitch))
        return

    def __adjustFocus(self, yawPitch = None):
        if self.__shotPointCalculator is None:
            return
        else:
            scanStart, scanDir = self.__getScanRay()
            self.focusOnPos(self.__shotPointCalculator.focusAtPos(scanStart, scanDir, yawPitch))
            return

    def disable(self):
        pass

    def setModelsToCollideWith(self, models):
        self.__cursor.setModelsToCollideWith(models)

    def focusOnPos(self, preferredPos):
        vehPos = Matrix(self.__vehicleMProv).translation
        posOnVehicle = vehPos + Vector3(0.0, self.__cursor.heightAboveBase, 0.0)
        self.yaw = (preferredPos - vehPos).yaw
        xzDir = Vector3(self.__cursor.focusRadius * math.sin(self.__cursor.yaw), 0.0, self.__cursor.focusRadius * math.cos(self.__cursor.yaw))
        pivotPos = posOnVehicle + xzDir
        self.pitch = self.__calcPitchAngle(self.__cursor.distanceFromFocus, preferredPos - pivotPos)
        self.__cursor.update(True)
        aimMatrix = self.__getLookToAimMatrix()
        aimMatrix.postMultiply(self.__cursor.matrix)
        self._matrix.set(aimMatrix)

    def __calcPitchAngle(self, distanceFromFocus, dir):
        fov = BigWorld.projection().fov
        near = BigWorld.projection().nearPlane
        yLength = near * math.tan(fov * 0.5)
        alpha = -self.__aimMatrix.pitch
        a = distanceFromFocus
        b = dir.length
        A = 2.0 * a * math.cos(alpha)
        B = a * a - b * b
        D = A * A - 4.0 * B
        if D > 0.0:
            c1 = (A + math.sqrt(D)) * 0.5
            c2 = (A - math.sqrt(D)) * 0.5
            c = c1 if c1 > c2 else c2
            cosValue = (a * a + b * b - c * c) / (2.0 * a * b) if a * b != 0.0 else 2.0
            if cosValue < -1.0 or cosValue > 1.0:
                LOG_WARNING('Invalid arg for acos: %f; distanceFromFocus: %f, dir: %s' % (cosValue, distanceFromFocus, dir))
                return -dir.pitch
            beta = math.acos(cosValue)
            eta = math.pi - beta
            return -dir.pitch - eta
        else:
            return -dir.pitch

    def getDesiredShotPoint(self):
        scanStart, scanDir = self.__getScanRay()
        if self.__shotPointCalculator is None:
            return self.getThirdPersonShotPoint()
        else:
            return self.__shotPointCalculator.getDesiredShotPoint(scanStart, scanDir)
            return

    def getThirdPersonShotPoint(self):
        if self.__shotPointCalculator is not None:
            return self.__shotPointCalculator.aimPlane.intersectRay(*self.__getScanRay())
        else:
            return AimingSystems.getDesiredShotPoint(*self.__getScanRay())
            return

    def handleMovement(self, dx, dy):
        self.yaw += dx
        self.pitch += dy

    def update(self, deltaTime):
        self.__cursor.update(True)
        aimMatrix = self.__getLookToAimMatrix()
        aimMatrix.postMultiply(self.__cursor.matrix)
        self._matrix.set(aimMatrix)
        if self.__shotPointCalculator is not None:
            self.__shotPointCalculator.update(*self.__getScanRay())
        return 0.0

    def __getScanRay(self):
        scanDir = self.matrix.applyVector(Vector3(0.0, 0.0, 1.0))
        scanStart = self.matrix.translation + scanDir * 0.3
        return (scanStart, scanDir)

    def __getLookToAimMatrix(self):
        return Matrix(self.__aimMatrix)


class _AimPlane(object):
    __EPS_COLLIDE_ARENA = 0.001

    def __init__(self):
        self.__plane = Math.Plane()
        self.init(Vector3(0.0, 0.0, 0.0), Vector3(0.0, 0.0, 0.0))

    def init(self, aimPos, targetPos):
        lookDir = targetPos - aimPos
        self.__lookLength = lookDir.length
        lookDir.normalise()
        self.__plane.init(targetPos, targetPos + Vector3(0.0, 0.0, 1.0), targetPos + Vector3(1.0, 0.0, 0.0))
        self.__initialProjection = Vector3(0.0, 1.0, 0.0).dot(lookDir)

    def intersectRay(self, startPos, dir, checkCloseness = True, checkSign = True):
        collisionPoint = self.__plane.intersectRay(startPos, dir)
        projection = Vector3(0.0, 1.0, 0.0).dot(dir)
        tooClose = collisionPoint.distTo(startPos) - self.__lookLength < -0.0001 and checkCloseness
        parallelToPlane = abs(projection) <= _AimPlane.__EPS_COLLIDE_ARENA
        projectionSignDiffers = projection * self.__initialProjection < 0.0 and checkSign
        backwardCollision = (collisionPoint - startPos).dot(dir) <= 0.0
        if tooClose or parallelToPlane or projectionSignDiffers or backwardCollision:
            return startPos + dir * self.__lookLength
        return collisionPoint


class ShotPointCalculatorPlanar(object):
    MIN_DIST = 50
    TERRAIN_MIN_ANGLE = math.pi / 6
    aimPlane = property(lambda self: self.__aimPlane)

    def __init__(self):
        self.__vehicleMat = BigWorld.player().getOwnVehicleMatrix()
        self.__vehicleDesc = BigWorld.player().vehicleTypeDescriptor
        self.__aimPlane = _AimPlane()
        self.__getTurretMat = functools.partial(AimingSystems.getTurretJointMat, self.__vehicleDesc, self.__vehicleMat)

    def update(self, scanStart, scanDir):
        point, isPointConvenient = self.__testMouseTargetPoint(scanStart, scanDir)
        if isPointConvenient:
            self.__aimPlane.init(scanStart, point)

    def focusAtPos(self, scanStart, scanDir, yawPitch = None):
        scanPos, isPointConvenient = self.__testMouseTargetPoint(scanStart, scanDir)
        if not isPointConvenient:
            if yawPitch is not None:
                turretYaw, gunPitch = yawPitch
                gunMat = AimingSystems.getGunJointMat(self.__vehicleDesc, self.__getTurretMat(turretYaw), gunPitch)
                planePos = self.__aimPlane.intersectRay(gunMat.translation, gunMat.applyVector(Vector3(0, 0, 1)), False, False)
            else:
                planePos = self.__aimPlane.intersectRay(scanStart, scanDir, False)
            if scanStart.distSqrTo(planePos) < scanStart.distSqrTo(scanPos):
                return scanPos
            return planePos
        else:
            self.__aimPlane.init(scanStart, scanPos)
            return scanPos

    def getDesiredShotPoint(self, scanStart, scanDir):
        scanPos, isPointConvenient = self.__testMouseTargetPoint(scanStart, scanDir)
        if isPointConvenient:
            return scanPos
        planePos = self.__aimPlane.intersectRay(scanStart, scanDir)
        if scanStart.distSqrTo(planePos) < scanStart.distSqrTo(scanPos):
            return scanPos
        turretYaw, gunPitch = AimingSystems.getTurretYawGunPitch(self.__vehicleDesc, self.__vehicleMat, planePos, True)
        gunMat = AimingSystems.getGunJointMat(self.__vehicleDesc, self.__getTurretMat(turretYaw), gunPitch)
        aimDir = gunMat.applyVector(Vector3(0.0, 0.0, 1.0))
        return AimingSystems.getDesiredShotPoint(gunMat.translation, aimDir)

    def __calculateClosestPoint(self, start, dir):
        dir.normalise()
        end = start + dir.scale(10000.0)
        testResTerrain = BigWorld.wg_collideSegment(BigWorld.player().spaceID, start, end, 128, lambda matKind, collFlags, itemId, chunkId: collFlags & 8)
        terrainSuitsForCheck = testResTerrain and testResTerrain[1].dot(Math.Vector3(0.0, 1.0, 0.0)) <= math.cos(ShotPointCalculatorPlanar.TERRAIN_MIN_ANGLE)
        testResNonTerrain = BigWorld.wg_collideSegment(BigWorld.player().spaceID, start, end, 136)
        testResDynamic = collideDynamic(start, end, (BigWorld.player().playerVehicleID,), False)
        closestPoint = None
        closestDist = 1000000
        isPointConvenient = True
        if testResTerrain:
            closestPoint = testResTerrain[0]
            closestDist = (testResTerrain[0] - start).length
        if terrainSuitsForCheck:
            isPointConvenient = closestDist >= ShotPointCalculatorPlanar.MIN_DIST
        if testResNonTerrain is not None:
            dist = (testResNonTerrain[0] - start).length
            if dist < closestDist:
                closestPoint = testResNonTerrain[0]
                closestDist = dist
                isPointConvenient = closestDist >= ShotPointCalculatorPlanar.MIN_DIST
        if closestPoint is None and testResDynamic is None:
            return (AimingSystems.shootInSkyPoint(start, dir), True)
        else:
            if testResDynamic is not None:
                dynDist = testResDynamic[0]
                if dynDist <= closestDist:
                    dir = end - start
                    dir.normalise()
                    closestPoint = start + dir * dynDist
                    isPointConvenient = True
            return (closestPoint, isPointConvenient)

    def __testMouseTargetPoint(self, start, dir):
        closestPoint, isPointConvenient = self.__calculateClosestPoint(start, dir)
        turretYaw, gunPitch = AimingSystems.getTurretYawGunPitch(self.__vehicleDesc, self.__vehicleMat, closestPoint, True)
        if not isPointConvenient:
            minPitch, maxPitch = gun_rotation_shared.calcPitchLimitsFromDesc(turretYaw, self.__vehicleDesc.gun['pitchLimits'])
            pitchInBorders = gunPitch <= maxPitch + 0.001
            isPointConvenient = not pitchInBorders
        if isPointConvenient:
            isPointConvenient = not self.__isTurretTurnRequired(dir, turretYaw, closestPoint)
        return (closestPoint, isPointConvenient)

    def __isTurretTurnRequired(self, viewDir, turretYawOnPoint, targetPoint):
        turretMat = self.__getTurretMat(turretYawOnPoint)
        turretPos = turretMat.translation
        gunPos = AimingSystems.getGunJointMat(self.__vehicleDesc, turretMat, 0.0).translation
        dirFromTurretPos = targetPoint - turretPos
        dirFromSniperPos = targetPoint - gunPos
        viewDir = Math.Vector3(viewDir)
        viewDir.y = 0.0
        viewDir.normalise()
        dirFromSniperPos.y = 0.0
        dirFromTurretPos.y = 0.0
        return viewDir.dot(dirFromSniperPos) < 0.0 or viewDir.dot(dirFromTurretPos) < 0.0
