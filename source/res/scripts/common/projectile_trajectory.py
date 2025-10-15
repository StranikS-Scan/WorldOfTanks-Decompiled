# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/projectile_trajectory.py
import BigWorld
import Math

def computeProjectileTrajectory(beginPoint, velocity, acceleration, time, epsilon):
    checkPoints = []
    endPoint = beginPoint + velocity.scale(time) + acceleration.scale(time * time * 0.5)
    accelerationDirection = Math.Vector3(acceleration)
    accelerationDirection.normalise()
    planeNormal = velocity * accelerationDirection
    planeNormal.normalise()
    stack = [(velocity, beginPoint, endPoint)]
    while len(stack) > 0:
        lastIdx = len(stack) - 1
        v1, p1, p2 = stack[lastIdx]
        del stack[lastIdx]
        normal = (p2 - p1) * planeNormal
        projectedNorm = accelerationDirection.dot(normal)
        if projectedNorm * projectedNorm < epsilon:
            checkPoints.append(p2)
            continue
        normal.normalise()
        normalVelocity = normal.dot(v1)
        extremeTime = -normalVelocity / normal.dot(acceleration)
        if normalVelocity * extremeTime * 0.5 > epsilon:
            extremeVelocity = v1 + acceleration.scale(extremeTime)
            extremePoint = (v1 + extremeVelocity) * (extremeTime * 0.5)
            stack.append((extremeVelocity, p1 + extremePoint, p2))
            stack.append((v1, p1, p1 + extremePoint))
        checkPoints.append(p2)

    return checkPoints


try:
    computeProjectileTrajectory = BigWorld.computeProjectileTrajectory
except AttributeError:
    pass

def getShotAngles(vehTypeDescr, vehMatrix, curShotAngles, point, adjust=True, overrideGunPosition=None, overrideShotIdx=None):
    turretOffs = vehTypeDescr.hull.turretPositions[0] + vehTypeDescr.chassis.hullPosition
    gunOffs = vehTypeDescr.activeGunShotPosition if overrideGunPosition is None else overrideGunPosition
    shot = vehTypeDescr.getShot(overrideShotIdx)
    speed = shot.speed
    gravity = shot.gravity
    return BigWorld.getShotAngles(turretOffs, gunOffs, vehMatrix, speed, gravity, curShotAngles[0], curShotAngles[1], point, adjust)
