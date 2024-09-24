# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/CompoundAppearance.py
from functools import partial
import logging
import math
from math import tan
import typing
import BigWorld
import Math
import constants
import items.vehicles
import BattleReplay
import SoundGroups
from CustomEffect import EffectSettings
from Event import Event
from debug_utils import LOG_ERROR
from aih_constants import ShakeReason
from shared_utils import findFirst
from items.components.component_constants import MAIN_TRACK_PAIR_IDX, DEFAULT_TRACK_HIT_VECTOR
from vehicle_systems.components.terrain_circle_component import TerrainCircleComponent
from vehicle_systems.components import engine_state
from vehicle_systems.stricted_loading import makeCallbackWeak, loadingPriority
from vehicle_systems.tankStructure import VehiclePartsTuple, TankNodeNames, TankPartNames, TankPartIndexes, TankSoundObjectsIndexes
from vehicle_systems.components.highlighter import Highlighter
from helpers.CallbackDelayer import CallbackDelayer
from helpers.EffectsList import SpecialKeyPointNames
from vehicle_systems import camouflages
from vehicle_systems import vehicle_composition
from cgf_obsolete_script.script_game_object import ComponentDescriptor
from vehicle_systems import model_assembler
from VehicleEffects import DamageFromShotDecoder
from common_tank_appearance import CommonTankAppearance
import CGF
import GenericComponents
_ROOT_NODE_NAME = 'V'
_GUN_RECOIL_NODE_NAME = 'G'
_PERIODIC_TIME_ENGINE = 0.1
_PERIODIC_TIME_DIRT = ((0.05, 0.25), (10.0, 400.0))
_DIRT_ALPHA = tan((_PERIODIC_TIME_DIRT[0][1] - _PERIODIC_TIME_DIRT[0][0]) / (_PERIODIC_TIME_DIRT[1][1] - _PERIODIC_TIME_DIRT[1][0]))
_MOVE_THROUGH_WATER_SOUND = '/vehicles/tanks/water'
_CAMOUFLAGE_MIN_INTENSITY = 1.0
_PITCH_SWINGING_MODIFIERS = (0.9, 1.88, 0.3, 4.0, 1.0, 1.0)
_MIN_DEPTH_FOR_HEAVY_SPLASH = 0.5
_logger = logging.getLogger(__name__)

class CompoundHolder(object):

    def __init__(self, compound):
        self.compound = compound


class PartsGameObjects(object):

    def __init__(self):
        self.__gameObjects = {}

    def destroy(self):
        self.__gameObjects = None
        return

    def getExistingGameObject(self, partName):
        go = self.__gameObjects.get(partName)
        return go if go is not None and go.isValid() else None

    def getPartGameObject(self, partName, spaceID, parentGO):
        go = self.__gameObjects.get(partName)
        if go is None or not go.isValid():
            go = CGF.GameObject(spaceID)
            go.activate()
            go.createComponent(GenericComponents.HierarchyComponent, parentGO)
            go.createComponent(GenericComponents.NodeFollower, partName, parentGO)
            go.createComponent(GenericComponents.TransformComponent, Math.Vector3(0, 0, 0))
            self.__gameObjects[partName] = go
        return go


class CompoundAppearance(CommonTankAppearance, CallbackDelayer):
    activated = property(lambda self: self.__activated)
    wheelsState = property(lambda self: self._vehicle.wheelsState if self._vehicle is not None else 0)
    wheelsSteering = property(lambda self: self._vehicle.wheelsSteeringSmoothed if self._vehicle is not None else None)
    wheelsScroll = property(lambda self: self._vehicle.wheelsScrollSmoothed if self._vehicle is not None else None)
    burnoutLevel = property(lambda self: self._vehicle.burnoutLevel / 255.0 if self._vehicle is not None else 0.0)
    isConstructed = property(lambda self: self.__isConstructed)
    highlighter = ComponentDescriptor()
    compoundHolder = ComponentDescriptor()
    partsGameObjects = ComponentDescriptor()

    def __init__(self):
        CallbackDelayer.__init__(self)
        CommonTankAppearance.__init__(self, BigWorld.player().spaceID)
        self.turretMatrix = Math.WGAdaptiveMatrixProvider()
        self.gunMatrix = Math.WGAdaptiveMatrixProvider()
        self.__originalFilter = None
        self.__terrainCircle = None
        self.__showCircleDelayed = None
        self.onModelChanged = Event()
        self.__activated = False
        self.__dirtUpdateTime = 0.0
        self.__inSpeedTreeCollision = False
        self.__isConstructed = False
        self.__ignoreEngineStart = False
        self.__tmpGameObjects = {}
        self.__engineStarted = False
        self.__turbochargerSoundPlaying = False
        self.partsGameObjects = PartsGameObjects()
        return

    def setVehicle(self, vehicle):
        self._vehicle = vehicle
        if self.customEffectManager is not None:
            self.customEffectManager.setVehicle(vehicle)
        if self.crashedTracksController is not None:
            self.crashedTracksController.setVehicle(vehicle)
        if self.frictionAudition is not None:
            self.frictionAudition.setVehicleMatrix(vehicle.matrix)
        self.highlighter.setVehicle(vehicle)
        self.__applyVehicleOutfit()
        fstList = vehicle.wheelsScrollFilters if vehicle.wheelsScrollFilters else []
        scndList = vehicle.wheelsSteeringFilters if vehicle.wheelsSteeringFilters else []
        for retriever, floatFilter in zip(self.filterRetrievers, fstList + scndList):
            retriever.setupFilter(floatFilter)

        return

    def setIgnoreEngineStart(self):
        self.__ignoreEngineStart = True

    def isIgnoreEngineStart(self):
        return self.__ignoreEngineStart

    def getVehicle(self):
        return self._vehicle

    def setVehicleInfo(self, vehInfo):
        super(CompoundAppearance, self).setVehicleInfo(vehInfo)
        self.__updateStickers()

    def __arenaPeriodChanged(self, period, *otherArgs):
        if self.detailedEngineState is None:
            return
        else:
            engine_state.notifyEngineOnArenaPeriodChange(self.detailedEngineState, period)
            return

    @property
    def _vehicleColliderInfo(self):
        if self.damageState.isCurrentModelDamaged:
            chassisCollisionMatrix = self.compoundModel.matrix
            gunNodeName = 'gun'
        else:
            chassisCollisionMatrix = self._vehicle.filter.groundPlacingMatrix
            gunNodeName = TankNodeNames.GUN_INCLINATION
        return (chassisCollisionMatrix, gunNodeName)

    def activate(self):
        if self.__activated or self._vehicle is None:
            return
        else:
            player = BigWorld.player()
            isPlayerVehicle = self._vehicle.isPlayerVehicle or self._vehicle.id == player.observedVehicleID
            self.__originalFilter = self._vehicle.filter
            if isPlayerVehicle and self.collisions is not None:
                colliderData = (self.collisions.getColliderID(), (TankPartNames.getIdx(TankPartNames.HULL), TankPartNames.getIdx(TankPartNames.TURRET), TankPartNames.getIdx(TankPartNames.GUN)))
                BigWorld.appendCameraCollider(colliderData)
                self.__inSpeedTreeCollision = True
                BigWorld.setSpeedTreeCollisionBody(self.compoundModel.getBoundsForPart(TankPartIndexes.HULL))
            self.__linkCompound()
            self.__createTerrainCircle()
            super(CompoundAppearance, self).activate()
            self.onModelChanged()
            if not self.isObserver:
                self.__dirtUpdateTime = BigWorld.time()
            BigWorld.player().arena.onPeriodChange += self.__arenaPeriodChanged
            BigWorld.player().arena.onVehicleUpdated += self.__vehicleUpdated
            BigWorld.player().inputHandler.onCameraChanged += self._onCameraChanged
            if self.detailedEngineState is not None:
                engine_state.checkEngineStart(self.detailedEngineState, BigWorld.player().arena.period)
            self.__activated = True
            return

    def disableCustomEffects(self):
        self.__customEffectsEnabled = False
        if self.customEffectManager is not None:
            self.customEffectManager.enable(False, EffectSettings.SETTING_DUST)
            self.customEffectManager.enable(False, EffectSettings.SETTING_EXHAUST)
            self.customEffectManager.disableSelectors()
        return

    def deactivate(self, stopEffects=True):
        if not self.__activated:
            return
        else:
            self.__engineStarted = False
            self.__activated = False
            self.highlighter.deactivate()
            super(CompoundAppearance, self).deactivate()
            if self.__inSpeedTreeCollision:
                BigWorld.setSpeedTreeCollisionBody(None)
            if self.collisions is not None:
                BigWorld.removeCameraCollider(self.collisions.getColliderID())
            self.turretMatrix.target = None
            self.gunMatrix.target = None
            self._vehicle.filter = self.__originalFilter
            self.filter.reset()
            self.__originalFilter = None
            self.__showCircleDelayed = None
            if self.__terrainCircle.isAttached():
                self.__terrainCircle.detach()
            if stopEffects:
                self._stopEffects(stopEffects)
            self._vehicle.model = None
            self.compoundModel.matrix = Math.Matrix()
            self._vehicle = None
            BigWorld.player().arena.onVehicleUpdated -= self.__vehicleUpdated
            BigWorld.player().arena.onPeriodChange -= self.__arenaPeriodChanged
            BigWorld.player().inputHandler.onCameraChanged -= self._onCameraChanged
            return

    def _startSystems(self):
        super(CompoundAppearance, self)._startSystems()
        if self._vehicle.isPlayerVehicle:
            self.delayCallback(_PERIODIC_TIME_ENGINE, self.__onPeriodicTimerEngine)
            self.highlighter.highlight(True)
        self.delayCallback(_PERIODIC_TIME_DIRT[0][0], self.__onPeriodicTimerDirt)

    def _stopSystems(self):
        super(CompoundAppearance, self)._stopSystems()
        if self._vehicle.isPlayerVehicle:
            self.highlighter.highlight(False)
            self.stopCallback(self.__onPeriodicTimerEngine)
        self.stopCallback(self.__onPeriodicTimerDirt)

    def _onEngineStart(self):
        if self.__ignoreEngineStart:
            return
        else:
            super(CompoundAppearance, self)._onEngineStart()
            self.__engineStarted = True
            if self._vehicle is not None:
                self.__setTurbochargerSound(self._vehicle.getOptionalDevices())
            return

    def __destroyEngineAudition(self):
        self.engineAudition = None
        if self.detailedEngineState is not None:
            self.detailedEngineState.onEngineStart = None
            self.detailedEngineState.onStateChanged = None
        self.__turbochargerSoundPlaying = False
        return

    def __processPostmortemComponents(self):
        if self.wheelsAnimator is not None and self.wheelsAnimator.activePostmortem:
            self.wheelsAnimator.reattachToCrash(self.compoundModel, self.fashion)
        if self.suspension is not None and self.suspension.activePostmortem:
            self.suspension.reattachCompound(self.compoundModel)
        if self.leveredSuspension is not None and self.leveredSuspension.activePostmortem:
            self.leveredSuspension.reattachCompound(self.compoundModel)
        if self.vehicleTraces is not None and self.vehicleTraces.activePostmortem:
            self.vehicleTraces.setCompound(self.compoundModel)
        if self.collisionObstaclesCollector is not None and self.collisionObstaclesCollector.activePostmortem:
            self.collisionObstaclesCollector.reattachCompound(self.compoundModel)
        if self.tessellationCollisionSensor is not None and self.tessellationCollisionSensor.activePostmortem:
            self.tessellationCollisionSensor.reattachCompound(self.compoundModel)
        return

    def __prepareSystemsForDamagedVehicle(self, vehicle, isTurretDetached):
        if self.flyingInfoProvider is not None:
            self.flyingInfoProvider.setData(vehicle.filter, None)
        if self.vehicleTraces is not None and not self.vehicleTraces.activePostmortem:
            self.vehicleTraces = None
        self.suspensionSound = None
        self.swingingAnimator = None
        self.burnoutProcessor = None
        self.gunRecoil = None
        self.gunAnimators = []
        self.gunLinkedNodesAnimator = None
        self.crashedTracksController = None
        if self.suspension is not None and not self.suspension.activePostmortem:
            self.suspension = None
        if self.leveredSuspension is not None and not self.leveredSuspension.activePostmortem:
            self.leveredSuspension = None
        self.trackNodesAnimator = None
        if self.wheelsAnimator is not None and not self.wheelsAnimator.activePostmortem:
            self.wheelsAnimator = None
        self.gearbox = None
        self.gunRotatorAudition = None
        while self.__tmpGameObjects:
            _, go = self.__tmpGameObjects.popitem()
            self.removeComponent(go)
            go.deactivate()

        fashions = VehiclePartsTuple(BigWorld.WGVehicleFashion(), None, None, None)
        self._setFashions(fashions, isTurretDetached)
        model_assembler.setupTracksFashion(self.typeDescriptor, self.fashion)
        self.showStickers(False)
        self.customEffectManager = None
        self.__destroyEngineAudition()
        self.detailedEngineState = None
        self.frictionAudition = None
        self.terrainMatKindSensor = None
        self._splineTracks = None
        model = self.compoundModel
        self.waterSensor.sensorPlaneLink = model.root
        self.dirtComponent = None
        self.tracks = None
        if self.collisionObstaclesCollector is not None and not self.collisionObstaclesCollector.activePostmortem:
            self.collisionObstaclesCollector = None
        if self.tessellationCollisionSensor is not None and not self.tessellationCollisionSensor.activePostmortem:
            self.tessellationCollisionSensor = None
        self.siegeEffects = None
        self.partsGameObjects = None
        self._destroySystems()
        self._loadingQueue = []
        self._destroyStickers()
        return

    def destroy(self):
        if self._vehicle is not None:
            self.deactivate()
        self.__destroyEngineAudition()
        if self.fashion is not None:
            self.fashion.removePhysicalTracks()
        if self.tracks is not None:
            self.tracks.reset()
        super(CompoundAppearance, self).destroy()
        self.__showCircleDelayed = None
        if self.__terrainCircle is not None:
            self.__terrainCircle.destroy()
            self.__terrainCircle = None
        self.onModelChanged.clear()
        self.onModelChanged = None
        CallbackDelayer.destroy(self)
        return

    def construct(self, isPlayer, resourceRefs):
        super(CompoundAppearance, self).construct(isPlayer, resourceRefs)
        if self.damageState.effect is not None:
            self.playEffect(self.damageState.effect, SpecialKeyPointNames.STATIC)
        self.highlighter = Highlighter(self.isAlive, self.collisions)
        vehicle_composition.createVehicleComposition(self.gameObject)
        self.__isConstructed = True
        return

    def addTempGameObject(self, component, name):
        if name in self.__tmpGameObjects:
            _logger.warning('Attempt to add existed Game Object %s', name)
        else:
            self.__tmpGameObjects[name] = component
            self.addComponent(component)

    def removeTempGameObject(self, name):
        go = self.__tmpGameObjects.pop(name, None)
        if go is not None:
            self.removeComponent(go)
            go.deactivate()
        else:
            _logger.warning('Component "%s" has not been found', name)
        return

    def removeTempGameObjectIfExists(self, name):
        if name in self.__tmpGameObjects:
            self.removeTempGameObject(name)

    def showStickers(self, show):
        if self.vehicleStickers is not None:
            self.vehicleStickers.show = show
        return

    def showTerrainCircle(self, radius=None, terrainCircleSettings=None):
        if (radius is None) != (terrainCircleSettings is None):
            LOG_ERROR('showTerrainCircle: radius or terrainCircleSetting is not set. You need to set both or none of them.')
            return
        elif self.__terrainCircle is None:
            self.__showCircleDelayed = partial(self.showTerrainCircle, radius, terrainCircleSettings)
            return
        else:
            if radius is not None:
                self.__terrainCircle.configure(radius, terrainCircleSettings)
            if not self.__terrainCircle.isAttached():
                self.__attachTerrainCircle()
            self.__terrainCircle.setVisible()
            return

    def hideTerrainCircle(self):
        self.__terrainCircle.setVisible(False)
        self.__showCircleDelayed = None
        return

    @property
    def isTerrainCircleVisible(self):
        return bool(self.__terrainCircle and self.__terrainCircle.isVisible())

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
        vehicle = self._vehicle
        if self.damageState.isCurrentModelDamaged:
            return
        else:
            if not vehicle.isAlive() and vehicle.health > 0:
                self.changeEngineMode((0, 0))
            currentState = self.damageState
            previousState = currentState.state
            isUnderWater = self.waterSensor.isUnderWater
            currentState.update(vehicle.health, vehicle.isCrewActive, isUnderWater)
            if previousState != currentState.state:
                if currentState.effect is not None and showEffects:
                    self.playEffect(currentState.effect)
                if vehicle.health <= 0:
                    BigWorld.player().inputHandler.onVehicleDeath(vehicle, currentState.state == 'ammoBayExplosion')
                    if currentState.state != 'ammoBayExplosion':
                        self.__requestModelsRefresh()
                elif not vehicle.isCrewActive:
                    self.__onCrewKilled()
            return

    def showAmmoBayEffect(self, mode, fireballVolume):
        if mode == constants.AMMOBAY_DESTRUCTION_MODE.POWDER_BURN_OFF:
            self.playEffect('ammoBayBurnOff')
            return
        volumes = items.vehicles.g_cache.commonConfig['miscParams']['explosionCandleVolumes']
        candleIdx = 0
        for idx, volume in enumerate(volumes):
            if volume >= fireballVolume:
                break
            candleIdx = idx + 1

        if candleIdx > 0:
            self.playEffect('explosionCandle%d' % candleIdx)
        else:
            self.playEffect('explosion')

    def stopSwinging(self):
        if self.swingingAnimator is not None:
            self.swingingAnimator.accelSwingingPeriod = 0.0
        return

    def removeDamageSticker(self, code):
        if self.vehicleStickers is not None:
            self.vehicleStickers.delDamageSticker(code)
        return

    def addDamageSticker(self, code, componentIdx, stickerID, segStart, segEnd, segLength=None):
        if self.vehicleStickers is not None:
            self.vehicleStickers.addDamageSticker(code, componentIdx, stickerID, segStart, segEnd, self.collisions, segLength)
        return

    def receiveShotImpulse(self, direction, impulse):
        if BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(CompoundAppearance, self).receiveShotImpulse(direction, impulse)

    def addCrashedTrack(self, isLeft, pairIndex=0, index=None):
        if not self._vehicle.isAlive():
            return
        self._addCrashedTrack(isLeft, pairIndex, self.isLeftSideFlying if isLeft else self.isRightSideFlying, self._vehicle.getExtraHitPoint(index))
        self.onChassisDestroySound(isLeft, True, trackPairIdx=pairIndex)

    def addSimulatedCrashedTrack(self, index, trackInAir, hitPoint=None):
        if not self._vehicle.isAlive() or self.crashedTracksController is None:
            return
        else:
            pairsCnt = self.crashedTracksController.getPairsCnt()
            isLeftTrack = True if index < pairsCnt else False
            trackIndex = index % pairsCnt
            if hitPoint is None:
                hitPoint = DEFAULT_TRACK_HIT_VECTOR
            self._addCrashedTrack(isLeftTrack, trackIndex, trackInAir[0] if isLeftTrack else trackInAir[1], Math.Vector3(hitPoint))
            return

    def delCrashedTrack(self, isLeft, pairIndex=0):
        self._delCrashedTrack(isLeft, pairIndex)
        self.onChassisDestroySound(isLeft, False, trackPairIdx=pairIndex)

    def onChassisDestroySound(self, isLeft, destroy, wheelsIdx=-1, trackPairIdx=MAIN_TRACK_PAIR_IDX):
        if self._vehicle is None:
            return
        else:
            if not self._vehicle.isEnteringWorld and self.engineAudition:
                if wheelsIdx == -1:
                    if isLeft:
                        position = Math.Matrix(self.compoundModel.node(TankNodeNames.TRACK_LEFT_MID)).translation
                    else:
                        position = Math.Matrix(self.compoundModel.node(TankNodeNames.TRACK_RIGHT_MID)).translation
                    materialType = 0
                else:
                    position = self.wheelsAnimator.getWheelWorldTransform(wheelsIdx).translation
                    materialType = 0 if self.wheelsAnimator.isWheelDeflatable(wheelsIdx) else 1
                vehicle = self.getVehicle()
                if not destroy and vehicle.isPlayerVehicle and any((device.groupName == 'extraHealthReserve' for device in vehicle.getOptionalDevices() if device is not None)):
                    SoundGroups.g_instance.playSound2D('cons_springs')
                if trackPairIdx == MAIN_TRACK_PAIR_IDX:
                    self.engineAudition.onChassisDestroy(position, destroy, materialType)
            return

    def turretDamaged(self):
        player = BigWorld.player()
        if player is None or self._vehicle is None or not self._vehicle.isPlayerVehicle:
            return 0
        else:
            deviceStates = getattr(player, 'deviceStates', None)
            if deviceStates is not None:
                if deviceStates.get('turretRotator', None) is None:
                    return 0
                return 1
            return 0

    def maxTurretRotationSpeed(self):
        player = BigWorld.player()
        if player is None or self._vehicle is None or not self._vehicle.isPlayerVehicle:
            return 0
        else:
            gunRotator = getattr(player, 'gunRotator', None)
            return gunRotator.maxturretRotationSpeed if gunRotator is not None else 0

    def _destroySystems(self):
        super(CompoundAppearance, self)._destroySystems()
        self.highlighter.destroy()

    def _prepareOutfit(self, outfitCD):
        vehicle = self._vehicle or BigWorld.entity(self.id)
        isPlayerVehicle = vehicle.isPlayerVehicle if vehicle is not None else False
        isPlayerVehicle |= BigWorld.player().playerVehicleID == self.id
        outfit = camouflages.prepareBattleOutfit(outfitCD, self.typeDescriptor, self.id, isPlayerVehicle)
        return outfit

    def _initiateRecoil(self, gunNodeName, gunFireNodeName, gunAnimator):
        impulseDir = super(CompoundAppearance, self)._initiateRecoil(gunNodeName, gunFireNodeName, gunAnimator)
        node = self.compoundModel.node(gunFireNodeName)
        gunPos = Math.Matrix(node).translation
        BigWorld.player().inputHandler.onVehicleShaken(self._vehicle, ShakeReason.OWN_SHOT_DELAYED, gunPos, impulseDir, self.typeDescriptor.shot.shell.caliber)
        return impulseDir

    def __applyVehicleOutfit(self):
        camouflages.updateFashions(self)

    def getBounds(self, partIdx):
        return self.collisions.getBoundingBox(DamageFromShotDecoder.convertComponentIndex(partIdx, vehicleDesc=self.typeDescriptor)) if self.collisions is not None else (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0), 0)

    def __requestModelsRefresh(self):
        self._onRequestModelsRefresh()
        self._isTurretDetached = self._vehicle.isTurretDetached
        modelsSetParams = self.modelsSetParams
        assembler = model_assembler.prepareCompoundAssembler(self.typeDescriptor, modelsSetParams, self.spaceID, self.isTurretDetached)
        collisionAssembler = model_assembler.prepareCollisionAssembler(self.typeDescriptor, self.isTurretDetached, self.spaceID)
        BigWorld.loadResourceListBG((assembler, collisionAssembler), makeCallbackWeak(self.__onModelsRefresh, modelsSetParams.state), loadingPriority(self._vehicle.id))

    def __onModelsRefresh(self, modelState, resourceList):
        if not self.damageState.isCurrentModelDamaged:
            _logger.error('Current model is not damaged. Wrong refresh request!')
        if modelState != self.damageState.modelState:
            _logger.error('Required modelState differs from actual one. Wrong refresh request!')
        if self._vehicle is None:
            return
        else:
            self.highlighter.highlight(False)
            oldHolder = self.findComponentByType(CompoundHolder)
            if oldHolder is not None:
                self.gameObject.removeComponent(oldHolder)
            holder = self.gameObject.createComponent(CompoundHolder, self._vehicle.model)
            self.gameObject.removeComponent(holder)
            prevTurretYaw = Math.Matrix(self.turretMatrix).yaw
            prevGunPitch = Math.Matrix(self.gunMatrix).pitch
            newCompoundModel = resourceList[self.typeDescriptor.name]
            isRightSideFlying = self.isRightSideFlying
            isLeftSideFlying = self.isLeftSideFlying
            self._vehicle.filter = self.__originalFilter
            self.filter.setFlyingInfo(None)
            self.filter.reset()
            self.shadowManager.reattachCompoundModel(self._vehicle, self.compoundModel, newCompoundModel)
            if self.__inSpeedTreeCollision:
                BigWorld.setSpeedTreeCollisionBody(None)
                self.__inSpeedTreeCollision = False
            self._compoundModel = newCompoundModel
            self.removeComponentByType(GenericComponents.DynamicModelComponent)
            self.createComponent(GenericComponents.DynamicModelComponent, self._compoundModel)
            self.collisions = None
            self.collisions = self.createComponent(BigWorld.CollisionComponent, resourceList['collisionAssembler'])
            model_assembler.setupCollisions(self.typeDescriptor, self.collisions)
            self.__linkCompound()
            self.__prepareSystemsForDamagedVehicle(self._vehicle, self.isTurretDetached)
            self.__processPostmortemComponents()
            if isRightSideFlying:
                self.fashion.changeTrackVisibility(False, False, MAIN_TRACK_PAIR_IDX)
            if isLeftSideFlying:
                self.fashion.changeTrackVisibility(True, False, MAIN_TRACK_PAIR_IDX)
            self._setupModels()
            self.__reattachComponents(self.compoundModel)
            self._connectCollider()
            self.filter.syncGunAngles(prevTurretYaw, prevGunPitch)
            model_assembler.setupTurretRotations(self)
            vehicle_composition.removeComposition(self.gameObject)
            vehicle_composition.createVehicleComposition(self.gameObject)
            self.onModelChanged()
            return

    def __reattachComponents(self, model):
        self.boundEffects.reattachTo(model)
        if self.engineAudition is not None:
            self.engineAudition.setWeaponEnergy(self.weaponEnergy)
            self.engineAudition.attachToModel(model)
        return

    def __onCrewKilled(self):
        self.__destroyEngineAudition()
        if self.customEffectManager is not None:
            self.customEffectManager = None
            self.siegeEffects = None
        return

    def onWaterSplash(self, waterHitPoint, isHeavySplash):
        effectName = 'waterCollisionHeavy' if isHeavySplash else 'waterCollisionLight'
        self._vehicle.showCollisionEffect(waterHitPoint, effectName, Math.Vector3(0.0, 1.0, 0.0))

    def onUnderWaterSwitch(self, isUnderWater):
        if isUnderWater and self.damageState.effect not in ('submersionDeath',):
            self._stopEffects()
        if self._vehicle is not None:
            if self._vehicle.isOnFire():
                self._vehicle.fire.onUnderWaterSwitch(isUnderWater)
        return

    def updateTracksScroll(self, leftScroll, rightScroll):
        if self.trackScrollController is not None:
            self.trackScrollController.setExternal(leftScroll, rightScroll)
        return

    def __onPeriodicTimerEngine(self):
        return None if self.detailedEngineState is None or self.engineAudition is None else _PERIODIC_TIME_ENGINE

    def _periodicUpdate(self):
        super(CompoundAppearance, self)._periodicUpdate()
        if self._vehicle is None:
            return
        elif not self._vehicle.isAlive():
            return
        else:
            self.__updateTransmissionScroll()
            return

    def __onPeriodicTimerDirt(self):
        if self.fashion is None or self._vehicle is None:
            return
        else:
            dt = 1.0
            distanceFromPlayer = self.lodCalculator.lodDistance
            if 0.0 <= distanceFromPlayer < _PERIODIC_TIME_DIRT[1][1]:
                time = BigWorld.time()
                simDt = time - self.__dirtUpdateTime
                if simDt > 0.0:
                    if self.dirtComponent:
                        roll = Math.Matrix(self.compoundModel.matrix).roll
                        hasContact = 0
                        waterHeight = self.waterHeight
                        if math.fabs(roll) > math.radians(120.0):
                            hasContact = 2
                            if self.waterSensor.isInWater:
                                waterHeight = 1.0
                        elif self.trackScrollController is not None:
                            hasContact = 0 if self.trackScrollController.hasContact() else 1
                        self.dirtComponent.update(self.filter.averageSpeed, waterHeight, self.waterSensor.waterHeightWorld, self.terrainMatKind[2], hasContact, simDt)
                    self.__dirtUpdateTime = time
                if distanceFromPlayer <= _PERIODIC_TIME_DIRT[1][0] or self._vehicle.isPlayerVehicle:
                    dt = _PERIODIC_TIME_DIRT[0][0]
                else:
                    dt = _PERIODIC_TIME_DIRT[0][0] + _DIRT_ALPHA * distanceFromPlayer
            return dt

    def deviceStateChanged(self, deviceName, state):
        if not self.isUnderwater and self.detailedEngineState is not None and deviceName == 'engine':
            engineState = engine_state.getEngineStateFromName(state)
            self.detailedEngineState.engineState = engineState
        return

    def __linkCompound(self):
        vehicle = self._vehicle
        vehicle.model = None
        vehicle.model = self.compoundModel
        vehicleMatrix = vehicle.matrix
        self.compoundModel.matrix = vehicleMatrix
        isPlayerVehicle = self._vehicle.isPlayerVehicle
        player = BigWorld.player()
        if isPlayerVehicle and self.collisions is not None:
            self.__inSpeedTreeCollision = True
            BigWorld.setSpeedTreeCollisionBody(self.compoundModel.getBoundsForPart(TankPartIndexes.HULL))
        self._vehicle.filter = self.filter
        self._vehicle.filter.enableStabilisedMatrix(isPlayerVehicle)
        self.filter.isStrafing = self._vehicle.isStrafing
        self.filter.vehicleCollisionCallback = player.handleVehicleCollidedVehicle
        return

    def _attachStickers(self):
        super(CompoundAppearance, self)._attachStickers()
        self.__updateStickers()

    def __updateStickers(self):
        self.__updateClanSticker()
        self.__updateInsigniaSticker()

    def __updateClanSticker(self):
        if self.vehicleStickers is not None:
            clanID = self._vehicleInfo.get('clanDBID', 0)
            self.vehicleStickers.setClanID(clanID)
        return

    def __updateInsigniaSticker(self):
        if self.vehicleStickers is not None:
            insigniaRank = self._vehicle.publicInfo['marksOnGun'] if self._vehicle is not None else 0
            self.vehicleStickers.setInsigniaRank(insigniaRank)
        return

    def __createTerrainCircle(self):
        if self.__terrainCircle is not None:
            return
        else:
            self.__terrainCircle = TerrainCircleComponent()
            if self.__showCircleDelayed is not None:
                self.__showCircleDelayed()
                self.__showCircleDelayed = None
            return

    def __attachTerrainCircle(self):
        self.__terrainCircle.attach(self._vehicle.id)

    def computeFullVehicleLength(self):
        vehicleLength = 0.0
        if self.compoundModel is not None:
            hullBB = Math.Matrix(self.compoundModel.getBoundsForPart(TankPartIndexes.HULL))
            vehicleLength = hullBB.applyVector(Math.Vector3(0.0, 0.0, 1.0)).length
        return vehicleLength

    def setupGunMatrixTargets(self, target):
        self.turretMatrix.target = target.turretMatrix
        self.gunMatrix.target = target.gunMatrix

    def onFriction(self, otherID, frictionPoint, state):
        if self.frictionAudition is not None:
            self.frictionAudition.processFriction(otherID, frictionPoint, state)
        return

    def _onCameraChanged(self, cameraName, currentVehicleId=None):
        if self.engineAudition is not None:
            self.engineAudition.onCameraChanged(cameraName, currentVehicleId if currentVehicleId is not None else 0)
        if self.tracks is not None:
            if cameraName == 'sniper':
                self.tracks.sniperMode(True)
            else:
                self.tracks.sniperMode(False)
        super(CompoundAppearance, self)._onCameraChanged(cameraName, currentVehicleId=currentVehicleId)
        return

    def __updateTransmissionScroll(self):
        self._commonSlip = 0.0
        self._commonScroll = 0.0
        worldMatrix = Math.Matrix(self.compoundModel.matrix)
        zAxis = worldMatrix.applyToAxis(2)
        vehicleSpeed = zAxis.dot(self.filter.velocity)
        if self.wheelsScroll is not None and self.wheelsAnimator is not None:
            wheelsSpeed = self.wheelsAnimator.getWheelsSpeed()
            wheelCount = len(wheelsSpeed)
            skippedWheelsCount = 0
            for wheelIndex in xrange(0, wheelCount):
                flying = self.wheelsAnimator.wheelIsFlying(wheelIndex)
                if not flying:
                    self._commonScroll += wheelsSpeed[wheelIndex]
                    self._commonSlip += wheelsSpeed[wheelIndex] - vehicleSpeed
                skippedWheelsCount += 1

            activeWheelCount = max(wheelCount - skippedWheelsCount, 1)
            self._commonSlip /= activeWheelCount
            self._commonScroll /= activeWheelCount
        elif self.trackScrollController is not None:
            self._commonScroll = max(self.trackScrollController.leftScroll(), self.trackScrollController.rightScroll())
            self._commonSlip = max(self.trackScrollController.leftSlip(), self.trackScrollController.rightSlip())
        return

    def addCameraCollider(self):
        collider = self.collisions
        if collider is not None:
            colliderData = (collider.getColliderID(), (TankPartNames.getIdx(TankPartNames.HULL), TankPartNames.getIdx(TankPartNames.TURRET), TankPartNames.getIdx(TankPartNames.GUN)))
            BigWorld.appendCameraCollider(colliderData)
        return

    def removeCameraCollider(self):
        collider = self.collisions
        if collider is not None:
            BigWorld.removeCameraCollider(collider.getColliderID())
        return

    def onEngineDamageRisk(self, risk):
        if self.engineAudition is not None:
            self.engineAudition.onEngineDamageRisk(risk)
        return

    def getWheelsSteeringMax(self):
        if self.wheelsSteering is not None and len(self.wheelsSteering) >= 2:
            wheelSteeringMax = self.wheelsSteering[0]
            if math.fabs(self.wheelsSteering[1]) > math.fabs(wheelSteeringMax):
                wheelSteeringMax = self.wheelsSteering[1]
            return -wheelSteeringMax
        else:
            return 0

    def __vehicleUpdated(self, vehicleId):
        if self._vehicle is not None and self._vehicle.id == vehicleId and self.__engineStarted:
            self.__setTurbochargerSound(self._vehicle.getOptionalDevices())
        return

    def __setTurbochargerSound(self, optDevices):
        isEnabled = findFirst(lambda d: d is not None and d.groupName == 'turbocharger', optDevices) is not None
        if isEnabled == self.__turbochargerSoundPlaying:
            return
        else:
            if self.engineAudition is not None:
                engineSoundObject = self.engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
                engineSoundObject.play('cons_turbine_start' if isEnabled else 'cons_turbine_stop')
                self.__turbochargerSoundPlaying = isEnabled
            return
