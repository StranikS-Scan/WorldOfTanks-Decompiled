# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/CompoundAppearance.py
import random
import math
from math import tan
import BigWorld
import Math
import constants
import items.vehicles
import BattleReplay
import material_kinds
import DataLinks
import Vehicular
from Event import Event
from CustomEffectManager import EffectSettings
from helpers.EffectMaterialCalculation import calcEffectMaterialIndex
from AvatarInputHandler.aih_constants import ShakeReason
from VehicleStickers import VehicleStickers
from svarog_script.auto_properties import AutoProperty
from vehicle_systems.components import engine_state
from vehicle_systems.stricted_loading import makeCallbackWeak, loadingPriority
from vehicle_systems.vehicle_damage_state import VehicleDamageState
from vehicle_systems.components.CrashedTracks import CrashedTrackController
from vehicle_systems.tankStructure import VehiclePartsTuple, TankNodeNames, ColliderTypes, TankPartNames, TankPartIndexes, ModelsSetParams
from vehicle_systems.components.vehicleDecal import VehicleDecal
from helpers.CallbackDelayer import CallbackDelayer
from helpers import bound_effects
from helpers.EffectsList import EffectsListPlayer, SpecialKeyPointNames
from vehicle_systems import camouflages
from svarog_script.py_component_system import ComponentDescriptor, ComponentSystem
from vehicle_systems import model_assembler
from gui.shared.gui_items.customization.outfit import Outfit
_VEHICLE_APPEAR_TIME = 0.2
_ROOT_NODE_NAME = 'V'
_GUN_RECOIL_NODE_NAME = 'G'
_PERIODIC_TIME = 0.25
_PERIODIC_TIME_ENGINE = 0.1
_PERIODIC_TIME_DIRT = ((0.05, 0.25), (10.0, 400.0))
_DIRT_ALPHA = tan((_PERIODIC_TIME_DIRT[0][1] - _PERIODIC_TIME_DIRT[0][0]) / (_PERIODIC_TIME_DIRT[1][1] - _PERIODIC_TIME_DIRT[1][0]))
_LOD_DISTANCE_EXHAUST = 200.0
_LOD_DISTANCE_TRAIL_PARTICLES = 100.0
_LOD_DISTANCE_TERRAIN_MATKIND_UPDATE = 120.0
_MOVE_THROUGH_WATER_SOUND = '/vehicles/tanks/water'
_CAMOUFLAGE_MIN_INTENSITY = 1.0
_PITCH_SWINGING_MODIFIERS = (0.9, 1.88, 0.3, 4.0, 1.0, 1.0)
_MIN_DEPTH_FOR_HEAVY_SPLASH = 0.5
MAX_DISTANCE = 500
_MATKIND_COUNT = 3
_DEFAULT_STICKERS_ALPHA = 1.0

class CompoundAppearance(ComponentSystem, CallbackDelayer):
    compoundModel = property(lambda self: self.__compoundModel)
    boundEffects = property(lambda self: self.__boundEffects)
    fashion = property(lambda self: self.__fashions.chassis)
    typeDescriptor = property(lambda self: self.__typeDesc)
    id = property(lambda self: self.__vID)
    isAlive = property(lambda self: self.__isAlive)
    isObserver = property(lambda self: self.__isObserver)

    def __setFashions(self, fashions, isTurretDetached=False):
        self.__fashions = fashions
        self.__fashion = fashions.chassis
        if isTurretDetached:
            self.__compoundModel.setupFashions((fashions.chassis, fashions.hull))
        else:
            self.__compoundModel.setupFashions(fashions)

    fashions = property(lambda self: self.__fashions, __setFashions)
    terrainMatKind = property(lambda self: self.__currTerrainMatKind)
    terrainEffectMaterialNames = property(lambda self: self.__terrainEffectMaterialNames)
    isInWater = property(lambda self: self.waterSensor.isInWater)
    isUnderwater = property(lambda self: self.waterSensor.isUnderWater)
    waterHeight = property(lambda self: self.waterSensor.waterHeight)
    damageState = property(lambda self: self.__currentDamageState)
    modelsSetParams = property(lambda self: ModelsSetParams(self.__outfit.modelsSet, self.__currentDamageState.modelState))
    frameTimeStamp = 0
    rightTrackScroll = property(lambda self: self.__rightTrackScroll)
    leftTrackScroll = property(lambda self: self.__leftTrackScroll)
    splineTracks = property(lambda self: self.__splineTracks)
    activated = property(lambda self: self.__activated)
    isFlying = property(lambda self: self.flyingInfoProvider is not None and self.flyingInfoProvider.isFlying)
    isLeftSideFlying = property(lambda self: self.flyingInfoProvider is not None and self.flyingInfoProvider.isLeftSideFlying)
    isRightSideFlying = property(lambda self: self.flyingInfoProvider is not None and self.flyingInfoProvider.isRightSideFlying)

    @property
    def rpm(self):
        return self.detailedEngineState.rpm if self.detailedEngineState is not None else 0.0

    @property
    def gear(self):
        return self.detailedEngineState.gearNum if self.detailedEngineState is not None else 0.0

    trackScrollController = property(lambda self: self.__trackScrollCtl)
    filter = AutoProperty()
    detailedEngineState = ComponentDescriptor()
    engineAudition = ComponentDescriptor()
    trackCrashAudition = ComponentDescriptor()
    customEffectManager = ComponentDescriptor()
    highlighter = ComponentDescriptor()
    shadowManager = ComponentDescriptor()
    gunRecoil = ComponentDescriptor()
    gunLinkedNodesAnimator = ComponentDescriptor()
    swingingAnimator = ComponentDescriptor()
    dirtComponent = ComponentDescriptor()
    suspensionSound = ComponentDescriptor()
    siegeEffects = ComponentDescriptor()
    lodCalculator = ComponentDescriptor()
    frictionAudition = ComponentDescriptor()
    suspension = ComponentDescriptor()
    leveredSuspension = ComponentDescriptor()
    suspensionController = ComponentDescriptor()
    collisions = ComponentDescriptor()
    wheelsAnimator = ComponentDescriptor()
    trackNodesAnimator = ComponentDescriptor()
    vehicleTraces = ComponentDescriptor()
    flyingInfoProvider = ComponentDescriptor()
    terrainMatKindSensor = ComponentDescriptor()
    waterSensor = ComponentDescriptor()
    peripheralsController = ComponentDescriptor()
    tracks = ComponentDescriptor()
    crashedTrackController = ComponentDescriptor()
    collisionObstaclesCollector = ComponentDescriptor()
    tessellationCollisionSensor = ComponentDescriptor()

    def __init__(self):
        CallbackDelayer.__init__(self)
        ComponentSystem.__init__(self)
        self.turretMatrix = Math.WGAdaptiveMatrixProvider()
        self.gunMatrix = Math.WGAdaptiveMatrixProvider()
        self.__vehicle = None
        self.__filter = None
        self.__originalFilter = None
        self.__typeDesc = None
        self.__fashion = None
        self.crashedTracksController = None
        self.__currentDamageState = VehicleDamageState()
        self.__effectsPlayer = None
        self.__engineMode = (0, 0)
        self.__currTerrainMatKind = [-1] * _MATKIND_COUNT
        self.__terrainEffectMaterialNames = [''] * _MATKIND_COUNT
        self.__terrainMatKindLodDistance = _LOD_DISTANCE_TERRAIN_MATKIND_UPDATE
        self.__chassisDecal = VehicleDecal(self)
        self.__splodge = None
        self.__vehicleStickers = None
        self.onModelChanged = Event()
        self.__leftTrackScroll = 0.0
        self.__rightTrackScroll = 0.0
        self.__fashions = None
        self.__compoundModel = None
        self.__boundEffects = None
        self.__splineTracks = None
        self.flyingInfoProvider = Vehicular.FlyingInfoProvider()
        self.__trackScrollCtl = BigWorld.PyTrackScroll()
        self.__trackScrollCtl.setFlyingInfo(DataLinks.createBoolLink(self.flyingInfoProvider, 'isLeftSideFlying'), DataLinks.createBoolLink(self.flyingInfoProvider, 'isRightSideFlying'))
        self.__weaponEnergy = 0.0
        self.__activated = False
        self.__systemStarted = False
        self.__outfit = None
        self.__vID = 0
        self.__isAlive = True
        self.__isTurretDetached = False
        self.__periodicTimerID = None
        self.__wasDeactivated = False
        self.__dirtUpdateTime = 0.0
        self.__inSpeedTreeCollision = False
        self.__isObserver = False
        self.__chassisColisionMatrix = Math.WGAdaptiveMatrixProvider()
        return

    def prerequisites(self, typeDescriptor, vID, health, isCrewActive, isTurretDetached, outfitCD):
        self.__currentDamageState.update(health, isCrewActive, False)
        self.__vID = vID
        self.__typeDesc = typeDescriptor
        self.__isTurretDetached = isTurretDetached
        self.__prepareOutfit(outfitCD)
        out = camouflages.getCamoPrereqs(self.__outfit, self.__typeDesc)
        splineDesc = typeDescriptor.chassis.splineDesc
        if splineDesc is not None:
            out.append(splineDesc.segmentModelLeft)
            out.append(splineDesc.segmentModelRight)
            if splineDesc.segment2ModelLeft is not None:
                out.append(splineDesc.segment2ModelLeft)
            if splineDesc.segment2ModelRight is not None:
                out.append(splineDesc.segment2ModelRight)
        self.__terrainMatKindLodDistance = typeDescriptor.chassis.traces.lodDist
        return out

    def setVehicle(self, vehicle):
        self.__vehicle = vehicle
        if self.customEffectManager is not None:
            self.customEffectManager.setVehicle(vehicle)
        if self.crashedTracksController is not None:
            self.crashedTracksController.setVehicle(vehicle)
        if self.frictionAudition is not None:
            self.frictionAudition.setVehicleMatrix(vehicle.matrix)
        self.highlighter.setVehicle(vehicle)
        self.__applyVehicleOutfit()
        return

    def __arenaPeriodChanged(self, period, *otherArgs):
        if self.detailedEngineState is None:
            return
        else:
            periodEndTime = BigWorld.player().arena.periodEndTime
            serverTime = BigWorld.serverTime()
            engine_state.notifyEngineOnArenaPeriodChange(self.detailedEngineState, period, periodEndTime, serverTime)
            return

    def activate(self):
        if self.__activated or self.__vehicle is None:
            return
        else:
            if self.collisions is not None and self.__vehicle.isTurretDetached:
                self.collisions.removeAttachment(TankPartNames.getIdx(TankPartNames.TURRET))
                self.collisions.removeAttachment(TankPartNames.getIdx(TankPartNames.GUN))
            super(CompoundAppearance, self).activate()
            isPlayerVehicle = self.__vehicle.isPlayerVehicle
            self.__isObserver = 'observer' in self.__typeDesc.type.tags
            player = BigWorld.player()
            self.__originalFilter = self.__vehicle.filter
            self.__vehicle.filter = self.__filter
            self.__vehicle.filter.enableStabilisedMatrix(isPlayerVehicle)
            self.__filter.isStrafing = self.__vehicle.isStrafing
            self.__filter.vehicleCollisionCallback = player.handleVehicleCollidedVehicle
            if isPlayerVehicle and self.collisions is not None:
                colliderData = (self.collisions.getColliderID(), (TankPartNames.getIdx(TankPartNames.HULL), TankPartNames.getIdx(TankPartNames.TURRET)))
                BigWorld.appendCameraCollider(colliderData)
                self.__inSpeedTreeCollision = True
                BigWorld.setSpeedTreeCollisionBody(self.__compoundModel.getBoundsForPart(TankPartIndexes.HULL))
            self.__linkCompound()
            if not self.__isObserver:
                self.__chassisDecal.attach()
            self.__createAndAttachStickers()
            if self.__currentDamageState.isCurrentModelDamaged:
                self.__chassisColisionMatrix.target = self.__compoundModel.matrix
                gunNodeName = 'gun'
            else:
                self.__chassisColisionMatrix.target = self.__vehicle.filter.groundPlacingMatrix
                gunNodeName = TankNodeNames.GUN_INCLINATION
            if not self.__isObserver:
                self.__startSystems()
            self.setupGunMatrixTargets()
            if not self.__isObserver:
                self.__vehicle.filter.enableLagDetection(not self.__currentDamageState.isCurrentModelDamaged)
            self.onModelChanged()
            if self.lodCalculator is not None:
                self.lodCalculator.setupPosition(DataLinks.linkMatrixTranslation(self.__compoundModel.matrix))
            if hasattr(self.filter, 'placingCompensationMatrix') and self.swingingAnimator is not None:
                self.swingingAnimator.placingCompensationMatrix = self.filter.placingCompensationMatrix
                self.swingingAnimator.worldMatrix = self.__compoundModel.matrix
            if not self.__isObserver:
                if self.__periodicTimerID is not None:
                    BigWorld.cancelCallback(self.__periodicTimerID)
                self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME, self.__onPeriodicTimer)
                self.__dirtUpdateTime = BigWorld.time()
            if self.fashion is not None:
                self.fashion.activate()
            if self.__isObserver:
                self.__compoundModel.visible = False
            BigWorld.player().arena.onPeriodChange += self.__arenaPeriodChanged
            BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged
            if self.detailedEngineState is not None:
                engine_state.checkEngineStart(self.detailedEngineState, BigWorld.player().arena.period)
            if self.collisions is not None:
                collisionData = ((TankPartNames.getIdx(TankPartNames.HULL), self.compoundModel.node(TankPartNames.HULL)),
                 (TankPartNames.getIdx(TankPartNames.TURRET), self.compoundModel.node(TankPartNames.TURRET)),
                 (TankPartNames.getIdx(TankPartNames.CHASSIS), self.__chassisColisionMatrix),
                 (TankPartNames.getIdx(TankPartNames.GUN), self.compoundModel.node(gunNodeName)))
                self.collisions.connect(self.id, ColliderTypes.VEHICLE_COLLIDER, collisionData)
            self.__activated = True
            return

    def deactivate(self, stopEffects=True):
        if not self.__activated:
            return
        else:
            self.shadowManager.unregisterCompoundModel(self.__compoundModel)
            self.__activated = False
            self.__wasDeactivated = True
            if self.fashion is not None:
                self.fashion.deactivate()
            self.__stopSystems()
            super(CompoundAppearance, self).deactivate()
            self.__chassisDecal.detach()
            if self.__inSpeedTreeCollision:
                BigWorld.setSpeedTreeCollisionBody(None)
            if self.collisions is not None:
                BigWorld.removeCameraCollider(self.collisions.getColliderID())
            self.__vehicle.filter.enableLagDetection(False)
            self.turretMatrix.target = None
            self.gunMatrix.target = None
            self.__vehicle.filter = self.__originalFilter
            self.__filter.reset()
            self.__originalFilter = None
            self.__vehicleStickers.detach()
            if stopEffects:
                self.__stopEffects()
                self.__boundEffects.stop()
            self.__vehicle.model = None
            self.__compoundModel.matrix = Math.Matrix()
            self.__vehicle = None
            BigWorld.player().arena.onPeriodChange -= self.__arenaPeriodChanged
            BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged
            return

    def __startSystems(self):
        if self.__systemStarted or self.__currentDamageState.isCurrentModelDamaged:
            return
        else:
            if self.flyingInfoProvider is not None:
                self.flyingInfoProvider.setData(self.__vehicle.filter, self.suspension)
            if self.__trackScrollCtl is not None:
                self.__trackScrollCtl.activate()
                self.__trackScrollCtl.setData(self.__vehicle.filter)
            if self.__vehicle.isPlayerVehicle:
                self.delayCallback(_PERIODIC_TIME_ENGINE, self.__onPeriodicTimerEngine)
                self.highlighter.highlight(True)
            if self.engineAudition is not None:
                self.engineAudition.setWeaponEnergy(self.__weaponEnergy)
                self.engineAudition.attachToModel(self.__compoundModel)
            if self.peripheralsController is not None:
                self.peripheralsController.attachToVehicle(self.__vehicle)
            if self.suspensionController is not None:
                self.suspensionController.setData(self.__vehicle.filter, self.__vehicle.typeDescriptor)
            if self.detailedEngineState is not None:
                self.detailedEngineState.onGearUpCbk = self.__onEngineStateGearUp
            self.delayCallback(_PERIODIC_TIME_DIRT[0][0], self.__onPeriodicTimerDirt)
            self.__systemStarted = True
            return

    def __stopSystems(self):
        if not self.__systemStarted:
            return
        else:
            self.__systemStarted = False
            if self.__periodicTimerID is not None:
                BigWorld.cancelCallback(self.__periodicTimerID)
                self.__periodicTimerID = None
            if self.flyingInfoProvider is not None:
                self.flyingInfoProvider.setData(None, None)
            if self.__vehicle.isPlayerVehicle:
                self.highlighter.highlight(False)
                self.stopCallback(self.__onPeriodicTimerEngine)
            self.stopCallback(self.__onPeriodicTimerDirt)
            if self.__trackScrollCtl is not None:
                self.__trackScrollCtl.deactivate()
                self.__trackScrollCtl.setData(None)
            if self.detailedEngineState is not None:
                self.detailedEngineState.onGearUpCbk = None
            return

    def __destroySystems(self):
        if self.__periodicTimerID is not None:
            BigWorld.cancelCallback(self.__periodicTimerID)
            self.__periodicTimerID = None
        if self.__trackScrollCtl is not None:
            self.__trackScrollCtl.deactivate()
            self.__trackScrollCtl = None
        if self.crashedTracksController is not None:
            self.crashedTracksController.destroy()
            self.crashedTracksController = None
        self.__systemStarted = False
        return

    def __destroyEngineAudition(self):
        self.engineAudition = None
        if self.detailedEngineState is not None:
            self.detailedEngineState.onEngineStart = None
            self.detailedEngineState.onStateChanged = None
        return

    def __prepareSystemsForDamagedVehicle(self, vehicle, isTurretDetached):
        if self.flyingInfoProvider is not None:
            self.flyingInfoProvider.setData(vehicle.filter, None)
        self.vehicleTraces = None
        self.suspensionSound = None
        self.swingingAnimator = None
        self.gunRecoil = None
        self.gunLinkedNodesAnimator = None
        self.suspension = None
        self.leveredSuspension = None
        self.trackNodesAnimator = None
        self.wheelsAnimator = None
        fashions = VehiclePartsTuple(None, None, None, None)
        self.__setFashions(fashions, isTurretDetached)
        self.customEffectManager = None
        self.__destroyEngineAudition()
        self.detailedEngineState = None
        self.trackCrashAudition = None
        self.frictionAudition = None
        self.terrainMatKindSensor = None
        self.__splineTracks = None
        model = self.compoundModel
        self.waterSensor.sensorPlaneLink = model.root
        self.peripheralsController = None
        self.dirtComponent = None
        self.tracks = None
        self.collisionObstaclesCollector = None
        self.tessellationCollisionSensor = None
        self.__destroySystems()
        return

    def destroy(self):
        if self.__vehicle is not None:
            self.deactivate()
        self.__destroySystems()
        ComponentSystem.destroy(self)
        self.__typeDesc = None
        if self.__boundEffects is not None:
            self.__boundEffects.destroy()
        self.__vehicleStickers = None
        self.onModelChanged = None
        self.__chassisDecal.destroy()
        self.__chassisDecal = None
        self.__compoundModel = None
        CallbackDelayer.destroy(self)
        return

    def start(self, prereqs=None):
        self.collisions = prereqs['collisionAssembler']
        self.__typeDesc.chassis.hitTester.bbox = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.CHASSIS))
        self.__typeDesc.hull.hitTester.bbox = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.HULL))
        self.__typeDesc.turret.hitTester.bbox = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.TURRET))
        self.__typeDesc.gun.hitTester.bbox = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN))
        self.__compoundModel = prereqs[self.__typeDesc.name]
        self.__boundEffects = bound_effects.ModelBoundEffects(self.__compoundModel)
        isCurrentModelDamaged = self.__currentDamageState.isCurrentModelDamaged
        fashions = camouflages.prepareFashions(isCurrentModelDamaged)
        if not isCurrentModelDamaged:
            model_assembler.setupTracksFashion(self.__typeDesc, fashions.chassis)
        self.__setFashions(fashions, self.__isTurretDetached)
        self.__setupModels()
        if not isCurrentModelDamaged:
            self.__splineTracks = model_assembler.setupSplineTracks(self.__fashion, self.__typeDesc, self.__compoundModel, prereqs)
            self.crashedTracksController = CrashedTrackController(self.__typeDesc, self.__fashion)
        else:
            self.__trackScrollCtl = None
        if self.__currentDamageState.effect is not None:
            self.__playEffect(self.__currentDamageState.effect, SpecialKeyPointNames.STATIC)
        self.__chassisDecal.create()
        return

    def showStickers(self, show):
        self.__vehicleStickers.show = show

    def updateTurretVisibility(self):
        self.__requestModelsRefresh()

    def changeVisibility(self, modelVisible):
        self.compoundModel.visible = modelVisible
        self.showStickers(modelVisible)
        if self.crashedTracksController is not None:
            self.crashedTracksController.setVisible(modelVisible)
        return

    def changeDrawPassVisibility(self, visibilityMask):
        colorPassEnabled = visibilityMask & BigWorld.ColorPassBit != 0
        self.compoundModel.visible = visibilityMask
        self.compoundModel.skipColorPass = not colorPassEnabled
        self.showStickers(colorPassEnabled)
        if self.crashedTracksController is not None:
            self.crashedTracksController.setVisible(visibilityMask)
        return

    def onVehicleHealthChanged(self, showEffects=True):
        vehicle = self.__vehicle
        if not vehicle.isAlive() and vehicle.health > 0:
            self.changeEngineMode((0, 0))
        currentState = self.__currentDamageState
        previousState = currentState.state
        isUnderWater = self.waterSensor.isUnderWater
        currentState.update(vehicle.health, vehicle.isCrewActive, isUnderWater)
        if previousState != currentState.state:
            if currentState.effect is not None and showEffects:
                self.__playEffect(currentState.effect)
            if vehicle.health <= 0:
                BigWorld.player().inputHandler.onVehicleDeath(vehicle, currentState.state == 'ammoBayExplosion')
                self.processVehicleDeath(currentState)
                self.__requestModelsRefresh()
            elif not vehicle.isCrewActive:
                self.__onCrewKilled()
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
        if self.detailedEngineState is not None:
            self.detailedEngineState.mode = self.__engineMode[0]
        if self.__trackScrollCtl is not None:
            self.__trackScrollCtl.setMode(self.__engineMode)
        return None if BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress else None

    def stopSwinging(self):
        if self.swingingAnimator is not None:
            self.swingingAnimator.accelSwingingPeriod = 0.0
        return

    def removeDamageSticker(self, code):
        self.__vehicleStickers.delDamageSticker(code)

    def addDamageSticker(self, code, componentIdx, stickerID, segStart, segEnd):
        self.__vehicleStickers.addDamageSticker(code, componentIdx, stickerID, segStart, segEnd)

    def receiveShotImpulse(self, direction, impulse):
        if BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            if not VehicleDamageState.isDamagedModel(self.__currentDamageState.modelState):
                self.swingingAnimator.receiveShotImpulse(direction, impulse)
                if self.crashedTracksController is not None:
                    self.crashedTracksController.receiveShotImpulse(direction, impulse)
            return

    def recoil(self):
        gunNode = self.compoundModel.node(TankNodeNames.GUN_INCLINATION)
        impulseDir = Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1))
        impulseValue = self.__typeDesc.gun.impulse
        self.receiveShotImpulse(impulseDir, impulseValue)
        self.gunRecoil.recoil()
        node = self.compoundModel.node('HP_gunFire')
        gunPos = Math.Matrix(node).translation
        BigWorld.player().inputHandler.onVehicleShaken(self.__vehicle, gunPos, impulseDir, self.__typeDesc.shot.shell.caliber, ShakeReason.OWN_SHOT_DELAYED)

    def addCrashedTrack(self, isLeft):
        if not self.__vehicle.isAlive():
            return
        else:
            if self.crashedTracksController is not None:
                self.crashedTracksController.addTrack(isLeft, self.isLeftSideFlying if isLeft else self.isRightSideFlying)
            if not self.__vehicle.isEnteringWorld and self.trackCrashAudition:
                self.trackCrashAudition.playCrashSound(isLeft)
            return

    def delCrashedTrack(self, isLeft):
        if self.crashedTracksController is not None:
            self.crashedTracksController.delTrack(isLeft)
        if not self.__vehicle.isEnteringWorld and self.trackCrashAudition and self.__vehicle.isPlayerVehicle:
            self.trackCrashAudition.playCrashSound(isLeft, True)
        return

    def __prepareOutfit(self, outfitCD):
        if self.__outfit:
            return
        outfit = Outfit(outfitCD)
        player = BigWorld.player()
        forceHistorical = player.isHistoricallyAccurate and player.playerVehicleID != self.__vID and not outfit.isHistorical()
        self.__outfit = Outfit() if forceHistorical else outfit

    def __applyVehicleOutfit(self):
        camouflages.updateFashions(self.__fashions, self.__typeDesc, self.__currentDamageState.isCurrentModelDamaged, self.__outfit)

    def getBounds(self, partIdx):
        return self.collisions.getBoundingBox(partIdx) if self.collisions is not None else (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0), 0)

    def __requestModelsRefresh(self):
        modelsSetParams = self.modelsSetParams
        assembler = model_assembler.prepareCompoundAssembler(self.__typeDesc, modelsSetParams, self.__vehicle.spaceID, self.__vehicle.isTurretDetached)
        BigWorld.loadResourceListBG((assembler,), makeCallbackWeak(self.__onModelsRefresh, modelsSetParams.state), loadingPriority(self.__vehicle.id))

    def __onModelsRefresh(self, modelState, resourceList):
        if BattleReplay.isFinished():
            return
        elif self.__vehicle is None:
            return
        else:
            prevTurretYaw = Math.Matrix(self.turretMatrix).yaw
            prevGunPitch = Math.Matrix(self.gunMatrix).pitch
            vehicle = self.__vehicle
            newCompoundModel = resourceList[self.__typeDesc.name]
            self.deactivate(False)
            self.shadowManager.reattachCompoundModel(vehicle, self.__compoundModel, newCompoundModel)
            self.__compoundModel = newCompoundModel
            self.__isTurretDetached = vehicle.isTurretDetached
            self.__prepareSystemsForDamagedVehicle(vehicle, self.__isTurretDetached)
            self.__setupModels()
            self.setVehicle(vehicle)
            self.activate()
            self.__reattachComponents(self.__compoundModel, self.__weaponEnergy)
            self.__filter.syncGunAngles(prevTurretYaw, prevGunPitch)
            model_assembler.setupTurretRotations(self)
            return

    def __setupModels(self):
        self.__isAlive = not self.__currentDamageState.isCurrentModelDamaged
        if self.__isAlive:
            _, gunLength = self.computeVehicleHeight()
            self.__weaponEnergy = gunLength * self.__typeDesc.shot.shell.caliber
        if MAX_DISTANCE > 0:
            transform = self.__typeDesc.chassis.AODecals[0]
            self.__attachSplodge(BigWorld.Splodge(transform, MAX_DISTANCE, self.__typeDesc.chassis.hullPosition.y))

    def __reattachComponents(self, model, weaponEnergy):
        self.__boundEffects.reattachTo(model)
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.reattachTo(model)
        if self.engineAudition is not None:
            self.engineAudition.setWeaponEnergy(weaponEnergy)
            self.engineAudition.attachToModel(model)
        return

    def __playEffect(self, kind, *modifs):
        self.__stopEffects()
        if kind == 'empty' or self.__vehicle is None:
            return
        else:
            enableDecal = True
            if kind in ('explosion', 'destruction') and self.isFlying:
                enableDecal = False
            if self.isUnderwater:
                if kind not in ('submersionDeath',):
                    return
            effects = self.typeDescriptor.type.effects[kind]
            if not effects:
                return
            vehicle = self.__vehicle
            effects = random.choice(effects)
            self.__effectsPlayer = EffectsListPlayer(effects[1], effects[0], showShockWave=vehicle.isPlayerVehicle, showFlashBang=vehicle.isPlayerVehicle, isPlayer=vehicle.isPlayerVehicle, showDecal=enableDecal, start=vehicle.position + Math.Vector3(0.0, 1.0, 0.0), end=vehicle.position + Math.Vector3(0.0, -1.0, 0.0), entity_id=vehicle.id)
            self.__effectsPlayer.play(self.__compoundModel, *modifs)
            return

    def __stopEffects(self):
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.stop()
        self.__effectsPlayer = None
        return

    def __onCrewKilled(self):
        self.__destroyEngineAudition()
        if self.customEffectManager is not None:
            self.customEffectManager = None
        return

    def onWaterSplash(self, waterHitPoint, isHeavySplash):
        effectName = 'waterCollisionHeavy' if isHeavySplash else 'waterCollisionLight'
        self.__vehicle.showCollisionEffect(waterHitPoint, effectName, Math.Vector3(0.0, 1.0, 0.0))

    def onUnderWaterSwitch(self, isUnderWater):
        if isUnderWater and self.__effectsPlayer is not None and self.__currentDamageState.effect not in ('submersionDeath',):
            self.__stopEffects()
        extra = self.__vehicle.typeDescriptor.extrasDict['fire']
        if extra.isRunningFor(self.__vehicle):
            extra.checkUnderwater(self.__vehicle, isUnderWater)
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
            if self.siegeEffects is not None:
                self.siegeEffects.tick(_PERIODIC_TIME_ENGINE)
            return _PERIODIC_TIME_ENGINE

    def __onPeriodicTimer(self):
        timeStamp = BigWorld.wg_getFrameTimestamp()
        if CompoundAppearance.frameTimeStamp >= timeStamp:
            self.__periodicTimerID = BigWorld.callback(0.0, self.__onPeriodicTimer)
            return
        else:
            CompoundAppearance.frameTimeStamp = timeStamp
            self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME, self.__onPeriodicTimer)
            if self.__vehicle is None:
                return
            vehicle = self.__vehicle
            if self.peripheralsController is not None:
                self.peripheralsController.update(vehicle, self.crashedTracksController)
            if not vehicle.isAlive():
                return
            distanceFromPlayer = self.lodCalculator.lodDistance
            self.__updateCurrTerrainMatKinds()
            if not self.__vehicle.isPlayerVehicle:
                if self.siegeEffects is not None:
                    self.siegeEffects.tick(_PERIODIC_TIME)
            self.__updateEffectsLOD(distanceFromPlayer)
            if self.customEffectManager:
                self.customEffectManager.update()
            return

    def __onPeriodicTimerDirt(self):
        if self.__fashion is None:
            return
        else:
            dt = 1.0
            distanceFromPlayer = self.lodCalculator.lodDistance
            if 0.0 <= distanceFromPlayer < _PERIODIC_TIME_DIRT[1][1]:
                time = BigWorld.time()
                simDt = time - self.__dirtUpdateTime
                if simDt > 0.0:
                    if self.dirtComponent:
                        roll = Math.Matrix(self.__compoundModel.matrix).roll
                        hasContact = 0
                        waterHeight = self.waterHeight
                        if math.fabs(roll) > math.radians(120.0):
                            hasContact = 2
                            if self.waterSensor.isInWater:
                                waterHeight = 1.0
                        elif self.__trackScrollCtl is not None:
                            hasContact = 0 if self.__trackScrollCtl.hasContact() else 1
                        self.dirtComponent.update(self.filter.averageSpeed, waterHeight, self.waterSensor.waterHeightWorld, self.__currTerrainMatKind[2], hasContact, simDt)
                    self.__dirtUpdateTime = time
                if distanceFromPlayer <= _PERIODIC_TIME_DIRT[1][0]:
                    dt = _PERIODIC_TIME_DIRT[0][0]
                else:
                    dt = _PERIODIC_TIME_DIRT[0][0] + _DIRT_ALPHA * distanceFromPlayer
            return dt

    def __updateEffectsLOD(self, distanceFromPlayer):
        if self.customEffectManager:
            enableExhaust = distanceFromPlayer <= _LOD_DISTANCE_EXHAUST and not self.isUnderwater
            enableTrails = distanceFromPlayer <= _LOD_DISTANCE_TRAIL_PARTICLES and BigWorld.wg_isVehicleDustEnabled()
            self.customEffectManager.enable(enableTrails, EffectSettings.SETTING_DUST)
            self.customEffectManager.enable(enableExhaust, EffectSettings.SETTING_EXHAUST)

    def __updateCurrTerrainMatKinds(self):
        if self.terrainMatKindSensor is None:
            return
        else:
            matKinds = self.terrainMatKindSensor.matKinds
            matKindsCount = len(matKinds)
            for i in xrange(_MATKIND_COUNT):
                matKind = matKinds[i] if i < matKindsCount else 0
                self.__currTerrainMatKind[i] = matKind
                effectIndex = calcEffectMaterialIndex(matKind)
                effectMaterialName = ''
                if effectIndex is not None:
                    effectMaterialName = material_kinds.EFFECT_MATERIALS[effectIndex]
                self.__terrainEffectMaterialNames[i] = effectMaterialName

            if self.vehicleTraces is not None:
                self.vehicleTraces.setCurrTerrainMatKinds(self.__currTerrainMatKind[0], self.__currTerrainMatKind[1])
            return

    def switchFireVibrations(self, bStart):
        if self.peripheralsController is not None:
            self.peripheralsController.switchFireVibrations(bStart)
        return

    def executeHitVibrations(self, hitEffectCode):
        if self.peripheralsController is not None:
            self.peripheralsController.executeHitVibrations(hitEffectCode)
        return

    def executeRammingVibrations(self, matKind=None):
        if self.peripheralsController is not None:
            self.peripheralsController.executeRammingVibrations(self.__vehicle, matKind)
        return

    def executeShootingVibrations(self, caliber):
        if self.peripheralsController is not None:
            self.peripheralsController.executeShootingVibrations(caliber)
        return

    def executeCriticalHitVibrations(self, vehicle, extrasName):
        if self.peripheralsController is not None:
            self.peripheralsController.executeCriticalHitVibrations(vehicle, extrasName)
        return

    def deviceStateChanged(self, deviceName, state):
        if not self.isUnderwater and self.detailedEngineState is not None and deviceName == 'engine':
            engineState = engine_state.getEngineStateFromName(state)
            self.detailedEngineState.engineState = engineState
        return

    def __linkCompound(self):
        vehicle = self.__vehicle
        vehicle.model = None
        vehicle.model = self.__compoundModel
        vehicleMatrix = vehicle.matrix
        self.__compoundModel.matrix = vehicleMatrix
        return

    def __createStickers(self):
        if self.__vehicleStickers is not None:
            return
        else:
            insigniaRank = self.__vehicle.publicInfo['marksOnGun']
            self.__vehicleStickers = VehicleStickers(self.__typeDesc, insigniaRank, self.__outfit)
            clanID = BigWorld.player().arena.vehicles[self.__vehicle.id]['clanDBID']
            self.__vehicleStickers.setClanID(clanID)
            return

    def __attachStickers(self, alpha=_DEFAULT_STICKERS_ALPHA, emblemsOnly=False):
        self.__vehicleStickers.alpha = alpha
        self.__vehicleStickers.attach(self.compoundModel, self.__currentDamageState.isCurrentModelDamaged, not emblemsOnly)

    def __createAndAttachStickers(self):
        isCurrentModelDamaged = self.__currentDamageState.isCurrentModelDamaged
        stickersAlpha = _DEFAULT_STICKERS_ALPHA
        if isCurrentModelDamaged:
            stickersAlpha = items.vehicles.g_cache.commonConfig['miscParams']['damageStickerAlpha']
        self.__createStickers()
        self.__attachStickers(stickersAlpha, isCurrentModelDamaged)

    def __attachSplodge(self, splodge):
        node = self.__compoundModel.node(TankPartNames.HULL)
        if splodge:
            self.__splodge = splodge
            node.attach(splodge)

    def __disableStipple(self):
        self.compoundModel.stipple = False

    def computeVehicleHeight(self):
        gunLength = 0.0
        height = 0.0
        if self.collisions is not None:
            desc = self.__typeDesc
            hullBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.HULL))
            turretBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.TURRET))
            gunBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN))
            hullTopY = desc.chassis.hullPosition[1] + hullBB[1][1]
            turretTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + turretBB[1][1]
            gunTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + desc.turret.gunPosition[1] + gunBB[1][1]
            gunLength = math.fabs(gunBB[1][2] - gunBB[0][2])
            height = max(hullTopY, max(turretTopY, gunTopY))
        return (height, gunLength)

    def setupGunMatrixTargets(self, target=None):
        if target is None:
            target = self.__filter
        self.turretMatrix.target = target.turretMatrix
        self.gunMatrix.target = target.gunMatrix
        return

    def onFriction(self, otherID, frictionPoint, state):
        if self.frictionAudition is not None:
            self.frictionAudition.processFriction(otherID, frictionPoint, state)
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
        gunRecoil = compound.node(TankNodeNames.GUN_RECOIL)
        if gunRecoil is not None:
            compound.node(TankNodeNames.GUN_RECOIL, gunRecoil.localMatrix)
        self.fashions = VehiclePartsTuple(None, None, None, None)
        return

    def onSiegeStateChanged(self, newState):
        if self.engineAudition is not None:
            self.engineAudition.onSiegeStateChanged(newState)
        if self.suspensionController is not None:
            self.suspensionController.onSiegeStateChanged(newState)
        if self.suspensionSound is not None:
            self.__suspensionSound.vehicleState = newState
        if self.siegeEffects is not None:
            self.siegeEffects.onSiegeStateChanged(newState)
        return

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if self.engineAudition is not None:
            self.engineAudition.onCameraChanged(cameraName, currentVehicleId if currentVehicleId is not None else 0)
        return

    def __onEngineStateGearUp(self):
        if self.customEffectManager is not None:
            self.customEffectManager.onGearUp()
        if self.engineAudition is not None:
            self.engineAudition.onEngineGearUp()
        return

    def addCameraCollider(self):
        collider = self.collisions
        if collider is not None:
            colliderData = (collider.getColliderID(), (TankPartNames.getIdx(TankPartNames.HULL), TankPartNames.getIdx(TankPartNames.TURRET)))
            BigWorld.appendCameraCollider(colliderData)
        return

    def removeCameraCollider(self):
        collider = self.collisions
        if collider is not None:
            BigWorld.removeCameraCollider(collider.getColliderID())
        return
