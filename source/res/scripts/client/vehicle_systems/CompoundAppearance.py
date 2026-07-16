# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/CompoundAppearance.py
from functools import partial
import logging
import math
from math import tan
import typing
from enum import IntEnum
import BigWorld
import CGF
import GenericComponents
import Math
import constants
import items.vehicles
import BattleReplay
import SoundGroups
import Vehicular
from CustomEffect import EffectSettings
from CustomEffectManager import CustomEffectManager
from Event import Event
from debug_utils import LOG_ERROR
from aih_constants import ShakeReason
from shared_utils import findFirst
from items.components.component_constants import MAIN_TRACK_PAIR_IDX, DEFAULT_TRACK_HIT_VECTOR
from vehicle_systems.components.hull_aiming_controller import HullAimingController
from vehicle_systems.components.terrain_circle_component import TerrainCircleComponent
from vehicle_systems.components import engine_state
from vehicle_systems.components.vehicle_shadow_manager import VehicleShadowManager
from vehicle_systems.stricted_loading import makeCallbackWeak, loadingPriority
from vehicle_systems.tankStructure import VehiclePartsTuple, TankNodeNames, TankPartIndexes, TankSoundObjectsIndexes
from vehicle_systems.components.highlighter import Highlighter
from vehicle_systems.vehicle_composition import getExtraSlotMap, getObjectSlots, createVehicleComposition, removeComposition
from helpers.EffectsList import SpecialKeyPointNames
from objects_hierarchy import PrefabsMapItem
from vehicle_systems import camouflages
from vehicle_systems import model_assembler
from VehicleEffects import DamageFromShotDecoder
from vehicle_appearance.constants import DIRT_UPDATE_MIN_TIME
from vehicle_appearance.component import VehicleAppearanceComponent
from vehicle_appearance.common_tank_appearance import CommonTankAppearance
from vehicle_systems.components.CrashedTracks import CrashedTracksController
from vehicle_systems.components.siegeEffectsController import SiegeEffectsController
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
    from VehicleStickers import DamageStickerData
    from vehicle_appearance.common_tank_appearance import ActivateContext, UpdateContext, DeactivateContext, DestroyContext
_ROOT_NODE_NAME = 'V'
_GUN_RECOIL_NODE_NAME = 'G'
_PERIODIC_TIME_DIRT = ((DIRT_UPDATE_MIN_TIME, 0.25), (10.0, 400.0))
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
        return go if go is not None and go.valid else None

    def getPartGameObject(self, partName, spaceID, parentGO):
        go = self.__gameObjects.get(partName)
        if go is None or not go.valid:
            queue = CGF.CommandQueue(spaceID)
            go = queue.createGameObject()
            queue.activateGameObject(go)
            queue.createComponent(go, CGF.HierarchyComponent, parentGO)
            queue.createComponent(go, GenericComponents.NodeFollowerComponent, partName, parentGO.uuid)
            queue.createComponent(go, CGF.TransformComponent, Math.Vector3(0, 0, 0))
            self.__gameObjects[partName] = go
        return go


class _ActivationState(IntEnum):
    NOT_ACTIVATED = 0
    ACTIVATED = 1
    MODEL_UPDATING = 2
    MODEL_UPDATED = 3
    DEACTIVATED = 4


_PostmortemContext = typing.NamedTuple('_PostmortemContext', (('collisionObstaclesCollector', Vehicular.CollisionObstaclesCollector), ('tessellationCollisionSensor', Vehicular.TessellationCollisionSensor)))
UpdateDirtContext = typing.NamedTuple('UpdateDirtContext', (('gameTime', float),
 ('appearanceComponent', VehicleAppearanceComponent),
 ('lodCalculator', Vehicular.LodCalculator),
 ('dirtComponent', Vehicular.DirtComponent),
 ('waterSensor', Vehicular.WaterSensor)))

class CompoundAppearance(CommonTankAppearance):
    wheelsState = property(lambda self: self._vehicle.wheelsState if self._vehicle is not None else 0)
    wheelsSteering = property(lambda self: self._vehicle.wheelsSteeringSmoothed if self._vehicle is not None else None)
    burnoutLevel = property(lambda self: self._vehicle.burnoutLevel / 255.0 if self._vehicle is not None else 0.0)
    highlighter = property(lambda self: self.__highlighter)

    def __init__(self):
        CommonTankAppearance.__init__(self, BigWorld.player().spaceID)
        self.turretMatrix = Math.WGAdaptiveMatrixProvider()
        self.gunMatrix = Math.WGAdaptiveMatrixProvider()
        self.__originalFilter = None
        self.__terrainCircle = None
        self.__showCircleDelayed = None
        self.onModelChanged = Event()
        self.__activationState = _ActivationState.NOT_ACTIVATED
        self.__dirtLastUpdateTime = 0.0
        self.__dirtNextUpdateTime = 0.0
        self.__inSpeedTreeCollision = False
        self.__tmpGameObjects = {}
        self.__engineStarted = False
        self.__turbochargerSoundPlaying = False
        self.partsGameObjects = PartsGameObjects()
        self.__resourceLoadID = None
        self.__highlighter = CGF.ComponentLink(self._gameObject, Highlighter)
        return

    def setVehicle(self, vehicle):
        self._vehicle = vehicle
        self._entityGameObject = vehicle.entityGameObject
        self._isPlayerVehicle = vehicle.isPlayerVehicle
        self.__applyVehicleOutfit()
        self.__linkCompound()
        if self.crashedTracksController:
            self.crashedTracksController.setVehicle(vehicle)

    def setVehicleInfo(self, vehInfo):
        super(CompoundAppearance, self).setVehicleInfo(vehInfo)
        self.__updateStickers()

    def _initDirtComponent(self, ctx):
        super(CompoundAppearance, self)._initDirtComponent(ctx)
        if not self.isObserver:
            self.__dirtLastUpdateTime = ctx.gameTime

    def __arenaPeriodChanged(self, period, *otherArgs):
        if self.detailedEngineState:
            engine_state.notifyEngineOnArenaPeriodChange(self.detailedEngineState, period)

    @property
    def _vehicleColliderInfo(self):
        if self.damageState.isCurrentModelDamaged:
            chassisCollisionMatrix = self.compoundModel.matrix
            gunNodeName = 'gun'
        else:
            chassisCollisionMatrix = self._vehicle.filter.groundPlacingMatrix
            gunNodeName = TankNodeNames.GUN_INCLINATION
        return (chassisCollisionMatrix, gunNodeName)

    def onActivate(self, ctx):
        if self.__activationState in (_ActivationState.NOT_ACTIVATED, _ActivationState.DEACTIVATED):
            if self._vehicle is None:
                return
            player = BigWorld.player()
            isPlayerVehicle = self._isPlayerVehicle or self._vehicle.id == player.observedVehicleID
            if isPlayerVehicle and ctx.collisions:
                self.addCameraCollider(ctx.collisions)
                self.__inSpeedTreeCollision = True
                BigWorld.setSpeedTreeCollisionBody(self.compoundModel.getBoundsForPart(TankPartIndexes.HULL))
            vehicle = self._vehicle
            if ctx.customEffectManager:
                ctx.customEffectManager.setVehicle(vehicle)
            if ctx.crashedTracksController:
                ctx.crashedTracksController.setVehicle(vehicle)
            if ctx.frictionAudition:
                ctx.frictionAudition.setVehicleMatrix(vehicle.matrix)
            if ctx.highlighter:
                ctx.highlighter.setVehicle(vehicle)
                ctx.highlighter.activate(ctx.collisions)
            self.__createTerrainCircle()
            super(CompoundAppearance, self).onActivate(ctx)
            self.onModelChanged()
            arena = player.arena
            arena.onPeriodChange += self.__arenaPeriodChanged
            arena.onVehicleUpdated += self.__vehicleUpdated
            player.inputHandler.onCameraChanged += self._onCameraChanged
            if ctx.detailedEngineState:
                engine_state.checkEngineStart(ctx.detailedEngineState, arena.period)
            if self.isObserver:
                self.disableCustomEffects()
            self.__activationState = _ActivationState.ACTIVATED
        elif self.__activationState == _ActivationState.MODEL_UPDATING:
            self.__activateOnModelUpdate(ctx)
            self.__activationState = _ActivationState.MODEL_UPDATED
            self.onModelChanged()
        return

    def disableCustomEffects(self):
        self.__customEffectsEnabled = False
        if self.customEffectManager:
            self.customEffectManager.enable(False, EffectSettings.SETTING_DUST)
            self.customEffectManager.enable(False, EffectSettings.SETTING_EXHAUST)
            self.customEffectManager.disableSelectors()

    def deactivate(self):
        super(CompoundAppearance, self).deactivate()
        if self.highlighter:
            if self._isPlayerVehicle:
                self.highlighter.highlight(False)
            self.highlighter.deactivate()
        player = BigWorld.player()
        arena = player.arena if player is not None else None
        if arena is not None:
            BigWorld.player().arena.onVehicleUpdated -= self.__vehicleUpdated
            BigWorld.player().arena.onPeriodChange -= self.__arenaPeriodChanged
            BigWorld.player().inputHandler.onCameraChanged -= self._onCameraChanged
        self._vehicle.filter = self.__originalFilter
        self.filter.reset()
        self.__originalFilter = None
        self._vehicle.model = None
        self.compoundModel.matrix = Math.Matrix()
        self._vehicle = None
        self._isPlayerVehicle = False
        return

    def onDeactivate(self, ctx):
        if self.__activationState in (_ActivationState.DEACTIVATED, _ActivationState.MODEL_UPDATING):
            return
        else:
            if self.__resourceLoadID is not None:
                BigWorld.stopLoadResourceListBGTask(self.__resourceLoadID)
            self.__engineStarted = False
            self.__activationState = _ActivationState.DEACTIVATED
            super(CompoundAppearance, self).onDeactivate(ctx)
            if self.__inSpeedTreeCollision:
                BigWorld.setSpeedTreeCollisionBody(None)
            if ctx.collisions:
                BigWorld.removeCameraCollider(ctx.collisions.getColliderID())
            self.turretMatrix.target = None
            self.gunMatrix.target = None
            self.__showCircleDelayed = None
            if self.__terrainCircle.isAttached():
                self.__terrainCircle.detach()
            self._stopEffects(True)
            return

    def isActualVehicle(self, vehicle):
        if not super(CompoundAppearance, self).isActualVehicle(vehicle):
            return False
        else:
            publicInfo = getattr(vehicle, 'publicInfo', None)
            return False if publicInfo is None else self.vStrCD == publicInfo['compDescr'] and self.vRespawnID == publicInfo['respawnID']

    def _startSystems(self, ctx):
        super(CompoundAppearance, self)._startSystems(ctx)
        if ctx.highlighter and self._isPlayerVehicle:
            ctx.highlighter.highlight(True)

    def _onEngineStart(self):
        if super(CompoundAppearance, self).isIgnoreEngineStart():
            return
        else:
            super(CompoundAppearance, self)._onEngineStart()
            self.__engineStarted = True
            if self._vehicle is not None:
                self.__setTurbochargerSound(self._vehicle.getOptionalDevices())
            return

    def __destroyEngineAudition(self, queue=None):
        queue = queue or CGF.CommandQueue(self._spaceID)
        queue.removeComponent(self._gameObject, Vehicular.VehicleAudition)
        if self.detailedEngineState:
            self.detailedEngineState.onEngineStart = None
        self.__turbochargerSoundPlaying = False
        return

    def __processPostmortemComponents(self, postmrtCtx):
        if self.wheelsAnimator and self.wheelsAnimator.activePostmortem:
            self.wheelsAnimator.reattachToCrash(self.compoundModel, self.fashion)
        if self.suspension and self.suspension.activePostmortem:
            self.suspension.reattachCompound(self.compoundModel)
        if self.leveredSuspension and self.leveredSuspension.activePostmortem:
            self.leveredSuspension.reattachCompound(self.compoundModel)
        if self.vehicleTraces and self.vehicleTraces.activePostmortem:
            self.vehicleTraces.setCompound(self.compoundModel)
        if postmrtCtx.collisionObstaclesCollector and postmrtCtx.collisionObstaclesCollector.activePostmortem:
            postmrtCtx.collisionObstaclesCollector.reattachCompound(self.compoundModel)
        if postmrtCtx.tessellationCollisionSensor and postmrtCtx.tessellationCollisionSensor.activePostmortem:
            postmrtCtx.tessellationCollisionSensor.reattachCompound(self.compoundModel)

    def __prepareSystemsForDamagedVehicle(self, vehicle, isTurretDetached, postmrtCtx):
        queue = CGF.CommandQueue(self._spaceID)
        if self.vehicleTraces and not self.vehicleTraces.activePostmortem:
            queue.removeComponent(self._gameObject, Vehicular.VehicleTraces)
        queue.removeComponent(self._gameObject, HullAimingController)
        queue.removeComponent(self._gameObject, Vehicular.SuspensionSound)
        self.resetSwingingAnimator()
        queue.removeComponent(self._gameObject, Vehicular.BurnoutProcessor)
        CGF.resetLink(self._gunRecoilLink)
        self._gunAnimators.setup(0)
        queue.removeComponent(self._gameObject, Vehicular.LinkedNodesPitchAnimator)
        queue.removeComponent(self._gameObject, CrashedTracksController)
        if self.suspension and not self.suspension.activePostmortem:
            queue.removeComponent(self._gameObject, Vehicular.Suspension)
        if self.leveredSuspension and not self.leveredSuspension.activePostmortem:
            queue.removeComponent(self._gameObject, Vehicular.LeveredSuspension)
        queue.removeComponent(self._gameObject, Vehicular.TrackNodesAnimator)
        if self.wheelsAnimator and not self.wheelsAnimator.activePostmortem:
            queue.removeComponent(self._gameObject, Vehicular.GeneralWheelsAnimator)
            queue.removeComponent(self._gameObject, Vehicular.TankWheelsAnimator)
        queue.removeComponent(self._gameObject, Vehicular.GearBox)
        queue.removeComponent(self._gameObject, Vehicular.GunRotatorAudition)
        for _, componentType in self.__tmpGameObjects.items():
            queue.removeComponent(self._gameObject, componentType)

        self.__tmpGameObjects.clear()
        fashions = VehiclePartsTuple(BigWorld.WGVehicleFashion(), None, None, None)
        self._setFashions(fashions, isTurretDetached)
        model_assembler.setupTracksFashion(self.typeDescriptor, self.fashion)
        self.showStickers(False)
        self.__destroyEngineAudition(queue)
        queue.removeComponent(self._gameObject, CustomEffectManager)
        queue.removeComponent(self._gameObject, Vehicular.DetailedGunState)
        queue.removeComponent(self._gameObject, Vehicular.SiegeState)
        queue.removeComponent(self._gameObject, Vehicular.DetailedEngineState)
        queue.removeComponent(self._gameObject, Vehicular.FrictionAudition)
        queue.removeComponent(self._gameObject, Vehicular.TerrainMatKindSensor)
        queue.removeComponent(self._gameObject, Vehicular.VehicleSoundTriggerTarget)
        self._splineTracks = None
        model = self.compoundModel
        self.waterSensor.sensorPlaneLink = model.root
        queue.removeComponent(self._gameObject, Vehicular.DirtComponent)
        if self.tracks:
            queue.removeComponent(self._gameObject, Vehicular.VehicleTracks)
        if postmrtCtx.collisionObstaclesCollector and not postmrtCtx.collisionObstaclesCollector.activePostmortem:
            queue.removeComponent(self._gameObject, Vehicular.CollisionObstaclesCollector)
        if postmrtCtx.tessellationCollisionSensor and not postmrtCtx.tessellationCollisionSensor.activePostmortem:
            queue.removeComponent(self._gameObject, Vehicular.TessellationCollisionSensor)
        queue.removeComponent(self._gameObject, SiegeEffectsController)
        self.partsGameObjects = None
        queue.removeComponent(self._gameObject, Highlighter)
        self._destroySystems()
        self._loadingQueue = []
        self._destroyStickers()
        return

    def onDestroy(self, ctx):
        _logger.debug('CompoundAppearance onDestroy(%r)', self.id)
        if not self.isConstructed:
            return
        else:
            self.__destroyEngineAudition()
            if self.fashion is not None:
                self.fashion.removePhysicalTracks()
            if ctx.vehicleTracks:
                ctx.vehicleTracks.reset()
            super(CompoundAppearance, self).onDestroy(ctx)
            self.__showCircleDelayed = None
            if self.__terrainCircle is not None:
                self.__terrainCircle.destroy()
                self.__terrainCircle = None
            self.onModelChanged.clear()
            self.onModelChanged = None
            return

    def construct(self, isPlayer, resourceRefs):
        super(CompoundAppearance, self).construct(isPlayer, resourceRefs)
        self.__resourceLoadID = None
        cgfQueue = CGF.CommandQueue(self._spaceID)
        cgfQueue.createComponent(self._gameObject, Highlighter, self.isAlive)
        if self.damageState.effect is not None:
            self.playEffect(self.damageState.effect, SpecialKeyPointNames.STATIC)
        return

    def addTempGameObject(self, component, name):
        if name in self.__tmpGameObjects:
            _logger.warning('Attempt to add existed Game Object %s', name)
        else:
            self.__tmpGameObjects[name] = type(component)
            queue = CGF.CommandQueue(self._spaceID)
            queue.assignComponent(self.gameObject, component)

    def removeTempGameObject(self, name):
        componentType = self.__tmpGameObjects.pop(name, None)
        if componentType is not None:
            queue = CGF.CommandQueue(self._spaceID)
            queue.removeComponent(self._gameObject, componentType)
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
        _logger.debug('CompoundAppearance.updateTurretVisibility (%r)', self.id)
        self.__requestModelsRefresh()

    def changeVisibility(self, modelVisible):
        self.compoundModel.visible = modelVisible
        self.showStickers(modelVisible)
        if self.crashedTracksController:
            self.crashedTracksController.setVisible(modelVisible)

    def changeDrawPassVisibility(self, visibilityMask):
        colorPassEnabled = visibilityMask & BigWorld.ColorPassBit != 0
        self.compoundModel.visible = visibilityMask
        self.compoundModel.skipColorPass = not colorPassEnabled
        self.compoundModel.skipEdgeDrawerPass = not colorPassEnabled
        self.showStickers(colorPassEnabled)
        if self.crashedTracksController:
            self.crashedTracksController.setVisible(visibilityMask)

    def onVehicleHealthChanged(self, showEffects=True):
        _logger.debug('CompoundAppearance.onVehicleHealthChanged (%r)', self.id)
        vehicle = self._vehicle
        if self.damageState.isCurrentModelDamaged:
            return
        else:
            if not vehicle.isAlive() and vehicle.health > 0:
                self.changeEngineMode((0, 0))
            currentState = self.damageState
            previousState = currentState.state
            currentState.update(vehicle.health, vehicle.isCrewActive, self.isUnderwater)
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
        if self.swingingAnimator:
            self.swingingAnimator.accelSwingingPeriod = 0.0

    def removeDamageSticker(self, code):
        if self.vehicleStickers is not None:
            self.vehicleStickers.delDamageSticker(code)
        return

    def addDamageSticker(self, code, stickerID, data, isActive=False):
        if self.vehicleStickers is not None:
            self.vehicleStickers.addDamageSticker(code, stickerID, data, self.collisions, self.isCompositionReady, isActive)
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
        if not self._vehicle.isAlive() or not self.crashedTracksController:
            return
        else:
            pairsCnt = self.crashedTracksController.getPairsCnt()
            isLeftTrack = index < pairsCnt
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
                if not destroy and self._isPlayerVehicle and any((device.groupName == 'extraHealthReserve' for device in vehicle.getOptionalDevices() if device is not None)):
                    SoundGroups.g_instance.playSound2D('cons_springs')
                if trackPairIdx == MAIN_TRACK_PAIR_IDX:
                    self.engineAudition.onChassisDestroy(position, destroy, materialType)
            return

    def turretDamaged(self):
        player = BigWorld.player()
        if player is None or self._vehicle is None or not self._isPlayerVehicle:
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
        if player is None or self._vehicle is None or not self._isPlayerVehicle:
            return 0
        else:
            gunRotator = getattr(player, 'gunRotator', None)
            return gunRotator.maxturretRotationSpeed if gunRotator is not None else 0

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
        BigWorld.player().inputHandler.onVehicleShaken(self._vehicle, ShakeReason.OWN_SHOT_DELAYED, gunPos, impulseDir, self.typeDescriptor.gun.effectsCaliber)
        return impulseDir

    def _getWheelsFilters(self):
        fstList = self._vehicle.wheelsScrollFilters if self._vehicle.wheelsScrollFilters else []
        scndList = self._vehicle.wheelsSteeringFilters if self._vehicle.wheelsSteeringFilters else []
        return fstList + scndList

    def __applyVehicleOutfit(self):
        camouflages.updateFashions(self)

    def getBounds(self, partIdx):
        return self.collisions.getBoundingBox(DamageFromShotDecoder.convertComponentIndex(partIdx, self.collisions)) if self.collisions else (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0), 0)

    def __requestModelsRefresh(self):
        _logger.debug('CompoundAppearance.__requestModelsRefresh (%r)', self.id)
        self._onRequestModelsRefresh()
        self._isTurretDetached = self._vehicle.isTurretDetached
        modelsSetParams = self.modelsSetParams
        assembler = model_assembler.prepareCompoundAssembler(self.typeDescriptor, modelsSetParams, self._spaceID, self.isTurretDetached)
        collisionAssembler = model_assembler.prepareCollisionAssembler(self.typeDescriptor, self.isTurretDetached, self._spaceID)
        self.__resourceLoadID = BigWorld.loadResourceListBG((assembler, collisionAssembler), makeCallbackWeak(self.__onModelsRefresh, modelsSetParams.state), loadingPriority(self._vehicle.id))

    def __onModelsRefresh(self, modelState, resourceList):
        _logger.debug('CompoundAppearance.__onModelsRefresh (%r)', self.id)
        self.__resourceLoadID = None
        if not self.damageState.isCurrentModelDamaged:
            _logger.error('Current model is not damaged. Wrong refresh request!')
        if modelState != self.damageState.modelState:
            _logger.error('Required modelState differs from actual one. Wrong refresh request!')
        if self._vehicle is None:
            return
        else:
            if self.highlighter:
                self.highlighter.highlight(False)
            queue = CGF.CommandQueue(self._spaceID)
            holder = queue.createPendingGameObject()
            queue.assignComponent(holder, CompoundHolder(self._vehicle.model))
            queue.createComponent(holder, GenericComponents.RemoveGoDelayedComponent, 1.0)
            prevTurretYaw = Math.Matrix(self.turretMatrix).yaw
            prevGunPitch = Math.Matrix(self.gunMatrix).pitch
            newCompoundModel = resourceList[self.typeDescriptor.name]
            isRightSideFlying = self.isRightSideFlying
            isLeftSideFlying = self.isLeftSideFlying
            if self.__originalFilter is not None:
                self._vehicle.filter = self.__originalFilter
            self.filter.setFlyingInfo(None)
            self.filter.reset()
            shadowManager = self._gameObject.findWrite(VehicleShadowManager)
            shadowManager.reattachCompoundModel(self._vehicle, self.compoundModel, newCompoundModel)
            if self.__inSpeedTreeCollision:
                BigWorld.setSpeedTreeCollisionBody(None)
                self.__inSpeedTreeCollision = False
            self._compoundModel = newCompoundModel
            queue.removeComponent(self._gameObject, GenericComponents.DynamicModelComponent)
            queue.createComponent(self._gameObject, GenericComponents.DynamicModelComponent, self._compoundModel)
            queue.removeComponent(self._gameObject, BigWorld.CollisionComponent)
            queue.createComponent(self._gameObject, BigWorld.CollisionComponent, self._spaceID, resourceList['collisionAssembler'])
            self.__linkCompound()
            postmortemCtx = _PostmortemContext(self._gameObject.findRead(Vehicular.CollisionObstaclesCollector), self._gameObject.findRead(Vehicular.TessellationCollisionSensor))
            self.__prepareSystemsForDamagedVehicle(self._vehicle, self.isTurretDetached, postmortemCtx)
            self.__processPostmortemComponents(postmortemCtx)
            if isRightSideFlying:
                self.fashion.changeTrackVisibility(False, False, MAIN_TRACK_PAIR_IDX)
            if isLeftSideFlying:
                self.fashion.changeTrackVisibility(True, False, MAIN_TRACK_PAIR_IDX)
            self._setupModels()
            self.boundEffects.reattachTo(self.compoundModel)
            self.filter.syncGunAngles(prevTurretYaw, prevGunPitch)
            self._updateAttachments()
            prefabMap = [ PrefabsMapItem(attachment.slotName, attachment.modelName) for attachment in self.attachments if not attachment.hidden ]
            extraSlots = getExtraSlotMap(self.typeDescriptor, self) + getObjectSlots(self.typeDescriptor)
            dynSlots = None
            if self.typeDescriptor.type.isWheeledVehicle:
                dynSlots = self.typeDescriptor.chassis.generalWheelsAnimatorConfig.getNonTrackWheelNodeNames()
            self.setCompositionReady(False)
            removeComposition(self._gameObject)
            createVehicleComposition(gameObject=self._gameObject, vehicleGameObject=self._entityGameObject, prefabMap=prefabMap, followNodes=True, extraSlots=extraSlots, dynSlotNodes=dynSlots)
            self.__activationState = _ActivationState.MODEL_UPDATING
            queue.deactivateGameObject(self._gameObject)
            queue.activateGameObject(self._gameObject)
            return

    def __activateOnModelUpdate(self, ctx):
        self._calcWeaponEnergy(ctx.collisions)
        if ctx.engineAudition:
            ctx.engineAudition.setWeaponEnergy(self.weaponEnergy)
        if ctx.flyingInfoProvider:
            ctx.flyingInfoProvider.setData(self._vehicle.filter, None)
        self._connectCollider(ctx.collisions)
        return

    def __onCrewKilled(self):
        queue = CGF.CommandQueue(self._spaceID)
        self.__destroyEngineAudition(queue)
        if self.customEffectManager:
            queue.removeComponent(self._gameObject, CustomEffectManager)
            queue.removeComponent(self._gameObject, SiegeEffectsController)

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

    def _periodicUpdate(self, ctx):
        super(CompoundAppearance, self)._periodicUpdate(ctx)
        if self._vehicle is None:
            return
        elif not self._vehicle.isAlive():
            return
        else:
            self.__updateTransmissionScroll(ctx.generalWheelsAnimator or ctx.tankWheelsAnimator)
            return

    def updateDirt(self, ctx):
        if self.fashion is None or self._vehicle is None:
            return
        elif self.__dirtNextUpdateTime >= ctx.gameTime:
            return
        else:
            dt = 1.0
            distanceFromPlayer = ctx.lodCalculator.lodDistance
            if 0.0 <= distanceFromPlayer < _PERIODIC_TIME_DIRT[1][1]:
                simDt = ctx.gameTime - self.__dirtLastUpdateTime
                if simDt > 0.0:
                    if ctx.dirtComponent:
                        roll = Math.Matrix(self.compoundModel.matrix).roll
                        hasContact = 0
                        waterHeight = ctx.waterSensor.waterHeight
                        if math.fabs(roll) > math.radians(120.0):
                            hasContact = 2
                            if ctx.waterSensor.isInWater:
                                waterHeight = 1.0
                        elif self.trackScrollController is not None:
                            hasContact = 0 if self.trackScrollController.hasContact() else 1
                        ctx.dirtComponent.update(self.filter.averageSpeed, waterHeight, ctx.waterSensor.waterHeightWorld, self.terrainMatKind[2], hasContact, simDt)
                    self.__dirtLastUpdateTime = ctx.gameTime
                if distanceFromPlayer <= _PERIODIC_TIME_DIRT[1][0] or self._isPlayerVehicle:
                    dt = _PERIODIC_TIME_DIRT[0][0]
                else:
                    dt = _PERIODIC_TIME_DIRT[0][0] + _DIRT_ALPHA * distanceFromPlayer
            self.__dirtNextUpdateTime = ctx.gameTime + dt
            return

    def deviceStateChanged(self, deviceName, state):
        waterSensor = self.waterSensor
        if waterSensor and not waterSensor.isUnderWater and self.detailedEngineState and deviceName == 'engine':
            engineState = engine_state.getEngineStateFromName(state)
            self.detailedEngineState.engineState = engineState

    def __linkCompound(self):
        vehicle = self._vehicle
        vehicle.model = None
        vehicle.model = self.compoundModel
        vehicleMatrix = vehicle.matrix
        self.compoundModel.matrix = vehicleMatrix
        player = BigWorld.player()
        self.__originalFilter = self._vehicle.filter
        self._vehicle.filter = self.filter
        self._vehicle.filter.enableStabilisedMatrix(self._isPlayerVehicle)
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
        if self.frictionAudition:
            self.frictionAudition.processFriction(otherID, frictionPoint, state)

    def _onCameraChanged(self, cameraName, currentVehicleId=None):
        if self.engineAudition:
            self.engineAudition.onCameraChanged(cameraName, currentVehicleId if currentVehicleId is not None else 0)
        if self.tracks:
            if cameraName == 'sniper':
                self.tracks.sniperMode(True)
            else:
                self.tracks.sniperMode(False)
        super(CompoundAppearance, self)._onCameraChanged(cameraName, currentVehicleId=currentVehicleId)
        return

    def __updateTransmissionScroll(self, wheelsAnimator):
        self._commonSlip = 0.0
        self._commonScroll = 0.0
        worldMatrix = Math.Matrix(self.compoundModel.matrix)
        zAxis = worldMatrix.applyToAxis(2)
        vehicleSpeed = zAxis.dot(self.filter.velocity)
        if self._vehicle.wheelsScrollFilters is not None and wheelsAnimator:
            wheelIsFlying = wheelsAnimator.wheelIsFlying
            wheelsSpeed = wheelsAnimator.getWheelsSpeed()
            wheelCount = len(wheelsSpeed)
            skippedWheelsCount = 0
            for wheelIndex in xrange(0, wheelCount):
                flying = wheelIsFlying(wheelIndex)
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

    def addCameraCollider(self, collisions=None):
        collisions = collisions or self.collisions
        if collisions:
            colliderData = (collisions.getColliderID(), tuple(collisions.partIndices))
            BigWorld.appendCameraCollider(colliderData)

    def removeCameraCollider(self):
        collider = self.collisions
        if collider:
            BigWorld.removeCameraCollider(collider.getColliderID())

    def onEngineDamageRisk(self, risk):
        if self.engineAudition:
            self.engineAudition.onEngineDamageRisk(risk)

    def getWheelsSteeringMax(self):
        if self._vehicle is not None:
            filters = self._vehicle.wheelsSteeringFilters
            if filters is not None and len(filters) >= 2:
                wheelsSteering = self._vehicle.wheelsSteeringSmoothed
                return -max(wheelsSteering[0], wheelsSteering[1], key=math.fabs)
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
            if self.engineAudition:
                engineSoundObject = self.engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
                engineSoundObject.play('cons_turbine_start' if isEnabled else 'cons_turbine_stop')
                self.__turbochargerSoundPlaying = isEnabled
            return
