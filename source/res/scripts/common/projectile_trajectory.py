# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/projectile_trajectory.py
import BigWorld
import Math

def computeProjectileTrajectory(beginPoint, velocity, gravity, time, epsilon):
    checkPoints = []
    endPoint = beginPoint + velocity.scale(time) + gravity.scale(time * time * 0.5)
    stack = [(velocity, beginPoint, endPoint)]
    while len(stack) > 0:
        lastIdx = len(stack) - 1
        v1, p1, p2 = stack[lastIdx]
        del stack[lastIdx]
        delta = p2 - p1
        xzNormal = Math.Vector3(-delta.z, 0.0, delta.x)
        normal = xzNormal * delta
        if abs(normal.y) < epsilon:
            checkPoints.append(p2)
            continue
        normal.normalise()
        extremeTime = normal.dot(v1) / (-gravity.y * normal.y)
        extremePoint = v1.scale(extremeTime) + gravity.scale(extremeTime * extremeTime * 0.5)
        dist = abs(normal.dot(extremePoint))
        if dist > epsilon:
            extremeVelocity = v1 + gravity.scale(extremeTime)
            stack.append((extremeVelocity, p1 + extremePoint, p2))
            stack.append((v1, p1, p1 + extremePoint))
        checkPoints.append(p2)

    return checkPoints


try:
    computeProjectileTrajectory = BigWorld.wg_computeProjectileTrajectory
except AttributeError:
    pass

def getShotAngles(vehTypeDescr, vehMatrix, curShotAngles, point, adjust=True, overrideGunPosition=None, overrideShotIdx=None):
    turretOffs = vehTypeDescr.hull.turretPositions[0] + vehTypeDescr.chassis.hullPosition
    gunOffs = vehTypeDescr.activeGunShotPosition if overrideGunPosition is None else overrideGunPosition
    shot = vehTypeDescr.getShot(overrideShotIdx)
    speed = shot.speed
    gravity = shot.gravity
    return BigWorld.wg_getShotAngles(turretOffs, gunOffs, vehMatrix, speed, gravity, curShotAngles[0], curShotAngles[1], point, adjust)
