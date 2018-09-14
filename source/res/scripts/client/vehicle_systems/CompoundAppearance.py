# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/CompoundAppearance.py
import functools
import random
import math
import DataLinks
from AvatarInputHandler import ShakeReason
import Math
from VehicleUtils import VehicleDamageState, _setupVehicleFashion, setupSplineTracks
from vehicle_systems.components.CrashedTracks import CrashedTrackController
from debug_utils import *
from vehicle_systems.tankStructure import VehiclePartsTuple, TankNodeNames
from constants import VEHICLE_PHYSICS_MODE
import constants
from OcclusionDecal import OcclusionDecal
from ShadowForwardDecal import ShadowForwardDecal
from helpers.CallbackDelayer import CallbackDelayer
from helpers import bound_effects
from helpers.EffectsList import EffectsListPlayer, SpecialKeyPointNames
import items.vehicles
from Event import Event
import material_kinds
from VehicleStickers import VehicleStickers
import AuxiliaryFx
import TriggersManager
from TriggersManager import TRIGGER_TYPE
from Vibroeffects.ControllersManager import ControllersManager as VibrationControllersManager
from LightFx.LightControllersManager import LightControllersManager as LightFxControllersManager
import LightFx.LightManager
import BattleReplay
from vehicle_systems import camouflages
from vehicle_systems.tankStructure import TankPartNames
from vehicle_systems.assembly_utility import ComponentSystem, ComponentDescriptor, AutoProperty
from vehicle_systems import model_assembler
from CustomEffectManager import EffectSettings
_VEHICLE_APPEAR_TIME = 0.2
_ROOT_NODE_NAME = 'V'
_GUN_RECOIL_NODE_NAME = 'G'
_PERIODIC_TIME = 0.25
_PERIODIC_TIME_ENGINE = 0.1
_LOD_DISTANCE_EXHAUST = 200.0
_LOD_DISTANCE_TRAIL_PARTICLES = 100.0
_MOVE_THROUGH_WATER_SOUND = '/vehicles/tanks/water'
_CAMOUFLAGE_MIN_INTENSITY = 1.0
_PITCH_SWINGING_MODIFIERS = (0.9, 1.88, 0.3, 4.0, 1.0, 1.0)
_MIN_DEPTH_FOR_HEAVY_SPLASH = 0.5
MAX_DISTANCE = 500
_MATKIND_COUNT = 3
_HIGHRLITER_MARK = 110

class CompoundAppearance(ComponentSystem, CallbackDelayer):
    distanceFromPlayer = property(lambda self: self.__distanceFromPlayer)
    compoundModel = property(lambda self: self.__compoundModel)
    boundEffects = property(lambda self: self.__boundEffects)
    fashion = property(lambda self: self.__fashions.chassis)

    def __setFashions(self, fashions):
        self.__fashions = fashions
        self.__fashion = fashions.chassis
        setupList = []
        if self.__vehicle.isTurretDetached:
            setupList.append(fashions.chassis)
            setupList.append(fashions.hull)
        else:
            setupList = fashions.stripEmpty()
        self.__compoundModel.setupFashions(setupList)

    fashions = property(lambda self: self.__fashions, __setFashions)
    terrainMatKind = property(lambda self: self.__currTerrainMatKind)
    isInWater = property(lambda self: self.__isInWater)
    isUnderwater = property(lambda self: self.__isUnderWater)
    waterHeight = property(lambda self: self.__waterHeight)
    damageState = property(lambda self: self.__currentDamageState)
    frameTimeStamp = 0
    engineMode = property(lambda self: self.__engineMode)
    rightTrackScroll = property(lambda self: self.__rightTrackScroll)
    leftTrackScroll = property(lambda self: self.__leftTrackScroll)
    gunSound = property(lambda self: self.__gunSound)
    isPillbox = property(lambda self: self.__isPillbox)
    rpm = property(lambda self: self.__rpm)
    gear = property(lambda self: self.__gear)
    trackScrollController = property(lambda self: self.__trackScrollCtl)
    gunLength = property(lambda self: self.__gunLength)
    detailedEngineState = ComponentDescriptor()
    engineAudition = ComponentDescriptor()
    trackCrashAudition = ComponentDescriptor()
    customEffectManager = ComponentDescriptor()
    highlighter = ComponentDescriptor()
    trailEffects = ComponentDescriptor()
    exhaustEffects = ComponentDescriptor()
    gunRecoil = AutoProperty()
    swingingAnimator = AutoProperty()
    markTurret = ComponentDescriptor()

    def __init__(self):
        CallbackDelayer.__init__(self)
        ComponentSystem.__init__(self)
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
        self.__effectsPlayer = None
        self.__engineMode = (0, 0)
        self.__swingMoveFlags = 0
        self.__currTerrainMatKind = [-1] * _MATKIND_COUNT
        self.__periodicTimerID = None
        self.__leftLightRotMat = None
        self.__rightLightRotMat = None
        self.__leftFrontLight = None
        self.__rightFrontLight = None
        self.__prevVelocity = None
        self.__prevTime = None
        self.__isPillbox = False
        self.__maxClimbAngle = math.radians(20.0)
        self.__chassisOcclusionDecal = OcclusionDecal()
        self.__chassisShadowForwardDecal = ShadowForwardDecal()
        self.__splodge = None
        self.__vehicleStickers = None
        self.__physicLoad = 0.0
        self.onModelChanged = Event()
        self.__speedInfo = Math.Vector4(0.0, 0.0, 0.0, 0.0)
        self.__wasOnSoftTerrain = False
        self.__vehicleMatrixProv = None
        self.__typeDesc = None
        self.__leftTrackScroll = 0.0
        self.__rightTrackScroll = 0.0
        self.__distanceFromPlayer = 0.0
        self.__fashions = None
        self.__compoundModel = None
        self.__boundEffects = None
        self.__swingingAnimator = None
        self.__splineTracks = None
        self.__gear = 127
        self.__rpm = 0.0
        self.__customEffectManager = None
        self.__exhaustEffects = None
        self.__trailEffects = None
        self.__trackScrollCtl = BigWorld.PyTrackScroll()
        self.__gunLength = 0.0
        self.__damageApplicationPoint = None
        self.__wreckedWheels = None
        return

    def prerequisites(self, vehicle):
        self.__currentDamageState.update(vehicle.health, vehicle.isCrewActive, self.__isUnderWater)
        out = []
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
        self.__trackScrollCtl = None
        if self.__vehicle is None:
            return
        else:
            ComponentSystem.destroy(self)
            self.__vehicleStickers.detach()
            vehicle = self.__vehicle
            self.__vehicle = None
            self.__vehicleMatrixProv = None
            self.__typeDesc = None
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
            if self.__boundEffects is not None:
                self.__boundEffects.destroy()
            BigWorld.player().inputHandler.removeVehicleFromCameraCollider(vehicle)
            self.__filter = None
            vehicle.filter = self.__originalFilter
            self.__originalFilter = None
            self.__vehicleStickers = None
            self.onModelChanged = None
            if self.__periodicTimerID is not None:
                BigWorld.cancelCallback(self.__periodicTimerID)
                self.__periodicTimerID = None
            self.__crashedTracksCtrl.destroy()
            self.__crashedTracksCtrl = None
            self.__chassisOcclusionDecal.destroy()
            self.__chassisOcclusionDecal = None
            self.__chassisShadowForwardDecal.destroy()
            self.__chassisShadowForwardDecal = None
            self.__compoundModel = None
            CallbackDelayer.destroy(self)
            return

    def preStart(self, typeDesc):
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

        self.__maxClimbAngle = math.acos(typeDesc.physics['minPlaneNormalY'])
        self.setupGunMatrixTargets()

    def start(self, vehicle, prereqs=None):
        self.__vehicle = vehicle
        player = BigWorld.player()
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
        vehicle.filter.enableStabilisedMatrix(vehicle.isPlayerVehicle)
        self.__createStickers(prereqs)
        self.__compoundModel = prereqs[self.__typeDesc.name]
        self.__compoundModel.isHighPriorityReflection = vehicle.isPlayerVehicle
        self.__boundEffects = bound_effects.ModelBoundEffects(self.__compoundModel)
        fashions = camouflages.prepareFashions(self.__typeDesc, self.__currentDamageState.isCurrentModelDamaged, self.__getCamouflageParams(vehicle)[0], vehicle.physicsMode == VEHICLE_PHYSICS_MODE.DETAILED)
        if not self.__currentDamageState.isCurrentModelDamaged:
            _setupVehicleFashion(self, fashions[0], self.__vehicle)
        self.__compoundModel.setupFashions(fashions)
        fashions = camouflages.applyCamouflage(self.__typeDesc, fashions, self.__currentDamageState.isCurrentModelDamaged, self.__getCamouflageParams(vehicle)[0])
        fashions = camouflages.applyRepaint(self.__typeDesc, fashions)
        self.fashions = fashions
        self.__setupModels(True)
        if not VehicleDamageState.isDamagedModel(self.__currentDamageState.modelState):
            self.__splineTracks = setupSplineTracks(self.__fashion, self.__vehicle.typeDescriptor, self.__compoundModel, prereqs)
        if self.__currentDamageState.effect is not None:
            self.__playEffect(self.__currentDamageState.effect, SpecialKeyPointNames.STATIC)
        toCrashedFashion = self.__fashion
        if self.__currentDamageState.isCurrentModelDamaged:
            toCrashedFashion = None
            self.__trackScrollCtl = None
        else:
            self.__trackScrollCtl.setData(self.__vehicle.filter, self.fashions.chassis)
        self.__crashedTracksCtrl = CrashedTrackController(vehicle.typeDescriptor, vehicle, toCrashedFashion, self.__vehicle.isPlayerVehicle)
        if vehicle.isAlive() and self.__vehicle.isPlayerVehicle:
            self.__vibrationsCtrl = VibrationControllersManager()
            if LightFx.LightManager.g_instance is not None and LightFx.LightManager.g_instance.isEnabled():
                self.__lightFxCtrl = LightFxControllersManager(self.__vehicle)
            if AuxiliaryFx.g_instance is not None:
                self.__auxiliaryFxCtrl = AuxiliaryFx.g_instance.createFxController(self.__vehicle)
        if not BattleReplay.isPlaying():
            self.compoundModel.stipple = True
            self.delayCallback(_VEHICLE_APPEAR_TIME, self.__disableStipple)
        self.__vehicleMatrixProv = vehicle.model.matrix
        return

    def startSystems(self):
        self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME, self.__onPeriodicTimer)
        if self.__trackScrollCtl is not None:
            self.__trackScrollCtl.start()
        self.detailedEngineState.start(self.__vehicle)
        if self.__vehicle.isPlayerVehicle:
            self.highlighter.highlight(True)
            self.delayCallback(_PERIODIC_TIME_ENGINE, self.__onPeriodicTimerEngine)
        elif self.__vehicle.typeDescriptor.name.find('uk:GB89_Mark') > -1 and _HIGHRLITER_MARK >= 0:
            self.highlighter.highlight(True)
            self.highlighter.lock(True)
        return

    def set_gear(self, gear):
        self.__gear = gear

    def set_normalisedRPM(self, rpm):
        self.__rpm = rpm

    def getGunSoundObj(self):
        if self.engineAudition is not None:
            return self.engineAudition.getGunSoundObj()
        else:
            return
            return

    def showStickers(self, show):
        self.__vehicleStickers.show = show

    def updateTurretVisibility(self):
        self.__requestModelsRefresh()

    def changeVisibility(self, modelVisible):
        self.compoundModel.visible = modelVisible
        self.showStickers(modelVisible)
        self.__crashedTracksCtrl.setVisible(modelVisible)

    def changeDrawPassVisibility(self, visibilityMask):
        colorPassEnabled = visibilityMask & BigWorld.ColorPassBit != 0
        self.compoundModel.visible = visibilityMask
        self.compoundModel.skipColorPass = not colorPassEnabled
        self.showStickers(colorPassEnabled)
        if self.__crashedTracksCtrl is not None:
            self.__crashedTracksCtrl.setVisible(visibilityMask)
        return

    def onVehicleHealthChanged(self):
        vehicle = self.__vehicle
        if not vehicle.isAlive():
            self.highlighter.lock(False)
            self.highlighter.highlight(False)
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
            if currentState.effect is not None:
                self.__playEffect(currentState.effect)
            if vehicle.health <= 0:
                BigWorld.player().inputHandler.onVehicleDeath(vehicle, currentState.state == 'ammoBayExplosion')
                self.processVehicleDeath(currentState)
                self.__requestModelsRefresh()
        return

    @ComponentSystem.groupCall
    def processVehicleDeath(self, vehicleDamageState):
        pass

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
        if self.exhaustEffects:
            self.__updateExhaust()
        if self.__trackScrollCtl is not None:
            self.__trackScrollCtl.setMode(self.__engineMode)
        if BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            isOldPhysicsMode = self.__vehicle.physicsMode == VEHICLE_PHYSICS_MODE.STANDARD
            if isOldPhysicsMode and forceSwinging:
                flags = mode[1]
                prevFlags = self.__swingMoveFlags
                swingingAnimator = self.__swingingAnimator
                if swingingAnimator is not None:
                    moveMask = 3
                    rotMask = 12
                    if flags & moveMask ^ prevFlags & moveMask:
                        swingPeriod = 2.0
                        if flags & 1:
                            swingingAnimator.accelSwingingDirection = -1
                        elif flags & 2:
                            swingingAnimator.accelSwingingDirection = 1
                        else:
                            swingingAnimator.accelSwingingDirection = 0
                    elif not flags & moveMask and flags & rotMask ^ prevFlags & rotMask:
                        swingPeriod = 1.0
                        swingingAnimator.accelSwingingDirection = 0
                    else:
                        swingPeriod = 0.0
                    if swingPeriod > swingingAnimator.accelSwingingPeriod:
                        swingingAnimator.accelSwingingPeriod = swingPeriod
                self.__swingMoveFlags = flags
            return

    def stopSwinging(self):
        if self.__swingingAnimator is not None:
            self.__swingingAnimator.accelSwingingPeriod = 0.0
        return

    def removeDamageSticker(self, code):
        self.__vehicleStickers.delDamageSticker(code)

    def addDamageSticker(self, code, componentName, stickerID, segStart, segEnd):
        self.__vehicleStickers.addDamageSticker(code, componentName, stickerID, segStart, segEnd)

    def storeHitPoint(self, pointVector):
        self.__damageApplicationPoint = pointVector

    def receiveShotImpulse(self, dir, impulse):
        if BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        if not VehicleDamageState.isDamagedModel(self.__currentDamageState.modelState):
            self.__swingingAnimator.receiveShotImpulse(dir, impulse)
            self.__crashedTracksCtrl.receiveShotImpulse(dir, impulse)

    def recoil(self, shootingExtra):
        gunNode = self.compoundModel.node(TankNodeNames.GUN_INCLINATION)
        impulseDir = Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1))
        impulseValue = self.__typeDesc.gun['impulse']
        self.receiveShotImpulse(impulseDir, impulseValue)
        if shootingExtra is self.__typeDesc.extrasDict['shoot']:
            self.__gunRecoil.recoil()
        else:
            self.markTurret.gunRecoil.recoil()
        node = self.compoundModel.node('HP_gunFire')
        gunPos = Math.Matrix(node).translation
        BigWorld.player().inputHandler.onVehicleShaken(self.__vehicle, gunPos, impulseDir, self.__typeDesc.shot['shell']['caliber'], ShakeReason.OWN_SHOT_DELAYED)

    def addCrashedWheel(self):
        if 'wheeledVehicle' not in self.__vehicle.typeDescriptor.type.tags or not self.__vehicle.isAlive():
            return
        else:
            if self.__damageApplicationPoint is not None:
                isLeft = self.__damageApplicationPoint.x < 0
                if isLeft and not self.__crashedTracksCtrl.isLeftTrackBroken() or not isLeft and not self.__crashedTracksCtrl.isRightTrackBroken():
                    return
                isLeading = self.__damageApplicationPoint.z < 1
                if self.__wreckedWheels is None:
                    self.__wreckedWheels = []
                self.__wreckedWheels.append((isLeft, isLeading))
                self.__crashedTracksCtrl.addWheel(isLeft, isLeading)
                self.__damageApplicationPoint = None
            return

    def addCrashedTrack(self, isLeft):
        if not self.__vehicle.isAlive():
            return
        else:
            if 'wheeledVehicle' in self.__vehicle.typeDescriptor.type.tags:
                if self.__damageApplicationPoint is not None:
                    isLeading = self.__damageApplicationPoint.z < 0
                else:
                    isLeading = False
                if self.__wreckedWheels is None:
                    self.__wreckedWheels = []
                self.__wreckedWheels.append((isLeft, isLeading))
                self.__crashedTracksCtrl.addWheel(isLeft, isLeading)
            self.__crashedTracksCtrl.addTrack(isLeft)
            if not self.__vehicle.isEnteringWorld and self.trackCrashAudition:
                self.trackCrashAudition.playCrashSound(isLeft, False, 'wheeledVehicle' in self.__vehicle.typeDescriptor.type.tags)
            return

    def delCrashedTrack(self, isLeft):
        if 'wheeledVehicle' in self.__vehicle.typeDescriptor.type.tags:
            if self.__wreckedWheels is not None:
                wheelsToRemove = []
                for wheel in self.__wreckedWheels:
                    if wheel[0] == isLeft:
                        wheelsToRemove.append(wheel)

                for wheel in wheelsToRemove:
                    self.__wreckedWheels.remove(wheel)
                    self.__crashedTracksCtrl.delWheel(wheel[0], wheel[1])

        self.__crashedTracksCtrl.delTrack(isLeft)
        if not self.__vehicle.isEnteringWorld and self.trackCrashAudition and self.__vehicle.isPlayerVehicle:
            self.trackCrashAudition.playCrashSound(isLeft, True, 'wheeledVehicle' in self.__vehicle.typeDescriptor.type.tags)
        return

    def __requestModelsRefresh(self):
        currentModelState = self.__currentDamageState.modelState
        assembler = model_assembler.prepareCompoundAssembler(self.__typeDesc, currentModelState, self.__vehicle.spaceID, self.__vehicle.isTurretDetached)
        BigWorld.loadResourceListBG([assembler], functools.partial(self.__onModelsRefresh, currentModelState))

    def __onModelsRefresh(self, modelState, resourceList):
        if self.__vehicle is None:
            return
        elif modelState != self.__currentDamageState.modelState:
            self.__requestModelsRefresh()
            return
        else:
            BigWorld.player().inputHandler.removeVehicleFromCameraCollider(self.__vehicle)
            self.__chassisOcclusionDecal.detach()
            self.__gunFireNode = None
            if self.exhaustEffects:
                self.__attachExhaust(False)
            if self.trailEffects:
                self.__trailEffects.stopEffects()
            if self.customEffectManager:
                self.__customEffectManager.stop()
            self.__crashedTracksCtrl.reset()
            self.__compoundModel = resourceList[self.__typeDesc.name]
            if self.__currentDamageState.isCurrentModelDamaged:
                self.fashions = VehiclePartsTuple(None, None, None, None)
                self.swingingAnimator = None
                self.gunRecoil = None
                self.__trackScrollCtl = None
            self.__setupModels(False)
            actualFilter = self.__vehicle.filter
            self.__vehicle.filter = self.__originalFilter
            self.__vehicle.filter = actualFilter
            from vehicle_systems.vehicle_assembler import setupUsualTurret
            if self.fashion is not None:
                lodLink = DataLinks.createFloatLink(self.fashion, 'lastLod')
            else:
                lodLink = None
            setupUsualTurret(self, self.__vehicle.typeDescriptor, lodLink)
            return

    def __setupModels(self, isFirstInit=False):
        vehicle = self.__vehicle
        self.__chassisShadowForwardDecal.detach()
        self.__linkCompound()
        if not isFirstInit:
            self.__reattachComponents()
        if not self.__currentDamageState.isCurrentModelDamaged:
            self.__attachStickers()
            self.__gunFireNode = self.__compoundModel.node('HP_gunFire')
        else:
            if self.exhaustEffects:
                self.exhaustEffects.destroy()
            self.__attachStickers(items.vehicles.g_cache.commonConfig['miscParams']['damageStickerAlpha'], True)
        self.__chassisShadowForwardDecal.attach(vehicle, self.__compoundModel)
        _, self.__gunLength = self.__computeVehicleHeight()
        self.onModelChanged()
        if 'observer' in vehicle.typeDescriptor.type.tags:
            self.__compoundModel.visible = False
        else:
            self.__chassisOcclusionDecal.attach(vehicle, self.__compoundModel)
        if MAX_DISTANCE > 0:
            transform = vehicle.typeDescriptor.chassis['AODecals'][0]
            self.__attachSplodge(BigWorld.Splodge(transform, MAX_DISTANCE, vehicle.typeDescriptor.chassis['hullPosition'].y))

    def __reattachComponents(self):
        self.__boundEffects.reattachTo(self.__compoundModel)
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.reattachTo(self.__compoundModel)
        if self.engineAudition is not None:
            self.engineAudition.reattachTo(self.__compoundModel)
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
        self.__effectsPlayer = EffectsListPlayer(effects[1], effects[0], showShockWave=vehicle.isPlayerVehicle, showFlashBang=vehicle.isPlayerVehicle, isPlayer=vehicle.isPlayerVehicle, showDecal=enableDecal, start=vehicle.position + Math.Vector3(0.0, -1.0, 0.0), end=vehicle.position + Math.Vector3(0.0, 1.0, 0.0), entity_id=vehicle.id)
        self.__effectsPlayer.play(self.__compoundModel, *modifs)

    EVENT_CAMOUFLAGES = {'ussr:T62A_sport': (95, 94),
     'usa:M24_Chaffee_GT': (82, 83),
     'uk:GB90_Lanchester_Armored_Car': (137, 136)}

    def __getCamouflageParams(self, vehicle):
        vDesc = vehicle.typeDescriptor
        vehicleInfo = BigWorld.player().arena.vehicles.get(vehicle.id)
        if vehicleInfo is not None:
            camouflageIdPerTeam = CompoundAppearance.EVENT_CAMOUFLAGES.get(vDesc.name)
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
                     'silver': 57},
                 6: {'black': 133,
                     'gold': 134,
                     'red': 135,
                     'silver': 136},
                 7: {'black': 141,
                     'gold': 142,
                     'red': 143,
                     'silver': 144},
                 8: {'black': 154,
                     'gold': 155,
                     'red': 156,
                     'silver': 157}}
                camouflIds = camouflIdsByNation.get(vDesc.type.customizationNationID)
                if camouflIds is not None:
                    ret = camouflIds.get(camouflagePseudoname)
                    if ret is not None:
                        return (ret, time.time(), 100.0)
        arenaType = BigWorld.player().arena.arenaType
        camouflageKind = arenaType.vehicleCamouflageKind
        return vDesc.camouflages[camouflageKind]

    def __stopEffects(self):
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.stop()
        self.__effectsPlayer = None
        return

    def __calcIsUnderwater(self):
        if not self.__isInWater:
            return False
        turretOffs = self.__vehicle.typeDescriptor.chassis['hullPosition'] + self.__vehicle.typeDescriptor.hull['turretPositions'][0]
        turretOffsetMat = Math.Matrix()
        turretOffsetMat.setTranslate(turretOffs)
        turretJointMat = Math.Matrix(self.__vehicle.matrix)
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
                collRes = BigWorld.wg_collideSegment(self.__vehicle.spaceID, waterHitPoint, waterHitPoint + (0.0, -_MIN_DEPTH_FOR_HEAVY_SPLASH, 0.0), 18, 8)
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
        if self.__trackScrollCtl is not None:
            self.__trackScrollCtl.setExternal(leftScroll, rightScroll)
        return

    def __onPeriodicTimerEngine(self):
        if self.detailedEngineState is None or self.engineAudition is None:
            return
        else:
            self.detailedEngineState.refresh(_PERIODIC_TIME_ENGINE)
            self.engineAudition.tick()
            return _PERIODIC_TIME_ENGINE

    def __onPeriodicTimer(self):
        timeStamp = BigWorld.wg_getFrameTimestamp()
        if CompoundAppearance.frameTimeStamp >= timeStamp:
            self.__periodicTimerID = BigWorld.callback(0.0, self.__onPeriodicTimer)
            return
        else:
            CompoundAppearance.frameTimeStamp = timeStamp
            self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME, self.__onPeriodicTimer)
            if self.__isPillbox or self.__vehicle is None:
                return
            vehicle = self.__vehicle
            self.__speedInfo = vehicle.speedInfo.value
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
                if self.__fashion is None:
                    return
                self.__updateCurrTerrainMatKinds()
                if not self.__vehicle.isPlayerVehicle and self.engineAudition is not None:
                    self.engineAudition.tick()
                self.__updateEffectsLOD()
                if self.customEffectManager:
                    self.__customEffectManager.update()
                if self.trailEffects:
                    self.__trailEffects.update()
                if self.exhaustEffects:
                    self.__updateExhaust()
                self.__vehicle.filter.placingOnGround = not self.__fashion.suspensionWorking
                if 'wheeledVehicle' in self.__vehicle.typeDescriptor.type.tags and (self.__crashedTracksCtrl.isLeftTrackBroken or self.__crashedTracksCtrl.isRightTrackBroken) and self.__damageApplicationPoint is not None:
                    self.addCrashedWheel()
            except:
                LOG_CURRENT_EXCEPTION()

            return

    def __updateEffectsLOD(self):
        enableExhaust = self.__distanceFromPlayer <= _LOD_DISTANCE_EXHAUST
        if self.exhaustEffects:
            if enableExhaust != self.__exhaustEffects.enabled:
                self.__exhaustEffects.enable(enableExhaust and not self.__isUnderWater)
        enableTrails = self.__distanceFromPlayer <= _LOD_DISTANCE_TRAIL_PARTICLES and BigWorld.wg_isVehicleDustEnabled()
        if self.trailEffects:
            self.__trailEffects.enable(enableTrails)
        if self.customEffectManager:
            self.__customEffectManager.enable(enableTrails, EffectSettings.SETTING_DUST)
            self.__customEffectManager.enable(enableExhaust, EffectSettings.SETTING_EXHAUST)
        if self.highlighter.locked and _HIGHRLITER_MARK > 0.0:
            self.highlighter.highlight(self.__distanceFromPlayer >= _HIGHRLITER_MARK, ignoreLock=True)

    def __updateCurrTerrainMatKinds(self):
        leftNode = self.compoundModel.node(TankNodeNames.TRACK_LEFT_MID)
        rightNode = self.compoundModel.node(TankNodeNames.TRACK_RIGHT_MID)
        testPoints = (Math.Matrix(leftNode).translation, Math.Matrix(rightNode).translation, self.__vehicle.position)
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

    def __linkCompound(self):
        vehicle = self.__vehicle
        vehicle.model = None
        vehicle.model = self.__compoundModel
        vehicleMatrix = vehicle.matrix
        self.__compoundModel.matrix = vehicleMatrix
        if vehicle.isPlayerVehicle:
            player = BigWorld.player()
            if player.inputHandler is not None:
                player.inputHandler.addVehicleToCameraCollider(vehicle)
        return

    def __attachExhaust(self, attach):
        if attach:
            self.__exhaustEffects.attach(self.__compoundModel, self.__vehicle.typeDescriptor.hull['exhaust'])
        else:
            self.__exhaustEffects.detach()

    def __updateExhaust(self):
        if self.__exhaustEffects.enabled == self.__isUnderWater:
            self.__exhaustEffects.enable(not self.__isUnderWater)
        self.__exhaustEffects.changeExhaust(self.__engineMode[0], self.detailedEngineState.rpm)

    def __createStickers(self, prereqs):
        insigniaRank = self.__vehicle.publicInfo['marksOnGun']
        self.__vehicleStickers = VehicleStickers(self.__typeDesc, insigniaRank)
        clanID = BigWorld.player().arena.vehicles[self.__vehicle.id]['clanDBID']
        self.__vehicleStickers.setClanID(clanID)

    def __attachStickers(self, alpha=1.0, emblemsOnly=False):
        try:
            self.__vehicleStickers.alpha = alpha
            self.__vehicleStickers.attach(self.compoundModel, self.__currentDamageState.isCurrentModelDamaged, not emblemsOnly)
        except:
            LOG_CURRENT_EXCEPTION()

    def __attachSplodge(self, splodge):
        node = self.__compoundModel.node(TankPartNames.HULL)
        if splodge is not None and self.__splodge is None:
            self.__splodge = splodge
            node.attach(splodge)
        return

    def __disableStipple(self):
        self.compoundModel.stipple = False

    def __computeVehicleHeight(self):
        desc = self.__typeDesc
        turretBBox = desc.turret['hitTester'].bbox
        gunBBox = desc.gun['hitTester'].bbox
        hullBBox = desc.hull['hitTester'].bbox
        hullTopY = desc.chassis['hullPosition'][1] + hullBBox[1][1]
        turretTopY = desc.chassis['hullPosition'][1] + desc.hull['turretPositions'][0][1] + turretBBox[1][1]
        gunTopY = desc.chassis['hullPosition'][1] + desc.hull['turretPositions'][0][1] + desc.turret['gunPosition'][1] + gunBBox[1][1]
        return (max(hullTopY, max(turretTopY, gunTopY)), math.fabs(gunBBox[1][2] - gunBBox[0][2]))

    def setupGunMatrixTargets(self, target=None):
        if target is None:
            target = self.__filter
        self.turretMatrix.target = target.turretMatrix
        self.gunMatrix.target = target.gunMatrix
        return

    def assembleStipple(self):
        compound = self.compoundModel
        compound.matrix = Math.Matrix(compound.matrix)
        hullNode = compound.node(TankPartNames.HULL)
        compound.node(TankPartNames.HULL, hullNode.localMatrix)
        turretRotation = compound.node(TankPartNames.TURRET)
        if turretRotation is not None:
            compound.node(TankPartNames.TURRET, turretRotation.localMatrix)
        gunInclination = compound.node(TankNodeNames.GUN_INCLINATION)
        if gunInclination is not None:
            compound.node(TankNodeNames.GUN_INCLINATION, gunInclination.localMatrix)
        return

    def setSteeringAngle(self, angle):
        if self.__fashion is not None:
            self.__fashion.addSteering(angle)
        return
