# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vehicle.py
import weakref
import random
import math
import Math
from AvatarInputHandler import ShakeReason
import SoundGroups
from VehicleEffects import DamageFromShotDecoder
from vehicle_systems.tankStructure import TankPartNames
from debug_utils import *
import constants
from constants import VEHICLE_HIT_EFFECT, VEHICLE_PHYSICS_MODE
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _GUI_EVENT_ID
from helpers.EffectMaterialCalculation import calcSurfaceMaterialNearPoint
from items import vehicles
from vehicle_systems import vehicle_assembler
from gui.LobbyContext import g_lobbyContext
import AreaDestructibles
import DestructiblesCache
import nations
import physics_shared
import ArenaType
import BattleReplay
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from ModelHitTester import segmentMayHitVehicle, SegmentCollisionResult
from gun_rotation_shared import decodeGunAngles
from constants import SPT_MATKIND
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_NAMES, EFFECT_MATERIALS
from CombatEquipmentManager import CombatEquipmentManager
LOW_ENERGY_COLLISION_D = 0.3
HIGH_ENERGY_COLLISION_D = 0.6
_g_waitingVehicle = dict()

class _Vector4Provider(object):
    __slots__ = ('_v',)

    @property
    def value(self):
        return self._v

    def __int__(self):
        self._v = Math.Vector4(0.0, 0.0, 0.0, 0.0)


class _VehicleSpeedProvider(object):
    __slots__ = ('__value',)

    @property
    def value(self):
        return self.__value.value

    def __init__(self):
        self.__value = _Vector4Provider()

    def set(self, val):
        self.__value = val

    def reset(self):
        self.__value = _Vector4Provider()


class Vehicle(BigWorld.Entity):
    hornMode = property(lambda self: self.__hornMode)
    isEnteringWorld = property(lambda self: self.__isEnteringWorld)
    isTurretDetached = property(lambda self: constants.SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health) and self.__turretDetachmentConfirmed)
    isTurretMarkedForDetachment = property(lambda self: constants.SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health))
    isTurretDetachmentConfirmationNeeded = property(lambda self: not self.__turretDetachmentConfirmed)

    @property
    def speedInfo(self):
        return self.__speedInfo

    def getSpeed(self):
        return self.__speedInfo.value[0]

    def __init__(self):
        global _g_waitingVehicle
        self.proxy = weakref.proxy(self)
        self.extras = {}
        self.typeDescriptor = None
        self.appearance = None
        self.isPlayerVehicle = False
        self.isStarted = False
        self.__prereqs = None
        self.__hornSounds = (None,)
        self.__hornMode = ''
        self.__stopHornSoundCallback = None
        self.__isEnteringWorld = False
        self.__turretDetachmentConfirmed = False
        self.__speedInfo = _VehicleSpeedProvider()
        self.assembler = None
        _g_waitingVehicle[self.id] = weakref.ref(self)
        self.respawnCompactDescr = None
        self.__bombArea = None
        return

    def __del__(self):
        if _g_waitingVehicle.has_key(self.id):
            del _g_waitingVehicle[self.id]

    def reload(self):
        wasStarted = self.isStarted
        if self.isStarted:
            self.stopVisual()
        vehicles.reload()
        self.respawn(self.publicInfo.compDescr)

    def prerequisites(self, respawnCompactDescr=None):
        if self.respawnCompactDescr is not None:
            respawnCompactDescr = self.respawnCompactDescr
            self.isCrewActive = True
            self.respawnCompactDescr = None
        if respawnCompactDescr is None and self.typeDescriptor is not None:
            return ()
        else:
            prereqs = []
            if respawnCompactDescr is not None:
                descr = vehicles.VehicleDescr(respawnCompactDescr)
                self.health = descr.maxHealth
            else:
                descr = vehicles.VehicleDescr(compactDescr=_stripVehCompDescrIfRoaming(self.publicInfo.compDescr))
            self.typeDescriptor = descr
            prereqs += descr.prerequisites(self.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED)
            for hitTester in descr.getHitTesters():
                if hitTester.bspModelName is not None and not hitTester.isBspModelLoaded():
                    prereqs.append(hitTester.bspModelName)

            self.assembler = vehicle_assembler.createAssembler(self)
            self.appearance = self.assembler.appearance
            prereqs += self.assembler.prerequisites()
            return prereqs

    @staticmethod
    def respawnVehicle(id, compactDescr):
        vehicleRef = _g_waitingVehicle.get(id, None)
        if vehicleRef is not None:
            vehicle = vehicleRef()
            if vehicle is not None:
                vehicle.respawnCompactDescr = compactDescr
                vehicle.wg_respawn()
        return

    def onEnterWorld(self, prereqs):
        self.__isEnteringWorld = True
        descr = self.typeDescriptor
        descr.keepPrereqs(prereqs, self.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED)
        self.__prereqs = prereqs
        self.__prevDamageStickers = frozenset()
        self.__prevPublicStateModifiers = frozenset()
        self.targetFullBounds = True
        player = BigWorld.player()
        for hitTester in descr.getHitTesters():
            hitTester.loadBspModel()
            player.hitTesters.add(hitTester)

        player.initSpace()
        player.vehicle_onEnterWorld(self)
        if self.typeDescriptor.name.find('uk:GB89_Mark') > -1:
            bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
            if bonusCtrl is not None:
                bonusCtrl.onBombPlanted += self.onBombPlanted
                bonusCtrl.onBombExploded += self.onBombExploded
        self.__isEnteringWorld = False
        return

    def onLeaveWorld(self):
        if self.__bombArea is not None:
            self.__bombArea.destroy()
            self.__bombArea = None
        if self.typeDescriptor.name.find('uk:GB89_Mark') > -1:
            bonusCtrl = g_sessionProvider.dynamic.mark1Bonus
            if bonusCtrl is not None:
                bonusCtrl.onBombPlanted -= self.onBombPlanted
                bonusCtrl.onBombExploded -= self.onBombExploded
        self.__stopExtras()
        BigWorld.player().vehicle_onLeaveWorld(self)
        assert not self.isStarted
        return

    def onBombPlanted(self, timeLeft):
        if self.__bombArea is not None:
            self.__bombArea.destroy()
            self.__bombArea = None
        eq = vehicles.g_cache.commonConfig['extrasDict']['explosive']
        self.__bombArea = CombatEquipmentManager.createEquipmentSelectedArea(self.position, Math.Vector3(1.0, 0.0, 0.0), eq)
        BigWorld.callback(0.02, self.updateZone)
        return

    def onBombExploded(self):
        if self.__bombArea is not None:
            self.__bombArea.destroy()
            self.__bombArea = None
        return

    def updateZone(self):
        if self.__bombArea is not None:
            self.__bombArea.updatePosition(Math.Matrix(self.matrix).translation)
            BigWorld.callback(0.02, self.updateZone)
        return

    def showShooting(self, burstCount, gunIndex, isPredictedShot=False):
        if not self.isStarted:
            return
        if not isPredictedShot and self.isPlayerVehicle and not BigWorld.player().isWaitingForShot:
            if not BattleReplay.g_replayCtrl.isPlaying:
                return
        extra = self.typeDescriptor.extrasDict['shoot']
        gunFireNodeName = 'HP_gunFire'
        if gunIndex > 0:
            extra = self.typeDescriptor.extrasDict['secondGunShoot']
            gunFireNodeName = 'HP_gunFire_02'
        extra.stopFor(self)
        extra.startFor(self, (burstCount, gunFireNodeName))
        if not isPredictedShot and self.isPlayerVehicle:
            BigWorld.player().cancelWaitingForShot()

    def showDamageFromShot(self, attackerID, points, effectsIndex, damageFactor):
        if not self.isStarted:
            return
        else:
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            maxHitEffectCode, decodedPoints = DamageFromShotDecoder.decodeHitPoints(points, self.typeDescriptor)
            hasPiercedHit = DamageFromShotDecoder.hasDamaged(maxHitEffectCode)
            firstHitDir = Math.Vector3(0)
            if decodedPoints:
                firstHitPoint = decodedPoints[0]
                compoundModel = self.appearance.compoundModel
                compMatrix = Math.Matrix(compoundModel.node(firstHitPoint.componentName))
                firstHitDirLocal = firstHitPoint.matrix.applyToAxis(2)
                firstHitDir = compMatrix.applyVector(firstHitDirLocal)
                if firstHitPoint.componentName == 'chassis' and 'wheeledVehicle' in self.typeDescriptor.type.tags:
                    self.appearance.storeHitPoint(firstHitPoint.matrix.translation)
                self.appearance.receiveShotImpulse(firstHitDir, effectsDescr['targetImpulse'])
                self.appearance.executeHitVibrations(maxHitEffectCode)
                player = BigWorld.player()
                player.inputHandler.onVehicleShaken(self, compMatrix.translation, firstHitDir, effectsDescr['caliber'], ShakeReason.HIT if hasPiercedHit else ShakeReason.HIT_NO_DAMAGE)
            for shotPoint in decodedPoints:
                showFullscreenEffs = self.isPlayerVehicle and self.isAlive()
                keyPoints, effects, _ = effectsDescr[shotPoint.hitEffectGroup]
                self.appearance.boundEffects.addNewToNode(shotPoint.componentName, shotPoint.matrix, effects, keyPoints, isPlayerVehicle=self.isPlayerVehicle, showShockWave=showFullscreenEffs, showFlashBang=showFullscreenEffs, entity_id=self.id, damageFactor=damageFactor, attackerID=attackerID, hitdir=firstHitDir)

            if not self.isAlive():
                return
            if attackerID == BigWorld.player().playerVehicleID:
                if maxHitEffectCode is not None and not self.isPlayerVehicle:
                    if hasPiercedHit:
                        eventID = _GUI_EVENT_ID.VEHICLE_ARMOR_PIERCED
                    else:
                        eventID = _GUI_EVENT_ID.VEHICLE_HIT
                    ctrl = g_sessionProvider.shared.feedback
                    ctrl is not None and ctrl.setVehicleState(self.id, eventID)
            return

    def showDamageFromExplosion(self, attackerID, center, effectsIndex, damageFactor):
        if not self.isStarted:
            return
        else:
            impulse = vehicles.g_cache.shotEffects[effectsIndex]['targetImpulse']
            dir = self.position - center
            dir.normalise()
            self.appearance.receiveShotImpulse(dir, impulse / 4.0)
            self.appearance.executeHitVibrations(VEHICLE_HIT_EFFECT.MAX_CODE + 1)
            if not self.isAlive():
                return
            self.showSplashHitEffect(effectsIndex, damageFactor)
            if self.id == attackerID:
                return
            player = BigWorld.player()
            player.inputHandler.onVehicleShaken(self, center, dir, vehicles.g_cache.shotEffects[effectsIndex]['caliber'], ShakeReason.SPLASH)
            if attackerID == BigWorld.player().playerVehicleID:
                ctrl = g_sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.setVehicleState(self.id, _GUI_EVENT_ID.VEHICLE_ARMOR_PIERCED)
            return

    def showVehicleCollisionEffect(self, pos, delta_spd):
        if not self.isStarted:
            return
        if delta_spd < 3:
            self.showCollisionEffect(pos, 'collisionVehicleLight')
        else:
            mass = self.typeDescriptor.physics['weight']
            if mass < 18000:
                self.showCollisionEffect(pos, 'collisionVehicleHeavy1')
            elif mass < 46000:
                self.showCollisionEffect(pos, 'collisionVehicleHeavy2')
            else:
                self.showCollisionEffect(pos, 'collisionVehicleHeavy3')
        self.appearance.executeRammingVibrations()

    def showCollisionEffect(self, hitPos, collisionEffectName='collisionVehicle', collisionNormal=None):
        invWorldMatrix = Math.Matrix(self.matrix)
        invWorldMatrix.invert()
        rot = Math.Matrix()
        if collisionNormal is None:
            rot.setRotateYPR((random.uniform(-3.14, 3.14), random.uniform(-1.5, 1.5), 0.0))
        else:
            rot.setRotateYPR((0, 0, 0))
        mat = Math.Matrix()
        mat.setTranslate(hitPos)
        mat.preMultiply(rot)
        mat.postMultiply(invWorldMatrix)
        effectsList = self.typeDescriptor.type.effects.get(collisionEffectName, [])
        if effectsList:
            keyPoints, effects, _ = random.choice(effectsList)
            self.appearance.boundEffects.addNewToNode(TankPartNames.HULL, mat, effects, keyPoints, entity=self, surfaceNormal=collisionNormal)
        return

    def showSplashHitEffect(self, effectsIndex, damageFactor):
        effectsList = vehicles.g_cache.shotEffects[effectsIndex].get('armorSplashHit', None)
        if effectsList:
            mat = Math.Matrix()
            mat.setTranslate((0.0, 0.0, 0.0))
            self.appearance.boundEffects.addNewToNode(TankPartNames.HULL, mat, effectsList[1], effectsList[0], entity=self, damageFactor=damageFactor)
        return

    def set_damageStickers(self, prev=None):
        if self.isStarted:
            prev = self.__prevDamageStickers
            curr = frozenset(self.damageStickers)
            self.__prevDamageStickers = curr
            for sticker in prev.difference(curr):
                self.appearance.removeDamageSticker(sticker)

            descr = self.typeDescriptor
            for sticker in curr.difference(prev):
                self.appearance.addDamageSticker(sticker, *DamageFromShotDecoder.decodeSegment(sticker, descr))

    def set_publicStateModifiers(self, prev=None):
        if self.isStarted:
            prev = self.__prevPublicStateModifiers
            curr = frozenset(self.publicStateModifiers)
            self.__prevPublicStateModifiers = curr
            self.__updateModifiers(curr.difference(prev), prev.difference(curr))

    def set_engineMode(self, prev):
        if self.isStarted:
            self.appearance.changeEngineMode(self.engineMode, True)

    def set_physicsMode(self, prev):
        if self.physicsMode != prev:
            if self.isPlayer:
                self.respawn(self.publicInfo.compDescr)
                BigWorld.player().physicModeChanged(self.physicsMode)
            else:
                self.respawn(self.publicInfo.compDescr)

    def set_isStrafing(self, prev):
        if hasattr(self.filter, 'isStrafing'):
            self.filter.isStrafing = self.isStrafing

    def set_gunAnglesPacked(self, prev):
        syncGunAngles = getattr(self.filter, 'syncGunAngles', None)
        if syncGunAngles:
            yaw, pitch = decodeGunAngles(self.gunAnglesPacked, self.typeDescriptor.gun['pitchLimits']['absolute'])
            syncGunAngles(yaw, pitch)
        return

    def set_secondGunAnglesPacked(self, prev):
        yaw, pitch = decodeGunAngles(self.secondGunAnglesPacked, self.typeDescriptor.gun['pitchLimits']['absolute'])
        self.appearance.markTurret.updateGunAngles(yaw, pitch)

    def set_health(self, prev):
        pass

    def set_isCrewActive(self, prev):
        if self.isStarted:
            self.appearance.onVehicleHealthChanged()
            if not self.isPlayerVehicle:
                ctrl = g_sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.setVehicleNewHealth(self.id, self.health)
            if not self.isCrewActive and self.health > 0:
                self.__onVehicleDeath()
        return

    def set_steeringAngle(self, prev):
        self.appearance.setSteeringAngle(self.steeringAngle)

    def onHealthChanged(self, newHealth, attackerID, attackReasonID):
        if newHealth > 0 and self.health <= 0:
            self.health = newHealth
            return
        elif not self.isStarted:
            return
        else:
            if not self.isPlayerVehicle:
                ctrl = g_sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.setVehicleNewHealth(self.id, newHealth, attackerID, attackReasonID)
            if not self.appearance.damageState.isCurrentModelDamaged:
                self.appearance.onVehicleHealthChanged()
            if self.health <= 0 and self.isCrewActive:
                self.__onVehicleDeath()
            return

    def showAmmoBayEffect(self, mode, fireballVolume, projectedTurretSpeed):
        if self.isStarted:
            self.appearance.showAmmoBayEffect(mode, fireballVolume)

    def onPushed(self, x, z):
        try:
            distSqr = BigWorld.player().position.distSqrTo(self.position)
            if distSqr > 1600.0:
                self.filter.setPosition(x, z)
        except:
            pass

    def showRammingEffect(self, energy, point):
        if not self.isStarted:
            return
        if energy < 600:
            self.showCollisionEffect(point, 'rammingCollisionLight')
        else:
            self.showCollisionEffect(point, 'rammingCollisionHeavy')

    def onStaticCollision(self, energy, point, normal, miscFlags):
        if not self.isStarted:
            return
        self.appearance.stopSwinging()
        BigWorld.player().inputHandler.onVehicleCollision(self, self.getSpeed())
        isTrackCollision = bool(miscFlags & 1)
        isSptCollision = bool(miscFlags >> 1 & 1)
        isSptDestroyed = bool(miscFlags >> 2 & 1)
        hitPoint = point
        surfNormal = normal
        if not isSptCollision:
            surfaceMaterial = calcSurfaceMaterialNearPoint(point, normal, self.spaceID)
            hitPoint, surfNormal, matKind, effectIdx = surfaceMaterial
        else:
            if isSptDestroyed:
                return
            hitPoint = point
            matKind = SPT_MATKIND.SOLID
            effectIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES['wood']
        self.__showStaticCollisionEffect(energy, matKind, effectIdx, hitPoint, surfNormal, isTrackCollision)

    def getComponents(self):
        res = []
        vehicleDescr = self.typeDescriptor
        m = Math.Matrix()
        m.setIdentity()
        res.append((vehicleDescr.chassis, m, True))
        hullOffset = vehicleDescr.chassis['hullPosition']
        m = Math.Matrix()
        m.setTranslate(-hullOffset)
        res.append((vehicleDescr.hull, m, True))
        turretYaw = Math.Matrix(self.appearance.turretMatrix).yaw
        turretMatrix = Math.Matrix()
        turretMatrix.setTranslate(-hullOffset - vehicleDescr.hull['turretPositions'][0])
        m = Math.Matrix()
        m.setRotateY(-turretYaw)
        turretMatrix.postMultiply(m)
        res.append((vehicleDescr.turret, turretMatrix, not self.isTurretDetached))
        gunPitch = Math.Matrix(self.appearance.gunMatrix).pitch
        gunMatrix = Math.Matrix()
        gunMatrix.setTranslate(-vehicleDescr.turret['gunPosition'])
        m = Math.Matrix()
        m.setRotateX(-gunPitch)
        gunMatrix.postMultiply(m)
        gunMatrix.preMultiply(turretMatrix)
        res.append((vehicleDescr.gun, gunMatrix, not self.isTurretDetached))
        return res

    def segmentMayHitVehicle(self, startPoint, endPoint):
        return segmentMayHitVehicle(self.typeDescriptor, startPoint, endPoint, self.position)

    def collideSegment(self, startPoint, endPoint, skipGun=False):
        filterMethod = getattr(self.filter, 'segmentMayHitEntity', self.segmentMayHitVehicle)
        if not filterMethod(startPoint, endPoint, 0):
            return
        else:
            worldToVehMatrix = Math.Matrix(self.model.matrix)
            worldToVehMatrix.invert()
            startPoint = worldToVehMatrix.applyPoint(startPoint)
            endPoint = worldToVehMatrix.applyPoint(endPoint)
            res = None
            for compDescr, compMatrix, isAttached in self.getComponents():
                if not isAttached:
                    continue
                if skipGun and compDescr.get('itemTypeName') == 'vehicleGun':
                    continue
                collisions = compDescr['hitTester'].localHitTest(compMatrix.applyPoint(startPoint), compMatrix.applyPoint(endPoint))
                if collisions is None:
                    continue
                for dist, _, hitAngleCos, matKind in collisions:
                    if res is None or res[0] >= dist:
                        matInfo = compDescr['materials'].get(matKind)
                        res = SegmentCollisionResult(dist, hitAngleCos, matInfo.armor if matInfo is not None else 0)

            return res

    def isAlive(self):
        return self.isCrewActive and self.health > 0

    def startVisual(self):
        assert not self.isStarted
        avatar = BigWorld.player()
        self.appearance.preStart(self.typeDescriptor)
        self.appearance.start(self, self.__prereqs)
        self.assembler.constructAppearance(self.__prereqs)
        del self.assembler
        self.appearance.startSystems()
        self.__prereqs = None
        self.appearance.changeEngineMode(self.engineMode)
        self.appearance.onVehicleHealthChanged()
        if self.isPlayerVehicle:
            if self.isAlive():
                self.appearance.setupGunMatrixTargets(avatar.gunRotator)
        if hasattr(self.filter, 'allowStrafeCompensation'):
            self.filter.allowStrafeCompensation = not self.isPlayerVehicle
        self.isStarted = True
        self.set_publicStateModifiers()
        self.set_damageStickers()
        g_sessionProvider.startVehicleVisual(self.proxy, True)
        if not self.isAlive():
            self.__onVehicleDeath(True)
        if self.isTurretMarkedForDetachment:
            self.confirmTurretDetachment()
        self.__startWGPhysics()
        self.refreshNationalVoice()
        return

    def refreshNationalVoice(self):
        if self is BigWorld.player().getVehicleAttached():
            nationId = self.typeDescriptor.type.id[0]
            LOG_DEBUG("Refreshing current vehicle's national voices", nationId)
            SoundGroups.g_instance.soundModes.setCurrentNation(nations.NAMES[nationId])

    def stopVisual(self):
        assert self.isStarted
        self.__stopExtras()
        g_sessionProvider.stopVehicleVisual(self.id, self.isPlayerVehicle)
        self.appearance.destroy()
        self.appearance = None
        self.isStarted = False
        self.__stopWGPhysics()
        return

    def show(self, show):
        if show:
            drawFlags = BigWorld.DrawAll
        else:
            drawFlags = BigWorld.ShadowPassBit
        if self.isStarted:
            va = self.appearance
            va.changeDrawPassVisibility(drawFlags)
            va.showStickers(show)

    def showPlayerMovementCommand(self, flags):
        if not self.isStarted:
            return
        powerMode = self.engineMode[0]
        if flags == 0 and powerMode != 0:
            self.appearance.changeEngineMode((1, 0))
            return
        if flags != 0 and powerMode != 0:
            self.appearance.changeEngineMode((3, flags))
            return

    def _isDestructibleMayBeBroken(self, chunkID, itemIndex, matKind, itemFilename, itemScale, vehSpeed):
        desc = AreaDestructibles.g_cache.getDescByFilename(itemFilename)
        if desc is None:
            return False
        else:
            ctrl = AreaDestructibles.g_destructiblesManager.getController(chunkID)
            if ctrl is None:
                return False
            if ctrl.isDestructibleBroken(itemIndex, matKind, desc['type']):
                return True
            mass = self.typeDescriptor.physics['weight']
            instantDamage = 0.5 * mass * vehSpeed * vehSpeed * 0.00015
            if desc['type'] == DestructiblesCache.DESTR_TYPE_STRUCTURE:
                moduleDesc = desc['modules'].get(matKind)
                if moduleDesc is None:
                    return False
                refHealth = moduleDesc['health']
            else:
                unitMass = AreaDestructibles.g_cache.unitVehicleMass
                instantDamage *= math.pow(mass / unitMass, desc['kineticDamageCorrection'])
                refHealth = desc['health']
            return DestructiblesCache.scaledDestructibleHealth(itemScale, refHealth) < instantDamage

    def __showStaticCollisionEffect(self, energy, matKind, effectIdx, hitPoint, normal, isTrackCollision):
        heavyVelocities = self.typeDescriptor.type.heavyCollisionEffectVelocities
        heavyEnergy = heavyVelocities['track'] if isTrackCollision else heavyVelocities['hull']
        heavyEnergy = 0.5 * heavyEnergy * heavyEnergy
        postfix = '%sCollisionLight' if energy < heavyEnergy else '%sCollisionHeavy'
        effectName = ''
        if effectIdx < len(EFFECT_MATERIALS):
            effectName = EFFECT_MATERIALS[effectIdx]
        effectName = postfix % effectName
        if effectName in self.typeDescriptor.type.effects:
            self.showCollisionEffect(hitPoint, effectName, normal)
        if self.isPlayerVehicle:
            self.appearance.executeRammingVibrations(matKind)

    def __startWGPhysics(self):
        if not hasattr(self.filter, 'setVehiclePhysics'):
            return
        else:
            typeDescr = self.typeDescriptor
            physics = BigWorld.WGVehiclePhysics()
            physics_shared.initVehiclePhysics(physics, typeDescr, None, False)
            arenaMinBound, arenaMaxBound = (-10000, -10000), (10000, 10000)
            physics.setArenaBounds(arenaMinBound, arenaMaxBound)
            physics.enginePower = typeDescr.physics['enginePower'] / 1000.0
            physics.owner = weakref.ref(self)
            physics.staticMode = False
            physics.movementSignals = 0
            physics.damageDestructibleCb = None
            physics.destructibleHealthRequestCb = None
            self.filter.setVehiclePhysics(physics)
            physics.visibilityMask = ArenaType.getVisibilityMask(BigWorld.player().arenaTypeID >> 16)
            yaw, pitch = decodeGunAngles(self.gunAnglesPacked, typeDescr.gun['pitchLimits']['absolute'])
            self.filter.syncGunAngles(yaw, pitch)
            self.__speedInfo.set(self.filter.speedInfo)
            return

    def __stopWGPhysics(self):
        self.__speedInfo.reset()

    def __stopExtras(self):
        extraTypes = self.typeDescriptor.extras
        for index, data in self.extras.items():
            extraTypes[index].stop(data)

        if self.extras:
            LOG_CODEPOINT_WARNING()

    def __updateModifiers(self, addedExtras, removedExtras):
        extraTypes = self.typeDescriptor.extras
        for idx in removedExtras:
            extraTypes[idx].stopFor(self)

        for idx in addedExtras:
            try:
                extraTypes[idx].startFor(self)
            except Exception:
                LOG_CURRENT_EXCEPTION()

    def __onVehicleDeath(self, isDeadStarted=False):
        if not self.isPlayerVehicle:
            ctrl = g_sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.setVehicleState(self.id, _GUI_EVENT_ID.VEHICLE_DEAD, isDeadStarted)
        self.stopHornSound(True)
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.VEHICLE_DESTROYED, vehicleId=self.id)
        bwfilter = self.filter
        if hasattr(bwfilter, 'velocityErrorCompensation'):
            bwfilter.velocityErrorCompensation = 100.0
        return

    def playHornSound(self, hornID):
        return
        hornDesc = vehicles.g_cache.horns().get(hornID)
        if hornDesc is None:
            return
        else:
            self.stopHornSound(True)
            self.__hornSounds = []
            self.__hornMode = hornDesc['mode']
            model = self.appearance.modelsDesc['turret']['model']
            for sndEventId in hornDesc['sounds']:
                snd = SoundGroups.g_instance.getSound3D(model.root, sndEventId)
                snd.volume *= self.typeDescriptor.type.hornVolumeFactor
                self.__hornSounds.append(snd)

            if self.__hornSounds[0] is not None:
                self.__hornSounds[0].play()
                if self.__hornMode == 'continuous' and hornDesc['maxDuration'] > 0:
                    self.__stopHornSoundCallback = BigWorld.callback(hornDesc['maxDuration'], self.stopHornSound)
            return

    def stopHornSound(self, forceSilence=False):
        if not forceSilence and self.__hornMode == 'twoSounds':
            if self.__hornSounds[1] is not None:
                self.__hornSounds[1].play()
        else:
            for snd in self.__hornSounds:
                if snd is not None:
                    snd.stop()

            self.__hornSounds = (None,)
        if self.__stopHornSoundCallback is not None:
            BigWorld.cancelCallback(self.__stopHornSoundCallback)
            self.__stopHornSoundCallback = None
        self.__hornMode = ''
        return

    def isHornActive(self):
        if self.__hornMode == 'twoSounds':
            return True
        else:
            anySoundPlaying = False
            for snd in self.__hornSounds:
                if snd is not None:
                    state = snd.state
                    if state is not None and state.find('playing') != -1:
                        return True

            return False

    def confirmTurretDetachment(self):
        self.__turretDetachmentConfirmed = True
        if not self.isTurretDetached:
            LOG_ERROR('Vehicle::confirmTurretDetachment: Confirming turret detachment, though the turret is not detached')
        self.appearance.updateTurretVisibility()

    def drawEdge(self, forceSimpleEdge=False):
        self.appearance.highlighter.highlight(True, forceSimpleEdge)

    def removeEdge(self, forceSimpleEdge=False):
        self.appearance.highlighter.highlight(False, forceSimpleEdge)

    def addModel(self, model):
        super(Vehicle, self).addModel(model)
        highlighter = self.appearance.highlighter
        if highlighter.enabled:
            highlighter.highlight(True, ignoreLock=True)

    def delModel(self, model):
        highlighter = self.appearance.highlighter
        hlEnabled = highlighter.enabled
        if hlEnabled:
            highlighter.highlight(False, ignoreLock=True)
        super(Vehicle, self).delModel(model)
        if hlEnabled:
            highlighter.highlight(True, ignoreLock=True)


def _stripVehCompDescrIfRoaming(vehCompDescr):
    serverSettings = g_lobbyContext.getServerSettings()
    if serverSettings:
        if serverSettings.roaming.isInRoaming():
            vehCompDescr = vehicles.stripCustomizationFromVehicleCompactDescr(vehCompDescr, True, True, False)[0]
    return vehCompDescr
