# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vehicle.py
import logging
import math
import random
import weakref
from collections import namedtuple
import BigWorld
import Math
import NetworkFilters
import WoT
import AreaDestructibles
import ArenaType
import BattleReplay
import DestructiblesCache
import TriggersManager
import constants
import physics_shared
from aih_constants import ShakeReason
from TriggersManager import TRIGGER_TYPE
from VehicleEffects import DamageFromShotDecoder
from constants import SPT_MATKIND
from constants import VEHICLE_HIT_EFFECT, VEHICLE_SIEGE_STATE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _GUI_EVENT_ID, VEHICLE_VIEW_STATE
from gun_rotation_shared import decodeGunAngles
from helpers import dependency
from helpers.EffectMaterialCalculation import calcSurfaceMaterialNearPoint
from helpers.EffectsList import SoundStartParam
from items import vehicles
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_NAMES, EFFECT_MATERIALS
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
from special_sound import setSpecialVoice
from vehicle_systems import appearance_cache
from vehicle_systems.entity_components.battle_abilities_component import BattleAbilitiesComponent
from vehicle_systems.stricted_loading import loadingPriority
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes, TankSoundObjectsIndexes
_logger = logging.getLogger(__name__)
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
        self.__value = Math.Vector4Basic()

    def set(self, val):
        self.__value = val

    def reset(self):
        self.__value = Math.Vector4Basic()


SegmentCollisionResultExt = namedtuple('SegmentCollisionResultExt', ('dist',
 'hitAngleCos',
 'matInfo',
 'compName'))
StunInfo = namedtuple('StunInfo', ('startTime',
 'endTime',
 'duration',
 'totalTime'))
VEHICLE_COMPONENTS = {BattleAbilitiesComponent}

class Vehicle(BigWorld.Entity, BattleAbilitiesComponent):
    isEnteringWorld = property(lambda self: self.__isEnteringWorld)
    isTurretDetached = property(lambda self: constants.SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health) and self.__turretDetachmentConfirmed)
    isTurretMarkedForDetachment = property(lambda self: constants.SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health))
    isTurretDetachmentConfirmationNeeded = property(lambda self: not self.__turretDetachmentConfirmed)
    hasMovingFlags = property(lambda self: self.engineMode is not None and self.engineMode[1] & 3)
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    @property
    def speedInfo(self):
        return self.__speedInfo

    @property
    def isWheeledTech(self):
        return 'wheeledVehicle' in self.typeDescriptor.type.tags

    @property
    def wheelsScrollSmoothed(self):
        if self.__wheelsScrollFilter is not None:
            return [ scrollFilter.output(BigWorld.time()) for scrollFilter in self.__wheelsScrollFilter ]
        else:
            return

    @property
    def wheelsScrollFilters(self):
        return self.__wheelsScrollFilter

    @property
    def wheelsSteeringSmoothed(self):
        if self.__wheelsSteeringFilter is not None:
            return [ steeringFilter.output(BigWorld.time()) for steeringFilter in self.__wheelsSteeringFilter ]
        else:
            return

    @property
    def wheelsSteeringFilters(self):
        return self.__wheelsSteeringFilter

    def getBounds(self, partIdx):
        return self.appearance.getBounds(partIdx) if self.appearance is not None else (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0), 0)

    def getSpeed(self):
        return self.__speedInfo.value[0]

    def __init__(self):
        global _g_waitingVehicle
        for comp in VEHICLE_COMPONENTS:
            comp.__init__(self)

        self.proxy = weakref.proxy(self)
        self.extras = {}
        self.typeDescriptor = None
        self.appearance = None
        self.isPlayerVehicle = False
        self.isStarted = False
        self.__isEnteringWorld = False
        self.__turretDetachmentConfirmed = False
        self.__speedInfo = _VehicleSpeedProvider()
        _g_waitingVehicle[self.id] = weakref.ref(self)
        self.respawnCompactDescr = None
        self.respawnOutfitCompactDescr = None
        self.__cachedStunInfo = StunInfo(0.0, 0.0, 0.0, 0.0)
        self.__burnoutStarted = False
        self.__handbrakeFired = False
        self.__wheelsScrollFilter = None
        self.__wheelsSteeringFilter = None
        return

    def __del__(self):
        if _g_waitingVehicle.has_key(self.id):
            del _g_waitingVehicle[self.id]

    def reload(self):
        if self.isStarted:
            self.stopVisual()
        vehicles.reload()
        self.respawn(self.publicInfo.compDescr)

    def prerequisites(self, respawnCompactDescr=None):
        if self.respawnCompactDescr is not None:
            respawnCompactDescr = self.respawnCompactDescr
            self.isCrewActive = True
            self.respawnCompactDescr = None
        if self.respawnOutfitCompactDescr is not None:
            outfitDescr = self.respawnOutfitCompactDescr
            self.respawnOutfitCompactDescr = None
        else:
            outfitDescr = self.publicInfo.outfit
        if respawnCompactDescr is None and self.typeDescriptor is not None:
            return
        else:
            self.typeDescriptor = self.getDescr(respawnCompactDescr)
            forceReloading = respawnCompactDescr is not None
            self.appearance, prereqs = appearance_cache.createAppearance(self.id, self.typeDescriptor, self.health, self.isCrewActive, self.isTurretDetached, outfitDescr, forceReloading)
            return (loadingPriority(self.id), prereqs)

    def getDescr(self, respawnCompactDescr):
        if respawnCompactDescr is not None:
            descr = vehicles.VehicleDescr(respawnCompactDescr)
            self.health = descr.maxHealth
            return descr
        else:
            return vehicles.VehicleDescr(compactDescr=_stripVehCompDescrIfRoaming(self.publicInfo.compDescr))

    @staticmethod
    def respawnVehicle(vID, compactDescr=None, outfitCompactDescr=None):
        vehicleRef = _g_waitingVehicle.get(vID, None)
        if vehicleRef is None and BigWorld.entities.get(vID) is not None:
            _g_waitingVehicle[vID] = vehicleRef = weakref.ref(BigWorld.entities[vID])
        if vehicleRef is not None:
            vehicle = vehicleRef()
            if vehicle is not None:
                vehicle.respawnCompactDescr = compactDescr
                vehicle.respawnOutfitCompactDescr = outfitCompactDescr
                if not BigWorld.entities.get(vID):
                    _logger.error('respawn vehicle: Vehicle ref is not None but entity does not exist anymore. Skip wg_respawn')
                else:
                    try:
                        vehicle.wg_respawn()
                    except Exception:
                        _logger.error('respawn vehicle: Vehicle ref is not None but failed to call respawn: %s', vID)

        return

    def __initAdditionalFilters(self):
        self.__wheelsScrollFilter = None
        self.__wheelsSteeringFilter = None
        if self.typeDescriptor.chassis.generalWheelsAnimatorConfig is not None:
            scrollableWheelsCount = self.typeDescriptor.chassis.generalWheelsAnimatorConfig.getNonTrackWheelsCount()
            self.__wheelsScrollFilter = []
            for _ in range(scrollableWheelsCount):
                self.__wheelsScrollFilter.append(NetworkFilters.FloatLatencyDelayingFilter())
                self.__wheelsScrollFilter[-1].input(BigWorld.time(), 0.0)

            steerableWheelsCount = self.typeDescriptor.chassis.generalWheelsAnimatorConfig.getSteerableWheelsCount()
            self.__wheelsSteeringFilter = []
            for _ in range(steerableWheelsCount):
                self.__wheelsSteeringFilter.append(NetworkFilters.FloatLatencyDelayingFilter())
                self.__wheelsSteeringFilter[-1].input(BigWorld.time(), 0.0)

        return

    def onEnterWorld(self, prereqs):
        self.__prereqs = prereqs
        self.__isEnteringWorld = True
        self.__prevDamageStickers = frozenset()
        self.__prevPublicStateModifiers = frozenset()
        self.targetFullBounds = True
        self.__initAdditionalFilters()
        player = BigWorld.player()
        player.vehicle_onEnterWorld(self)
        if self.isPlayerVehicle:
            self.cell.sendStateToOwnClient()
        player.initSpace()
        self.__isEnteringWorld = False
        if self.respawnCompactDescr:
            _logger.debug('respawn compact descr is still valid, request reloading of tank resources')
            BigWorld.callback(0.0, lambda : Vehicle.respawnVehicle(self.id, self.respawnCompactDescr))

    def onLeaveWorld(self):
        self.__stopExtras()
        BigWorld.player().vehicle_onLeaveWorld(self)

    def showShooting(self, burstCount, isPredictedShot=False):
        blockShooting = self.siegeState is not None and self.siegeState != VEHICLE_SIEGE_STATE.ENABLED and self.siegeState != VEHICLE_SIEGE_STATE.DISABLED
        if not self.isStarted or blockShooting:
            return
        else:
            if not isPredictedShot and self.isPlayerVehicle and not BigWorld.player().isWaitingForShot:
                if not BattleReplay.g_replayCtrl.isPlaying:
                    return
            extra = self.typeDescriptor.extrasDict['shoot']
            extra.stopFor(self)
            extra.startFor(self, burstCount)
            if not isPredictedShot and self.isPlayerVehicle:
                ctrl = self.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.onShotDone()
                BigWorld.player().cancelWaitingForShot()
            return

    def showDamageFromShot(self, attackerID, points, effectsIndex, damageFactor):
        if not self.isStarted:
            return
        else:
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            maxComponentIdx = TankPartIndexes.ALL[-1]
            wheelsConfig = self.appearance.typeDescriptor.chassis.generalWheelsAnimatorConfig
            if wheelsConfig:
                maxComponentIdx = maxComponentIdx + wheelsConfig.getNonTrackWheelsCount()
            maxHitEffectCode, decodedPoints, maxDamagedComponent = DamageFromShotDecoder.decodeHitPoints(points, self.appearance.collisions, maxComponentIdx)
            hasPiercedHit = DamageFromShotDecoder.hasDamaged(maxHitEffectCode)
            firstHitDir = Math.Vector3(0)
            if decodedPoints:
                firstHitPoint = decodedPoints[0]
                compoundModel = self.appearance.compoundModel
                compMatrix = Math.Matrix(compoundModel.node(firstHitPoint.componentName))
                firstHitDirLocal = firstHitPoint.matrix.applyToAxis(2)
                firstHitDir = compMatrix.applyVector(firstHitDirLocal)
                self.appearance.receiveShotImpulse(firstHitDir, effectsDescr['targetImpulse'])
                self.appearance.executeHitVibrations(maxHitEffectCode)
                player = BigWorld.player()
                player.inputHandler.onVehicleShaken(self, compMatrix.translation, firstHitDir, effectsDescr['caliber'], ShakeReason.HIT if hasPiercedHit else ShakeReason.HIT_NO_DAMAGE)
            sessionProvider = self.guiSessionProvider
            isAlly = sessionProvider.getArenaDP().isAlly(attackerID)
            showFriendlyFlashBang = sessionProvider.arenaVisitor.hasCustomAllyDamageEffect() and isAlly
            for shotPoint in decodedPoints:
                showFullscreenEffs = self.isPlayerVehicle and self.isAlive()
                keyPoints, effects, _ = effectsDescr[shotPoint.hitEffectGroup]
                self.appearance.boundEffects.addNewToNode(shotPoint.componentName, shotPoint.matrix, effects, keyPoints, isPlayerVehicle=self.isPlayerVehicle, showShockWave=showFullscreenEffs, showFlashBang=showFullscreenEffs and not showFriendlyFlashBang, showFriendlyFlashBang=showFullscreenEffs and showFriendlyFlashBang, entity_id=self.id, damageFactor=damageFactor, attackerID=attackerID, hitdir=firstHitDir)

            if not self.isAlive():
                return
            if attackerID == BigWorld.player().playerVehicleID:
                if maxHitEffectCode is not None and not self.isPlayerVehicle:
                    if maxHitEffectCode in VEHICLE_HIT_EFFECT.RICOCHETS:
                        eventID = _GUI_EVENT_ID.VEHICLE_RICOCHET
                    elif maxHitEffectCode == VEHICLE_HIT_EFFECT.CRITICAL_HIT:
                        if maxDamagedComponent == TankPartNames.CHASSIS:
                            if damageFactor:
                                eventID = _GUI_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS_PIERCED
                            else:
                                eventID = _GUI_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS
                        else:
                            eventID = _GUI_EVENT_ID.VEHICLE_CRITICAL_HIT
                    elif hasPiercedHit:
                        eventID = _GUI_EVENT_ID.VEHICLE_ARMOR_PIERCED
                    else:
                        eventID = _GUI_EVENT_ID.VEHICLE_HIT
                    ctrl = self.guiSessionProvider.shared.feedback
                    ctrl is not None and ctrl.setVehicleState(self.id, eventID)
            return

    def showDamageFromExplosion(self, attackerID, center, effectsIndex, damageFactor):
        if not self.isStarted:
            return
        else:
            impulse = vehicles.g_cache.shotEffects[effectsIndex]['targetImpulse']
            direction = self.position - center
            direction.normalise()
            self.appearance.receiveShotImpulse(direction, impulse / 4.0)
            self.appearance.executeHitVibrations(VEHICLE_HIT_EFFECT.MAX_CODE + 1)
            if not self.isAlive():
                return
            self.showSplashHitEffect(effectsIndex, damageFactor)
            if self.id == attackerID:
                return
            player = BigWorld.player()
            player.inputHandler.onVehicleShaken(self, center, direction, vehicles.g_cache.shotEffects[effectsIndex]['caliber'], ShakeReason.SPLASH)
            if attackerID == BigWorld.player().playerVehicleID:
                ctrl = self.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.setVehicleState(self.id, _GUI_EVENT_ID.VEHICLE_ARMOR_PIERCED)
            return

    def showVehicleCollisionEffect(self, pos, delta_spd, energy=0):
        if not self.isStarted:
            return
        else:
            if delta_spd >= 3:
                effectName = 'collisionVehicleHeavy2'
                mass = self.typeDescriptor.physics['weight']
                if mass < 18000:
                    effectName = 'collisionVehicleHeavy1'
                elif mass > 46000:
                    effectName = 'collisionVehicleHeavy3'
            else:
                effectName = 'collisionVehicleLight'
            self.showCollisionEffect(pos, effectName, None, False, 0, None, energy)
            self.appearance.executeRammingVibrations()
            return

    def showCollisionEffect(self, hitPos, collisionEffectName='collisionVehicle', collisionNormal=None, isTracks=False, damageFactor=0, impulse=None, pcEnergy=None):
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
        if pcEnergy is not None:
            collisionEnergy = [SoundStartParam('RTPC_ext_collision_impulse_tank', pcEnergy)]
        else:
            collisionEnergy = []
        effectsList = self.typeDescriptor.type.effects.get(collisionEffectName, [])
        if effectsList:
            keyPoints, effects, _ = random.choice(effectsList)
            self.appearance.boundEffects.addNewToNode(TankPartNames.HULL, mat, effects, keyPoints, entity=self, surfaceNormal=collisionNormal, isTracks=isTracks, impulse=impulse, damageFactor=damageFactor, hitPoint=hitPos, soundParams=collisionEnergy)
        return

    def showSplashHitEffect(self, effectsIndex, damageFactor):
        effectsList = vehicles.g_cache.shotEffects[effectsIndex].get('armorSplashHit', None)
        if effectsList:
            mat = Math.Matrix()
            mat.setTranslate((0.0, 0.0, 0.0))
            self.appearance.boundEffects.addNewToNode(TankPartNames.HULL, mat, effectsList[1], effectsList[0], entity=self, damageFactor=damageFactor)
        return

    def set_burnoutLevel(self, prev):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None:
            return
        else:
            isAttachedVehicle = self.id == attachedVehicle.id
            if self.appearance.detailedEngineState is not None:
                self.appearance.detailedEngineState.throttle = 1 if self.burnoutLevel > 0.01 else 0
            if self.burnoutLevel > 0 and not self.__handbrakeFired:
                if self.getSpeed() > 0.5:
                    if not self.__burnoutStarted:
                        soundObject = self.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.CHASSIS)
                        soundObject.play('wheel_vehicle_burnout')
                        self.__burnoutStarted = True
            else:
                self.__burnoutStarted = False
            if isAttachedVehicle:
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BURNOUT, self.burnoutLevel)
            return

    def set_wheelsState(self, prev):
        if self.appearance is None:
            return
        else:
            __WHEEL_DESTROYED = 3
            for i in xrange(0, 8):
                prevState = prev >> i * 2 & 3
                newState = self.wheelsState >> i * 2 & 3
                if prevState != newState:
                    if newState == __WHEEL_DESTROYED:
                        self.appearance.onChassisDestroySound(False, True, i)
                    elif prevState == __WHEEL_DESTROYED:
                        self.appearance.onChassisDestroySound(False, False, i)

            return

    def set_damageStickers(self, prev=None):
        if self.isStarted:
            prev = self.__prevDamageStickers
            curr = frozenset(self.damageStickers)
            self.__prevDamageStickers = curr
            for sticker in prev.difference(curr):
                self.appearance.removeDamageSticker(sticker)

            maxComponentIdx = TankPartIndexes.ALL[-1]
            wheelsConfig = self.appearance.typeDescriptor.chassis.generalWheelsAnimatorConfig
            if wheelsConfig:
                maxComponentIdx = maxComponentIdx + wheelsConfig.getNonTrackWheelsCount()
            for sticker in curr.difference(prev):
                self.appearance.addDamageSticker(sticker, *DamageFromShotDecoder.decodeSegment(sticker, self.appearance.collisions, maxComponentIdx))

    def set_publicStateModifiers(self, prev=None):
        if self.isStarted:
            prev = self.__prevPublicStateModifiers
            curr = frozenset(self.publicStateModifiers)
            self.__prevPublicStateModifiers = curr
            self.__updateModifiers(curr.difference(prev), prev.difference(curr))
            if not self.isPlayerVehicle:
                self.updateStunInfo()

    def set_engineMode(self, prev):
        if self.isStarted and self.isAlive():
            self.appearance.changeEngineMode(self.engineMode, True)

    def set_isStrafing(self, prev):
        if hasattr(self.filter, 'isStrafing'):
            self.filter.isStrafing = self.isStrafing

    def set_gunAnglesPacked(self, prev):
        syncGunAngles = getattr(self.filter, 'syncGunAngles', None)
        if syncGunAngles:
            yaw, pitch = decodeGunAngles(self.gunAnglesPacked, self.typeDescriptor.gun.pitchLimits['absolute'])
            syncGunAngles(yaw, pitch)
        return

    def set_health(self, prev):
        pass

    def set_isCrewActive(self, prev):
        if self.isStarted:
            self.appearance.onVehicleHealthChanged()
            if not self.isPlayerVehicle:
                ctrl = self.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.setVehicleNewHealth(self.id, self.health)
            if not self.isCrewActive and self.health > 0:
                self.__onVehicleDeath()
        return

    def set_siegeState(self, prev):
        if not self.isPlayerVehicle:
            self.onSiegeStateUpdated(self.siegeState, 0.0)

    def set_isSpeedCapturing(self, prev=None):
        _logger.debug('set_isSpeedCapturing %s', self.isSpeedCapturing)
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidatePassiveEngineering(self.id, (True, self.isSpeedCapturing))
        return

    def set_isBlockingCapture(self, prev=None):
        _logger.debug('set_isBlockingCapture %s', self.isBlockingCapture)
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidatePassiveEngineering(self.id, (False, self.isBlockingCapture))
        return

    def set_steeringAngles(self, prev=None):
        if self.__wheelsSteeringFilter is not None:
            for packedValue, steeringFilter in zip(self.steeringAngles, self.__wheelsSteeringFilter):
                unpackedValue = WoT.unpackWheelSteering(packedValue)
                steeringFilter.input(BigWorld.time(), unpackedValue)

        return

    def set_wheelsScroll(self, prev=None):
        if self.__wheelsScrollFilter is not None:
            for packedValue, scrollFilter in zip(self.wheelsScroll, self.__wheelsScrollFilter):
                unpackedValue = WoT.unpackWheelScroll(packedValue)
                scrollFilter.input(BigWorld.time(), unpackedValue)

        return

    def onHealthChanged(self, newHealth, attackerID, attackReasonID):
        if newHealth > 0 and self.health <= 0:
            self.health = newHealth
            return
        if not self.isStarted:
            return
        self.guiSessionProvider.setVehicleHealth(self.isPlayerVehicle, self.id, newHealth, attackerID, attackReasonID)
        if not self.appearance.damageState.isCurrentModelDamaged:
            self.appearance.onVehicleHealthChanged()
        if self.health <= 0 and self.isCrewActive:
            self.__onVehicleDeath()
        if self.isPlayerVehicle:
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_RECEIVE_DAMAGE, attackerId=attackerID)

    def set_stunInfo(self, prev):
        _logger.debug('Set stun info(curr,~ prev): %s, %s', self.stunInfo, prev)
        self.updateStunInfo()

    def __updateCachedStunInfo(self, endTime):
        if endTime:
            cachedStartTime = self.__cachedStunInfo.startTime
            startTime = cachedStartTime if cachedStartTime > 0.0 else BigWorld.serverTime()
            totalTime = max(self.__cachedStunInfo.duration, endTime - startTime)
            duration = endTime - BigWorld.serverTime() if endTime > 0.0 else 0.0
            self.__cachedStunInfo = StunInfo(startTime, endTime, duration, totalTime)
        else:
            self.__cachedStunInfo = StunInfo(0.0, 0.0, 0.0, 0.0)

    def updateStunInfo(self):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None:
            return
        else:
            self.__updateCachedStunInfo(self.stunInfo)
            if self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                isAttachedVehicle = self.id == attachedVehicle.id
                if isAttachedVehicle:
                    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.STUN, self.__cachedStunInfo)
                if not self.isPlayerVehicle:
                    ctrl = self.guiSessionProvider.shared.feedback
                    if ctrl is not None:
                        ctrl.invalidateStun(self.id, self.__cachedStunInfo)
            else:
                _logger.warning('Stun features is disabled!')
            return

    def showAmmoBayEffect(self, mode, fireballVolume, projectedTurretSpeed):
        if self.isStarted:
            self.appearance.showAmmoBayEffect(mode, fireballVolume)

    def onPushed(self, x, z):
        try:
            distSqr = BigWorld.player().position.distSqrTo(self.position)
            if distSqr > 1600.0:
                self.filter.setPosition(x, z)
        except Exception:
            pass

    def showRammingEffect(self, energy, point):
        if not self.isStarted:
            return
        if energy < 600:
            self.showCollisionEffect(point, 'rammingCollisionLight')
        else:
            self.showCollisionEffect(point, 'rammingCollisionHeavy')

    def onStaticCollision(self, energy, point, normal, miscFlags, damage, destrEffectIdx, destrMaxHealth):
        if not self.isStarted:
            return
        self.appearance.stopSwinging()
        BigWorld.player().inputHandler.onVehicleCollision(self, self.getSpeed())
        isTrackCollision = bool(miscFlags & 1)
        isSptCollision = bool(miscFlags >> 1 & 1)
        isSptDestroyed = bool(miscFlags >> 2 & 1)
        if isSptDestroyed:
            return
        hitPoint = point
        surfNormal = normal
        matKind = SPT_MATKIND.SOLID
        if destrEffectIdx < 0:
            if not isSptCollision:
                surfaceMaterial = calcSurfaceMaterialNearPoint(hitPoint, normal, self.spaceID)
                hitPoint, surfNormal, matKind, effectIdx = surfaceMaterial
            else:
                effectIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES['wood']
            if matKind != 0:
                self.__showStaticCollisionEffect(energy, effectIdx, hitPoint, surfNormal, isTrackCollision, damage * 100.0)
        else:
            self.__showDynamicCollisionEffect(energy, destrMaxHealth, hitPoint, surfNormal)
        if self.isPlayerVehicle:
            self.appearance.executeRammingVibrations(matKind)

    def getAimParams(self):
        if self.appearance is not None:
            turretYaw = Math.Matrix(self.appearance.turretMatrix).yaw
            gunPitch = Math.Matrix(self.appearance.gunMatrix).pitch
            return (turretYaw, gunPitch)
        else:
            return (0.0, 0.0)

    def onSiegeStateUpdated(self, newState, timeToNextMode):
        if not self.isStarted:
            return
        else:
            if self.typeDescriptor is not None and self.typeDescriptor.hasSiegeMode:
                self.typeDescriptor.onSiegeStateChanged(newState)
                self.appearance.onSiegeStateChanged(newState)
                if self.isPlayerVehicle:
                    inputHandler = BigWorld.player().inputHandler
                    inputHandler.siegeModeControl.notifySiegeModeChanged(self, newState, timeToNextMode)
            else:
                _logger.error('Wrong usage! Should be called only on vehicle with valid typeDescriptor and siege mode')
            return

    def collideSegmentExt(self, startPoint, endPoint):
        if self.appearance.collisions is not None:
            collisions = self.appearance.collisions.collideAllWorld(startPoint, endPoint)
            if collisions:
                res = []
                for collision in collisions:
                    matInfo = self.getMatinfo(collision[3], collision[2])
                    res.append(SegmentCollisionResultExt(collision[0], collision[1], matInfo, collision[3]))

                return res
        return

    def getMatinfo(self, parIndex, matKind):
        matInfo = None
        if parIndex == TankPartIndexes.CHASSIS:
            matInfo = self.typeDescriptor.chassis.materials.get(matKind)
        elif parIndex == TankPartIndexes.HULL:
            matInfo = self.typeDescriptor.hull.materials.get(matKind)
        elif parIndex == TankPartIndexes.TURRET:
            matInfo = self.typeDescriptor.turret.materials.get(matKind)
        elif parIndex == TankPartIndexes.GUN:
            matInfo = self.typeDescriptor.gun.materials.get(matKind)
        return matInfo

    def isAlive(self):
        return self.isCrewActive and self.health > 0

    def isPitchHullAimingAvailable(self):
        return self.typeDescriptor is not None and self.typeDescriptor.isPitchHullAimingAvailable

    def getServerGunAngles(self):
        return decodeGunAngles(self.gunAnglesPacked, self.typeDescriptor.gun.pitchLimits['absolute'])

    def startVisual(self):
        if self.isStarted:
            raise SoftException('Vehicle is already started')
        avatar = BigWorld.player()
        self.appearance = appearance_cache.getAppearance(self.id, self.__prereqs)
        self.appearance.setVehicle(self)
        self.appearance.activate()
        self.appearance.changeEngineMode(self.engineMode)
        self.appearance.onVehicleHealthChanged(self.isPlayerVehicle)
        if self.isPlayerVehicle:
            if self.isAlive():
                self.appearance.setupGunMatrixTargets(avatar.gunRotator)
        if hasattr(self.filter, 'allowStrafeCompensation'):
            self.filter.allowStrafeCompensation = not self.isPlayerVehicle
        self.isStarted = True
        if not self.appearance.isObserver:
            self.show(True)
        self.set_publicStateModifiers()
        self.set_damageStickers()
        if TriggersManager.g_manager:
            TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED, vehicleId=self.id, isVisible=True)
        self.guiSessionProvider.startVehicleVisual(self.proxy, True)
        if self.stunInfo > 0.0:
            self.updateStunInfo()
        self.set_inspiringEffect()
        self.set_inspired()
        if self.isSpeedCapturing:
            self.set_isSpeedCapturing()
        if self.isBlockingCapture:
            self.set_isBlockingCapture()
        if not self.isAlive():
            self.__onVehicleDeath(True)
        if self.isTurretMarkedForDetachment:
            self.confirmTurretDetachment()
        self.__startWGPhysics()
        self.refreshNationalVoice()
        self.__prereqs = None
        self.appearance.highlighter.setVehicleOwnership()
        if self.respawnCompactDescr:
            _logger.debug('respawn compact descr is still valid, request reloading of tank resources %s', self.id)
            BigWorld.callback(0.0, lambda : Vehicle.respawnVehicle(self.id, self.respawnCompactDescr))
        return

    def refreshNationalVoice(self):
        player = BigWorld.player()
        if self is not player.getVehicleAttached():
            return
        commanderSkinID = self.publicInfo.commanderSkinID
        vehicleType = self.typeDescriptor.type
        setSpecialVoice(self.publicInfo.crewGroup, commanderSkinID, vehicleType, self.id == player.playerVehicleID)

    def stopVisual(self, showStipple=False):
        if not self.isStarted:
            raise SoftException('Vehicle is already stopped')
        stippleModel = None
        showStipple = False
        if showStipple:
            self.appearance.assembleStipple()
        self.__stopExtras()
        if TriggersManager.g_manager:
            TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED, vehicleId=self.id, isVisible=False)
        self.guiSessionProvider.stopVehicleVisual(self.id, self.isPlayerVehicle)
        self.appearance.deactivate()
        self.appearance = None
        self.isStarted = False
        self.__speedInfo.reset()
        return stippleModel

    def show(self, show):
        if show:
            drawFlags = BigWorld.DrawAll
        else:
            drawFlags = BigWorld.ShadowPassBit
        if self.isStarted:
            va = self.appearance
            va.changeDrawPassVisibility(drawFlags)
            va.showStickers(show)

    def addCameraCollider(self):
        if self.appearance is not None:
            self.appearance.addCameraCollider()
        return

    def removeCameraCollider(self):
        if self.appearance is not None:
            self.appearance.removeCameraCollider()
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

    def __showStaticCollisionEffect(self, energy, effectIdx, hitPoint, normal, isTrackCollision, damageFactor):
        heavyVelocities = self.typeDescriptor.type.heavyCollisionEffectVelocities
        heavyEnergy = heavyVelocities['track'] if isTrackCollision else heavyVelocities['hull']
        heavyEnergy = 0.5 * heavyEnergy * heavyEnergy
        postfix = '%sCollisionLight' if energy < heavyEnergy else '%sCollisionHeavy'
        effectName = ''
        if effectIdx < len(EFFECT_MATERIALS):
            effectName = EFFECT_MATERIALS[effectIdx]
        effectName = postfix % effectName
        if effectName in self.typeDescriptor.type.effects:
            self.showCollisionEffect(hitPoint, effectName, normal, isTrackCollision, damageFactor, self.__getImpulse(self.getSpeed()))

    def __showDynamicCollisionEffect(self, energy, destrMaxHealth, hitPoint, surfNormal):
        effectName = 'dynamicCollision'
        if effectName in self.typeDescriptor.type.effects:
            self.showCollisionEffect(hitPoint, effectName, surfNormal, False, 0, self.__getDynamicImpulse(self.getSpeed(), destrMaxHealth))

    def __startWGPhysics(self):
        if not hasattr(self.filter, 'setVehiclePhysics'):
            return
        typeDescr = self.typeDescriptor
        isWheeled = 'wheeledVehicle' in self.typeDescriptor.type.tags
        physics = BigWorld.WGWheeledPhysics() if isWheeled else BigWorld.WGTankPhysics()
        physics_shared.initVehiclePhysicsClient(physics, typeDescr)
        arenaMinBound, arenaMaxBound = (-10000, -10000), (10000, 10000)
        physics.setArenaBounds(arenaMinBound, arenaMaxBound)
        physics.owner = weakref.ref(self)
        physics.staticMode = False
        physics.movementSignals = 0
        self.filter.setVehiclePhysics(physics)
        physics.visibilityMask = ArenaType.getVisibilityMask(BigWorld.player().arenaTypeID >> 16)
        yaw, pitch = decodeGunAngles(self.gunAnglesPacked, typeDescr.gun.pitchLimits['absolute'])
        self.filter.syncGunAngles(yaw, pitch)
        self.__speedInfo.set(self.filter.speedInfo)

    def __stopWGPhysics(self):
        self.__speedInfo.reset()

    def __getImpulse(self, speed):
        mass = self.typeDescriptor.physics['weight']
        maxSpeed = self.typeDescriptor.physics['speedLimits'][0]
        return math.fabs(speed * mass / (maxSpeed * mass))

    def __getDynamicImpulse(self, speed, maxHealth):
        maxSpeed = 20.0
        relSpeed = min(math.fabs(speed / maxSpeed), 1.0)
        relSpeed *= relSpeed
        relHeath = min(min(maxHealth, 90.0) / 90.0, 1.0)
        return 0.5 * (relSpeed + relHeath)

    def __stopExtras(self):
        extraTypes = self.typeDescriptor.extras
        for index, data in self.extras.items():
            extraTypes[index].stop(data)

        if self.extras:
            _logger.warning('this code point should have never been reached')

    def __updateModifiers(self, addedExtras, removedExtras):
        extraTypes = self.typeDescriptor.extras
        for idx in removedExtras:
            extraTypes[idx].stopFor(self)

        for idx in addedExtras:
            try:
                extraTypes[idx].startFor(self)
            except Exception:
                _logger.exception('Update modifiers')

    def __onVehicleDeath(self, isDeadStarted=False):
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.setVehicleState(self.id, _GUI_EVENT_ID.VEHICLE_DEAD, isDeadStarted)
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.VEHICLE_DESTROYED, vehicleId=self.id)
        self._removeInspire()
        bwfilter = self.filter
        if hasattr(bwfilter, 'velocityErrorCompensation'):
            bwfilter.velocityErrorCompensation = 100.0
        return

    def confirmTurretDetachment(self):
        self.__turretDetachmentConfirmed = True
        if not self.isTurretDetached:
            _logger.error('Vehicle::confirmTurretDetachment: Confirming turret detachment, though the turret is not detached')
        self.appearance.updateTurretVisibility()

    def drawEdge(self, forceSimpleEdge=False):
        self.appearance.highlighter.highlight(True, forceSimpleEdge)

    def removeEdge(self, forceSimpleEdge=False):
        self.appearance.highlighter.highlight(False, forceSimpleEdge)

    def addModel(self, model):
        super(Vehicle, self).addModel(model)
        highlighter = self.appearance.highlighter
        if highlighter.enabled:
            highlighter.highlight(True)

    def delModel(self, model):
        highlighter = self.appearance.highlighter
        hlEnabled = highlighter.enabled
        hlSimpleEdge = highlighter.isSimpleEdge
        if hlEnabled:
            highlighter.removeHighlight()
        super(Vehicle, self).delModel(model)
        if hlEnabled:
            highlighter.highlight(True, hlSimpleEdge)

    def notifyInputKeysDown(self, movementDir, rotationDir, handbrakeFired):
        self.filter.notifyInputKeysDown(movementDir, rotationDir)
        self.__handbrakeFired = handbrakeFired
        if self.appearance.detailedEngineState is not None:
            self.appearance.detailedEngineState.throttle = movementDir or rotationDir
        return

    def turnoffThrottle(self):
        if self.appearance.detailedEngineState is not None:
            self.appearance.detailedEngineState.throttle = 0
        return


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _stripVehCompDescrIfRoaming(vehCompDescr, lobbyContext=None):
    serverSettings = lobbyContext.getServerSettings() if lobbyContext is not None else None
    if serverSettings is not None:
        if serverSettings.roaming.isInRoaming():
            vehCompDescr = vehicles.stripCustomizationFromVehicleCompactDescr(vehCompDescr, True, True, False)[0]
    return vehCompDescr
