# Embedded file name: scripts/client/DetachedTurret.py
from AvatarInputHandler import mathUtils
import BigWorld
import Math
from debug_utils import LOG_ERROR, LOG_DEBUG
import material_kinds
from Math import Matrix
from ModelHitTester import SegmentCollisionResult
from VehicleEffects import DamageFromShotDecoder, TankComponentNames
from helpers.EffectMaterialCalculation import calcSurfaceMaterialNearPoint
from helpers.EffectsList import EffectsListPlayer, SoundStartParam, SpecialKeyPointNames
from helpers.bound_effects import ModelBoundEffects
from items import vehicles
from constants import SERVER_TICK_LENGTH
import FMOD
_MIN_COLLISION_SPEED = 3.5

class DetachedTurret(BigWorld.Entity):
    allTurrets = list()

    def __init__(self):
        self.__vehDescr = vehicles.VehicleDescr(compactDescr=self.vehicleCompDescr)
        self.filter = BigWorld.WGTurretFilter()
        self.__detachConfirmationTimer = SynchronousDetachment(self)
        self.__detachConfirmationTimer.onInit()
        self.__detachmentEffects = None
        self.__hitEffects = {TankComponentNames.TURRET: None,
         TankComponentNames.GUN: None}
        self.__reactors = []
        self.targetFullBounds = True
        self.targetCaps = [1]
        self.__isBeingPulledCallback = None
        return

    def reload(self):
        pass

    def prerequisites(self):
        prereqs = [self.__vehDescr.turret['models']['exploded'], self.__vehDescr.gun['models']['exploded']]
        prereqs += self.__vehDescr.prerequisites()
        return prereqs

    def onEnterWorld(self, prereqs):
        self.model = prereqs[self.__vehDescr.turret['models']['exploded']]
        self.__gunModel = prereqs[self.__vehDescr.gun['models']['exploded']]
        node = self.model.node('HP_gunJoint', Math.Matrix())
        node.attach(self.__gunModel)
        self.__detachConfirmationTimer.onEnterWorld()
        self.__vehDescr.keepPrereqs(prereqs)
        turretDescr = self.__vehDescr.turret
        if self.isUnderWater == 0:
            self.__detachmentEffects = _TurretDetachmentEffects(self.model, turretDescr['turretDetachmentEffects'], self.isCollidingWithWorld == 1)
            self.__reactors.append(self.__detachmentEffects)
        else:
            self.__detachmentEffects = None
        self.__hitEffects[TankComponentNames.TURRET] = turretHitEffects = _HitEffects(self.model)
        self.__hitEffects[TankComponentNames.GUN] = gunHitEffects = _HitEffects(self.__gunModel)
        self.__reactors.append(turretHitEffects)
        self.__reactors.append(gunHitEffects)
        self.__componentsDesc = (self.__vehDescr.turret, self.__vehDescr.gun)
        for desc in self.__componentsDesc:
            desc['hitTester'].loadBspModel()

        from helpers.CallbackDelayer import CallbackDelayer
        self.__isBeingPulledCallback = CallbackDelayer()
        self.__isBeingPulledCallback.delayCallback(self.__checkIsBeingPulled(), self.__checkIsBeingPulled)
        DetachedTurret.allTurrets.append(self)
        return

    def onLeaveWorld(self):
        DetachedTurret.allTurrets.remove(self)
        self.__detachConfirmationTimer.cancel()
        self.__detachConfirmationTimer = None
        for reactor in self.__reactors:
            if reactor is not None:
                reactor.destroy()

        self.__isBeingPulledCallback.destroy()
        self.__isBeingPulledCallback = None
        return

    def onStaticCollision(self, energy, point, normal):
        if self.__detachmentEffects is not None:
            surfaceMaterial = calcSurfaceMaterialNearPoint(point, normal, self.spaceID)
            effectIdx = surfaceMaterial.effectIdx
            groundEffect = True
            distToWater = BigWorld.wg_collideWater(self.position, surfaceMaterial.point)
            if distToWater != -1:
                vel = Math.Vector3(self.velocity).length
                if vel < _MIN_COLLISION_SPEED:
                    groundEffect = False
                effectIdx = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES['water']
            self.__detachmentEffects.notifyAboutCollision(energy, point, effectIdx, groundEffect, self.isUnderWater)
        return

    def showDamageFromShot(self, points, effectsIndex):
        maxHitEffectCode, decodedPoints = DamageFromShotDecoder.decodeHitPoints(points, self.__vehDescr)
        for shotPoint in decodedPoints:
            hitEffects = self.__hitEffects.get(shotPoint.componentName)
            if hitEffects is not None:
                hitEffects.showHit(shotPoint, effectsIndex)
            else:
                LOG_ERROR("Detached turret got hit into %s component, but it's impossible" % shotPoint.componentName)

        return

    def collideSegment(self, startPoint, endPoint, skipGun = False):
        res = None
        filterMethod = getattr(self.filter, 'segmentMayHitEntity', lambda : True)
        if not filterMethod(startPoint, endPoint, 0):
            return res
        else:
            modelsToCheck = (self.model,) if skipGun else (self.model, self.__gunModel)
            for model, desc in zip(modelsToCheck, self.__componentsDesc):
                toModel = Matrix(model.matrix)
                toModel.invert()
                collisions = desc['hitTester'].localHitTest(toModel.applyPoint(startPoint), toModel.applyPoint(endPoint))
                if collisions is None:
                    continue
                for dist, _, hitAngleCos, matKind in collisions:
                    if res is None or res.dist >= dist:
                        matInfo = desc['materials'].get(matKind)
                        res = SegmentCollisionResult(dist, hitAngleCos, matInfo.armor if matInfo is not None else 0)

            return res

    def set_isUnderWater(self, prev):
        if self.__detachmentEffects is not None:
            if self.isUnderWater:
                self.__detachmentEffects.stopEffects()
        return

    def set_isCollidingWithWorld(self, prev):
        pass

    def changeAppearanceVisibility(self, isVisible):
        self.model.visible = isVisible
        self.model.visibleAttachments = isVisible

    def __checkIsBeingPulled(self):
        if self.__detachmentEffects is not None:
            if self.isCollidingWithWorld and not self.isUnderWater and self.velocity.lengthSquared > 0.1:
                extent = Math.Matrix(self.model.bounds).applyVector(Math.Vector3(0.5, 0.5, 0.5)).length
                surfaceMaterial = calcSurfaceMaterialNearPoint(self.position, Math.Vector3(0, extent, 0), self.spaceID)
                self.__detachmentEffects.notifyAboutBeingPulled(True, surfaceMaterial.effectIdx)
                if surfaceMaterial.matKind == 0:
                    LOG_ERROR('calcSurfaceMaterialNearPoint failed to find the collision point')
            else:
                self.__detachmentEffects.notifyAboutBeingPulled(False, None)
        return SERVER_TICK_LENGTH


class _TurretDetachmentEffects(object):

    class State:
        FLYING = 0
        ON_GROUND = 1

    __EFFECT_NAMES = {State.FLYING: 'flight',
     State.ON_GROUND: 'flamingOnGround'}
    _MAX_COLLISION_ENERGY = 98.10000000000001
    _MIN_COLLISION_ENERGY = _MIN_COLLISION_SPEED ** 2 * 0.5
    _MIN_NORMALIZED_ENERGY = 0.1
    if FMOD.enabled:
        _DROP_ENERGY_PARAM = 'dropEnergy'

    def __init__(self, turretModel, detachmentEffectsDesc, onGround):
        self.__turretModel = turretModel
        self.__detachmentEffectsDesc = detachmentEffectsDesc
        self.__stateEffectListPlayer = None
        self.__pullEffectListPlayer = None
        startKeyPoint = SpecialKeyPointNames.START
        if onGround:
            self.__state = self.State.ON_GROUND
            startKeyPoint = SpecialKeyPointNames.STATIC
        else:
            self.__state = self.State.FLYING
        self.__playStateEffect(startKeyPoint)
        return

    def destroy(self):
        self.stopEffects()

    def __stopStateEffects(self):
        if self.__stateEffectListPlayer is not None:
            self.__stateEffectListPlayer.stop()
            self.__stateEffectListPlayer = None
        return

    def __stopPullEffects(self):
        if self.__pullEffectListPlayer is not None:
            self.__pullEffectListPlayer.stop()
            self.__pullEffectListPlayer = None
        return

    def stopEffects(self):
        self.__stopStateEffects()
        self.__stopPullEffects()

    def notifyAboutCollision(self, energy, collisionPoint, effectMaterialIdx, groundEffect, underWater):
        if groundEffect:
            stages, effectsList, _ = self.__detachmentEffectsDesc['collision'][effectMaterialIdx]
            normalizedEnergy = self.__normalizeEnergy(energy)
            dropEnergyParam = SoundStartParam(_TurretDetachmentEffects._DROP_ENERGY_PARAM, normalizedEnergy)
            BigWorld.player().terrainEffects.addNew(collisionPoint, effectsList, stages, None, soundParams=(dropEnergyParam,))
        if self.__state != self.State.ON_GROUND:
            self.__state = self.State.ON_GROUND
            if not underWater:
                self.__playStateEffect()
        return

    def notifyAboutBeingPulled(self, isPulled, effectMaterialIdx):
        if isPulled:
            if self.__pullEffectListPlayer is None or self.__pullEffectListPlayer.effectMaterialIdx != effectMaterialIdx:
                self.__playPullEffect(effectMaterialIdx)
        else:
            self.__stopPullEffects()
        return

    def __playPullEffect(self, effectMaterialIdx):
        self.__stopPullEffects()
        stages, effectsList, _ = self.__detachmentEffectsDesc['pull'][effectMaterialIdx]
        self.__pullEffectListPlayer = EffectsListPlayer(effectsList, stages)
        self.__pullEffectListPlayer.play(self.__turretModel, SpecialKeyPointNames.START)
        self.__pullEffectListPlayer.effectMaterialIdx = effectMaterialIdx

    def __playStateEffect(self, startKeyPoint = SpecialKeyPointNames.START):
        self.__stopStateEffects()
        effectName = _TurretDetachmentEffects.__EFFECT_NAMES[self.__state]
        stages, effectsList, _ = self.__detachmentEffectsDesc[effectName]
        self.__stateEffectListPlayer = EffectsListPlayer(effectsList, stages)
        self.__stateEffectListPlayer.play(self.__turretModel, startKeyPoint)

    def __normalizeEnergy(self, energy):
        minBound, maxBound = _TurretDetachmentEffects._MIN_COLLISION_ENERGY, _TurretDetachmentEffects._MAX_COLLISION_ENERGY
        clampedEnergy = mathUtils.clamp(minBound, maxBound, energy)
        t = (clampedEnergy - minBound) / (maxBound - minBound)
        return mathUtils.lerp(_TurretDetachmentEffects._MIN_NORMALIZED_ENERGY, 1.0, t)


class _HitEffects(ModelBoundEffects):

    def __init__(self, model):
        ModelBoundEffects.__init__(self, model)

    def showHit(self, shotPoint, effectsIndex):
        effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
        effectsTimeLine = effectsDescr[shotPoint.hitEffectGroup]
        self.addNew(shotPoint.matrix, effectsTimeLine.effectsList, effectsTimeLine.keyPoints)


class VehicleEnterTimer(object):
    isRunning = property(lambda self: self.__callbackId is not None)

    def __init__(self, vehicleID):
        self.__vehicleID = vehicleID
        self.__time = None
        self.__maxTime = 5 * SERVER_TICK_LENGTH
        self.__timeOut = SERVER_TICK_LENGTH
        self.__callbackId = None
        return

    def getVehicle(self):
        vehicle = BigWorld.entity(self.__vehicleID)
        if vehicle is None:
            return
        elif not vehicle.inWorld or not vehicle.isStarted:
            return
        elif not self._canAcceptVehicle(vehicle):
            return
        else:
            return vehicle

    def __startCallback(self):
        if not self.__callbackId is None:
            raise AssertionError
            self.__callbackId = self.__time < self.__maxTime and BigWorld.callback(self.__timeOut, self.__onCallback)
        else:
            self._onTimedOutTick()
        return

    def __onCallback(self):
        self.__callbackId = None
        self.__time += self.__timeOut
        progressRatio = self.__time / self.__maxTime
        self._onSearchProgress(progressRatio)
        v = self.getVehicle()
        if v is None:
            self.__startCallback()
        else:
            self._onCallbackTick(v)
        return

    def start(self):
        self.__time = 0.0
        self._onSearchProgress(0.0)
        v = self.getVehicle()
        if v is None:
            self.__startCallback()
        else:
            self._onDirectTick(v)
        return

    def cancel(self):
        if self.__callbackId is not None:
            BigWorld.cancelCallback(self.__callbackId)
            self.__callbackId = None
        return

    def _onDirectTick(self, vehicle):
        pass

    def _onCallbackTick(self, vehicle):
        pass

    def _onTimedOutTick(self):
        pass

    def _onSearchProgress(self, ratio):
        pass

    def _canAcceptVehicle(self, vehicle):
        return True


class SynchronousDetachment(VehicleEnterTimer):

    def __init__(self, turret):
        VehicleEnterTimer.__init__(self, turret.vehicleID)
        self.__turret = turret
        self.__entered = False
        self.__finished = False
        self.__acceptAnyVehicle = False

    def onInit(self):
        self.__finished = False
        self.__entered = False
        self.__acceptAnyVehicle = False
        self.start()

    def onEnterWorld(self):
        self.__entered = True
        self.__updateVisibility()

    def __updateVisibility(self):
        if self.__entered:
            self.__turret.changeAppearanceVisibility(self.__finished)

    def _onDirectTick(self, vehicle):
        turret = self.__turret
        if vehicle.isTurretDetachmentConfirmationNeeded:
            vehicle.confirmTurretDetachment()
            import traceback
            lines = [ l for l in traceback.format_stack() if '__init__' in l ]
            if not lines:
                raise Exception('SynchronousDetachment._directTick() requires to be called from __init__()')
            self.transferInputs(vehicle, turret)
            turret.filter.ignoreNextReset = True
        self.__finished = True
        self.__updateVisibility()

    def _onCallbackTick(self, vehicle):
        turret = self.__turret
        if vehicle.isTurretDetachmentConfirmationNeeded:
            vehicle.confirmTurretDetachment()
        self.__finished = True
        self.__updateVisibility()

    def _onTimedOutTick(self):
        self.__finished = True
        self.__updateVisibility()

    def _onSearchProgress(self, ratio):
        if ratio > 0.8:
            self.__acceptAnyVehicle = True

    def _canAcceptVehicle(self, vehicle):
        return self.__acceptAnyVehicle or vehicle.isTurretMarkedForDetachment

    @staticmethod
    def needSynchronousDetachment(turret):
        return True

    @staticmethod
    def transferInputs(vehicle, turret):
        vehicleDescriptor = vehicle.typeDescriptor
        hullOffset = vehicleDescriptor.chassis['hullPosition']
        turretMatrix = Math.Matrix()
        turretMatrix.setTranslate(hullOffset + vehicleDescriptor.hull['turretPositions'][0])
        turretMatrix.preMultiply(vehicle.appearance.turretMatrix)
        turret.filter.transferInputAsVehicle(vehicle.filter, turretMatrix)
