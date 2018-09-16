# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vehicle.py
import math
import random
import weakref
from collections import namedtuple
import BigWorld
import Math
import AreaDestructibles
import ArenaType
import BattleReplay
import DestructiblesCache
import SoundGroups
import TriggersManager
import constants
import nations
import physics_shared
from AvatarInputHandler.aih_constants import ShakeReason
from SoundGroups import CREW_GENDER_SWITCHES
from TriggersManager import TRIGGER_TYPE
from VehicleEffects import DamageFromShotDecoder
from constants import SPT_MATKIND
from constants import VEHICLE_HIT_EFFECT, VEHICLE_SIEGE_STATE
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_DEBUG, LOG_CODEPOINT_WARNING, LOG_CURRENT_EXCEPTION
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _GUI_EVENT_ID, VEHICLE_VIEW_STATE
from gun_rotation_shared import decodeGunAngles
from helpers import dependency
from helpers.EffectMaterialCalculation import calcSurfaceMaterialNearPoint
from helpers.EffectsList import SoundStartParam
from items import vehicles, sabaton_crew, tankmen
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_NAMES, EFFECT_MATERIALS
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from vehicle_systems import appearance_cache
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes
from vehicle_systems.stricted_loading import loadingPriority
from soft_exception import SoftException
LOW_ENERGY_COLLISION_D = 0.3
HIGH_ENERGY_COLLISION_D = 0.6
_g_waitingVehicle = dict()
_VALKYRIE_SOUND_MODES = {(6, 205): 'valkyrie1',
 (6, 206): 'valkyrie2'}
_GIANLUIGI_BUFFON_VEH_NAME = 'italy:It13_Progetto_M35_mod_46'

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

class Vehicle(BigWorld.Entity):
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

    def getBounds(self, partIdx):
        return self.appearance.getBounds(partIdx) if self.appearance is not None else (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0), 0)

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
        self.__isEnteringWorld = False
        self.__turretDetachmentConfirmed = False
        self.__speedInfo = _VehicleSpeedProvider()
        self.assembler = None
        _g_waitingVehicle[self.id] = weakref.ref(self)
        self.respawnCompactDescr = None
        self.respawnOutfitCompactDescr = None
        self.__prevStunInfo = 0.0
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
            self.appearance, _, prereqs = appearance_cache.createAppearance(self.id, self.typeDescriptor, self.health, self.isCrewActive, self.isTurretDetached, outfitDescr, forceReloading)
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
        if vehicleRef is not None:
            vehicle = vehicleRef()
            if vehicle is not None:
                vehicle.respawnCompactDescr = compactDescr
                vehicle.respawnOutfitCompactDescr = outfitCompactDescr
                if not BigWorld.entities.get(vID):
                    LOG_ERROR('respawn vehicle: Vehicle ref is not None but entity does not exist anymore. Skip wg_respawn ')
                else:
                    try:
                        vehicle.wg_respawn()
                    except Exception:
                        LOG_ERROR('respawn vehicle: Vehicle ref is not None but failed to call respawn: ', vID)

        return

    def onEnterWorld(self, prereqs):
        self.__prereqs = prereqs
        self.__isEnteringWorld = True
        self.__prevDamageStickers = frozenset()
        self.__prevPublicStateModifiers = frozenset()
        self.targetFullBounds = True
        player = BigWorld.player()
        player.vehicle_onEnterWorld(self)
        if self.isPlayerVehicle:
            self.cell.sendStateToOwnClient()
        player.initSpace()
        self.__isEnteringWorld = False
        if self.respawnCompactDescr:
            LOG_DEBUG('respawn compact descr is still valid, request reloading of tank resources')
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
            maxHitEffectCode, decodedPoints, maxDamagedComponent = DamageFromShotDecoder.decodeHitPoints(points, self.appearance.collisions)
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
            for shotPoint in decodedPoints:
                showFullscreenEffs = self.isPlayerVehicle and self.isAlive()
                keyPoints, effects, _ = effectsDescr[shotPoint.hitEffectGroup]
                self.appearance.boundEffects.addNewToNode(shotPoint.componentName, shotPoint.matrix, effects, keyPoints, isPlayerVehicle=self.isPlayerVehicle, showShockWave=showFullscreenEffs, showFlashBang=showFullscreenEffs, entity_id=self.id, damageFactor=damageFactor, attackerID=attackerID, hitdir=firstHitDir)

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

    def set_damageStickers(self, prev=None):
        if self.isStarted:
            prev = self.__prevDamageStickers
            curr = frozenset(self.damageStickers)
            self.__prevDamageStickers = curr
            for sticker in prev.difference(curr):
                self.appearance.removeDamageSticker(sticker)

            for sticker in curr.difference(prev):
                self.appearance.addDamageSticker(sticker, *DamageFromShotDecoder.decodeSegment(sticker, self.appearance.collisions))

    def set_publicStateModifiers(self, prev=None):
        if self.isStarted:
            prev = self.__prevPublicStateModifiers
            curr = frozenset(self.publicStateModifiers)
            self.__prevPublicStateModifiers = curr
            self.__updateModifiers(curr.difference(prev), prev.difference(curr))
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

    def set_inspiringEffect(self, prev=None):
        if not self.isStarted or self.inspiringEffect == prev:
            return
        else:
            data = self.inspiringEffect
            componentSystem = self.guiSessionProvider.arenaVisitor.getComponentSystem()
            if componentSystem is not None:
                equipmentComp = getattr(componentSystem, 'arenaEquipmentComponent', None)
                if equipmentComp is not None:
                    if data:
                        equipmentComp.updateInspiringSource(self.id, data.startTime, data.endTime, data.inactivationDelay, data.radius)
                    else:
                        equipmentComp.updateInspiringSource(self.id, None, None, None, None)
            return

    def set_inspired(self, prev=None):
        if not self.isStarted or self.inspired == prev:
            return
        else:
            data = self.inspired
            componentSystem = self.guiSessionProvider.arenaVisitor.getComponentSystem()
            if componentSystem is not None:
                equipmentComp = getattr(componentSystem, 'arenaEquipmentComponent', None)
                if equipmentComp is not None:
                    if data is not None:
                        equipmentComp.updateInspired(self.id, data.startTime, data.endTime, data.inactivationStartTime, data.inactivationEndTime)
                    else:
                        equipmentComp.updateInspired(self.id, None, None, None, None)
            return

    def __removeInspire(self):
        if self.inspired or self.inspiringEffect:
            componentSystem = self.guiSessionProvider.arenaVisitor.getComponentSystem()
            if componentSystem is not None:
                equipmentComp = getattr(componentSystem, 'arenaEquipmentComponent', None)
                if equipmentComp is not None:
                    equipmentComp.removeInspire(self.id)
        return

    def set_isSpeedCapturing(self, prev=None):
        LOG_DEBUG('set_isSpeedCapturing ', self.isSpeedCapturing)
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidatePassiveEngineering(self.id, (True, self.isSpeedCapturing))
        return

    def set_isBlockingCapture(self, prev=None):
        LOG_DEBUG('set_isBlockingCapture ', self.isBlockingCapture)
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidatePassiveEngineering(self.id, (False, self.isBlockingCapture))
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
        LOG_DEBUG('Set stun info(curr,~ prev): ', self.stunInfo, prev)
        self.updateStunInfo()

    def updateStunInfo(self):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None or self.__prevStunInfo == self.stunInfo:
            return
        else:
            self.__prevStunInfo = self.stunInfo
            isAttachedVehicle = self.id == attachedVehicle.id
            if self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                stunDuration = self.stunInfo - BigWorld.serverTime() if self.stunInfo else 0.0
                if isAttachedVehicle:
                    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.STUN, stunDuration)
                if not self.isPlayerVehicle:
                    ctrl = self.guiSessionProvider.shared.feedback
                    if ctrl is not None:
                        ctrl.invalidateStun(self.id, stunDuration)
            else:
                LOG_WARNING('Stun features is disabled!')
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

    def onStaticCollision(self, energy, point, normal, miscFlags, damageHull, damageLeftTrack, damageRightTrack, destrEffectIdx, destrMaxHealth):
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
            if isTrackCollision:
                damageFactor = damageLeftTrack if damageLeftTrack > damageRightTrack else damageRightTrack
            else:
                damageFactor = damageHull
            if not isSptCollision:
                surfaceMaterial = calcSurfaceMaterialNearPoint(hitPoint, normal, self.spaceID)
                hitPoint, surfNormal, matKind, effectIdx = surfaceMaterial
            else:
                effectIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES['wood']
            if matKind != 0:
                self.__showStaticCollisionEffect(energy, effectIdx, hitPoint, surfNormal, isTrackCollision, damageFactor * 100.0)
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
        if self.typeDescriptor is not None and self.typeDescriptor.hasSiegeMode:
            self.typeDescriptor.onSiegeStateChanged(newState)
            if self.isStarted:
                self.appearance.onSiegeStateChanged(newState)
            if self.isPlayerVehicle:
                inputHandler = BigWorld.player().inputHandler
                inputHandler.siegeModeControl.notifySiegeModeChanged(self, newState, timeToNextMode)
        else:
            LOG_ERROR('Wrong usage! Should be called only on vehicle with validtypeDescriptor and siege mode')
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
            LOG_DEBUG('respawn compact descr is still valid, request reloading of tank resources ', self.id)
            BigWorld.callback(0.0, lambda : Vehicle.respawnVehicle(self.id, self.respawnCompactDescr))
        return

    def refreshNationalVoice(self):
        player = BigWorld.player()
        if self is not player.getVehicleAttached():
            return
        else:
            crewGroup = 0
            arena = getattr(player, 'arena', None)
            if arena is not None:
                crewGroup = arena.vehicles[self.id]['crewGroup']
            vehicleTypeID = self.typeDescriptor.type.id
            nationID, _ = vehicleTypeID
            LOG_DEBUG("Refreshing current vehicle's national voices", nationID)
            groupID, isFemaleCrewCommander, isPremium = tankmen.unpackCrewParams(crewGroup)
            if nationID == nations.INDICES['sweden'] and tankmen.hasTagInTankmenGroup(nationID, groupID, isPremium, sabaton_crew.SABATON_VEH_NAME):
                SoundGroups.g_instance.setSwitch(CREW_GENDER_SWITCHES.GROUP, CREW_GENDER_SWITCHES.MALE)
                SoundGroups.g_instance.soundModes.setMode('sabaton')
                return
            if nationID == nations.INDICES['italy'] and tankmen.hasTagInTankmenGroup(nationID, groupID, isPremium, _GIANLUIGI_BUFFON_VEH_NAME):
                SoundGroups.g_instance.setSwitch(CREW_GENDER_SWITCHES.GROUP, CREW_GENDER_SWITCHES.MALE)
                SoundGroups.g_instance.soundModes.setMode('buffon')
                return
            if vehicleTypeID in _VALKYRIE_SOUND_MODES and self.id == player.playerVehicleID:
                SoundGroups.g_instance.soundModes.setMode(_VALKYRIE_SOUND_MODES[vehicleTypeID])
                return
            genderSwitch = CREW_GENDER_SWITCHES.DEFAULT
            if SoundGroups.g_instance.soundModes.currentNationalPreset[1]:
                if isFemaleCrewCommander:
                    genderSwitch = CREW_GENDER_SWITCHES.FEMALE
            nation = nations.NAMES[nationID]
            SoundGroups.g_instance.soundModes.setCurrentNation(nation, genderSwitch)
            return

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
        physics = BigWorld.WGVehiclePhysics()
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
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.setVehicleState(self.id, _GUI_EVENT_ID.VEHICLE_DEAD, isDeadStarted)
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.VEHICLE_DESTROYED, vehicleId=self.id)
        self.__removeInspire()
        bwfilter = self.filter
        if hasattr(bwfilter, 'velocityErrorCompensation'):
            bwfilter.velocityErrorCompensation = 100.0
        return

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
            highlighter.highlight(True)

    def delModel(self, model):
        highlighter = self.appearance.highlighter
        hlEnabled = highlighter.enabled
        if hlEnabled:
            highlighter.highlight(False)
        super(Vehicle, self).delModel(model)
        if hlEnabled:
            highlighter.highlight(True)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _stripVehCompDescrIfRoaming(vehCompDescr, lobbyContext=None):
    serverSettings = lobbyContext.getServerSettings() if lobbyContext is not None else None
    if serverSettings is not None:
        if serverSettings.roaming.isInRoaming():
            vehCompDescr = vehicles.stripCustomizationFromVehicleCompactDescr(vehCompDescr, True, True, False)[0]
    return vehCompDescr
