# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/vehicle_appearance/common_tank_appearance.py
from __future__ import absolute_import
import math
import random
import logging
import typing
from future.utils import viewitems, viewvalues
from past.builtins import xrange
import BigWorld
import WoT
import CGF
import GenericComponents
import Triggers
import Math
import Vehicular
import NetworkFilters
import material_kinds
from Event import SafeEvent, EventManager
from cgf_client_common.prefab_loader import PrefabLoader
from cgf_modules.variable_components import VariableStorageComponent
from constants import IS_EDITOR, VEHICLE_SIEGE_STATE, UNKNOWN_RESPAWN_ID
from CustomEffectManager import CustomEffectManager, EffectSettings
from helpers.EffectMaterialCalculation import calcEffectMaterialIndex
from helpers.prefab_effects import resolveGunPrefabEffects
from VehicleStickers import VehicleStickers
from items.components.component_constants import MAIN_TRACK_PAIR_IDX
from items.vehicle_items import CHASSIS_ITEM_TYPE
from objects_hierarchy import ExtraSlotsMapItem
from objects_hierarchy import PrefabsMapItem
from vehicle_systems import model_assembler
from vehicle_systems import camouflages
from vehicle_systems.components.highlighter import Highlighter
from vehicle_systems.vehicle_composition import getExtraSlotMap, getObjectSlots, createVehicleComposition, VehicleSlots, removeComposition
from vehicle_systems.vehicle_damage_state import VehicleDamageState
from vehicle_systems.tankStructure import VehiclePartsTuple, ModelsSetParams, TankPartNames, ColliderTypes, TankPartIndexes, TankNodeNames, CgfTankNodes, TankSoundObjectsIndexes, TankRenderMode
from vehicle_systems.components.CrashedTracks import CrashedTracksController
from vehicle_systems.components.hull_aiming_controller import HullAimingController
from vehicle_systems.components.vehicleDecal import VehicleDecal
from vehicle_systems.components.siegeEffectsController import SiegeEffectsController
from vehicle_systems.components.vehicle_shadow_manager import VehicleShadowManager
from vehicle_appearance.constants import DEFAULT_STICKERS_ALPHA, AppearanceState
from vehicle_appearance.component import VehicleAppearanceComponent
from helpers import bound_effects, gEffectsDisabled
from vehicle_outfit.outfit import Outfit
from items.battle_royale import isSpawnedBot
from helpers import isPlayerAvatar
from ModelHitTester import ModelStatus
from vehicle_systems.components.debris_crashed_track_component import DebrisCrashedTrackComponent
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)
MATKIND_COUNT = 3
MATKIND_COUNT_RANGE = list(range(MATKIND_COUNT))
MAX_DISTANCE = 500
VEHICLE_PRIORITY_GROUP = 1
WHEELED_CHASSIS_PRIORITY_GROUP = 2
TANK_FRICTION_EVENT = 'collision_tank_friction_pc'
_LOD_DISTANCE_EXHAUST = 200.0
_LOD_DISTANCE_TRAIL_PARTICLES = 100.0

class PartProperties(object):
    HIGHLIGHTABLE = 1
    HIGHLIGHTBYVISUAL = 2


class GunAnimators(object):

    def __init__(self):
        self._animatorsLinks = []

    def setup(self, count):
        self._animatorsLinks = [ CGF.ComponentLink() for _ in xrange(count) ]

    def get(self, index):
        if len(self._animatorsLinks) > index:
            return self._animatorsLinks[index]
        else:
            _logger.error('Trying to get gun animator by index %i, but there are only %i gun animators', index, len(self._animatorsLinks))
            return None

    def set(self, index, gameObject):
        if len(self._animatorsLinks) > index:
            self._animatorsLinks[index] = CGF.ComponentLink(gameObject, Vehicular.RecoilComponent)
            return
        _logger.error('Trying to set gun animator by index %i, but there are only %i gun animators', index, len(self._animatorsLinks))


ActivateContext = typing.NamedTuple('ActivateContext', (('gameTime', float),
 ('appearanceComponent', VehicleAppearanceComponent),
 ('collisions', BigWorld.CollisionComponent),
 ('lodCalculator', Vehicular.LodCalculator),
 ('generalWheelsAnimator', Vehicular.GeneralWheelsAnimator),
 ('tankWheelsAnimator', Vehicular.TankWheelsAnimator),
 ('flyingInfoProvider', Vehicular.FlyingInfoProvider),
 ('engineAudition', Vehicular.VehicleAudition),
 ('hullAimingController', HullAimingController),
 ('detailedEngineState', Vehicular.DetailedEngineState),
 ('dirtComponent', Vehicular.DirtComponent),
 ('gearbox', Vehicular.GearBox),
 ('suspension', Vehicular.Suspension),
 ('leveredSuspension', Vehicular.LeveredSuspension),
 ('collisionObstaclesCollector', Vehicular.CollisionObstaclesCollector),
 ('tessellationCollisionSensor', Vehicular.TessellationCollisionSensor),
 ('suspensionSound', Vehicular.SuspensionSound),
 ('waterSensor', Vehicular.WaterSensor),
 ('vehicleTracks', Vehicular.VehicleTracks),
 ('vehicleTraces', Vehicular.VehicleTraces),
 ('trackNodesAnimator', Vehicular.TrackNodesAnimator),
 ('customEffectManager', CustomEffectManager),
 ('terrainMatKindSensor', Vehicular.TerrainMatKindSensor),
 ('frictionAudition', Vehicular.FrictionAudition),
 ('crashedTracksController', CrashedTracksController),
 ('highlighter', Highlighter)))
DeactivateContext = typing.NamedTuple('DeactivateContext', (('appearanceComponent', VehicleAppearanceComponent),
 ('collisions', BigWorld.CollisionComponent),
 ('shadowManager', VehicleShadowManager),
 ('flyingInfoProvider', Vehicular.FlyingInfoProvider)))
DestroyContext = typing.NamedTuple('DestroyContext', (('appearanceComponent', VehicleAppearanceComponent), ('vehicleTracks', Vehicular.VehicleTracks)))
UpdateContext = typing.NamedTuple('UpdateContext', (('appearanceComponent', VehicleAppearanceComponent),
 ('lodCalculator', Vehicular.LodCalculator),
 ('collisions', BigWorld.CollisionComponent),
 ('waterSensor', Vehicular.WaterSensor),
 ('generalWheelsAnimator', Vehicular.GeneralWheelsAnimator),
 ('tankWheelsAnimator', Vehicular.TankWheelsAnimator),
 ('customEffectManager', CustomEffectManager),
 ('detailedEngineState', Vehicular.DetailedEngineState),
 ('vehicleTraces', Vehicular.VehicleTraces),
 ('terrainMatKindSensor', Vehicular.TerrainMatKindSensor),
 ('siegeEffects', SiegeEffectsController)))

class CommonTankAppearance(PrefabLoader):
    state = property(lambda self: self._state)
    isConstructed = property(lambda self: self._state >= AppearanceState.CONSTRUCTED)
    isComponentsCreated = property(lambda self: self._state >= AppearanceState.COMPONENTS_CREATED)
    compoundModel = property(lambda self: self._compoundModel)
    boundEffects = property(lambda self: self.__boundEffects)
    fashions = property(lambda self: self.__fashions)
    fashion = property(lambda self: self.fashions.chassis)
    typeDescriptor = property(lambda self: self.__typeDesc if self._vehicle is None else self._vehicle.typeDescriptor)
    id = property(lambda self: self.__vID)
    vStrCD = property(lambda self: self.__vStrCD)
    vRespawnID = property(lambda self: self.__vRespawnID)
    isAlive = property(lambda self: self.__currentDamageState.isAlive)
    isDestroyed = property(lambda self: self.__currentDamageState.isCurrentModelDamaged)
    isCrewActive = property(lambda self: self.__currentDamageState.isCrewActive)
    isObserver = property(lambda self: self.__isObserver)
    outfit = property(lambda self: self.__outfit)
    renderMode = property(lambda self: self.__renderMode)

    def isReady(self):
        return self.compoundModel is not None

    def _setFashions(self, fashions, isTurretDetached=False):
        if IS_EDITOR and self.__fashions:
            for fashion in self.__fashions:
                if fashion:
                    fashion.disowned()

        self.__fashions = fashions
        if isTurretDetached:
            self.compoundModel.setupFashions((fashions.chassis, fashions.hull))
        else:
            self.compoundModel.setupFashions(fashions)

    def _setOutfit(self, outfitCD):
        self.__outfit = self._prepareOutfit(outfitCD)

    terrainEffectMaterialNames = property(lambda self: self.__terrainEffectMaterialNames)
    isInWater = property(lambda self: self.waterSensor.isInWater if self.waterSensor else False)
    isUnderwater = property(lambda self: self.waterSensor.isUnderWater if self.waterSensor else False)
    waterHeight = property(lambda self: self.waterSensor.waterHeight if self.waterSensor else -1.0)
    damageState = property(lambda self: self.__currentDamageState)
    modelsSetParams = property(lambda self: ModelsSetParams(self.outfit.modelsSet, self.damageState.modelState, self.__attachments))
    attachments = property(lambda self: self.__attachments)
    splineTracks = property(lambda self: self._splineTracks)
    isFlying = property(lambda self: self.flyingInfoProvider and self.flyingInfoProvider.isFlying)
    isLeftSideFlying = property(lambda self: self.flyingInfoProvider and self.flyingInfoProvider.isLeftSideFlying)
    isRightSideFlying = property(lambda self: self.flyingInfoProvider and self.flyingInfoProvider.isRightSideFlying)
    trackScrollController = property(lambda self: self.__trackScrollCtl)
    wheelsState = property(lambda self: 0)
    wheelsSteering = property(lambda self: 0)
    burnoutLevel = property(lambda self: 0.0)
    transmissionSlip = property(lambda self: self._commonSlip)
    vehicleStickers = property(lambda self: self._vehicleStickers)
    isTurretDetached = property(lambda self: self._isTurretDetached)
    weaponEnergy = property(lambda self: self.__weaponEnergy)
    isCompositionReady = property(lambda self: self.__isCompositionReady)
    filter = property(lambda self: self.__filter)
    collisions = property(lambda self: self._collisions)
    crashedTracksController = property(lambda self: self.__crashedTracksController)
    customEffectManager = property(lambda self: self._customEffectManager)
    detailedEngineState = property(lambda self: self._detailedEngineState)
    detailedGunState = property(lambda self: self._detailedGunState)
    engineAudition = property(lambda self: self._engineAudition)
    flyingInfoProvider = property(lambda self: self._flyingInfoProvider)
    frictionAudition = property(lambda self: self._frictionAudition)
    gearbox = property(lambda self: self._gearbox)
    gunRecoil = property(lambda self: self._gunRecoilLink)
    gunAnimators = property(lambda self: self._gunAnimators)
    hullAimingController = property(lambda self: self._hullAimingController)
    leveredSuspension = property(lambda self: self._leveredSuspension)
    suspension = property(lambda self: self._suspension)
    suspensionSound = property(lambda self: self._suspensionSound)
    swingingAnimator = property(lambda self: self._swingingAnimator)
    tracks = property(lambda self: self._tracks)
    vehicleTraces = property(lambda self: self._vehicleTraces)
    waterSensor = property(lambda self: self._waterSensor)
    wheelsAnimator = property(lambda self: self._generalWheelsAnimator or self._tankWheelsAnimator)
    collisionObstaclesCollector = property(lambda self: self._collisionObstaclesCollector)
    tessellationCollisionSensor = property(lambda self: self._tessellationCollisionSensor)

    def __init__(self, spaceID):
        super(CommonTankAppearance, self).__init__(spaceID, CgfTankNodes.TANK_ROOT)
        queue = CGF.CommandQueue(spaceID)
        queue.createComponent(self._gameObject, CGF.HierarchyComponent)
        self._vehicle = None
        self._isPlayerVehicle = False
        self.__wheelsGameObject = queue.createGameObject('Tank.Wheels.Root')
        queue.createComponent(self.__wheelsGameObject, CGF.HierarchyComponent, self._gameObject)
        self.__filter = None
        self.__typeDesc = None
        self.__crashedTracksController = CGF.ComponentLink(self._gameObject, CrashedTracksController)
        self.__currentDamageState = VehicleDamageState()
        self.terrainMatKind = [-1] * MATKIND_COUNT
        self.terrainGroundType = [-1] * MATKIND_COUNT
        self.__terrainEffectMaterialNames = [''] * MATKIND_COUNT
        self._chassisDecal = VehicleDecal(self)
        self.__splodge = None
        self.__boundEffects = None
        self._splineTracks = None
        self.__trackScrollCtl = BigWorld.PyTrackScroll()
        self.__weaponEnergy = 0.0
        self.__outfit = None
        self.__systemStarted = False
        self._isTurretDetached = False
        self.__isObserver = False
        self.__attachments = []
        self.__modelAnimators = []
        self.turretMatrix = None
        self.gunMatrix = None
        self._commonScroll = 0.0
        self._commonSlip = 0.0
        self._compoundModel = None
        self.__fashions = None
        self.__filterRetrieversGo = CGF.GameObject.INVALID_GAME_OBJECT
        self._vehicleStickers = None
        self._vehicleInfo = {}
        self.__vID = 0
        self.__vStrCD = None
        self.__vRespawnID = UNKNOWN_RESPAWN_ID
        self.__renderMode = None
        self.__forceDynAttachmentLoading = False
        self.customizationGameObjects = []
        self.__customEffectsEnabled = True
        self.__useEngStartControlIdle = False
        self.__ignoreEngineStart = False
        self._entityGameObject = CGF.GameObject.INVALID_GAME_OBJECT
        self.__isCompositionReady = False
        self.__eventManager = EventManager()
        self.onComponentsCreated = SafeEvent(self.__eventManager)
        self.onAppearanceActivated = SafeEvent(self.__eventManager)
        self._swingingAnimator = CGF.ComponentLink(self._gameObject, Vehicular.SwingingAnimator)
        self._gunRecoilLink = CGF.ComponentLink(self._gameObject, Vehicular.RecoilComponent)
        self._gunAnimators = GunAnimators()
        self._engineAudition = CGF.ComponentLink(self._gameObject, Vehicular.VehicleAudition)
        self._flyingInfoProvider = CGF.ComponentLink(self._gameObject, Vehicular.FlyingInfoProvider)
        self._frictionAudition = CGF.ComponentLink(self._gameObject, Vehicular.FrictionAudition)
        self._hullAimingController = CGF.ComponentLink(self._gameObject, HullAimingController)
        self._vehicleTraces = CGF.ComponentLink(self._gameObject, Vehicular.VehicleTraces)
        self._waterSensor = CGF.ComponentLink(self._gameObject, Vehicular.WaterSensor)
        self._collisions = CGF.ComponentLink(self._gameObject, BigWorld.CollisionComponent)
        self._suspension = CGF.ComponentLink(self._gameObject, Vehicular.Suspension)
        self._leveredSuspension = CGF.ComponentLink(self._gameObject, Vehicular.LeveredSuspension)
        self._suspensionSound = CGF.ComponentLink(self._gameObject, Vehicular.SuspensionSound)
        self._detailedEngineState = CGF.ComponentLink(self._gameObject, Vehicular.DetailedEngineState)
        self._detailedGunState = CGF.ComponentLink(self._gameObject, Vehicular.DetailedGunState)
        self._gearbox = CGF.ComponentLink(self._gameObject, Vehicular.GearBox)
        self._generalWheelsAnimator = CGF.ComponentLink(self._gameObject, Vehicular.GeneralWheelsAnimator)
        self._tankWheelsAnimator = CGF.ComponentLink(self._gameObject, Vehicular.TankWheelsAnimator)
        self._tracks = CGF.ComponentLink(self._gameObject, Vehicular.VehicleTracks)
        self._customEffectManager = CGF.ComponentLink(self._gameObject, CustomEffectManager)
        self._collisionObstaclesCollector = CGF.ComponentLink(self._gameObject, Vehicular.CollisionObstaclesCollector)
        self._tessellationCollisionSensor = CGF.ComponentLink(self._gameObject, Vehicular.TessellationCollisionSensor)
        self._state = AppearanceState.CREATED
        return

    @property
    def slotPrefabs(self):
        return [ PrefabsMapItem(*it) for it in self.typeDescriptor.getSlotPrefabs(styleName=self.outfit.modelsSet) ]

    def prerequisites(self, vID, vInfo, renderMode=None):
        typeDescriptor = vInfo.typeDescr
        self.damageState.update(vInfo.health, vInfo.isCrewActive, False)
        self.__typeDesc = typeDescriptor
        self.__vID = vID
        self.__vStrCD = typeDescriptor.makeCompactDescr()
        self.__vRespawnID = vInfo.respawnID
        self.__forceDynAttachmentLoading = vInfo.forceDynAttachmentLoading
        self._isTurretDetached = vInfo.isTurretDetached
        self._entityGameObject = vInfo.entityGameObject
        self.__updateModelStatus()
        self.__outfit = self._prepareOutfit(vInfo.outfitCD)
        self._updateAttachments()
        self.__renderMode = renderMode
        prereqs = self.typeDescriptor.prerequisites(True, self.outfit.modelsSet)
        prereqs.extend(camouflages.getCamoPrereqs(self.outfit, self.typeDescriptor))
        prereqs.extend(camouflages.getModelAnimatorsPrereqs(self.outfit, self._spaceID))
        prereqs.extend(camouflages.getAttachmentsAnimatorsPrereqs(self.__attachments, self._spaceID))
        modelsSetParams = self.modelsSetParams
        if IS_EDITOR and not modelsSetParams.skin:
            modelsSetParams = ModelsSetParams(self.currentModelsSet, modelsSetParams.state, modelsSetParams.attachments)
        splineDesc = self.typeDescriptor.chassis.splineDesc
        modelsSet = self.outfit.modelsSet if not IS_EDITOR else modelsSetParams.skin
        if splineDesc is not None:
            for trackDesc in viewvalues(splineDesc.trackPairs):
                prereqs += trackDesc.prerequisites(modelsSet)

        compoundAssembler = model_assembler.prepareCompoundAssembler(self.typeDescriptor, modelsSetParams, self._spaceID, self.isTurretDetached, renderMode=self.renderMode)
        prereqs.append(compoundAssembler)
        collisionAssembler = model_assembler.prepareCollisionAssembler(self.typeDescriptor, self.isTurretDetached, self._spaceID)
        prereqs.append(collisionAssembler)
        physicalTracksBuilders = self.typeDescriptor.chassis.physicalTracks
        for name, builders in viewitems(physicalTracksBuilders):
            for index, builder in enumerate(builders):
                prereqs.append(builder.createLoader(self._spaceID, '{0}{1}PhysicalTrack'.format(name, index), modelsSetParams.skin))

        return prereqs

    def actualize(self, vInfo):
        self.__vRespawnID = vInfo.respawnID

    def construct(self, isPlayer, resourceRefs):
        _logger.debug('Appearance construct(%r)', self.id)
        cgfQueue = CGF.CommandQueue(self._spaceID)
        cgfQueue.createComponent(self._gameObject, VehicleAppearanceComponent, self)
        self.__isObserver = 'observer' in self.typeDescriptor.type.tags
        self._compoundModel = resourceRefs[self.typeDescriptor.name]
        cgfQueue.removeComponent(self._gameObject, GenericComponents.DynamicModelComponent)
        cgfQueue.createComponent(self._gameObject, GenericComponents.DynamicModelComponent, self._compoundModel)
        if not self._compoundModel.isValid():
            _logger.error('compoundModel is not valid')
        if self.typeDescriptor.gun.edgeByVisualModel:
            self._compoundModel.setPartProperties(TankPartIndexes.GUN, PartProperties.HIGHLIGHTABLE | PartProperties.HIGHLIGHTBYVISUAL)
        self._compoundModel.setPartProperties(TankPartIndexes.CHASSIS, PartProperties.HIGHLIGHTABLE | PartProperties.HIGHLIGHTBYVISUAL)
        self.__boundEffects = bound_effects.ModelBoundEffects(self.compoundModel)
        isCurrentModelDamaged = self.damageState.isCurrentModelDamaged
        fashions = camouflages.prepareFashions(isCurrentModelDamaged)
        if not isCurrentModelDamaged:
            model_assembler.setupTracksFashion(self.typeDescriptor, fashions.chassis)
        cgfQueue.createComponent(self._gameObject, BigWorld.CollisionComponent, self._spaceID, resourceRefs['collisionAssembler'])
        self._setFashions(fashions, self.isTurretDetached)
        self._setupModels()
        if not isCurrentModelDamaged:
            modelsSet = self.outfit.modelsSet
            if IS_EDITOR:
                modelsSet = self.modelsSetParams.skin if self.modelsSetParams.skin else self.currentModelsSet
            self._splineTracks = model_assembler.setupSplineTracks(self.fashion, self.typeDescriptor, self.compoundModel, resourceRefs, modelsSet)
            cgfQueue.createComponent(self._gameObject, CrashedTracksController, self.typeDescriptor, self.fashion, modelsSet, self._gameObject)
        else:
            self.__trackScrollCtl = None
        self._chassisDecal.create()
        if not isCurrentModelDamaged:
            self.__modelAnimators = camouflages.getModelAnimators(self.outfit, self.typeDescriptor, self._spaceID, resourceRefs, self.compoundModel)
            self.__modelAnimators.extend(camouflages.getAttachmentsAnimators(self.__attachments, self._spaceID, resourceRefs, self.compoundModel))
        cgfQueue.createComponent(self._gameObject, CGF.TransformComponent, Math.Vector3(0, 0, 0))
        cgfQueue.createComponent(self._gameObject, Triggers.AreaTriggerTarget)
        self.__filter = model_assembler.createVehicleFilter(self.typeDescriptor)
        compoundModel = self.compoundModel
        if self.isAlive:
            model_assembler.assembleDrivetrain(self, isPlayer, cgfQueue)
            cgfQueue.createComponent(self._gameObject, Vehicular.DetailedGunState)
            if not gEffectsDisabled():
                cgfQueue.createComponent(self._gameObject, CustomEffectManager, self)
                if self.typeDescriptor.hasSiegeMode:
                    shouldStopEngineOnSiegeSwitch = self.typeDescriptor.type.shouldStopEngineOnSiegeSwitch
                    cgfQueue.createComponent(self._gameObject, SiegeEffectsController, self, shouldStopEngineOnSiegeSwitch)
                model_assembler.assembleVehicleAudition(isPlayer, self, cgfQueue)
                cgfQueue.createComponent(self._gameObject, Vehicular.VehicleSoundTriggerTarget)
            if isPlayer:
                turret = self.typeDescriptor.turret
                gunRotatorAudition = cgfQueue.createComponent(self._gameObject, Vehicular.GunRotatorAudition, turret.turretRotatorSoundManual, turret.weight / 1000.0, compoundModel.node(TankPartNames.TURRET))
                gunRotatorAudition.vehicleMatrixLink = self.compoundModel.root
                gunRotatorAudition.damaged = lambda : self.turretDamaged()
                gunRotatorAudition.maxTurretRotationSpeed = lambda : self.maxTurretRotationSpeed()
                cgfQueue.createComponent(self._gameObject, Vehicular.FrictionAudition, TANK_FRICTION_EVENT)
        isLodTopPriority = isPlayer
        cgfQueue.createComponent(self._gameObject, Vehicular.LodCalculator, CGF.linkMatrixTranslation(compoundModel.matrix), True, VEHICLE_PRIORITY_GROUP, isLodTopPriority)
        if IS_EDITOR:
            matrixBinding = None
            changeCamera = None
        else:
            matrixBinding = BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged
            changeCamera = BigWorld.player().inputHandler.onCameraChanged
        cgfQueue.createComponent(self._gameObject, VehicleShadowManager, compoundModel, matrixBinding, changeCamera)
        if not self.damageState.isCurrentModelDamaged:
            self.__assembleNonDamagedOnly(resourceRefs, isPlayer, cgfQueue)
            dirtEnabled = BigWorld.WG_dirtEnabled() and 'HD' in self.typeDescriptor.type.tags
            if dirtEnabled and self.fashions is not None:
                cgfQueue.createComponent(self._gameObject, Vehicular.DirtComponent)
        model_assembler.assembleWaterSensor(self.typeDescriptor, self, self._spaceID, cgfQueue)
        cgfQueue.createComponent(self._gameObject, Vehicular.FlyingInfoProvider)
        compoundModel.setPartBoundingBoxAttachNode(TankPartIndexes.GUN, TankNodeNames.GUN_INCLINATION)
        self.createVehicleComposition(cgfQueue)
        camouflages.updateFashions(self, cgfQueue)
        if self.damageState.isCurrentModelUndamaged:
            model_assembler.assembleCustomLogicComponents(self, self.typeDescriptor, self.__attachments, self.__modelAnimators, cgfQueue)
        self._createStickers()
        self._flushLoadingQueue()
        self._state = AppearanceState.CONSTRUCTED
        return

    def destroy(self):
        _logger.debug('Appearance destroy(%r)', self.id)
        queue = CGF.CommandQueue(self._spaceID)
        removeComposition(self._gameObject, queue)
        self._destroy(queue)

    def onDestroy(self, ctx):
        _logger.debug('Appearance onDestroy(%r)', self.id)
        self._vehicleInfo = {}
        self._cancelPrefabLoadRequests()
        queue = CGF.CommandQueue(self._spaceID)
        queue.removeComponent(self._gameObject, Vehicular.FlagComponent)
        queue.removeComponent(self._gameObject, Vehicular.VehicleSoundTriggerTarget)
        self.__forceDynAttachmentLoading = False
        self._destroySystems()
        fashions = VehiclePartsTuple(None, None, None, None)
        self._setFashions(fashions, self._isTurretDetached)
        self.__wheelsGameObject.destroy()
        self.__typeDesc = None
        if self.boundEffects is not None:
            self.boundEffects.destroy()
        self._vehicleStickers = None
        self._chassisDecal.destroy()
        self._chassisDecal = None
        self._compoundModel = None
        self._destroyStickers()
        self._clearLoadingQueue()
        self.__eventManager.clear()
        self._state = AppearanceState.DESTROYED
        return

    def onComponentsCreate(self):
        _logger.debug('Appearance onComponentsCreate(%r)', self.id)
        self._state = AppearanceState.COMPONENTS_CREATED
        self.onComponentsCreated()

    def activate(self, parentUuid):
        _logger.debug('Appearance activate(%r)', self.id)
        self._gameObject.activate()
        hierarchy = self._gameObject.findWrite(CGF.HierarchyComponent)
        if hierarchy:
            hierarchy.parent = parentUuid
        else:
            _logger.error('Unable to find appearance HierarchyComponent')
        self._attachStickers()

    def onActivate(self, ctx):
        _logger.debug('Appearance onActivate(%r)', self.id)
        if ctx.flyingInfoProvider:
            if self.modelsSetParams.state == 'undamaged':
                self.__filter.setFlyingInfo(CGF.createBoolLink(ctx.flyingInfoProvider, 'isFlying'))
            if self.__trackScrollCtl is not None:
                self.__trackScrollCtl.setFlyingInfo(CGF.createBoolLink(ctx.flyingInfoProvider, 'isLeftSideFlying'), CGF.createBoolLink(ctx.flyingInfoProvider, 'isRightSideFlying'))
        self._calcWeaponEnergy(ctx.collisions)
        self.__postSetupFilter(ctx.suspension, ctx.leveredSuspension)
        if ctx.generalWheelsAnimator:
            typeDescr = self.typeDescriptor
            wheelConfig = typeDescr.chassis.generalWheelsAnimatorConfig
            if wheelConfig is not None:
                ctx.generalWheelsAnimator.createCollision(wheelConfig, ctx.collisions)
            self._initWheelsLinks(ctx.generalWheelsAnimator)
        if not self.isObserver:
            self._chassisDecal.attach()
            self._startSystems(ctx)
            self.filter.enableLagDetection(not self.damageState.isCurrentModelDamaged)
        self.setupGunMatrixTargets(self.filter)
        lodStateLink = None
        if ctx.lodCalculator:
            lodStateLink = ctx.lodCalculator.lodStateLink
            ctx.lodCalculator.setupPosition(CGF.linkMatrixTranslation(self.compoundModel.matrix))
            self._initLodLinks(ctx)
        wheeledLodCalculator = self.__wheelsGameObject.findRead(Vehicular.LodCalculator)
        if wheeledLodCalculator:
            lodStateLink = wheeledLodCalculator.lodStateLink
            wheeledLodCalculator.setupPosition(CGF.linkMatrixTranslation(self.compoundModel.matrix))
        if ctx.suspension:
            ctx.suspension.setLodLink(lodStateLink)
        if ctx.leveredSuspension:
            ctx.leveredSuspension.setupLodLink(lodStateLink)
        if ctx.vehicleTracks:
            ctx.vehicleTracks.setLodLink(lodStateLink)
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.setEnabled(True)
            modelAnimator.animator.start()

        if self.isObserver:
            self.compoundModel.visible = False
        self._connectCollider(ctx.collisions)
        if ctx.dirtComponent:
            self._initDirtComponent(ctx)
        if ctx.engineAudition:
            self._initEngineAudition(ctx)
        if ctx.suspensionSound:
            ctx.suspensionSound.setSoundObject(ctx.engineAudition.getSoundObject(TankSoundObjectsIndexes.CHASSIS))
        if ctx.detailedEngineState:
            self._initDrivetrain(ctx)
        self._state = AppearanceState.ACTIVATED
        self.onAppearanceActivated()
        return

    def deactivate(self):
        _logger.debug('Appearance deactivate(%r)', self.id)
        self._gameObject.deactivate()
        hierarchy = self._gameObject.findWrite(CGF.HierarchyComponent)
        if hierarchy:
            hierarchy.parent = CGF.INVALID_UUID

    def onDeactivate(self, ctx):
        _logger.debug('Appearance onDeactivate(%r)', self.id)
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.setEnabled(False)

        ctx.shadowManager.unregisterCompoundModel(self.compoundModel)
        self._stopSystems(ctx)
        self._chassisDecal.detach()
        self._detachStickers()
        self._state = AppearanceState.DEACTIVATED

    def update(self, ctx):
        self._periodicUpdate(ctx)

    def getVehicle(self):
        return self._vehicle

    def isActualVehicle(self, vehicle):
        return self.__vID == vehicle.id

    def setIgnoreEngineStart(self):
        self.__ignoreEngineStart = True

    def isIgnoreEngineStart(self):
        return self.__ignoreEngineStart

    def setSwingingAnimator(self, gameObject):
        CGF.setLinkObject(self._swingingAnimator, gameObject)

    def resetSwingingAnimator(self):
        CGF.resetLink(self._swingingAnimator)

    def setGunRecoil(self, gameObject):
        CGF.setLinkObject(self._gunRecoilLink, gameObject)

    def setVehicleInfo(self, vehInfo):
        self._vehicleInfo = vehInfo

    def setupGunMatrixTargets(self, target):
        self.turretMatrix = target.turretMatrix
        self.gunMatrix = target.gunMatrix

    def receiveShotImpulse(self, direction, impulse):
        if not VehicleDamageState.isDamagedModel(self.damageState.modelState):
            if self.swingingAnimator:
                self.swingingAnimator.receiveShotImpulse(direction, impulse)
            if self.crashedTracksController:
                self.crashedTracksController.receiveShotImpulse(direction, impulse)

    def recoil(self):
        if self.isDestroyed:
            return
        self._initiateRecoil(TankNodeNames.GUN_INCLINATION, 'HP_gunFire', self.gunRecoil)

    def multiGunRecoil(self, indexes):
        if self.isDestroyed:
            return
        for index in indexes:
            typeDescr = self.typeDescriptor
            gunNodeName = typeDescr.gun.multiGun[index].node
            gunFireNodeName = typeDescr.gun.multiGun[index].gunFire
            self._initiateRecoil(gunNodeName, gunFireNodeName, self.gunAnimators.get(index))

    def computeFullVehicleLength(self):
        vehicleLength = 0.0
        if self.compoundModel is not None:
            hullBB = Math.Matrix(self.compoundModel.getBoundsForPart(TankPartIndexes.HULL))
            vehicleLength = hullBB.applyVector(Math.Vector3(0.0, 0.0, 1.0)).length
        return vehicleLength

    def setUseEngStartControlIdle(self, useIdle=False):
        self.__useEngStartControlIdle = useIdle

    def _initiateRecoil(self, gunNodeName, gunFireNodeName, gunRecoil):
        gunNode = self.compoundModel.node(gunNodeName)
        impulseDir = Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1))
        impulseValue = self.typeDescriptor.gun.impulse
        self.receiveShotImpulse(impulseDir, impulseValue)
        if gunRecoil:
            gunRecoil.recoil()
        return impulseDir

    def _connectCollider(self, collisions):
        chassisCollisionMatrix, gunNodeName = self._vehicleColliderInfo
        if self.isTurretDetached:
            collisions.removeAttachment(TankPartNames.getIdx(TankPartNames.TURRET))
            collisions.removeAttachment(TankPartNames.getIdx(TankPartNames.GUN))
            collisionData = ((TankPartNames.getIdx(TankPartNames.HULL), self.compoundModel.node(TankPartNames.HULL)), (TankPartNames.getIdx(TankPartNames.CHASSIS), chassisCollisionMatrix))
        else:
            collisionData = ((TankPartNames.getIdx(TankPartNames.HULL), self.compoundModel.node(TankPartNames.HULL)),
             (TankPartNames.getIdx(TankPartNames.TURRET), self.compoundModel.node(TankPartNames.TURRET)),
             (TankPartNames.getIdx(TankPartNames.CHASSIS), chassisCollisionMatrix),
             (TankPartNames.getIdx(TankPartNames.GUN), self.compoundModel.node(gunNodeName)))
        defaultPartLength = len(TankPartNames.ALL)
        additionalChassisParts = []
        trackPairs = self.typeDescriptor.chassis.trackPairs
        if not trackPairs:
            trackPairs = [None]
        for x in xrange(len(trackPairs) - 1):
            additionalChassisParts.append((defaultPartLength + x, chassisCollisionMatrix))

        if additionalChassisParts:
            collisionData += tuple(additionalChassisParts)
        collisions.connect(self.id, ColliderTypes.VEHICLE_COLLIDER, collisionData)
        model_assembler.setupCollisions(self.typeDescriptor, collisions)
        return

    def computeVehicleHeight(self, collisions):
        desc = self.typeDescriptor
        hullBB = collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.HULL))
        turretBB = collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.TURRET))
        gunBB = collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN))
        hullTopY = desc.chassis.hullPosition[1] + hullBB[1][1]
        turretTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + turretBB[1][1]
        gunTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + desc.turret.gunPosition[1] + gunBB[1][1]
        gunLength = math.fabs(gunBB[1][2] - gunBB[0][2])
        height = max(hullTopY, turretTopY, gunTopY)
        return (height, gunLength)

    def onWaterSplash(self, waterHitPoint, isHeavySplash):
        pass

    def onUnderWaterSwitch(self, isUnderWater):
        pass

    def getWheelsSteeringMax(self):
        pass

    def setCompositionReady(self, ready):
        self.__isCompositionReady = ready

    def _initDirtComponent(self, ctx):
        compoundModel = self.compoundModel
        dirtHandlers = [BigWorld.PyDirtHandler(True, compoundModel.node(TankPartNames.CHASSIS).position.y),
         BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.HULL).position.y),
         BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.TURRET).position.y),
         BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.GUN).position.y)]
        modelHeight, _ = self.computeVehicleHeight(ctx.collisions)
        ctx.dirtComponent.init(dirtHandlers, modelHeight)
        for fashionIdx, _ in enumerate(TankPartNames.ALL):
            self.fashions[fashionIdx].addMaterialHandler(dirtHandlers[fashionIdx])
            self.fashions[fashionIdx].addTrackMaterialHandler(dirtHandlers[fashionIdx])

    def _initEngineAudition(self, ctx):
        ctx.engineAudition.setTracksInfo(lambda : self._commonScroll, lambda : self._commonSlip, self.getWheelsSteeringMax, CGF.createBoolLink(ctx.flyingInfoProvider, 'isFlying'))
        ctx.engineAudition.setIsUnderwaterInfo(CGF.createBoolLink(ctx.waterSensor, 'isUnderWater'))
        ctx.engineAudition.setIsInWaterInfo(CGF.createBoolLink(ctx.waterSensor, 'isInWater'))
        if self.__useEngStartControlIdle:
            engineSoundObject = ctx.engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
            engineSoundObject.setSwitch('SWITCH_ext_eng_start_control', 'SWITCH_ext_eng_start_control_idle')

    def _initLodLinks(self, ctx):
        lodLink = CGF.createFloatLink(ctx.lodCalculator, 'lodDistance')
        lodStateLink = ctx.lodCalculator.lodStateLink
        if ctx.waterSensor:
            ctx.waterSensor.setLodLink(lodStateLink)
        if ctx.terrainMatKindSensor:
            ctx.terrainMatKindSensor.setLodLink(lodStateLink)
        if ctx.collisionObstaclesCollector:
            ctx.collisionObstaclesCollector.setLodLink(lodStateLink)
            model_assembler.setLodSettings(self, ctx.collisionObstaclesCollector)
        if ctx.tessellationCollisionSensor:
            ctx.tessellationCollisionSensor.setLodLink(lodStateLink)
            model_assembler.setLodSettings(self, ctx.tessellationCollisionSensor)
        if ctx.generalWheelsAnimator:
            ctx.generalWheelsAnimator.setLodLink(lodStateLink)
        if ctx.tankWheelsAnimator:
            ctx.tankWheelsAnimator.setLodLink(lodStateLink)
        if ctx.suspensionSound:
            ctx.suspensionSound.lodLink = lodLink
        if ctx.trackNodesAnimator:
            ctx.trackNodesAnimator.setLodLink(lodStateLink)
        if ctx.vehicleTracks:
            ctx.vehicleTracks.setLodLink(lodStateLink)
        if ctx.vehicleTraces:
            ctx.vehicleTraces.setLodLink(lodStateLink)

    def _initDrivetrain(self, ctx):
        ctx.detailedEngineState.vehicleSpeedLink = CGF.createFloatLink(self.filter, 'averageSpeed')
        ctx.detailedEngineState.rotationSpeedLink = CGF.createFloatLink(self.filter, 'averageRotationSpeed')
        ctx.detailedEngineState.vehicleMatrixLink = self.compoundModel.root
        if ctx.gearbox:
            ctx.gearbox.vehicleSpeedLink = CGF.createFloatLink(self.filter, 'averageSpeed')
        if self._isPlayerVehicle:
            if not ctx.gearbox and not IS_EDITOR:
                p = BigWorld.player()
                ctx.detailedEngineState.physicRPMLink = lambda : WoT.unpackAuxVehiclePhysicsData(p.ownVehicleAuxPhysicsData)[5]
                ctx.detailedEngineState.physicGearLink = lambda : BigWorld.player().ownVehicleGear
        else:
            ctx.detailedEngineState.physicRPMLink = None
            ctx.detailedEngineState.physicGearLink = None
        if not gEffectsDisabled():
            ctx.detailedEngineState.onEngineStart = self._onEngineStart
        return

    def _prepareOutfit(self, outfitCD):
        outfitComponent = camouflages.getOutfitComponent(outfitCD)
        return Outfit(component=outfitComponent, vehicleCD=self.typeDescriptor.makeCompactDescr())

    def _calcWeaponEnergy(self, collisions):
        if self.isAlive:
            _, gunLength = self.computeVehicleHeight(collisions)
            self.__weaponEnergy = gunLength * self.typeDescriptor.shot.shell.caliber

    def _setupModels(self):
        if MAX_DISTANCE > 0 and not self.isObserver:
            transform = self.typeDescriptor.chassis.AODecals[0]
            splodge = BigWorld.Splodge(transform, MAX_DISTANCE, self.typeDescriptor.chassis.hullPosition.y)
            if splodge:
                self.__splodge = splodge
                node = self.compoundModel.node(TankPartNames.HULL)
                node.attach(splodge)

    def _createStickers(self):
        _logger.debug('Creating VehicleStickers for vehicleType: %s', self.typeDescriptor)
        isCurrentModelDamaged = self.damageState.isCurrentModelDamaged
        if isCurrentModelDamaged:
            return
        else:
            if self.vehicleStickers is not None:
                self._destroyStickers()
            self._vehicleStickers = VehicleStickers(self._spaceID, self._gameObject, self.typeDescriptor, outfit=self.outfit)
            return

    def _destroyStickers(self):
        _logger.debug('Detaching VehicleStickers for vehicleType: %s', self.__typeDesc)
        self._detachStickers()
        self._vehicleStickers = None
        return

    def _attachStickers(self):
        _logger.debug('Attaching VehicleStickers for vehicle: %s', self._vehicle)
        isCurrentModelDamaged = self.damageState.isCurrentModelDamaged
        if self.vehicleStickers is None:
            if not isCurrentModelDamaged:
                _logger.error('Failed to attach VehicleStickers. Missing VehicleStickers. Vehicle: %s', self._vehicle)
            return
        else:
            self.vehicleStickers.alpha = DEFAULT_STICKERS_ALPHA
            self.vehicleStickers.attach(compoundModel=self.compoundModel, isDamaged=isCurrentModelDamaged, showDamageStickers=not isCurrentModelDamaged, attachChildPart=True)
            return

    def _detachStickers(self):
        _logger.debug('Detaching VehicleStickers for vehicle: %s', self._vehicle)
        if self.vehicleStickers is not None:
            self.vehicleStickers.detach()
        return

    @property
    def _vehicleColliderInfo(self):
        chassisColisionMatrix = self.compoundModel.matrix
        if self.damageState.isCurrentModelDamaged:
            gunNodeName = 'gun'
        else:
            gunNodeName = TankNodeNames.GUN_INCLINATION
        return (chassisColisionMatrix, gunNodeName)

    def _startSystems(self, ctx):
        if ctx.flyingInfoProvider:
            ctx.flyingInfoProvider.setData(self.filter, ctx.suspension)
        if self.damageState.isCurrentModelDamaged or self.__systemStarted:
            return
        else:
            self.__systemStarted = True
            if self.trackScrollController is not None:
                self.trackScrollController.activate()
                self.trackScrollController.setData(self.filter)
            if ctx.engineAudition:
                ctx.engineAudition.setWeaponEnergy(self.weaponEnergy)
                ctx.engineAudition.attachToModel(self.compoundModel)
            if ctx.hullAimingController:
                ctx.hullAimingController.setData(self.filter, self.typeDescriptor)
            if ctx.detailedEngineState:
                ctx.detailedEngineState.onGearUpCbk = self.__onEngineStateGearUp
            return

    def _stopSystems(self, ctx):
        if ctx.flyingInfoProvider:
            ctx.flyingInfoProvider.setData(None, None)
        if self.__systemStarted:
            self.__systemStarted = False
        if self.trackScrollController is not None:
            self.trackScrollController.deactivate()
            self.trackScrollController.setData(None)
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.stop()

        self.filter.enableLagDetection(False)
        return

    def _destroySystems(self):
        self.__systemStarted = False
        if self.trackScrollController is not None:
            self.trackScrollController.deactivate()
            self.__trackScrollCtl = None
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.stop()

        self.__modelAnimators = []
        self.filter.enableLagDetection(False)
        queue = CGF.CommandQueue(self.spaceID)
        for go in self.customizationGameObjects:
            if go.valid:
                queue.removeGameObject(go)

        self.customizationGameObjects = []
        return

    def _onRequestModelsRefresh(self):
        queue = CGF.CommandQueue(self._spaceID)
        queue.removeComponent(self._gameObject, Vehicular.FlagComponent)
        self.__updateModelStatus()

    def __updateModelStatus(self):
        if self.damageState.isCurrentModelUndamaged:
            modelStatus = ModelStatus.NORMAL
        else:
            modelStatus = ModelStatus.CRASHED
        for htManager in self.typeDescriptor.getHitTesterManagers():
            htManager.setStatus(modelStatus)

    def _onEngineStart(self):
        if self.__ignoreEngineStart:
            return
        if self.engineAudition:
            self.engineAudition.onEngineStart()

    @staticmethod
    def _getShotEffectSlotName():
        return VehicleSlots.GUN_FIRE.value + '_ShotEffectSlot'

    def _getShotEffectCompositionItems(self):
        prefabMapItems = []
        extraSlotMapItems = []
        gunDescr = self.typeDescriptor.gun
        if self.damageState.isCurrentModelDamaged or gunDescr.prefabBased or self.typeDescriptor.isDualgunVehicle:
            return (prefabMapItems, extraSlotMapItems)
        else:
            gunPrefabEffects, _ = resolveGunPrefabEffects(gunDescr.prefabEffects)
            explosionPrefab = gunPrefabEffects.explosion.prefab if gunPrefabEffects is not None else ''
            groundwavePrefab = gunPrefabEffects.groundwave.prefab if gunPrefabEffects is not None else ''
            prefabs = [ prefab for prefab in (explosionPrefab, groundwavePrefab) if prefab ]
            if not prefabs:
                return (prefabMapItems, extraSlotMapItems)
            gunRecoilSlot = VehicleSlots.GUN_RECOIL.value
            gunRecoilMatrix = Math.Matrix(self.compoundModel.node(gunRecoilSlot))
            gunRecoilMatrix.invert()
            gunFireSlot = VehicleSlots.GUN_FIRE.value
            node = self.compoundModel.node(gunFireSlot)
            if node is not None:
                shotEffectSlot = self._getShotEffectSlotName()
                gunFireMatrix = Math.Matrix(node)
                gunFireMatrix.postMultiply(gunRecoilMatrix)
                extraSlotMapItems.append(ExtraSlotsMapItem(shotEffectSlot, gunRecoilSlot, gunFireMatrix))
                for prefab in prefabs:
                    prefabMapItems.append(PrefabsMapItem(shotEffectSlot, prefab))

            else:
                _logger.error('Failed to setup shot effect. Missing node %s for gun %s.', gunFireSlot, gunDescr.name)
            return (prefabMapItems, extraSlotMapItems)

    def createVehicleComposition(self, queue):
        prefabMap = [ PrefabsMapItem(attachment.slotName, attachment.modelName) for attachment in self.__attachments if not attachment.hidden ]
        if IS_EDITOR or self.__forceDynAttachmentLoading:
            prefabMap += self.slotPrefabs
        collisionState = self.renderMode in (TankRenderMode.CLIENT_COLLISION,
         TankRenderMode.SERVER_COLLISION,
         TankRenderMode.CRASH_COLLISION,
         TankRenderMode.ARMOR_WIDTH_COLLISION)
        if IS_EDITOR and collisionState:
            prefabMap = []
        extraSlots = getExtraSlotMap(self.typeDescriptor, self) + getObjectSlots(self.typeDescriptor)
        shotEffectPrefabs, shotEffectExtraSlots = self._getShotEffectCompositionItems()
        prefabMap += shotEffectPrefabs
        extraSlots += shotEffectExtraSlots
        dynSlots = None
        if self.typeDescriptor.type.isWheeledVehicle:
            dynSlots = self.typeDescriptor.chassis.generalWheelsAnimatorConfig.getNonTrackWheelNodeNames()
        if not self._gameObject.hasComponent(GenericComponents.VisibilityTunnelVehicleMarkerComponent):
            slotInfoMap = {attachment.slotName:attachment.enableVisTunnel for attachment in self.__attachments}
            queue.createComponent(self._gameObject, GenericComponents.VisibilityTunnelVehicleMarkerComponent, slotInfoMap)
        extraSlotComponents = [] if self.typeDescriptor.gun.prefabBased else [(VehicleSlots.GUN.value, [VariableStorageComponent])]
        createVehicleComposition(gameObject=self._gameObject, vehicleGameObject=self._entityGameObject, prefabMap=prefabMap, followNodes=True, extraSlots=extraSlots, dynSlotNodes=dynSlots, extraSlotComponents=extraSlotComponents, queue=queue)
        return

    def __assembleNonDamagedOnly(self, resourceRefs, isPlayer, queue):
        multiGun = self.typeDescriptor.gun.multiGun
        self._gunAnimators.setup(len(multiGun) if multiGun else 0)
        model_assembler.assembleTerrainMatKindSensor(self, queue)
        model_assembler.assembleGunLinkedNodesAnimator(self, queue)
        collisionObstaclesCollector = model_assembler.assembleCollisionObstaclesCollector(self, self.typeDescriptor, queue)
        tessellationCollisionSensor = model_assembler.assembleTessellationCollisionSensor(self, queue)
        generalWheelsAnimatorConfig = self.typeDescriptor.chassis.generalWheelsAnimatorConfig
        if generalWheelsAnimatorConfig is not None:
            self.__filterRetrieversGo = queue.createGameObject(name='wheelsScrollFilterRetrievers')
            queue.createComponent(self.__filterRetrieversGo, CGF.HierarchyComponent, self._gameObject)
            scrollableWheelsCount = generalWheelsAnimatorConfig.getNonTrackWheelsCount()
            steerableWheelsCount = generalWheelsAnimatorConfig.getSteerableWheelsCount()
            for i in xrange(scrollableWheelsCount + steerableWheelsCount):
                name = 'scrollable_{}'.format(i) if i < scrollableWheelsCount else 'steerable_{}'.format(i - scrollableWheelsCount)
                retrieverGameObject = queue.createPendingGameObject(name=name)
                queue.createComponent(retrieverGameObject, NetworkFilters.FloatFilterRetriever)
                queue.createComponent(retrieverGameObject, CGF.HierarchyComponent, self.__filterRetrieversGo)

        wheelsAnimator = model_assembler.createWheelsAnimator(self, ColliderTypes.VEHICLE_COLLIDER, self.typeDescriptor, lambda : self.wheelsState, self.splineTracks, queue)
        if queue.hasComponent(self._gameObject, CustomEffectManager):
            customEffectManager = queue.component(self._gameObject, CustomEffectManager)
            customEffectManager.setWheelsData(self.typeDescriptor, wheelsAnimator)
        if 'wheeledVehicle' in self.typeDescriptor.type.tags:
            queue.createComponent(self.__wheelsGameObject, Vehicular.LodCalculator, CGF.linkMatrixTranslation(self.compoundModel.matrix), True, WHEELED_CHASSIS_PRIORITY_GROUP, isPlayer)
        model_assembler.assembleSuspensionIfNeed(self, collisionObstaclesCollector, tessellationCollisionSensor, queue)
        model_assembler.assembleLeveredSuspensionIfNeed(self, tessellationCollisionSensor, queue)
        model_assembler.assembleBurnoutProcessor(self, queue)
        model_assembler.assembleSuspensionSound(self, isPlayer, queue)
        model_assembler.assembleHullAimingController(self, queue)
        model_assembler.createTrackNodesAnimator(self, self.typeDescriptor, queue)
        model_assembler.assembleVehicleTraces(self, self.filter, wheelsAnimator, queue)
        self._setupTracks(resourceRefs, queue)
        return

    def _setupTracks(self, resourceRefs, queue):
        model_assembler.assembleTracks(resourceRefs, self.typeDescriptor, self, self.splineTracks, False, queue)

    def __postSetupFilter(self, suspension, leveredSuspension):
        suspensionWorking = suspension and suspension.hasGroundNodes
        placingOnGround = not (suspensionWorking or leveredSuspension)
        self.filter.placingOnGround = placingOnGround

    def _periodicUpdate(self, ctx):
        if self._vehicle is None or not self._vehicle.isAlive() and self._gameObject.valid:
            return
        else:
            self._updateCurrTerrainMatKinds(ctx.terrainMatKindSensor, ctx.vehicleTraces)
            self.__updateEffectsLOD(ctx.lodCalculator, ctx.customEffectManager, ctx.waterSensor)
            if ctx.customEffectManager:
                ctx.customEffectManager.update(ctx.generalWheelsAnimator or ctx.tankWheelsAnimator, ctx.detailedEngineState, ctx.waterSensor)
                if ctx.siegeEffects:
                    ctx.siegeEffects.tick()
            if self._vehicleStickers is not None:
                self._vehicleStickers.processPendingDamageStickers(ctx.collisions, self.isCompositionReady)
            return

    def __updateEffectsLOD(self, lodCalculator, customEffectManager, waterSensor):
        if customEffectManager and self.__customEffectsEnabled:
            distanceFromPlayer = lodCalculator.lodDistance
            enableExhaust = distanceFromPlayer <= _LOD_DISTANCE_EXHAUST and not waterSensor.isUnderWater
            enableTrails = distanceFromPlayer <= _LOD_DISTANCE_TRAIL_PARTICLES and BigWorld.wg_isVehicleDustEnabled()
            customEffectManager.enable(enableTrails, EffectSettings.SETTING_DUST)
            customEffectManager.enable(enableExhaust, EffectSettings.SETTING_EXHAUST)

    def _stopEffects(self, forceDelete=False):
        self.boundEffects.stop(forceDelete)

    def playEffectWithStopCallback(self, effects):
        self._stopEffects()
        vehicle = self._vehicle
        return self.boundEffects.addNew(None, effects[1], effects[0], isPlayerVehicle=vehicle.isPlayerVehicle, showShockWave=vehicle.isPlayerVehicle, showFlashBang=vehicle.isPlayerVehicle, entity_id=vehicle.id, isPlayer=vehicle.isPlayerVehicle, showDecal=True, start=vehicle.position + Math.Vector3(0.0, 1.0, 0.0), end=vehicle.position + Math.Vector3(0.0, -1.0, 0.0)).stop

    def playEffect(self, kind, *modifs):
        self._stopEffects()
        if kind == 'empty' or self._vehicle is None:
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
            vehicle = self._vehicle
            effects = random.choice(effects)
            args = dict(isPlayerVehicle=vehicle.isPlayerVehicle, showShockWave=vehicle.isPlayerVehicle, showFlashBang=vehicle.isPlayerVehicle, entity_id=vehicle.id, isPlayer=vehicle.isPlayerVehicle, showDecal=enableDecal, start=vehicle.position + Math.Vector3(0.0, 1.0, 0.0), end=vehicle.position + Math.Vector3(0.0, -1.0, 0.0))
            if modifs:
                args['playSound'] = modifs[0]
            if isSpawnedBot(self.typeDescriptor.type.tags) and kind in ('explosion', 'destruction'):
                if isPlayerAvatar():
                    if self.isFlying:
                        instantExplosionEff = self.typeDescriptor.type.effects['instantExplosion']
                        if instantExplosionEff:
                            effects = random.choice(instantExplosionEff)
                    BigWorld.player().terrainEffects.addNew(self._vehicle.position, effects[1], effects[0], None, **args)
            else:
                self.boundEffects.addNew(None, effects[1], effects[0], **args)
            return

    def _updateCurrTerrainMatKinds(self, terrainMatKindSensor, vehicleTraces):
        if not terrainMatKindSensor:
            return
        else:
            matKinds = terrainMatKindSensor.matKinds
            groundTypes = terrainMatKindSensor.groundTypes
            materialsCount = len(matKinds)
            for i in MATKIND_COUNT_RANGE:
                matKind = matKinds[i] if i < materialsCount else 0
                groundType = groundTypes[i] if i < materialsCount else 0
                self.terrainMatKind[i] = matKind
                self.terrainGroundType[i] = groundType
                effectIndex = calcEffectMaterialIndex(matKind)
                effectMaterialName = ''
                if effectIndex is not None:
                    effectMaterialName = material_kinds.EFFECT_MATERIALS[effectIndex]
                self.__terrainEffectMaterialNames[i] = effectMaterialName

            if vehicleTraces:
                vehicleTraces.setCurrTerrainMatKinds(self.terrainMatKind[0], self.terrainMatKind[1])
            return

    def onSiegeStateChanged(self, newState):
        siegeState = self._gameObject.findWrite(Vehicular.SiegeState)
        if siegeState:
            siegeState.onSiegeStateChanged(newState)
        if self.engineAudition:
            self.engineAudition.onSiegeStateChanged(newState)
        if self.hullAimingController:
            self.hullAimingController.onSiegeStateChanged(newState)
        if self.suspensionSound:
            self.suspensionSound.vehicleState = newState
        siegeEffects = self.gameObject.findWrite(SiegeEffectsController)
        if siegeEffects:
            siegeEffects.onSiegeStateChanged(newState)
        enabled = newState in VEHICLE_SIEGE_STATE.SIEGE_MODE
        if self.suspension:
            self.suspension.setLiftMode(enabled)
        if self.leveredSuspension:
            self.leveredSuspension.setLiftMode(enabled)
        if self.vehicleTraces:
            self.vehicleTraces.setLiftMode(enabled)

    def changeEngineMode(self, mode, forceSwinging=False):
        if self.detailedEngineState:
            self.detailedEngineState.mode = mode[0]
        if self.trackScrollController is not None:
            self.trackScrollController.setMode(mode)
        return

    def changeSiegeState(self, siegeState):
        if self.engineAudition:
            self.engineAudition.onSiegeStateChanged(siegeState)

    def turretDamaged(self):
        pass

    def maxTurretRotationSpeed(self):
        pass

    def _onCameraChanged(self, cameraName, currentVehicleId=None):
        if self.id != BigWorld.player().playerVehicleID:
            return
        isEnabled = cameraName != 'sniper'
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.setEnabled(isEnabled)

    def __onEngineStateGearUp(self):
        if self.customEffectManager:
            self.customEffectManager.onGearUp()
        if self.engineAudition:
            self.engineAudition.onEngineGearUp()

    def __animatorCallback(self, name, time):
        _logger.debug('Callback aquired %s %f', name, time)
        if self.shellAnimator is not None:
            self.shellAnimator.throwShell(self.typeDescriptor.shot.shell.animation)
        return

    def getCurrentModelsSet(self):
        has3DStyle = self.outfit is not None and self.outfit.modelsSet is not None and self.outfit.modelsSet != ''
        return self.outfit.modelsSet if has3DStyle else 'default'

    def getTrackStates(self):
        if not self.crashedTracksController:
            return []
        leftTrackStates = self.crashedTracksController.getTrackStates(isLeft=True)
        rightTrackStates = self.crashedTracksController.getTrackStates(isLeft=False)
        return leftTrackStates + rightTrackStates

    def __shouldCreatePhysicalDestroyedTracks(self):
        quality = BigWorld.trackPhysicsQuality()
        if BigWorld.isForwardPipeline() or quality >= len(DebrisCrashedTrackComponent.MAX_DEBRIS_COUNT):
            return False
        maxDebrisCount = DebrisCrashedTrackComponent.MAX_DEBRIS_COUNT[quality]
        debrisCount = DebrisCrashedTrackComponent.CURRENT_DEBRIS_COUNT
        return False if debrisCount >= maxDebrisCount and not self._isPlayerVehicle else True

    def __shouldUseTrackCrashWithDebris(self, pairIndex, shouldCreateDebris):
        chassisType = self.typeDescriptor.chassis.chassisType
        if chassisType == CHASSIS_ITEM_TYPE.TRACK_WITHIN_TRACK and pairIndex != MAIN_TRACK_PAIR_IDX:
            return True
        else:
            tracks = self.typeDescriptor.chassis.tracks
            return tracks is not None and tracks.trackPairs[pairIndex].tracksDebris is not None and shouldCreateDebris

    def _getTrackPairIndicesToDestroy(self, pairIndex):
        chassis = self.typeDescriptor.chassis
        if chassis.chassisType == CHASSIS_ITEM_TYPE.MONOLITHIC:
            pairsCount = len(chassis.tracks.trackPairs) if chassis.tracks is not None else 1
            return xrange(pairsCount)
        else:
            return (pairIndex,)

    def _addCrashedTrack(self, isLeft, pairIndex, isSideFlying, hitPoint):
        indices = self._getTrackPairIndicesToDestroy(pairIndex)
        shouldCreateDebris = self.__shouldCreatePhysicalDestroyedTracks()
        if not self.__shouldUseTrackCrashWithDebris(pairIndex, shouldCreateDebris):
            if self.crashedTracksController:
                for idx in indices:
                    self.crashedTracksController.addCrashedTrack(isLeft, idx, hitPoint, isSideFlying)

            return
        modelsSet = self.getCurrentModelsSet()
        queue = CGF.CommandQueue(self._spaceID)
        for idx in indices:
            track = self.tracks.getTrackGameObject(isLeft, idx)
            queue.assignComponent(track, DebrisCrashedTrackComponent(isLeft, idx, self.typeDescriptor, self._gameObject, self.boundEffects, self.filter, self._isPlayerVehicle, shouldCreateDebris, hitPoint, modelsSet))
            if self.crashedTracksController:
                self.crashedTracksController.addCrashedTrack(isLeft, idx, hitPoint, isDebris=True)

    def _delCrashedTrack(self, isLeft, pairIndex):
        indices = self._getTrackPairIndicesToDestroy(pairIndex)
        foundCrashedTrackWithDebris = False
        if self.tracks:
            for idx in indices:
                track = self.tracks.getTrackGameObject(isLeft, idx)
                if track.valid:
                    hasDebris = False
                    if self.crashedTracksController:
                        hasDebris = self.crashedTracksController.hasDebris(isLeft, idx)
                    if hasDebris:
                        track.removeComponent(DebrisCrashedTrackComponent)
                        foundCrashedTrackWithDebris = True
                        if self.crashedTracksController:
                            self.crashedTracksController.delCrashedTrack(isLeft, idx)

        if not foundCrashedTrackWithDebris and self.crashedTracksController:
            for idx in indices:
                self.crashedTracksController.delCrashedTrack(isLeft, idx)

    def _updateAttachments(self):
        self.__attachments = camouflages.getAttachments(self.outfit, self.typeDescriptor, self.damageState.isCurrentModelDamaged)

    def _getWheelsFilters(self):
        return []

    def _initWheelsLinks(self, generalWheelsAnimator):
        generalWheelsAnimatorConfig = self.typeDescriptor.chassis.generalWheelsAnimatorConfig
        filters = self._getWheelsFilters()
        if generalWheelsAnimatorConfig is not None and filters:
            wheelsScroll, wheelsSteering = [], []
            hierarchy = CGF.findHierarchySingleton(self._spaceID)
            retrieversGos = hierarchy.getDirectChildren(self.__filterRetrieversGo)
            scrollableWheelsCount = generalWheelsAnimatorConfig.getNonTrackWheelsCount()
            for go, floatFilter in zip(retrieversGos, filters):
                retriever = go.findWrite(NetworkFilters.FloatFilterRetriever)
                retriever.setupFilter(floatFilter)
                linkList = wheelsScroll if len(wheelsScroll) < scrollableWheelsCount else wheelsSteering
                linkList.append(CGF.createFloatLink(retriever, 'value'))

            generalWheelsAnimator.setWheelsLinks(wheelsScroll, wheelsSteering)
        return
