# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleAppearance.py
import BigWorld
import Math
from debug_utils import *
import weakref
from VehicleEffects import VehicleTrailEffects, VehicleExhaustEffects
from constants import IS_DEVELOPMENT, ARENA_GUI_TYPE, VEHICLE_PHYSICS_MODE
import constants
from OcclusionDecal import OcclusionDecal
from ShadowForwardDecal import ShadowForwardDecal
from helpers.CallbackDelayer import CallbackDelayer
from helpers import bound_effects, DecalMap, isPlayerAvatar, newFakeModel
from helpers.EffectsList import EffectsListPlayer, SpecialKeyPointNames
import items.vehicles
import random
import math
import time
from Event import Event
from functools import partial
import material_kinds
from VehicleStickers import VehicleStickers
import AuxiliaryFx
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from Vibroeffects.ControllersManager import ControllersManager as VibrationControllersManager
from LightFx.LightControllersManager import LightControllersManager as LightFxControllersManager
import LightFx.LightManager
import BattleReplay
from VehicleEffects import TankComponentNames
from VehicleEffects import RepaintParams
from vehicle_systems.assembly_utility import ComponentSystem, ComponentDescriptor
_ENABLE_VEHICLE_VALIDATION = False
_VEHICLE_DISAPPEAR_TIME = 0.2
_VEHICLE_APPEAR_TIME = 0.2
_ROOT_NODE_NAME = 'V'
_GUN_RECOIL_NODE_NAME = 'G'
_PERIODIC_TIME = 0.25
_PERIODIC_TIME_ENGINE = 0.1
_LOD_DISTANCE_EXHAUST = 200.0
_LOD_DISTANCE_TRAIL_PARTICLES = 100.0
_MOVE_THROUGH_WATER_SOUND = '/vehicles/tanks/water'
_CAMOUFLAGE_MIN_INTENSITY = 1.0
_PITCH_SWINGING_MODIFIERS = (0.9,
 1.88,
 0.3,
 4.0,
 1.0,
 1.0)
_MIN_DEPTH_FOR_HEAVY_SPLASH = 0.5
_ALLOW_LAMP_LIGHTS = False
MAX_DISTANCE = 500
_MATKIND_COUNT = 3

class VehicleAppearance(CallbackDelayer, ComponentSystem):
    gunRecoil = property(lambda self: self.__gunRecoil)
    fashion = property(lambda self: self.__fashion)
    terrainMatKind = property(lambda self: self.__currTerrainMatKind)
    isInWater = property(lambda self: self.__isInWater)
    isUnderwater = property(lambda self: self.__isUnderWater)
    waterHeight = property(lambda self: self.__waterHeight)
    destroyedState = property(lambda self: self.__currentDamageState.model == 'destroyed')
    frameTimeStamp = 0
    engineMode = property(lambda self: self.__engineMode)
    rightTrackScroll = property(lambda self: self.__rightTrackScroll)
    leftTrackScroll = property(lambda self: self.__leftTrackScroll)
    gunSound = property(lambda self: self.__gunSound)
    isPillbox = property(lambda self: self.__isPillbox)
    rpm = property(lambda self: self.__rpm)
    gear = property(lambda self: self.__gear)
    detailedEngineState = ComponentDescriptor()
    engineAudition = ComponentDescriptor()
    trackCrashAudition = ComponentDescriptor()
    customEffectManager = ComponentDescriptor()

    def __init__(self):
        CallbackDelayer.__init__(self)
        ComponentSystem.__init__(self)
        self.modelsDesc = {'chassis': {'model': None,
                     'state': None,
                     'boundEffects': None,
                     '_visibility': (True, True),
                     '_fetchedModel': None,
                     '_fetchedState': None,
                     '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.chassis['models'][state]},
         'hull': {'model': None,
                  'state': None,
                  'boundEffects': None,
                  '_visibility': (True, True),
                  '_node': None,
                  '_fetchedModel': None,
                  '_fetchedState': None,
                  '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.hull['models'][state]},
         'turret': {'model': None,
                    'state': None,
                    'boundEffects': None,
                    '_visibility': (True, True),
                    '_node': None,
                    '_fetchedModel': None,
                    '_fetchedState': None,
                    '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.turret['models'][state]},
         'gun': {'model': None,
                 'state': None,
                 'boundEffects': None,
                 '_visibility': (True, True),
                 '_fetchedModel': None,
                 '_fetchedState': None,
                 '_node': None,
                 '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.gun['models'][state]}}
        self.turretMatrix = Math.WGAdaptiveMatrixProvider()
        self.gunMatrix = Math.WGAdaptiveMatrixProvider()
        self.__vehicle = None
        self.__filter = None
        self.__originalFilter = None
        self.__waterHeight = -1.0
        self.__isInWater = False
        self.__isUnderWater = False
        self.__splashedWater = False
        self.__vibrationsCtrl = None
        self.__lightFxCtrl = None
        self.__auxiliaryFxCtrl = None
        self.__fashion = None
        self.__crashedTracksCtrl = None
        self.__gunRecoil = None
        self.__currentDamageState = VehicleDamageState()
        self.__loadingProgress = 0
        self.__invalidateLoading = False
        self.__effectsPlayer = None
        self.__engineMode = (0, 0)
        self.__swingMoveFlags = 0
        self.__currTerrainMatKind = [-1] * _MATKIND_COUNT
        self.__periodicTimerID = None
        self.__periodicTimerIDEngine = None
        self.__trailEffects = None
        self.__exhaustEffects = None
        self.__customEffectManager = None
        self.__leftLightRotMat = None
        self.__rightLightRotMat = None
        self.__leftFrontLight = None
        self.__rightFrontLight = None
        self.__prevVelocity = None
        self.__prevTime = None
        self.__isPillbox = False
        self.__chassisOcclusionDecal = OcclusionDecal()
        self.__chassisShadowForwardDecal = ShadowForwardDecal()
        self.__splodge = None
        self.__vehicleStickers = None
        self.onModelChanged = Event()
        self.__speedInfo = Math.Vector4(0.0, 0.0, 0.0, 0.0)
        self.__wasOnSoftTerrain = False
        self.__vehicleMatrixProv = None
        self.__typeDesc = None
        self.__leftTrackScroll = 0.0
        self.__rightTrackScroll = 0.0
        self.__distanceFromPlayer = 0.0
        self.__gear = 127
        self.__rpm = 0.0
        return

    def prerequisites(self, vehicle):
        self.__currentDamageState.update(vehicle.health, vehicle.isCrewActive, self.__isUnderWater)
        out = []
        for desc in self.modelsDesc.itervalues():
            part = desc['_stateFunc'](vehicle, self.__currentDamageState.model)
            out.append(part)

        vDesc = vehicle.typeDescriptor
        out.append(vDesc.type.camouflageExclusionMask)
        splineDesc = vDesc.chassis['splineDesc']
        if splineDesc is not None:
            out.append(splineDesc['segmentModelLeft'])
            out.append(splineDesc['segmentModelRight'])
            if splineDesc['segment2ModelLeft'] is not None:
                out.append(splineDesc['segment2ModelLeft'])
            if splineDesc['segment2ModelRight'] is not None:
                out.append(splineDesc['segment2ModelRight'])
        customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
        camouflageParams = self.__getCamouflageParams(vehicle)
        if camouflageParams is not None and customization is not None:
            camouflageId = camouflageParams[0]
            camouflageDesc = customization['camouflages'].get(camouflageId)
            if camouflageDesc is not None and camouflageDesc['texture'] != '':
                out.append(camouflageDesc['texture'])
                for tgDesc in (vDesc.turret, vDesc.gun):
                    exclMask = tgDesc.get('camouflageExclusionMask')
                    if exclMask is not None and exclMask != '':
                        out.append(exclMask)

        return out

    def destroy(self):
        if self.__vehicle is None:
            return
        else:
            ComponentSystem.destroy(self)
            CallbackDelayer.destroy(self)
            vehicle = self.__vehicle
            vehicle.removeEdge()
            self.__vehicle = None
            self.__vehicleMatrixProv = None
            self.__typeDesc = None
            if IS_DEVELOPMENT and _ENABLE_VEHICLE_VALIDATION and self.__validateCallbackId is not None:
                BigWorld.cancelCallback(self.__validateCallbackId)
                self.__validateCallbackId = None
            if self.__vibrationsCtrl is not None:
                self.__vibrationsCtrl.destroy()
                self.__vibrationsCtrl = None
            if self.__lightFxCtrl is not None:
                self.__lightFxCtrl.destroy()
                self.__lightFxCtrl = None
            if self.__auxiliaryFxCtrl is not None:
                self.__auxiliaryFxCtrl.destroy()
                self.__auxiliaryFxCtrl = None
            self.__stopEffects()
            if vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
                if self.__trailEffects is not None:
                    self.__trailEffects.destroy()
                    self.__trailEffects = None
                if self.__exhaustEffects is not None:
                    self.__exhaustEffects.destroy()
                    self.__exhaustEffects = None
            vehicle.stopHornSound(True)
            for desc in self.modelsDesc.iteritems():
                boundEffects = desc[1].get('boundEffects', None)
                if boundEffects is not None:
                    boundEffects.destroy()

            if vehicle.isPlayerVehicle:
                player = BigWorld.player()
                if player.inputHandler is not None:
                    arcadeCamera = player.inputHandler.ctrls['arcade'].camera
                    if arcadeCamera is not None:
                        arcadeCamera.removeVehicleToCollideWith(self)
            vehicle.model.delMotor(vehicle.model.motors[0])
            self.__filter = None
            vehicle.filter = self.__originalFilter
            self.__originalFilter = None
            self.__vehicleStickers = None
            self.__removeHavok()
            self.modelsDesc = None
            self.onModelChanged = None
            id = getattr(self, '_VehicleAppearance__stippleCallbackID', None)
            if id is not None:
                BigWorld.cancelCallback(id)
                self.__stippleCallbackID = None
            if self.__periodicTimerID is not None:
                BigWorld.cancelCallback(self.__periodicTimerID)
                self.__periodicTimerID = None
            if self.__periodicTimerIDEngine is not None:
                BigWorld.cancelCallback(self.__periodicTimerIDEngine)
                self.__periodicTimerIDEngine = None
            self.__crashedTracksCtrl.destroy()
            self.__crashedTracksCtrl = None
            self.__chassisOcclusionDecal.destroy()
            self.__chassisOcclusionDecal = None
            self.__chassisShadowForwardDecal.destroy()
            self.__chassisShadowForwardDecal = None
            return

    def preStart(self, typeDesc, newPhysic):
        self.__typeDesc = typeDesc
        self.__isPillbox = 'pillbox' in self.__typeDesc.type.tags
        if self.__isPillbox:
            self.__filter = BigWorld.WGPillboxFilter()
        else:
            self.__filter = BigWorld.WGVehicleFilter()
            self.__filter.vehicleWidth = typeDesc.chassis['topRightCarryingPoint'][0] * 2
            self.__filter.maxMove = typeDesc.physics['speedLimits'][0] * 2.0
            self.__filter.vehicleMinNormalY = typeDesc.physics['minPlaneNormalY']
            for p1, p2, p3 in typeDesc.physics['carryingTriangles']:
                self.__filter.addTriangle((p1[0], 0, p1[1]), (p2[0], 0, p2[1]), (p3[0], 0, p3[1]))

        self.setupGunMatrixTargets()
        self.__createGunRecoil()
        self.__fashion = BigWorld.WGVehicleFashion(False, 1.0, newPhysic)

    def start(self, vehicle, prereqs=None):
        self.__vehicle = vehicle
        player = BigWorld.player()
        modelsDesc = self.modelsDesc
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
            self.__createExhaust()
        if prereqs is None:
            self.__typeDesc.chassis['hitTester'].loadBspModel()
            self.__typeDesc.hull['hitTester'].loadBspModel()
            self.__typeDesc.turret['hitTester'].loadBspModel()
        if not self.__isPillbox:
            self.__filter.isStrafing = vehicle.isStrafing
            self.__filter.vehicleCollisionCallback = player.handleVehicleCollidedVehicle
        self.__originalFilter = vehicle.filter
        vehicle.filter = self.__filter
        enableNewPhysics = vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED
        vehicle.filter.enableNewPhysics(enableNewPhysics)
        if vehicle.isPlayerVehicle:
            vehicle.filter.enableStabilisedMatrix(True)
        self.__createStickers(prereqs)
        _setupVehicleFashion(self, self.__fashion, self.__vehicle)
        currentModelState = self.__currentDamageState.model
        boundEffectNodes = {'chassis': '',
         'hull': '',
         'turret': '',
         'gun': 'Gun'}
        for desc, boundEffectNode in zip(modelsDesc.itervalues(), boundEffectNodes.itervalues()):
            modelName = desc['_stateFunc'](vehicle, currentModelState)
            if prereqs is not None:
                try:
                    desc['model'] = prereqs[modelName]
                    desc['state'] = currentModelState
                except:
                    LOG_ERROR("can't load model <%s> from prerequisites." % modelName)

                if desc['model'] is None:
                    modelName = desc['_stateFunc'](vehicle, 'undamaged')
                    try:
                        desc['model'] = BigWorld.Model(modelName)
                        desc['state'] = 'undamaged'
                    except:
                        LOG_ERROR("can't load model <%s> for tank state %s - no model was loaded from prerequisites, direct load of the model has been failed" % (modelName, self.__currentDamageState.model))

            else:
                try:
                    desc['model'] = BigWorld.Model(modelName)
                    desc['state'] = currentModelState
                except:
                    LOG_ERROR("can't load model <%s> - prerequisites were empty, direct load of the model has been failed" % modelName)

            desc['model'].outsideOnly = 1
            desc['model'].wg_isPlayer = vehicle.isPlayerVehicle
            if desc.has_key('boundEffects'):
                desc['boundEffects'] = bound_effects.ModelBoundEffects(desc['model'], boundEffectNode)

        self.__loadingProgress = len(modelsDesc)
        self.__setupModels(True)
        if not VehicleDamageState.isDamagedModel(modelsDesc['chassis']['state']):
            setupSplineTracks(self.__fashion, self.__vehicle.typeDescriptor, modelsDesc['chassis']['model'], prereqs)
        if self.__currentDamageState.effect is not None:
            self.__playEffect(self.__currentDamageState.effect, SpecialKeyPointNames.STATIC)
        self.__crashedTracksCtrl = _CrashedTrackController(vehicle, self)
        if self.__invalidateLoading:
            self.__invalidateLoading = False
            self.__fetchModels(self.__currentDamageState.model)
        if vehicle.isAlive() and self.__vehicle.isPlayerVehicle:
            self.__vibrationsCtrl = VibrationControllersManager()
            if LightFx.LightManager.g_instance is not None and LightFx.LightManager.g_instance.isEnabled():
                self.__lightFxCtrl = LightFxControllersManager(self.__vehicle)
            if AuxiliaryFx.g_instance is not None:
                self.__auxiliaryFxCtrl = AuxiliaryFx.g_instance.createFxController(self.__vehicle)
        vehicle.model.stipple = True
        self.__vehicleMatrixProv = vehicle.model.matrix
        period = _VEHICLE_APPEAR_TIME
        if BattleReplay.isPlaying():
            vehicle.model.stipple = False
            if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
                period = 0
        self.__stippleCallbackID = BigWorld.callback(period, self.__disableStipple)
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
            self.__setupTrailParticles()
        return

    def startSystems(self):
        self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME, self.__onPeriodicTimer)
        if self.__vehicle.isPlayerVehicle:
            self.delayCallback(_PERIODIC_TIME_ENGINE, self.__onPeriodicTimerEngine)
        self.detailedEngineState.start(self.__vehicle)

    def set_gear(self, gear):
        self.__gear = gear

    def set_normalisedRPM(self, rpm):
        self.__rpm = rpm

    def getGunSoundObj(self):
        return self.engineAudition.getGunSoundObj()

    def showStickers(self, show):
        self.__vehicleStickers.show = show

    def updateTurretVisibility(self):
        if self.__vehicle is not None:
            isTurretOK = not self.__vehicle.isTurretDetached
            self.changeVisibility('turret', isTurretOK, isTurretOK)
            self.changeVisibility('gun', isTurretOK, isTurretOK)
        return

    def changeVisibility(self, modelName, modelVisible, attachmentsVisible):
        desc = self.modelsDesc.get(modelName, None)
        if desc is None:
            LOG_ERROR("invalid model's description name <%s>." % modelName)
        desc['model'].visible = modelVisible
        desc['model'].visibleAttachments = attachmentsVisible
        desc['_visibility'] = (modelVisible, attachmentsVisible)
        if modelName == 'chassis':
            self.__crashedTracksCtrl.setVisible(modelVisible)
        return

    def changeDrawPassVisibility(self, modelName, drawFlags, modelVisible, attachmentsVisible):
        desc = self.modelsDesc.get(modelName, None)
        if desc is None:
            LOG_ERROR("invalid model's description name <%s>." % modelName)
        desc['model'].visibleDrawPass = drawFlags
        desc['model'].visibleAttachments = attachmentsVisible
        desc['_visibility'] = (modelVisible, attachmentsVisible)
        if modelName == 'chassis':
            self.__crashedTracksCtrl.setVisible(modelVisible)
        return

    def onVehicleHealthChanged(self):
        vehicle = self.__vehicle
        if not vehicle.isAlive():
            vehicle.removeEdge()
            stopEngine = stopMovement = True
            if vehicle.health > 0:
                self.changeEngineMode((0, 0))
            if self.engineAudition is not None:
                self.engineAudition.stopSounds(stopEngine, stopMovement)
            if self.trackCrashAudition is not None:
                self.trackCrashAudition.destroy()
                self.trackCrashAudition = None
        currentState = self.__currentDamageState
        previousState = currentState.state
        currentState.update(vehicle.health, vehicle.isCrewActive, self.__isUnderWater)
        if previousState != currentState.state:
            if self.__loadingProgress == len(self.modelsDesc):
                if currentState.effect is not None:
                    self.__playEffect(currentState.effect)
                if vehicle.health <= 0:
                    BigWorld.player().inputHandler.onVehicleDeath(vehicle, currentState.state == 'ammoBayExplosion')
                if currentState.model != self.modelsDesc['chassis']['state']:
                    if VehicleDamageState.isExplodedModel(currentState.model):
                        self.__havokExplosion()
                    self.__fetchModels(currentState.model)
            elif currentState.model != self.modelsDesc['chassis']['state']:
                self.__invalidateLoading = True
        return

    def showAmmoBayEffect(self, mode, fireballVolume):
        if mode == constants.AMMOBAY_DESTRUCTION_MODE.POWDER_BURN_OFF:
            self.__playEffect('ammoBayBurnOff')
            return
        volumes = items.vehicles.g_cache.commonConfig['miscParams']['explosionCandleVolumes']
        candleIdx = 0
        for idx, volume in enumerate(volumes):
            if volume >= fireballVolume:
                break
            candleIdx = idx + 1

        if candleIdx > 0:
            self.__playEffect('explosionCandle%d' % candleIdx)
        else:
            self.__playEffect('explosion')

    def changeEngineMode(self, mode, forceSwinging=False):
        self.__engineMode = mode
        self.detailedEngineState.setMode(self.__engineMode[0])
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
            self.__updateExhaust()
            if forceSwinging:
                flags = mode[1]
                prevFlags = self.__swingMoveFlags
                fashion = self.fashion
                moveMask = 3
                rotMask = 12
                if flags & moveMask ^ prevFlags & moveMask:
                    swingPeriod = 2.0
                    if flags & 1:
                        fashion.accelSwingingDirection = -1
                    elif flags & 2:
                        fashion.accelSwingingDirection = 1
                    else:
                        fashion.accelSwingingDirection = 0
                elif not flags & moveMask and flags & rotMask ^ prevFlags & rotMask:
                    swingPeriod = 1.0
                    fashion.accelSwingingDirection = 0
                else:
                    swingPeriod = 0.0
                if swingPeriod > fashion.accelSwingingPeriod:
                    fashion.accelSwingingPeriod = swingPeriod
                self.__swingMoveFlags = flags
        return None if BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress else None

    def stopSwinging(self):
        self.fashion.accelSwingingPeriod = 0.0

    def removeDamageSticker(self, code):
        self.__vehicleStickers.delDamageSticker(code)

    def addDamageSticker(self, code, componentName, stickerID, segStart, segEnd):
        self.__vehicleStickers.addDamageSticker(code, componentName, stickerID, segStart, segEnd)

    def receiveShotImpulse(self, dir, impulse):
        if BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        if not VehicleDamageState.isDamagedModel(self.modelsDesc['chassis']['state']):
            self.__fashion.receiveShotImpulse(dir, impulse)
            self.__crashedTracksCtrl.receiveShotImpulse(dir, impulse)

    def addCrashedTrack(self, isLeft):
        self.__crashedTracksCtrl.addTrack(isLeft)
        if not self.__vehicle.isEnteringWorld and self.trackCrashAudition:
            self.trackCrashAudition.playCrashSound(isLeft)

    def delCrashedTrack(self, isLeft):
        self.__crashedTracksCtrl.delTrack(isLeft)
        if not self.__vehicle.isEnteringWorld and self.trackCrashAudition and self.__vehicle.isPlayerVehicle:
            self.trackCrashAudition.playCrashSound(isLeft, True)

    def __fetchModels(self, modelState):
        if self.__loadingProgress != len(self.modelsDesc):
            raise Exception('Tried to break model loading process')
        self.__loadingProgress = 0
        for name, desc in self.modelsDesc.iteritems():
            desc['_fetchedState'] = modelState
            BigWorld.fetchModel(desc['_stateFunc'](self.__vehicle, modelState), partial(self.__onModelLoaded, name, modelState, self.modelsDesc))

    def __attemptToSetupModels(self):
        self.__loadingProgress += 1
        if self.__loadingProgress == len(self.modelsDesc):
            if self.__invalidateLoading:
                self.__invalidateLoading = False
                self.__fetchModels(self.__currentDamageState.model)
            else:
                self.__setupModels()

    def __setupModels(self, isFirstInit=False):
        vehicle = self.__vehicle
        modelsDesc = self.modelsDesc
        chassis = modelsDesc['chassis']
        hull = modelsDesc['hull']
        turret = modelsDesc['turret']
        gun = modelsDesc['gun']
        if not isFirstInit:
            self.__detachStickers()
            if MAX_DISTANCE > 0:
                self.__detachSplodge(self.__splodge)
            self.__removeHavok()
            self.__chassisOcclusionDecal.detach()
            self.__chassisShadowForwardDecal.detach()
            self.__destroyLampLights()
            if hasattr(gun['model'], 'wg_gunRecoil'):
                delattr(gun['model'], 'wg_gunRecoil')
            self.__gunFireNode = None
            if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
                self.__customEffectManager.stop()
            else:
                self.__attachExhaust(False)
                self.__trailEffects.stopEffects()
            self.__crashedTracksCtrl.reset()
            chassis['model'].stopSoundsOnDestroy = False
            hull['model'].stopSoundsOnDestroy = False
            turret['model'].stopSoundsOnDestroy = False
            hull['_node'].detach(hull['model'])
            turret['_node'].detach(turret['model'])
            gun['_node'].detach(gun['model'])
            chassis['model'] = chassis['_fetchedModel']
            hull['model'] = hull['_fetchedModel']
            turret['model'] = turret['_fetchedModel']
            gun['model'] = gun['_fetchedModel']
            chassis['state'] = chassis['_fetchedState']
            hull['state'] = hull['_fetchedState']
            turret['state'] = turret['_fetchedState']
            gun['state'] = gun['_fetchedState']
            if hasattr(vehicle.model, 'wg_fashion'):
                delattr(vehicle.model, 'wg_fashion')
        vehicle.model = None
        vehicle.model = chassis['model']
        vehicle.model.delMotor(vehicle.model.motors[0])
        matrix = vehicle.matrix
        matrix.notModel = True
        vehicle.model.addMotor(BigWorld.Servo(matrix))
        self.__assembleModels()
        if not isFirstInit:
            chassis['boundEffects'].reattachTo(chassis['model'])
            hull['boundEffects'].reattachTo(hull['model'])
            turret['boundEffects'].reattachTo(turret['model'])
            gun['boundEffects'].reattachTo(gun['model'])
            self.__reattachEffects()
        if not VehicleDamageState.isDamagedModel(chassis['state']):
            self.__attachStickers()
            try:
                vehicle.model.wg_fashion = self.__fashion
            except:
                LOG_CURRENT_EXCEPTION()

            if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
                self.__attachExhaust(True)
            gun['model'].wg_gunRecoil = self.__gunRecoil
            self.__createLampLights()
            self.__gunFireNode = gun['model'].node('HP_gunFire')
            self.__setupHavok()
            if vehicle.isPlayerVehicle:
                vehicle.drawEdge(0, 1, True)
        else:
            if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
                self.__destroyExhaust()
            filter = self.__vehicle.filter
            if not self.__isPillbox and filter.placingOnGround:
                contactsWithGround = filter.numLeftTrackContacts + filter.numRightTrackContacts
                notFlying = True if contactsWithGround > 0 else False
            else:
                notFlying = False if self.fashion.isFlying else True
            chassis['_visibility'] = (notFlying, True)
            self.__attachStickers(items.vehicles.g_cache.commonConfig['miscParams']['damageStickerAlpha'], True)
        self.__updateCamouflage()
        self.__updateRepaint()
        self.__chassisShadowForwardDecal.attach(vehicle, self.modelsDesc)
        self.__chassisShadowForwardDecal.attach(vehicle, self.modelsDesc)
        self.__applyVisibility()
        self.__vehicle.model.height = self.__computeVehicleHeight()
        self.onModelChanged()
        if 'observer' in vehicle.typeDescriptor.type.tags:
            vehicle.model.visible = False
            vehicle.model.visibleAttachments = False
        else:
            self.__chassisOcclusionDecal.attach(vehicle, self.modelsDesc)
        if MAX_DISTANCE > 0:
            transform = vehicle.typeDescriptor.chassis['AODecals'][0]
            self.__attachSplodge(BigWorld.Splodge(transform, MAX_DISTANCE, vehicle.typeDescriptor.chassis['hullPosition'].y))
        return

    def __reattachEffects(self):
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.reattachTo(self.modelsDesc['hull']['model'])
        return

    def __playEffect(self, kind, *modifs):
        self.__stopEffects()
        if kind == 'empty':
            return
        enableDecal = True
        if not self.__isPillbox and kind in ('explosion', 'destruction'):
            filter = self.__vehicle.filter
            isFlying = filter.numLeftTrackContacts < 2 and filter.numRightTrackContacts < 2
            if isFlying:
                enableDecal = False
        if self.isUnderwater:
            if kind not in ('submersionDeath',):
                return
        vehicle = self.__vehicle
        effects = vehicle.typeDescriptor.type.effects[kind]
        if not effects:
            return
        effects = random.choice(effects)
        modelMap = {}
        for i, j in self.modelsDesc.iteritems():
            modelMap[i] = j['model']

        self.__effectsPlayer = EffectsListPlayer(effects[1], effects[0], showShockWave=vehicle.isPlayerVehicle, showFlashBang=vehicle.isPlayerVehicle, isPlayerVehicle=vehicle.isPlayerVehicle, showDecal=enableDecal, start=vehicle.position + Math.Vector3(0.0, -1.0, 0.0), end=vehicle.position + Math.Vector3(0.0, 1.0, 0.0), modelMap=modelMap, entity_id=vehicle.id)
        self.__effectsPlayer.play(self.modelsDesc['hull']['model'], *modifs)

    def __updateCamouflage(self):
        texture = ''
        colors = [0,
         0,
         0,
         0]
        weights = Math.Vector4(1, 0, 0, 0)
        camouflagePresent = False
        vDesc = self.__vehicle.typeDescriptor
        camouflageParams = self.__getCamouflageParams(self.__vehicle)
        customization = items.vehicles.g_cache.customization(vDesc.type.customizationNationID)
        defaultTiling = None
        if camouflageParams is not None and customization is not None:
            camouflage = customization['camouflages'].get(camouflageParams[0])
            if camouflage is not None:
                camouflagePresent = True
                texture = camouflage['texture']
                colors = camouflage['colors']
                weights = Math.Vector4(*[ (c >> 24) / 255.0 for c in colors ])
                defaultTiling = camouflage['tiling'].get(vDesc.type.compactDescr)
        if VehicleDamageState.isDamagedModel(self.modelsDesc['chassis']['state']):
            weights *= 0.1
        if camouflageParams is not None:
            _, camStartTime, camNumDays = camouflageParams
            if camNumDays > 0:
                timeAmount = (time.time() - camStartTime) / (camNumDays * 86400)
                if timeAmount > 1.0:
                    weights *= _CAMOUFLAGE_MIN_INTENSITY
                elif timeAmount > 0:
                    weights *= (1.0 - timeAmount) * (1.0 - _CAMOUFLAGE_MIN_INTENSITY) + _CAMOUFLAGE_MIN_INTENSITY
        for descId in ('chassis', 'hull', 'turret', 'gun'):
            exclusionMap = vDesc.type.camouflageExclusionMask
            tiling = defaultTiling
            if tiling is None:
                tiling = vDesc.type.camouflageTiling
            model = self.modelsDesc[descId]['model']
            if descId == 'chassis':
                compDesc = vDesc.chassis
            elif descId == 'hull':
                compDesc = vDesc.hull
            elif descId == 'turret':
                compDesc = vDesc.turret
            elif descId == 'gun':
                compDesc = vDesc.gun
            else:
                compDesc = None
            if compDesc is not None:
                coeff = compDesc.get('camouflageTiling')
                if coeff is not None:
                    if tiling is not None:
                        tiling = (tiling[0] * coeff[0],
                         tiling[1] * coeff[1],
                         tiling[2] + coeff[2],
                         tiling[3] + coeff[3])
                    else:
                        tiling = coeff
                if compDesc.get('camouflageExclusionMask'):
                    exclusionMap = compDesc['camouflageExclusionMask']
            useCamouflage = camouflagePresent and texture
            fashion = None
            if hasattr(model, 'wg_fashion'):
                fashion = model.wg_fashion
            elif hasattr(model, 'wg_gunRecoil'):
                fashion = model.wg_gunRecoil
            elif useCamouflage:
                fashion = model.wg_baseFashion = BigWorld.WGBaseFashion()
            elif hasattr(model, 'wg_baseFashion'):
                delattr(model, 'wg_baseFashion')
            if fashion is not None:
                if useCamouflage:
                    fashion.setCamouflage(texture, exclusionMap, tiling, colors[0], colors[1], colors[2], colors[3], weights)
                else:
                    fashion.removeCamouflage()

        return

    __SPORT_ACTIONS_CAMOUFLAGES = {'ussr:T62A_sport': (95, 94),
     'usa:M24_Chaffee_GT': (82, 83)}

    def __getCamouflageParams(self, vehicle):
        vDesc = vehicle.typeDescriptor
        vehicleInfo = BigWorld.player().arena.vehicles.get(vehicle.id)
        if vehicleInfo is not None:
            camouflageIdPerTeam = VehicleAppearance.__SPORT_ACTIONS_CAMOUFLAGES.get(vDesc.name)
            if camouflageIdPerTeam is not None:
                camouflageId = camouflageIdPerTeam[0] if vehicleInfo['team'] == 1 else camouflageIdPerTeam[1]
                return (camouflageId, time.time(), 100.0)
            camouflagePseudoname = vehicleInfo['events'].get('hunting', None)
            if camouflagePseudoname is not None:
                camouflIdsByNation = {0: {'black': 29,
                     'gold': 30,
                     'red': 31,
                     'silver': 32},
                 1: {'black': 25,
                     'gold': 26,
                     'red': 27,
                     'silver': 28},
                 2: {'black': 52,
                     'gold': 50,
                     'red': 51,
                     'silver': 53},
                 3: {'black': 48,
                     'gold': 46,
                     'red': 47,
                     'silver': 49},
                 4: {'black': 60,
                     'gold': 58,
                     'red': 59,
                     'silver': 61},
                 5: {'black': 56,
                     'gold': 54,
                     'red': 55,
                     'silver': 57}}
                camouflIds = camouflIdsByNation.get(vDesc.type.customizationNationID)
                if camouflIds is not None:
                    ret = camouflIds.get(camouflagePseudoname)
                    if ret is not None:
                        return (ret, time.time(), 100.0)
        arenaType = BigWorld.player().arena.arenaType
        camouflageKind = arenaType.vehicleCamouflageKind
        return vDesc.camouflages[camouflageKind]

    def __updateRepaint(self):
        if not hasattr(self.__vehicle.typeDescriptor.type, 'repaintParameters'):
            return
        else:
            repaintReferenceColor, repaintReplaceColor, repaintGlossRangeScale = RepaintParams.getRepaintParams(self.__vehicle.typeDescriptor)
            for descId in ('hull', 'turret', 'gun', 'chassis'):
                model = self.modelsDesc[descId]['model']
                fashion = None
                if hasattr(model, 'wg_fashion'):
                    fashion = model.wg_fashion
                elif hasattr(model, 'wg_gunRecoil'):
                    fashion = model.wg_gunRecoil
                else:
                    fashion = model.wg_baseFashion = BigWorld.WGBaseFashion()
                if fashion is not None:
                    fashion.setRepaint(repaintReferenceColor, repaintReplaceColor, repaintGlossRangeScale)

            return

    def __stopEffects(self):
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.stop()
        self.__effectsPlayer = None
        return

    def __calcIsUnderwater(self):
        if not self.__isInWater:
            return False
        chassisModel = self.modelsDesc['chassis']['model']
        turretOffs = self.__vehicle.typeDescriptor.chassis['hullPosition'] + self.__vehicle.typeDescriptor.hull['turretPositions'][0]
        turretOffsetMat = Math.Matrix()
        turretOffsetMat.setTranslate(turretOffs)
        turretJointMat = Math.Matrix(chassisModel.matrix)
        turretJointMat.preMultiply(turretOffsetMat)
        turretHeight = turretJointMat.translation.y - self.__vehicle.position.y
        return turretHeight < self.__waterHeight

    def __updateWaterStatus(self):
        vehiclePosition = self.__vehicle.position
        self.__waterHeight = BigWorld.wg_collideWater(vehiclePosition, vehiclePosition + Math.Vector3(0.0, 1.0, 0.0), False)
        self.__isInWater = self.__waterHeight != -1
        self.__isUnderWater = self.__calcIsUnderwater()
        wasSplashed = self.__splashedWater
        waterHitPoint = None
        if self.__isInWater:
            self.__splashedWater = True
            waterHitPoint = vehiclePosition + Math.Vector3(0.0, self.__waterHeight, 0.0)
        else:
            trPoint = self.__typeDesc.chassis['topRightCarryingPoint']
            cornerPoints = (Math.Vector3(trPoint.x, 0.0, trPoint.y),
             Math.Vector3(trPoint.x, 0.0, -trPoint.y),
             Math.Vector3(-trPoint.x, 0.0, -trPoint.y),
             Math.Vector3(-trPoint.x, 0.0, trPoint.y))
            vehMat = Math.Matrix(self.__vehicleMatrixProv)
            for cornerPoint in cornerPoints:
                pointToTest = vehMat.applyPoint(cornerPoint)
                dist = BigWorld.wg_collideWater(pointToTest, pointToTest + Math.Vector3(0.0, 1.0, 0.0))
                if dist != -1:
                    self.__splashedWater = True
                    waterHitPoint = pointToTest + Math.Vector3(0.0, dist, 0.0)
                    break

            self.__splashedWater = False
        if self.__splashedWater and not wasSplashed:
            lightVelocityThreshold = self.__typeDesc.type.collisionEffectVelocities['waterContact']
            heavyVelocityThreshold = self.__typeDesc.type.heavyCollisionEffectVelocities['waterContact']
            vehicleVelocity = abs(self.__speedInfo[0])
            if vehicleVelocity >= lightVelocityThreshold:
                collRes = BigWorld.wg_collideSegment(self.__vehicle.spaceID, waterHitPoint, waterHitPoint + (0.0, -_MIN_DEPTH_FOR_HEAVY_SPLASH, 0.0), 18, lambda matKind, collFlags, itemId, chunkId: collFlags & 8)
                deepEnough = collRes is None
                effectName = 'waterCollisionLight' if vehicleVelocity < heavyVelocityThreshold or not deepEnough else 'waterCollisionHeavy'
                self.__vehicle.showCollisionEffect(waterHitPoint, effectName, Math.Vector3(0.0, 1.0, 0.0))
        if self.__effectsPlayer is not None:
            if self.isUnderwater != (self.__currentDamageState.effect in ('submersionDeath',)):
                self.__stopEffects()
        return

    def updateTracksScroll(self, leftScroll, rightScroll):
        self.__leftTrackScroll = leftScroll
        self.__rightTrackScroll = rightScroll
        if self.__vehicle is not None and self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
            self.customEffectManager.updateTrackScroll(leftScroll, rightScroll)
        return

    def __onPeriodicTimerEngine(self):
        self.detailedEngineState.refresh(_PERIODIC_TIME_ENGINE)
        self.engineAudition.tick()
        return _PERIODIC_TIME_ENGINE

    def __onPeriodicTimer(self):
        timeStamp = BigWorld.wg_getFrameTimestamp()
        if VehicleAppearance.frameTimeStamp >= timeStamp:
            self.__periodicTimerID = BigWorld.callback(0.0, self.__onPeriodicTimer)
            return
        else:
            VehicleAppearance.frameTimeStamp = timeStamp
            self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME, self.__onPeriodicTimer)
            if self.__isPillbox or self.__vehicle is None:
                return
            vehicle = self.__vehicle
            self.__speedInfo = vehicle.filter.speedInfo.value
            if not self.__vehicle.isPlayerVehicle:
                self.detailedEngineState.refresh(_PERIODIC_TIME)
            try:
                self.__updateVibrations()
                if self.__lightFxCtrl is not None:
                    self.__lightFxCtrl.update(vehicle)
                if self.__auxiliaryFxCtrl is not None:
                    self.__auxiliaryFxCtrl.update(vehicle)
                self.__updateWaterStatus()
                if not vehicle.isAlive():
                    return
                self.__distanceFromPlayer = (BigWorld.camera().position - vehicle.position).length
                extra = vehicle.typeDescriptor.extrasDict['fire']
                if extra.isRunningFor(vehicle):
                    extra.checkUnderwater(vehicle, self.isUnderwater)
                self.__updateCurrTerrainMatKinds()
                if not self.__vehicle.isPlayerVehicle:
                    self.engineAudition.tick()
                self.__updateEffectsLOD()
                vehicle.filter.placingOnGround = not self.__fashion.suspensionWorking
                if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
                    self.__customEffectManager.update()
                else:
                    self.__trailEffects.update()
                    self.__updateExhaust()
                self.__vehicle.filter.placingOnGround = not self.__fashion.suspensionWorking
            except:
                LOG_CURRENT_EXCEPTION()

            return

    def __updateEffectsLOD(self):
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
            enableExhaust = self.__distanceFromPlayer <= _LOD_DISTANCE_EXHAUST
            if enableExhaust != self.__exhaustEffects.enabled:
                self.__exhaustEffects.enable(enableExhaust and not self.__isUnderWater)
        enableTrails = self.__distanceFromPlayer <= _LOD_DISTANCE_TRAIL_PARTICLES and BigWorld.wg_isVehicleDustEnabled()
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
            self.__customEffectManager.enable(enableTrails)
        else:
            self.__trailEffects.enable(enableTrails)

    def __setupTrailParticles(self):
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
            self.__trailEffects = VehicleTrailEffects(self.__vehicle)

    def __updateCurrTerrainMatKinds(self):
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
            testPoints = (Math.Matrix(self.__customEffectManager.getTrackCenterNode(0)).translation, Math.Matrix(self.__customEffectManager.getTrackCenterNode(1)).translation, self.__vehicle.position)
        else:
            testPoints = (Math.Matrix(self.__trailEffects.getTrackCenterNode(0)).translation, Math.Matrix(self.__trailEffects.getTrackCenterNode(1)).translation, self.__vehicle.position)
        isOnSoftTerrain = False
        for i in xrange(_MATKIND_COUNT):
            testPoint = testPoints[i]
            res = BigWorld.wg_collideSegment(self.__vehicle.spaceID, testPoint + Math.Vector3(0.0, 2.0, 0.0), testPoint + Math.Vector3(0.0, -2.0, 0.0), 18)
            matKind = res[2] if res is not None else 0
            self.__currTerrainMatKind[i] = matKind
            if not isOnSoftTerrain:
                groundStr = material_kinds.GROUND_STRENGTHS_BY_IDS.get(matKind)
                isOnSoftTerrain = groundStr == 'soft'

        if self.__vehicle.isPlayerVehicle and self.__wasOnSoftTerrain != isOnSoftTerrain:
            self.__wasOnSoftTerrain = isOnSoftTerrain
            if isOnSoftTerrain:
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_ON_SOFT_TERRAIN)
            else:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_ON_SOFT_TERRAIN)
        self.__fashion.setCurrTerrainMatKinds(self.__currTerrainMatKind[0], self.__currTerrainMatKind[1])
        return

    def switchFireVibrations(self, bStart):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.switchFireVibrations(bStart)
        return

    def executeHitVibrations(self, hitEffectCode):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeHitVibrations(hitEffectCode)
        return

    def executeRammingVibrations(self, matKind=None):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeRammingVibrations(self.__vehicle.getSpeed(), matKind)
        return

    def executeShootingVibrations(self, caliber):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeShootingVibrations(caliber)
        return

    def executeCriticalHitVibrations(self, vehicle, extrasName):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeCriticalHitVibrations(vehicle, extrasName)
        return

    def deviceDestroyed(self, deviceName):
        if self.engineAudition is not None:
            self.engineAudition.deviceDestroyed(deviceName)
        return

    def deviceRepairedToCritical(self, deviceName):
        if self.engineAudition is not None:
            self.engineAudition.deviceRepairedToCritical(deviceName)
        return

    def __updateVibrations(self):
        if self.__vibrationsCtrl is None:
            return
        else:
            vehicle = self.__vehicle
            crashedTrackCtrl = self.__crashedTracksCtrl
            self.__vibrationsCtrl.update(vehicle, crashedTrackCtrl.isLeftTrackBroken(), crashedTrackCtrl.isRightTrackBroken())
            return

    def __onModelLoaded(self, name, state, desc, model):
        if self.modelsDesc is None or self.modelsDesc != desc:
            return
        else:
            desc = self.modelsDesc[name]
            if state != desc['_fetchedState']:
                raise Exception('The wrong model state was loaded for ' + name)
            if model is not None:
                desc['_fetchedModel'] = model
            else:
                desc['_fetchedModel'] = desc['model']
                desc['_fetchedState'] = desc['state']
                LOG_ERROR('Model %s not loaded.' % state)
            self.__attemptToSetupModels()
            return

    def __assembleModels(self):
        vehicle = self.__vehicle
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        gun = self.modelsDesc['gun']
        try:
            hull['_node'] = vehicle.model.node(_ROOT_NODE_NAME)
            hull['_node'].attach(hull['model'])
            turretJointName = self.__typeDesc.hull['turretHardPoints'][0]
            turret['_node'] = hull['model'].node(turretJointName, self.turretMatrix)
            turret['_node'].attach(turret['model'])
            gun['_stickerNode'] = turret['model'].node('HP_gunJoint', self.gunMatrix)
            if self.__currentDamageState.model == 'destroyed':
                gun['_node'] = gun['_stickerNode']
            else:
                gun['_node'] = turret['model'].node('HP_gunJoint')
                self.gunRecoil.rotationMatrix = self.gunMatrix
            gun['_node'].attach(gun['model'])
            self.updateTurretVisibility()
            if vehicle.isPlayerVehicle:
                player = BigWorld.player()
                if player.inputHandler is not None:
                    arcadeCamera = player.inputHandler.ctrls['arcade'].camera
                    if arcadeCamera is not None:
                        arcadeCamera.addVehicleToCollideWith(self)
        except Exception:
            LOG_ERROR('Can not assemble models for %s.' % self.__typeDesc.name)
            raise

        if IS_DEVELOPMENT and _ENABLE_VEHICLE_VALIDATION:
            self.__validateCallbackId = BigWorld.callback(0.01, self.__validateAssembledModel)
        return

    def __applyVisibility(self):
        chassis = self.modelsDesc['chassis']
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        gun = self.modelsDesc['gun']
        chassis['model'].visible = chassis['_visibility'][0]
        chassis['model'].visibleAttachments = chassis['_visibility'][1]
        hull['model'].visible = hull['_visibility'][0]
        hull['model'].visibleAttachments = hull['_visibility'][1]
        turret['model'].visible = turret['_visibility'][0]
        turret['model'].visibleAttachments = turret['_visibility'][1]
        gun['model'].visible = gun['_visibility'][0]
        gun['model'].visibleAttachments = gun['_visibility'][1]

    def __validateAssembledModel(self):
        self.__validateCallbackId = None
        vehicle = self.__vehicle
        vDesc = self.__typeDesc
        state = self.__currentDamageState.model
        chassis = self.modelsDesc['chassis']
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        gun = self.modelsDesc['gun']
        _validateCfgPos(chassis, hull, vDesc.chassis['hullPosition'], 'hullPosition', vehicle, state)
        _validateCfgPos(hull, turret, vDesc.hull['turretPositions'][0], 'turretPosition', vehicle, state)
        _validateCfgPos(turret, gun, vDesc.turret['gunPosition'], 'gunPosition', vehicle, state)
        return

    def __createExhaust(self):
        self.__exhaustEffects = VehicleExhaustEffects(self.__typeDesc)

    def __attachExhaust(self, attach):
        if attach:
            hullModel = self.modelsDesc['hull']['model']
            self.__exhaustEffects.attach(hullModel, self.__vehicle.typeDescriptor.hull['exhaust'])
        else:
            self.__exhaustEffects.detach()

    def __destroyExhaust(self):
        self.__exhaustEffects.destroy()

    def __updateExhaust(self):
        if self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
            if self.__exhaustEffects.enabled == self.__isUnderWater:
                self.__exhaustEffects.enable(not self.__isUnderWater)
        self.__exhaustEffects.changeExhaust(self.__engineMode[0], self.detailedEngineState.rpm)

    def __createGunRecoil(self):
        recoilDescr = self.__typeDesc.gun['recoil']
        recoil = BigWorld.WGGunRecoil(_GUN_RECOIL_NODE_NAME)
        recoil.setLod(recoilDescr['lodDist'])
        recoil.setDuration(recoilDescr['backoffTime'], recoilDescr['returnTime'])
        recoil.setDepth(recoilDescr['amplitude'])
        self.__gunRecoil = recoil

    def __createStickers(self, prereqs):
        insigniaRank = self.__vehicle.publicInfo['marksOnGun']
        self.__vehicleStickers = VehicleStickers(self.__typeDesc, insigniaRank)
        clanID = BigWorld.player().arena.vehicles[self.__vehicle.id]['clanDBID']
        self.__vehicleStickers.setClanID(clanID)

    def __attachStickers(self, alpha=1.0, emblemsOnly=False):
        self.__vehicleStickers.alpha = alpha
        ignoredComponents = set(('turret', 'gun')) if self.__vehicle.isTurretMarkedForDetachment else set()
        modelsAndParents = []
        for componentName in VehicleStickers.COMPONENT_NAMES:
            if componentName in ignoredComponents:
                modelsAndParents.append((None, None))
            modelDesc = self.modelsDesc[componentName]
            stickerNode = modelDesc.get('_stickerNode', None)
            if stickerNode is not None:
                modelsAndParents.append((modelDesc['model'], stickerNode))
            modelsAndParents.append((modelDesc['model'], modelDesc['_node']))

        self.__vehicleStickers.attach(modelsAndParents, VehicleDamageState.isDamagedModel(self.modelsDesc['chassis']['state']), not emblemsOnly)
        return

    def __detachStickers(self):
        self.__vehicleStickers.detach()

    def __attachSplodge(self, splodge):
        node = self.modelsDesc[TankComponentNames.HULL]['_node']
        if splodge is not None and self.__splodge is None:
            self.__splodge = splodge
            node.attach(splodge)
        return

    def __detachSplodge(self, splodge):
        if self.__splodge is not None:
            self.modelsDesc[TankComponentNames.HULL]['_node'].detach(self.__splodge)
            self.__splodge = None
        return

    def __createLampLights(self):
        if not _ALLOW_LAMP_LIGHTS:
            return
        try:
            rotate = Math.Matrix()
            rotate.setRotateX(-0.7)
            self.__leftLightRotMat = Math.Matrix()
            self.__leftLightRotMat.setTranslate(Math.Vector3(0.25, 1.2, 0.25))
            self.__leftLightRotMat.preMultiply(rotate)
            self.__rightLightRotMat = Math.Matrix()
            self.__rightLightRotMat.setTranslate(Math.Vector3(-0.25, 1.2, 0.25))
            self.__rightLightRotMat.preMultiply(rotate)
            hull = self.modelsDesc['hull']
            node1 = hull['model'].node('HP_TrackUp_LFront', self.__leftLightRotMat)
            node2 = hull['model'].node('HP_TrackUp_RFront', self.__rightLightRotMat)
            self.__leftFrontLight = BigWorld.PyChunkSpotLight()
            self.__leftFrontLight.innerRadius = 5
            self.__leftFrontLight.outerRadius = 20
            self.__leftFrontLight.coneAngle = 0.43
            self.__leftFrontLight.castShadows = True
            self.__leftFrontLight.multiplier = 5
            self.__leftFrontLight.source = node1
            self.__leftFrontLight.colour = (255, 255, 255, 0)
            self.__leftFrontLight.visible = True
            self.__rightFrontLight = BigWorld.PyChunkSpotLight()
            self.__rightFrontLight.innerRadius = 5
            self.__rightFrontLight.outerRadius = 20
            self.__rightFrontLight.coneAngle = 0.43
            self.__rightFrontLight.castShadows = True
            self.__rightFrontLight.multiplier = 5
            self.__rightFrontLight.source = node2
            self.__rightFrontLight.colour = (255, 255, 255, 0)
            self.__rightFrontLight.visible = True
        except Exception:
            LOG_ERROR('Can not attach lamp lights to tank model for %s.' % self.__typeDesc.name)

    def __destroyLampLights(self):
        if self.__leftFrontLight is not None:
            self.__leftFrontLight.visible = False
            self.__leftFrontLight.source = None
            self.__leftFrontLight = None
            self.__leftLightRotMat = None
        if self.__rightFrontLight is not None:
            self.__rightFrontLight.visible = False
            self.__rightFrontLight.source = None
            self.__rightFrontLight = None
            self.__rightLightRotMat = None
        return

    def __disableStipple(self):
        self.__vehicle.model.stipple = False
        self.__stippleCallbackID = None
        return

    def __computeVehicleHeight(self):
        desc = self.__typeDesc
        turretBBox = desc.turret['hitTester'].bbox
        gunBBox = desc.gun['hitTester'].bbox
        hullBBox = desc.hull['hitTester'].bbox
        hullTopY = desc.chassis['hullPosition'][1] + hullBBox[1][1]
        turretTopY = desc.chassis['hullPosition'][1] + desc.hull['turretPositions'][0][1] + turretBBox[1][1]
        gunTopY = desc.chassis['hullPosition'][1] + desc.hull['turretPositions'][0][1] + desc.turret['gunPosition'][1] + gunBBox[1][1]
        return max(hullTopY, max(turretTopY, gunTopY))

    def __setupHavok(self):
        vehicle = self.__vehicle
        vDesc = self.__typeDesc
        hull = self.modelsDesc['hull']
        hullModel = self.modelsDesc['hull']['model']
        turret = self.modelsDesc['turret']
        turretModel = self.modelsDesc['turret']['model']
        chassis = self.modelsDesc['chassis']
        chassisModel = self.modelsDesc['chassis']['model']
        gun = self.modelsDesc['gun']
        gunModel = self.modelsDesc['gun']['model']
        rootModel = chassisModel
        hkm = BigWorld.wg_createHKAttachment(hullModel, rootModel, vDesc.hull['hitTester'].getBspModel())
        if hkm is not None:
            hull['_node'].attach(hkm)
            hkm.maxAcceleration = vDesc.physics['speedLimits'][0] * 40
            hkm.maxAngularAcceleration = 50
        hull['havok'] = hkm
        hkm = BigWorld.wg_createHKAttachment(turretModel, hullModel, vDesc.turret['hitTester'].getBspModel())
        if hkm is not None:
            turret['_node'].attach(hkm)
            hkm.maxAcceleration = vDesc.physics['speedLimits'][0] * 40
            hkm.maxAngularAcceleration = 150
        turret['havok'] = hkm
        hkm = BigWorld.wg_createHKAttachment(chassisModel, rootModel, vDesc.chassis['hitTester'].getBspModel())
        if hkm is not None:
            chassisModel.root.attach(hkm)
            hkm.addUpdateAttachment(chassisModel)
            hkm.addUpdateAttachment(hullModel)
            hkm.addUpdateAttachment(turretModel)
        chassis['havok'] = hkm
        hkm = BigWorld.wg_createHKAttachment(gunModel, rootModel, vDesc.gun['hitTester'].getBspModel())
        if hkm is not None:
            gun['_node'].attach(hkm)
        gun['havok'] = hkm
        return

    def __removeHavok(self):
        LOG_DEBUG('__removeHavok')
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        chassis = self.modelsDesc['chassis']
        gun = self.modelsDesc['gun']
        if hull.get('havok', None) is not None:
            hull['_node'].detach(hull['havok'])
            hull['havok'] = None
        if turret.get('havok', None) is not None:
            turret['_node'].detach(turret['havok'])
            turret['havok'] = None
        if chassis.get('havok', None) is not None:
            chassis['model'].root.detach(chassis['havok'])
            chassis['havok'] = None
        if gun.get('havok', None) is not None:
            gun['_node'].detach(gun['havok'])
            gun['havok'] = None
        return

    def __havokExplosion(self):
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        chassis = self.modelsDesc['chassis']
        gun = self.modelsDesc['gun']
        if hull['havok'] is not None:
            hull['havok'].releaseBreakables()
        if turret['havok'] is not None:
            turret['havok'].releaseBreakables()
        if chassis['havok'] is not None:
            chassis['havok'].releaseBreakables()
        BigWorld.wg_havokExplosion(hull['model'].position, 300, 5)
        return

    def setupGunMatrixTargets(self, target=None):
        if target is None:
            target = self.__filter
        self.turretMatrix.target = target.turretMatrix
        self.gunMatrix.target = target.gunMatrix
        return

    def assembleStipple(self):
        if self.__currentDamageState.model == 'destroyed':
            return
        try:
            turretMatrix = Math.Matrix()
            gunMatrix = Math.Matrix()
            turret = self.modelsDesc['turret']
            hull = self.modelsDesc['hull']
            gun = self.modelsDesc['gun']
            turret['_node'].detach(turret['model'])
            gun['_node'].detach(gun['model'])
            turretJointName = self.__typeDesc.hull['turretHardPoints'][0]
            turretMatrix.set(self.turretMatrix)
            turret['_node'] = hull['model'].node(turretJointName, turretMatrix)
            turret['_node'].attach(turret['model'])
            gunMatrix.set(self.gunMatrix)
            gun['_node'] = turret['model'].node('HP_gunJoint', gunMatrix)
            gun['_node'].attach(gun['model'])
        except:
            LOG_ERROR('Can not assemble stipple model for %s.' % self.__typeDesc.name)


class StippleManager():

    def __init__(self):
        self.__stippleDescs = {}
        self.__stippleToAddDescs = {}

    def showFor(self, vehicle, model):
        if not model.stipple:
            model.stipple = True
            callbackID = BigWorld.callback(0.0, partial(self.__addStippleModel, vehicle.id))
            self.__stippleToAddDescs[vehicle.id] = (model, callbackID)

    def hideIfExistFor(self, vehicle):
        desc = self.__stippleDescs.get(vehicle.id)
        if desc is not None:
            BigWorld.cancelCallback(desc[1])
            BigWorld.player().delModel(desc[0])
            del self.__stippleDescs[vehicle.id]
        desc = self.__stippleToAddDescs.get(vehicle.id)
        if desc is not None:
            BigWorld.cancelCallback(desc[1])
            del self.__stippleToAddDescs[vehicle.id]
        return

    def destroy(self):
        for model, callbackID in self.__stippleDescs.itervalues():
            BigWorld.cancelCallback(callbackID)
            BigWorld.player().delModel(model)

        for model, callbackID in self.__stippleToAddDescs.itervalues():
            BigWorld.cancelCallback(callbackID)

        self.__stippleDescs = None
        self.__stippleToAddDescs = None
        return

    def __addStippleModel(self, vehID):
        model = self.__stippleToAddDescs[vehID][0]
        if model.attached:
            callbackID = BigWorld.callback(0.0, partial(self.__addStippleModel, vehID))
            self.__stippleToAddDescs[vehID] = (model, callbackID)
            return
        del self.__stippleToAddDescs[vehID]
        BigWorld.player().addModel(model)
        callbackID = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self.__removeStippleModel, vehID))
        self.__stippleDescs[vehID] = (model, callbackID)

    def __removeStippleModel(self, vehID):
        BigWorld.player().delModel(self.__stippleDescs[vehID][0])
        del self.__stippleDescs[vehID]


class _CrashedTrackController():

    def __init__(self, vehicle, va):
        self.__vehicle = vehicle.proxy
        self.__va = weakref.ref(va)
        self.__flags = 0
        self.__model = None
        self.__fashion = None
        self.__inited = True
        self.__forceHide = False
        self.__loadInfo = [False, False]
        return

    def isLeftTrackBroken(self):
        return self.__flags & 1

    def isRightTrackBroken(self):
        return self.__flags & 2

    def destroy(self):
        self.__vehicle = None
        return

    def setVisible(self, bool):
        self.__forceHide = not bool
        self.__setupTracksHiding(not bool)

    def addTrack(self, isLeft):
        if not self.__inited:
            return
        else:
            if self.__flags == 0 and self.__vehicle is not None and self.__vehicle.isPlayerVehicle:
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            if self.__vehicle.filter.placingOnGround:
                flying = self.__vehicle.filter.numLeftTrackContacts == 0
                self.__flags |= 1 if isLeft else 2
            elif isLeft:
                flying = self.__va().fashion.isFlyingLeft
                self.__flags |= 1
            else:
                flying = self.__va().fashion.isFlyingRight
                self.__flags |= 2
            if self.__model is None and not flying:
                self.__loadInfo = [True, isLeft]
                BigWorld.fetchModel(self.__va().modelsDesc['chassis']['_stateFunc'](self.__vehicle, 'destroyed'), self.__onModelLoaded)
            if self.__fashion is None:
                self.__fashion = BigWorld.WGVehicleFashion(True, 1.0, False)
                _setupVehicleFashion(self, self.__fashion, self.__vehicle, True)
            self.__fashion.setCrashEffectCoeff(0.0)
            self.__setupTracksHiding()
            return

    def delTrack(self, isLeft):
        if not self.__inited or self.__fashion is None:
            return
        else:
            if self.__loadInfo[0] and self.__loadInfo[1] == isLeft:
                self.__loadInfo = [False, False]
            if isLeft:
                self.__flags &= -2
            else:
                self.__flags &= -3
            self.__setupTracksHiding()
            if self.__flags == 0 and self.__model is not None:
                self.__va().modelsDesc['chassis']['model'].root.detach(self.__model)
                self.__model = None
                self.__fashion = None
            if self.__flags != 0 and self.__vehicle is not None and self.__vehicle.isPlayerVehicle:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_TRACKS_DAMAGED)
            return

    def receiveShotImpulse(self, dir, impulse):
        if not self.__inited or self.__fashion is None:
            return
        else:
            self.__fashion.receiveShotImpulse(dir, impulse)
            return

    def reset(self):
        if not self.__inited:
            return
        else:
            if self.__fashion is not None:
                self.__fashion.setCrashEffectCoeff(-1.0)
            self.__flags = 0
            if self.__model is not None:
                self.__va().modelsDesc['chassis']['model'].root.detach(self.__model)
                self.__model = None
                self.__fashion = None
            return

    def __setupTracksHiding(self, force=False):
        if force or self.__forceHide:
            tracks = (True, True)
            invTracks = (True, True)
        else:
            tracks = (self.__flags & 1, self.__flags & 2)
            invTracks = (not tracks[0], not tracks[1])
        self.__va().fashion.hideTracks(*tracks)
        if self.__fashion is not None:
            self.__fashion.hideTracks(*invTracks)
        return

    def __onModelLoaded(self, model):
        if self.__va() is None or not self.__loadInfo[0] or not self.__inited:
            return
        else:
            va = self.__va()
            self.__loadInfo = [False, False]
            if model:
                self.__model = model
            else:
                self.__inited = False
                modelState = va.modelsDesc['chassis']['_stateFunc'](self.__vehicle, 'destroyed')
                LOG_ERROR('Model %s not loaded.' % modelState)
                return
            try:
                self.__model.wg_fashion = self.__fashion
                va.modelsDesc['chassis']['model'].root.attach(self.__model)
            except:
                va.fashion.hideTracks(False, False)
                self.__inited = False
                LOG_CURRENT_EXCEPTION()

            return


class _SkeletonCollider():

    def __init__(self, vehicle, vehicleAppearance):
        self.__vehicle = vehicle.proxy
        self.__vAppearance = weakref.proxy(vehicleAppearance)
        self.__boxAttachments = list()
        descr = vehicle.typeDescriptor
        descList = [('Scene Root', descr.chassis['hitTester'].bbox),
         ('Scene Root', descr.hull['hitTester'].bbox),
         ('Scene Root', descr.turret['hitTester'].bbox),
         ('Scene Root', descr.gun['hitTester'].bbox)]
        self.__createBoxAttachments(descList)
        vehicle.skeletonCollider = BigWorld.SkeletonCollider()
        for boxAttach in self.__boxAttachments:
            vehicle.skeletonCollider.addCollider(boxAttach)

    def destroy(self):
        delattr(self.__vehicle, 'skeletonCollider')
        self.__vehicle = None
        self.__vAppearance = None
        self.__boxAttachments = None
        return

    def attach(self):
        va = self.__vAppearance.modelsDesc
        collider = self.__vehicle.skeletonCollider.getCollider(0)
        va['chassis']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(1)
        va['hull']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(2)
        va['turret']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(3)
        va['gun']['model'].node(collider.name).attach(collider)

    def detach(self):
        va = self.__vAppearance.modelsDesc
        collider = self.__vehicle.skeletonCollider.getCollider(0)
        va['chassis']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(1)
        va['hull']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(2)
        va['turret']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(3)
        va['gun']['model'].node(collider.name).detach(collider)

    def __createBoxAttachments(self, descList):
        for desc in descList:
            boxAttach = BigWorld.BoxAttachment()
            boxAttach.name = desc[0]
            boxAttach.minBounds = desc[1][0]
            boxAttach.maxBounds = desc[1][1]
            self.__boxAttachments.append(boxAttach)


def _almostZero(val, epsilon=0.0004):
    return -epsilon < val < epsilon


def _createWheelsListByTemplate(startIndex, template, count):
    return [ '%s%d' % (template, i) for i in range(startIndex, startIndex + count) ]


def _setupVehicleFashion(self, fashion, vehicle, isCrashedTrack=False):
    vDesc = vehicle.typeDescriptor
    tracesCfg = vDesc.chassis['traces']
    fashion.maxMovement = vDesc.physics['speedLimits'][0]
    try:
        isTrackFashionSet = setupTracksFashion(fashion, vehicle.typeDescriptor, isCrashedTrack)
        if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
            fashion.placingCompensationMatrix = vehicle.filter.placingCompensationMatrix
            fashion.physicsInfo = vehicle.filter.physicsInfo
            fashion.movementInfo = vehicle.filter.movementInfo
            vehicle.filter.placingOnGround = vehicle.filter.placingOnGround if isTrackFashionSet else False
        textures = {}
        for matKindName, texId in DecalMap.g_instance.getTextureSet(tracesCfg['textureSet']).iteritems():
            if matKindName != 'bump':
                for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[matKindName]:
                    textures[matKind] = texId

        fashion.setTrackTraces(tracesCfg['bufferPrefs'], textures, tracesCfg['centerOffset'], tracesCfg['size'])
    except:
        LOG_CURRENT_EXCEPTION()


def setupTracksFashion(fashion, vDesc, isCrashedTrack=False):
    retValue = True
    tracesCfg = vDesc.chassis['traces']
    tracksCfg = vDesc.chassis['tracks']
    wheelsCfg = vDesc.chassis['wheels']
    groundNodesCfg = vDesc.chassis['groundNodes']
    suspensionArmsCfg = vDesc.chassis['suspensionArms']
    trackNodesCfg = vDesc.chassis['trackNodes']
    trackParams = vDesc.chassis['trackParams']
    swingingCfg = vDesc.hull['swinging']
    splineDesc = vDesc.chassis['splineDesc']
    pp = tuple((p * m for p, m in zip(swingingCfg['pitchParams'], _PITCH_SWINGING_MODIFIERS)))
    fashion.setPitchSwinging(_ROOT_NODE_NAME, *pp)
    fashion.setRollSwinging(_ROOT_NODE_NAME, *swingingCfg['rollParams'])
    fashion.setShotSwinging(_ROOT_NODE_NAME, swingingCfg['sensitivityToImpulse'])
    splineLod = 9999
    if splineDesc is not None:
        splineLod = splineDesc['lodDist']
    fashion.setLods(tracesCfg['lodDist'], wheelsCfg['lodDist'], tracksCfg['lodDist'], swingingCfg['lodDist'], splineLod)
    fashion.setTracks(tracksCfg['leftMaterial'], tracksCfg['rightMaterial'], tracksCfg['textureScale'])
    if isCrashedTrack:
        return retValue
    else:
        for group in wheelsCfg['groups']:
            nodes = _createWheelsListByTemplate(group[3], group[1], group[2])
            fashion.addWheelGroup(group[0], group[4], nodes)

        for wheel in wheelsCfg['wheels']:
            fashion.addWheel(wheel[0], wheel[2], wheel[1], wheel[3], wheel[4])

        for groundGroup in groundNodesCfg['groups']:
            nodes = _createWheelsListByTemplate(groundGroup[3], groundGroup[1], groundGroup[2])
            retValue = not fashion.addGroundNodesGroup(nodes, groundGroup[0], groundGroup[4], groundGroup[5])

        for groundNode in groundNodesCfg['nodes']:
            retValue = not fashion.addGroundNode(groundNode[0], groundNode[1], groundNode[2], groundNode[3])

        for suspensionArm in suspensionArmsCfg:
            if suspensionArm[3] is not None and suspensionArm[4] is not None:
                retValue = not fashion.addSuspensionArm(suspensionArm[0], suspensionArm[1], suspensionArm[2], suspensionArm[3], suspensionArm[4])
            if suspensionArm[5] is not None and suspensionArm[6] is not None:
                retValue = not fashion.addSuspensionArmWheels(suspensionArm[0], suspensionArm[1], suspensionArm[2], suspensionArm[5], suspensionArm[6])

        if trackParams is not None:
            fashion.setTrackParams(trackParams['thickness'], trackParams['gravity'], trackParams['maxAmplitude'], trackParams['maxOffset'])
        for trackNode in trackNodesCfg['nodes']:
            leftSibling = trackNode[5]
            if leftSibling is None:
                leftSibling = ''
            rightSibling = trackNode[6]
            if rightSibling is None:
                rightSibling = ''
            fashion.addTrackNode(trackNode[0], trackNode[1], trackNode[2], trackNode[3], trackNode[4], leftSibling, rightSibling, trackNode[7], trackNode[8])

        fashion.initialUpdateTracks(1.0, 10.0)
        return retValue


def setupSplineTracks(fashion, vDesc, chassisModel, prereqs):
    splineDesc = vDesc.chassis['splineDesc']
    if splineDesc is not None:
        leftSpline = None
        rightSpline = None
        segmentModelLeft = segmentModelRight = segment2ModelLeft = segment2ModelRight = None
        modelName = splineDesc['segmentModelLeft']
        try:
            segmentModelLeft = prereqs[modelName]
        except Exception:
            LOG_ERROR("can't load track segment model <%s>" % modelName)

        modelName = splineDesc['segmentModelRight']
        try:
            segmentModelRight = prereqs[modelName]
        except Exception:
            LOG_ERROR("can't load track segment model <%s>" % modelName)

        modelName = splineDesc['segment2ModelLeft']
        if modelName is not None:
            try:
                segment2ModelLeft = prereqs[modelName]
            except Exception:
                LOG_ERROR("can't load track segment 2 model <%s>" % modelName)

        modelName = splineDesc['segment2ModelRight']
        if modelName is not None:
            try:
                segment2ModelRight = prereqs[modelName]
            except Exception:
                LOG_ERROR("can't load track segment 2 model <%s>" % modelName)

        if segmentModelLeft is not None and segmentModelRight is not None:
            if splineDesc['leftDesc'] is not None:
                leftSpline = BigWorld.wg_createSplineTrack(fashion, chassisModel, splineDesc['leftDesc'], splineDesc['segmentLength'], segmentModelLeft, splineDesc['segmentOffset'], segment2ModelLeft, splineDesc['segment2Offset'], _ROOT_NODE_NAME, splineDesc['atlasUTiles'], splineDesc['atlasVTiles'])
                if leftSpline is not None:
                    chassisModel.root.attach(leftSpline)
            if splineDesc['rightDesc'] is not None:
                rightSpline = BigWorld.wg_createSplineTrack(fashion, chassisModel, splineDesc['rightDesc'], splineDesc['segmentLength'], segmentModelRight, splineDesc['segmentOffset'], segment2ModelRight, splineDesc['segment2Offset'], _ROOT_NODE_NAME, splineDesc['atlasUTiles'], splineDesc['atlasVTiles'])
                if rightSpline is not None:
                    chassisModel.root.attach(rightSpline)
            fashion.setSplineTrack(leftSpline, rightSpline)
    return


def _restoreSoundParam(sound, paramName, paramValue):
    param = sound.param(paramName)
    if param is not None and param.value == 0.0 and param.value != paramValue:
        seekSpeed = param.seekSpeed
        param.seekSpeed = 0
        param.value = paramValue
        param.seekSpeed = seekSpeed
    return


def _seekSoundParam(sound, paramName, paramValue):
    param = sound.param(paramName)
    if param is not None and param.value != paramValue:
        seekSpeed = param.seekSpeed
        param.seekSpeed = 0
        param.value = paramValue
        param.seekSpeed = seekSpeed
    return


def _validateCfgPos(srcModelDesc, dstModelDesc, cfgPos, paramName, vehicle, state):
    invMat = Math.Matrix(srcModelDesc['model'].root)
    invMat.invert()
    invMat.preMultiply(Math.Matrix(dstModelDesc['_node']))
    realOffset = invMat.applyToOrigin()
    length = (realOffset - cfgPos).length
    if length > 0.01 and not _almostZero(realOffset.length):
        modelState = srcModelDesc['_stateFunc'](vehicle, state)
        from debug_utils import LOG_WARNING
        LOG_WARNING('%s parameter is incorrect. \n Note: it must be <%s>.\nPlayer: %s; Model: %s' % (paramName,
         realOffset,
         vehicle.publicInfo['name'],
         modelState))
        dstModelDesc['model'].visibleAttachments = True
        dstModelDesc['model'].visible = False


class VehicleDamageState(object):
    __healthToStateMap = {0: 'destruction',
     constants.SPECIAL_VEHICLE_HEALTH.AMMO_BAY_DESTROYED: 'ammoBayBurnOff',
     constants.SPECIAL_VEHICLE_HEALTH.TURRET_DETACHED: 'ammoBayExplosion',
     constants.SPECIAL_VEHICLE_HEALTH.FUEL_EXPLODED: 'fuelExplosion',
     constants.SPECIAL_VEHICLE_HEALTH.DESTR_BY_FALL_RAMMING: 'rammingDestruction'}

    @staticmethod
    def getState(health, isCrewActive, isUnderWater):
        if health > 0:
            if not isCrewActive:
                if isUnderWater:
                    return 'submersionDeath'
                else:
                    return 'crewDeath'
            else:
                return 'alive'
        else:
            return VehicleDamageState.__healthToStateMap[health]

    __stateToModelEffectsMap = {'ammoBayExplosion': ('exploded', None),
     'ammoBayBurnOff': ('destroyed', None),
     'fuelExplosion': ('destroyed', 'fuelExplosion'),
     'destruction': ('destroyed', 'destruction'),
     'crewDeath': ('undamaged', 'crewDeath'),
     'rammingDestruction': ('destroyed', 'rammingDestruction'),
     'submersionDeath': ('undamaged', 'submersionDeath'),
     'alive': ('undamaged', 'empty')}

    @staticmethod
    def getStateParams(state):
        return VehicleDamageState.__stateToModelEffectsMap[state]

    state = property(lambda self: self.__state)
    model = property(lambda self: self.__model)
    effect = property(lambda self: self.__effect)

    @staticmethod
    def isDamagedModel(model):
        return model != 'undamaged'

    @staticmethod
    def isExplodedModel(model):
        return model == 'exploded'

    def __init__(self):
        self.__state = None
        self.__model = None
        self.__effect = None
        return

    def update(self, health, isCrewActive, isUnderWater):
        self.__state = VehicleDamageState.getState(health, isCrewActive, isUnderWater)
        params = VehicleDamageState.getStateParams(self.__state)
        self.__model, self.__effect = params
