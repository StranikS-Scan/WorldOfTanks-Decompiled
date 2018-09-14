# Embedded file name: scripts/client/ProjectileMover.py
from collections import namedtuple
import itertools
import BigWorld
from DetachedTurret import DetachedTurret
import Math
import math
from ModelHitTester import segmentMayHitVehicle
import items
import constants
import ClientArena
import TriggersManager
import AreaDestructibles
from TriggersManager import TRIGGER_TYPE
from ClientArena import Plane
from debug_utils import *
from projectile_trajectory import computeProjectileTrajectory
from constants import DESTRUCTIBLE_MATKIND

class ProjectileMover(object):
    __PROJECTILE_HIDING_TIME = 0.05
    __PROJECTILE_TIME_AFTER_DEATH = 2.0
    __MOVEMENT_CALLBACK_TIMEOUT = 0.001
    __AUTO_SCALE_DISTANCE = 180.0

    def __init__(self):
        self.__projectiles = dict()
        self.__movementCallbackId = None
        return

    def destroy(self):
        if self.__movementCallbackId is not None:
            BigWorld.cancelCallback(self.__movementCallbackId)
            self.__movementCallbackId = None
        for shotID, proj in self.__projectiles.items():
            projEffects = proj['effectsDescr']['projectile'][2]
            projEffects.detachAllFrom(proj['effectsData'])
            BigWorld.player().delModel(proj['model'])
            del self.__projectiles[shotID]

        return

    def add(self, shotID, effectsDescr, gravity, refStartPoint, refVelocity, startPoint, maxDistance, isOwnShoot = False, tracerCameraPos = Math.Vector3(0, 0, 0)):
        import BattleReplay
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            projectiles = self.__projectiles
            if shotID in projectiles:
                return
            if -shotID in projectiles:
                projectiles[-shotID]['startTime'] = BigWorld.time() - 1.0
            projModelName, projModelOwnShotName, projEffects = effectsDescr['projectile']
            gravity = Math.Vector3(0.0, -gravity, 0.0)
            trajectory = self.__calcTrajectory(refStartPoint, refVelocity, gravity, maxDistance, isOwnShoot, tracerCameraPos)
            trajectoryEnd = trajectory[len(trajectory) - 1]
            if (trajectoryEnd[0] - startPoint).length == 0.0 or trajectoryEnd[1] == 0.0:
                LOG_CODEPOINT_WARNING()
                return
            model = BigWorld.Model(projModelOwnShotName if isOwnShoot else projModelName)
            proj = {'model': model,
             'startTime': BigWorld.time(),
             'effectsDescr': effectsDescr,
             'refStartPoint': refStartPoint,
             'refVelocity': refVelocity,
             'startPoint': startPoint,
             'stopPlane': None,
             'gravity': gravity,
             'showExplosion': False,
             'impactVelDir': None,
             'deathTime': None,
             'fireMissedTrigger': isOwnShoot,
             'autoScaleProjectile': isOwnShoot,
             'collisions': trajectory,
             'velocity': self.__calcStartVelocity(trajectoryEnd[0], startPoint, trajectoryEnd[1], gravity),
             'effectsData': {}}
            BigWorld.player().addModel(model)
            model.position = startPoint
            model.visible = False
            model.visibleAttachments = True
            projEffects.attachTo(proj['model'], proj['effectsData'], 'flying')
            if self.__movementCallbackId is None:
                self.__movementCallbackId = BigWorld.callback(self.__MOVEMENT_CALLBACK_TIMEOUT, self.__movementCallback)
            projectiles[shotID] = proj
            return

    def hide(self, shotID, endPoint):
        proj = self.__projectiles.pop(shotID, None)
        if proj is None:
            return
        else:
            self.__projectiles[-shotID] = proj
            proj['fireMissedTrigger'] = False
            proj['showExplosion'] = False
            proj['stopPlane'] = self.__getStopPlane(endPoint, proj['refStartPoint'], proj['refVelocity'], proj['gravity'])
            self.__notifyProjectileHit(endPoint, proj)
            return

    def explode(self, shotID, effectsDescr, effectMaterial, endPoint, velocityDir):
        proj = self.__projectiles.get(shotID)
        if proj is None:
            self.__addExplosionEffect(endPoint, effectsDescr, effectMaterial, velocityDir)
            return
        else:
            if proj['fireMissedTrigger']:
                proj['fireMissedTrigger'] = False
                TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_MISSED)
            if proj['deathTime'] is not None:
                pos = proj['model'].position
                self.__addExplosionEffect(pos, effectsDescr, effectMaterial, proj['impactVelDir'])
            else:
                proj['showExplosion'] = True
                proj['effectMaterial'] = effectMaterial
                proj['stopPlane'] = self.__getStopPlane(endPoint, proj['refStartPoint'], proj['refVelocity'], proj['gravity'])
                nearestDist = None
                nearestCollision = None
                for p, t, d in proj['collisions']:
                    dist = (Math.Vector3(p) - Math.Vector3(endPoint)).lengthSquared
                    if dist < nearestDist or nearestDist is None:
                        nearestCollision = (p, t, d)
                        nearestDist = dist

                proj['collisions'] = [nearestCollision]
            self.__notifyProjectileHit(endPoint, proj)
            return

    def hold(self, shotID):
        proj = self.__projectiles.get(shotID)
        proj['holdTime'] = self.__PROJECTILE_HIDING_TIME

    def __notifyProjectileHit(self, hitPosition, proj):
        caliber = proj['effectsDescr']['caliber']
        isOwnShot = proj['autoScaleProjectile']
        BigWorld.player().inputHandler.onProjectileHit(hitPosition, caliber, isOwnShot)

    def __addExplosionEffect(self, position, effectsDescr, effectMaterial, velocityDir):
        effectTypeStr = effectMaterial + 'Hit'
        p0 = Math.Vector3(position.x, 1000, position.z)
        p1 = Math.Vector3(position.x, -1000, position.z)
        waterDist = BigWorld.wg_collideWater(p0, p1)
        if waterDist > 0:
            waterY = p0.y - waterDist
            testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, p0, p1, 128)
            staticY = testRes[0].y if testRes is not None else waterY
            if staticY < waterY and position.y - waterY <= 0.1:
                shallowWaterDepth, rippleDiameter = effectsDescr['waterParams']
                if waterY - staticY < shallowWaterDepth:
                    effectTypeStr = 'shallowWaterHit'
                else:
                    effectTypeStr = 'deepWaterHit'
                position = Math.Vector3(position.x, waterY, position.z)
                self.__addWaterRipples(position, rippleDiameter, 5)
        keyPoints, effects, _ = effectsDescr[effectTypeStr]
        BigWorld.player().terrainEffects.addNew(position, effects, keyPoints, None, dir=velocityDir, start=position + velocityDir.scale(-1.0), end=position + velocityDir.scale(1.0))
        return

    def __calcTrajectory(self, r0, v0, gravity, maxDistance, isOwnShoot, tracerCameraPos):
        ret = []
        ownVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        prevPos = r0
        prevVelocity = v0
        dt = 0.0
        destrID = []
        while True:
            dt += constants.SERVER_TICK_LENGTH
            checkPoints = computeProjectileTrajectory(prevPos, prevVelocity, gravity, constants.SERVER_TICK_LENGTH, constants.SHELL_TRAJECTORY_EPSILON_CLIENT)
            prevCheckPoint = prevPos
            prevDist0 = r0.distTo(prevCheckPoint)
            for curCheckPoint in checkPoints:
                curDist0 = r0.distTo(curCheckPoint)
                if curDist0 > maxDistance:
                    curCheckPoint = prevCheckPoint + (curCheckPoint - prevCheckPoint) * ((maxDistance - prevDist0) / (curDist0 - prevDist0))
                    ret.append((curCheckPoint, (curCheckPoint[0] - r0[0]) / v0[0], None))
                    return ret
                hitPoint = BigWorld.player().arena.collideWithSpaceBB(prevCheckPoint, curCheckPoint)
                if hitPoint is not None:
                    ret.append((hitPoint, (hitPoint[0] - r0[0]) / v0[0], None))
                    return ret
                testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, prevCheckPoint, curCheckPoint, 128, lambda matKind, collFlags, itemID, chunkID: (False if itemID in destrID else True))
                if testRes is not None:
                    hitPoint = testRes[0]
                    distStatic = (hitPoint - prevCheckPoint).length
                    destructibleDesc = None
                    matKind = testRes[2]
                    if matKind in xrange(DESTRUCTIBLE_MATKIND.NORMAL_MIN, DESTRUCTIBLE_MATKIND.NORMAL_MAX + 1):
                        destructibleDesc = (testRes[5], testRes[4], matKind)
                        destrID.append(testRes[4])
                    distWater = -1.0
                    useTracerCameraPos = False
                    if isOwnShoot:
                        rayDir = hitPoint - tracerCameraPos
                        rayDir.normalise()
                        if ownVehicle is not None:
                            gunPos = ownVehicle.appearance.modelsDesc['gun']['model'].position
                            if tracerCameraPos.y > gunPos.y:
                                if (hitPoint - gunPos).length > 30.0:
                                    useTracerCameraPos = True
                        if not useTracerCameraPos:
                            distWater = BigWorld.wg_collideWater(prevCheckPoint, curCheckPoint)
                        else:
                            rayEnd = hitPoint + rayDir * 1.5
                            testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, tracerCameraPos, rayEnd, 128)
                            if testRes is not None:
                                distStatic = (testRes[0] - tracerCameraPos).length
                                distWater = BigWorld.wg_collideWater(tracerCameraPos, rayEnd)
                    else:
                        distWater = BigWorld.wg_collideWater(prevCheckPoint, curCheckPoint)
                    if distWater < 0 or distWater > distStatic:
                        ret.append((hitPoint, self.__getCollisionTime(r0, hitPoint, v0), destructibleDesc))
                        if destructibleDesc is None:
                            return ret
                        prevCheckPoint = hitPoint
                        continue
                    if distWater >= 0:
                        srcPoint = tracerCameraPos if useTracerCameraPos else prevCheckPoint
                        hitDirection = hitPoint - srcPoint
                        hitDirection.normalise()
                        hitPoint = srcPoint + hitDirection * distWater
                        ret.append((hitPoint, self.__getCollisionTime(r0, hitPoint, v0), None))
                        return ret
                prevCheckPoint = curCheckPoint
                prevDist0 = curDist0

            prevPos = r0 + v0.scale(dt) + gravity.scale(dt * dt * 0.5)
            prevVelocity = v0 + gravity.scale(dt)

        return

    def __getCollisionTime(self, startPoint, hitPoint, velocity):
        if velocity[0] != 0:
            return (hitPoint[0] - startPoint[0]) / velocity[0]
        elif velocity[2] != 0:
            return (hitPoint[2] - startPoint[2]) / velocity[2]
        else:
            return 1000000.0

    def __getStopPlane(self, point, r0, v0, gravity):
        t = (point[0] - r0[0]) / v0[0]
        v = v0 + gravity.scale(t)
        v.normalise()
        d = v.dot(point)
        return Plane(v, d)

    def __moveByTrajectory(self, proj, time):
        model = proj['model']
        gravity = proj['gravity']
        r0 = proj['startPoint']
        v0 = proj['velocity']
        if 'holdTime' in proj:
            time -= proj['holdTime']
        dt = time - proj['startTime']
        if dt < 0:
            return False
        else:
            if not model.visible and dt >= self.__PROJECTILE_HIDING_TIME:
                model.visible = True
            endPoint = None
            endTime = None
            for p, t, destrDesc in proj['collisions']:
                if dt < t:
                    break
                if destrDesc is not None:
                    areaDestr = AreaDestructibles.g_destructiblesManager.getController(destrDesc[0])
                    if areaDestr is not None:
                        if areaDestr.isDestructibleBroken(destrDesc[1], destrDesc[2]):
                            continue
                endPoint = p
                endTime = t
                break

            if endPoint is not None:
                stopPlane = proj['stopPlane']
                if stopPlane is not None and stopPlane.testPoint(endPoint):
                    testRes = stopPlane.intersectSegment(model.position, endPoint)
                    if testRes is not None:
                        endPoint = testRes
                dir = endPoint - model.position
                dir.normalise()
                proj['impactVelDir'] = dir
                model.visible = False
                self.__setModelLocation(model, endPoint - dir.scale(0.01), v0, proj['autoScaleProjectile'])
                return True
            r = r0 + v0.scale(dt) + gravity.scale(dt * dt * 0.5)
            v = v0 + gravity.scale(dt)
            stopPlane = proj['stopPlane']
            if stopPlane is not None and stopPlane.testPoint(r):
                testRes = stopPlane.intersectSegment(model.position, r)
                if testRes is None:
                    testRes = stopPlane.intersectSegment(proj['refStartPoint'], r0)
                    if testRes is None:
                        testRes = model.position
                dir = testRes - model.position
                dir.normalise()
                proj['impactVelDir'] = dir
                model.visible = False
                self.__setModelLocation(model, testRes - dir.scale(0.01), v, proj['autoScaleProjectile'])
                return True
            self.__setModelLocation(model, r, v, proj['autoScaleProjectile'])
            return False

    def __setModelLocation(self, model, pos, velocity, autoScaleProjectile):
        model.straighten()
        model.rotate(velocity.pitch, Math.Vector3(1.0, 0.0, 0.0))
        model.rotate(velocity.yaw, Math.Vector3(0.0, 1.0, 0.0))
        model.vel = velocity
        model.position = pos
        if autoScaleProjectile:
            model.scale = self.__calcModelAutoScale(pos)

    def __calcModelAutoScale(self, modelPos):
        camera = BigWorld.camera()
        distance = (camera.position - modelPos).length
        inputHandler = BigWorld.player().inputHandler
        from AvatarInputHandler.control_modes import SniperControlMode
        if distance <= ProjectileMover.__AUTO_SCALE_DISTANCE or not isinstance(inputHandler.ctrl, SniperControlMode):
            return Math.Vector3(1, 1, 1)
        return Math.Vector3(1, 1, 1) * distance / ProjectileMover.__AUTO_SCALE_DISTANCE

    def __movementCallback(self):
        self.__movementCallbackId = None
        time = BigWorld.time()
        for shotID, proj in self.__projectiles.items():
            player = BigWorld.player()
            effectsDescr = proj['effectsDescr']
            deathTime = proj['deathTime']
            if deathTime is None and self.__moveByTrajectory(proj, time):
                proj['deathTime'] = time
                projEffects = effectsDescr['projectile'][2]
                projEffects.detachFrom(proj['effectsData'], 'stopFlying')
                if proj['showExplosion']:
                    pos = proj['model'].position
                    dir = proj['impactVelDir']
                    self.__addExplosionEffect(pos, effectsDescr, proj['effectMaterial'], dir)
            if deathTime is not None and time - deathTime >= self.__PROJECTILE_TIME_AFTER_DEATH:
                projEffects = effectsDescr['projectile'][2]
                projEffects.detachAllFrom(proj['effectsData'])
                player.delModel(proj['model'])
                del self.__projectiles[shotID]
                if proj['fireMissedTrigger']:
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_MISSED)

        self.__movementCallbackId = BigWorld.callback(self.__MOVEMENT_CALLBACK_TIMEOUT, self.__movementCallback)
        return

    def __calcStartVelocity(self, r, r0, dt, gravity):
        v0 = (r - r0).scale(1.0 / dt) - gravity.scale(dt * 0.5)
        return v0

    def __addWaterRipples(self, position, rippleDiameter, ripplesLeft):
        BigWorld.wg_addWaterRipples(position, rippleDiameter)
        if ripplesLeft > 0:
            BigWorld.callback(0, lambda : self.__addWaterRipples(position, rippleDiameter, ripplesLeft - 1))


class EntityCollisionData(namedtuple('collisionData', ('entity', 'hitAngleCos', 'armor'))):

    def isVehicle(self):
        return self.entity.__class__.__name__ == 'Vehicle'


def collideEntities(startPoint, endPoint, entities, skipGun = False):
    res = None
    dir = endPoint - startPoint
    endDist = dir.length
    dir.normalise()
    for entity in entities:
        collisionResult = entity.collideSegment(startPoint, endPoint, skipGun)
        if collisionResult is None:
            continue
        dist = collisionResult[0]
        if dist < endDist:
            endPoint = startPoint + dir * dist
            endDist = dist
            res = (dist, EntityCollisionData(entity, collisionResult.hitAngleCos, collisionResult.armor))

    return res


def collideVehiclesAndStaticScene(startPoint, endPoint, vehicles, collisionFlags = 128, skipGun = False):
    testResStatic = BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, collisionFlags)
    testResDynamic = collideEntities(startPoint, endPoint if testResStatic is None else testResStatic[0], vehicles, skipGun)
    if testResStatic is None and testResDynamic is None:
        return
    else:
        distDynamic = 1000000.0
        if testResDynamic is not None:
            distDynamic = testResDynamic[0]
        distStatic = 1000000.0
        if testResStatic is not None:
            distStatic = (testResStatic[0] - startPoint).length
        if distDynamic <= distStatic:
            dir = endPoint - startPoint
            dir.normalise()
            return (startPoint + distDynamic * dir, testResDynamic[1])
        return (testResStatic[0], None)
        return


def segmentMayHitEntity(entity, startPoint, endPoint):
    method = getattr(entity.filter, 'segmentMayHitEntity', lambda : True)
    return method(startPoint, endPoint)


def getCollidableEntities(exceptIDs, startPoint = None, endPoint = None):
    segmentTest = startPoint is not None and endPoint is not None
    vehicles = []
    for vehicleID in BigWorld.player().arena.vehicles.iterkeys():
        if vehicleID in exceptIDs:
            continue
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is None or not vehicle.isStarted:
            continue
        if segmentTest and not segmentMayHitEntity(vehicle, startPoint, endPoint):
            continue
        vehicles.append(vehicle)

    for turret in DetachedTurret.allTurrets:
        if segmentTest and not segmentMayHitEntity(turret, startPoint, endPoint):
            continue
        vehicles.append(turret)

    return vehicles


def collideDynamic(startPoint, endPoint, exceptIDs, skipGun = False):
    return collideEntities(startPoint, endPoint, getCollidableEntities(exceptIDs, startPoint, endPoint), skipGun)


def collideDynamicAndStatic(startPoint, endPoint, exceptIDs, collisionFlags = 128, skipGun = False):
    return collideVehiclesAndStaticScene(startPoint, endPoint, getCollidableEntities(exceptIDs, startPoint, endPoint), collisionFlags, skipGun)
