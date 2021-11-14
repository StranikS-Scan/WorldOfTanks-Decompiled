# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ProjectileMover.py
import BigWorld
import Math
import constants
import TriggersManager
from TriggersManager import TRIGGER_TYPE
import FlockManager
from vehicle_systems.tankStructure import TankPartNames, ColliderTypes
from helpers import gEffectsDisabled
from helpers.trajectory_drawer import TrajectoryDrawer

def ownVehicleGunShotPositionGetter():
    ownVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID, None)
    if not ownVehicle:
        return Math.Vector3(0.0, 0.0, 0.0)
    else:
        return Math.Vector3(0.0, 0.0, 0.0) if not ownVehicle.typeDescriptor else ownVehicle.typeDescriptor.activeGunShotPosition


class ProjectileMover(object):
    __START_POINT_MAX_DIFF = 20
    __PROJECTILE_HIDING_TIME = 0.05
    __PROJECTILE_TIME_AFTER_DEATH = 2.0
    __AUTO_SCALE_DISTANCE = 180.0

    def __init__(self):
        self.__projectiles = dict()
        self.salvo = BigWorld.PySalvo(1000, 0, -100)
        self.__ballistics = BigWorld.PyBallisticsSimulator(lambda start, end: BigWorld.player().arena.collideWithSpaceBB(start, end)[1], self.__killProjectile, self.__deleteProjectile)
        if self.__ballistics is not None:
            self.__ballistics.setFixedBallisticsParams(self.__PROJECTILE_HIDING_TIME, self.__PROJECTILE_TIME_AFTER_DEATH, self.__AUTO_SCALE_DISTANCE, constants.SERVER_TICK_LENGTH)
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged += self.__onCameraChanged
        self.__debugDrawer = None
        return

    def destroy(self):
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        self.__ballistics = None
        if self.__debugDrawer is not None:
            self.__debugDrawer.destroy()
        shotIDs = self.__projectiles.keys()
        for shotID in shotIDs:
            self.__delProjectile(shotID)

        return

    def add(self, shotID, effectsDescr, gravity, refStartPoint, refVelocity, startPoint, maxDistance, attackerID=0, tracerCameraPos=Math.Vector3(0, 0, 0)):
        import BattleReplay
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            if startPoint.distTo(refStartPoint) > ProjectileMover.__START_POINT_MAX_DIFF:
                startPoint = refStartPoint
            artID = effectsDescr.get('artilleryID')
            if artID is not None:
                self.salvo.addProjectile(artID, gravity, refStartPoint, refVelocity)
                return
            isOwnShoot = attackerID == BigWorld.player().playerVehicleID
            projectileMotor, collisionTime, _ = self.__ballistics.addProjectile(shotID, gravity, refStartPoint, refVelocity, startPoint, maxDistance, isOwnShoot, attackerID, ownVehicleGunShotPositionGetter(), tracerCameraPos)
            if self.__debugDrawer is not None:
                self.__debugDrawer.addProjectile(shotID, attackerID, refStartPoint, refVelocity, Math.Vector3(0.0, -gravity, 0.0), maxDistance, isOwnShoot)
            if projectileMotor is None:
                return
            projModelName, projModelOwnShotName, projEffects = effectsDescr['projectile']
            model = BigWorld.Model(projModelOwnShotName if isOwnShoot else projModelName)
            proj = {'model': model,
             'motor': projectileMotor,
             'effectsDescr': effectsDescr,
             'showExplosion': False,
             'fireMissedTrigger': isOwnShoot,
             'autoScaleProjectile': isOwnShoot,
             'attackerID': attackerID,
             'effectsData': {}}
            if not gEffectsDisabled():
                BigWorld.player().addModel(model)
                model.addMotor(projectileMotor)
                model.visible = False
                model.visibleAttachments = True
                projEffects.attachTo(proj['model'], proj['effectsData'], 'flying', isPlayerVehicle=isOwnShoot, isArtillery=False, attackerID=attackerID, collisionTime=collisionTime)
            self.__projectiles[shotID] = proj
            FlockManager.getManager().onProjectile(startPoint)
            return

    def hide(self, shotID, endPoint):
        proj = self.__projectiles.pop(shotID, None)
        if proj is None:
            return
        else:
            if -shotID in self.__projectiles:
                self.__delProjectile(-shotID)
            self.__projectiles[-shotID] = proj
            proj['fireMissedTrigger'] = False
            proj['showExplosion'] = False
            self.__notifyProjectileHit(endPoint, proj)
            self.__ballistics.hideProjectile(shotID, endPoint)
            return

    def explode(self, shotID, effectsDescr, effectMaterial, endPoint, velocityDir):
        if effectsDescr.has_key('artilleryID'):
            return
        else:
            proj = self.__projectiles.get(shotID)
            if proj is None:
                __proj = {}
                __proj['effectsDescr'] = effectsDescr
                __proj['effectMaterial'] = effectMaterial
                __proj['attackerID'] = 0
                self.__addExplosionEffect(endPoint, __proj, velocityDir)
                return
            if proj['fireMissedTrigger']:
                proj['fireMissedTrigger'] = False
                TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_MISSED)
            params = self.__ballistics.explodeProjectile(shotID, endPoint)
            if params is not None:
                if not proj.has_key('effectMaterial'):
                    proj['effectMaterial'] = effectMaterial
                self.__addExplosionEffect(params[0], proj, params[1])
            else:
                proj['showExplosion'] = True
                proj['effectMaterial'] = effectMaterial
            self.__notifyProjectileHit(endPoint, proj)
            return

    def hold(self, shotID):
        self.__ballistics.holdProjectile(shotID)

    def setSpaceID(self, spaceID):
        if self.__ballistics:
            self.__ballistics.setVariableBallisticsParams(spaceID)
        self.__debugDrawer = TrajectoryDrawer(spaceID)

    def __notifyProjectileHit(self, hitPosition, proj):
        caliber = proj['effectsDescr']['caliber']
        isOwnShot = proj['autoScaleProjectile']
        BigWorld.player().inputHandler.onProjectileHit(hitPosition, caliber, isOwnShot)
        FlockManager.getManager().onProjectile(hitPosition)

    def __addExplosionEffect(self, position, proj, velocityDir):
        effectTypeStr = proj.get('effectMaterial', '') + 'Hit'
        p0 = Math.Vector3(position.x, 1000, position.z)
        p1 = Math.Vector3(position.x, -1000, position.z)
        waterDist = BigWorld.wg_collideWater(p0, p1, False)
        if waterDist > 0:
            waterY = p0.y - waterDist
            testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, p0, p1, 128)
            staticY = testRes.closestPoint.y if testRes is not None else waterY
            if staticY < waterY and position.y - waterY <= 0.1:
                shallowWaterDepth, rippleDiameter = proj['effectsDescr']['waterParams']
                if waterY - staticY < shallowWaterDepth:
                    effectTypeStr = 'shallowWaterHit'
                else:
                    effectTypeStr = 'deepWaterHit'
                position = Math.Vector3(position.x, waterY, position.z)
                self.__addWaterRipples(position, rippleDiameter, 5)
        keyPoints, effects, _ = proj['effectsDescr'][effectTypeStr]
        BigWorld.player().terrainEffects.addNew(position, effects, keyPoints, None, dir=velocityDir, start=position + velocityDir.scale(-1.0), end=position + velocityDir.scale(1.0), attackerID=proj['attackerID'])
        return

    def __killProjectile(self, shotID, position, impactVelDir, deathType, explode):
        proj = self.__projectiles.get(shotID)
        if proj is None:
            return
        else:
            effectsDescr = proj['effectsDescr']
            projEffects = effectsDescr['projectile'][2]
            projEffects.detachFrom(proj['effectsData'], 'stopFlying', deathType)
            if proj['showExplosion'] and explode:
                self.__addExplosionEffect(position, proj, impactVelDir)
            return

    def __deleteProjectile(self, shotID):
        proj = self.__projectiles.get(shotID)
        if proj is None:
            return
        else:
            self.__delProjectile(shotID)
            if proj['fireMissedTrigger']:
                TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_MISSED)
            return

    def __addWaterRipples(self, position, rippleDiameter, ripplesLeft):
        BigWorld.wg_addWaterRipples(position, rippleDiameter)
        if ripplesLeft > 0:
            BigWorld.callback(0, lambda : self.__addWaterRipples(position, rippleDiameter, ripplesLeft - 1))

    def __delProjectile(self, shotID):
        proj = self.__projectiles.pop(shotID)
        if self.__debugDrawer is not None:
            self.__debugDrawer.removeProjectile(shotID if shotID > 0 else -shotID)
        if proj is None:
            return
        else:
            projEffects = proj['effectsDescr']['projectile'][2]
            projEffects.detachAllFrom(proj['effectsData'])
            proj['model'].delMotor(proj['motor'])
            BigWorld.player().delModel(proj['model'])
            return

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        self.__ballistics.setBallisticsAutoScale(cameraName != 'sniper')


class EntityCollisionData(object):
    __slots__ = ('hitAngleCos', 'armor', '__isVehicle', 'entity')

    def __init__(self, entityID, partIndex, matKind, isVehicle=True):
        self.hitAngleCos = 0.0
        self.__isVehicle = isVehicle
        if isVehicle:
            self.entity = BigWorld.entity(entityID)
            if self.entity is None:
                self.__isVehicle = False
            else:
                matInfo = self.entity.getMatinfo(partIndex, matKind)
                self.armor = matInfo.armor if matInfo is not None and matInfo.armor is not None else 0.0
        else:
            self.entity = None
        return

    def isVehicle(self):
        return self.__isVehicle


def collideDynamicAndStatic(startPoint, endPoint, exceptIDs, collisionFlags=128, skipGun=False):
    ignoreDynamicID = 0
    if exceptIDs:
        ignoreDynamicID = exceptIDs[0]
    testRes = BigWorld.wg_collideDynamicStatic(BigWorld.player().spaceID, startPoint, endPoint, collisionFlags, ignoreDynamicID, -1 if not skipGun else TankPartNames.getIdx(TankPartNames.GUN))
    if testRes is not None:
        if testRes[1]:
            return (testRes[0], EntityCollisionData(testRes[2], testRes[3], testRes[4], True))
        return (testRes[0], None)
    else:
        return


def collideDynamic(startPoint, endPoint, exceptIDs, skipGun=False):
    ignoreID = 0
    if exceptIDs:
        ignoreID = exceptIDs[0]
    res = BigWorld.wg_collideDynamic(BigWorld.player().spaceID, startPoint, endPoint, ignoreID, -1 if skipGun else TankPartNames.getIdx(TankPartNames.GUN))
    if res is not None:
        isVehicle = res[2] == ColliderTypes.VEHICLE_COLLIDER
        res = (res[0], EntityCollisionData(res[3], res[4], res[5], isVehicle))
    return res


def collideVehiclesAndStaticScene(startPoint, endPoint, vehicles, collisionFlags=128, skipGun=False):
    testResStatic = BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, collisionFlags)
    testResDynamic = collideDynamic(startPoint, endPoint if testResStatic is None else testResStatic.closestPoint, vehicles, skipGun)
    if testResStatic is None and testResDynamic is None:
        return
    else:
        distDynamic = 1000000.0
        if testResDynamic is not None:
            distDynamic = testResDynamic[0]
        distStatic = 1000000.0
        if testResStatic is not None:
            distStatic = (testResStatic.closestPoint - startPoint).length
        return (startPoint + (endPoint - startPoint) * distDynamic, testResDynamic[1]) if distDynamic <= distStatic else (testResStatic.closestPoint, None)
