# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/common_tank_appearance.py
import math
import random
import logging
import BigWorld
import CGF
import GenericComponents
import Triggers
import Math
import DataLinks
import Vehicular
import NetworkFilters
import material_kinds
from constants import IS_EDITOR, VEHICLE_SIEGE_STATE
from CustomEffectManager import CustomEffectManager, EffectSettings
from helpers.EffectMaterialCalculation import calcEffectMaterialIndex
from VehicleStickers import VehicleStickers
from cgf_obsolete_script.script_game_object import ComponentDescriptor, ScriptGameObject
from cgf_obsolete_script.auto_properties import AutoProperty
from items.components.component_constants import MAIN_TRACK_PAIR_IDX
from items.vehicle_items import CHASSIS_ITEM_TYPE
from vehicle_systems import model_assembler
from vehicle_systems import camouflages
from vehicle_systems.vehicle_damage_state import VehicleDamageState
from vehicle_systems.tankStructure import VehiclePartsTuple, ModelsSetParams, TankPartNames, ColliderTypes, TankPartIndexes, TankNodeNames, TankRenderMode, CgfTankNodes
from vehicle_systems.components.CrashedTracks import CrashedTrackController
from vehicle_systems.components.vehicleDecal import VehicleDecal
from vehicle_systems.components.siegeEffectsController import SiegeEffectsController
from vehicle_systems.components.vehicle_shadow_manager import VehicleShadowManager
from helpers import bound_effects, gEffectsDisabled
from vehicle_outfit.outfit import Outfit
from items.battle_royale import isSpawnedBot
from helpers import isPlayerAvatar
from ModelHitTester import ModelStatus
from vehicle_systems.components.debris_crashed_tracks import TrackCrashWithDebrisComponent
_logger = logging.getLogger(__name__)
DEFAULT_STICKERS_ALPHA = 1.0
MATKIND_COUNT = 3
MAX_DISTANCE = 500
VEHICLE_PRIORITY_GROUP = 1
WHEELED_CHASSIS_PRIORITY_GROUP = 2
TANK_FRICTION_EVENT = 'collision_tank_friction_pc'
PERIODIC_UPDATE_TIME = 0.25
_LOD_DISTANCE_EXHAUST = 200.0
_LOD_DISTANCE_TRAIL_PARTICLES = 100.0

class PartProperties(object):
    HIGHLIGHTABLE = 1
    HIGHLIGHTBYVISUAL = 2


class VehicleAppearanceComponent(object):
    appearance = property(lambda self: self.__appearance)

    def __init__(self, appearance):
        self.__appearance = appearance


class CommonTankAppearance(ScriptGameObject):
    compoundModel = property(lambda self: self._compoundModel)
    boundEffects = property(lambda self: self.__boundEffects)
    fashions = property(lambda self: self.__fashions)
    fashion = property(lambda self: self.fashions.chassis)
    typeDescriptor = property(lambda self: self.__typeDesc if self._vehicle is None else self._vehicle.typeDescriptor)
    id = property(lambda self: self.__vID)
    isAlive = property(lambda self: self.__isAlive)
    isObserver = property(lambda self: self.__isObserver)
    outfit = property(lambda self: self.__outfit)
    renderMode = property(lambda self: self.__renderMode)

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

    terrainMatKind = property(lambda self: self.__currTerrainMatKind)
    terrainGroundType = property(lambda self: self.__currTerrainGroundType)
    terrainEffectMaterialNames = property(lambda self: self.__terrainEffectMaterialNames)
    isInWater = property(lambda self: self.waterSensor.isInWater)
    isUnderwater = property(lambda self: self.waterSensor.isUnderWater)
    waterHeight = property(lambda self: self.waterSensor.waterHeight)
    damageState = property(lambda self: self.__currentDamageState)
    modelsSetParams = property(lambda self: ModelsSetParams(self.outfit.modelsSet, self.damageState.modelState, self.__attachments))
    splineTracks = property(lambda self: self._splineTracks)
    isFlying = property(lambda self: self.flyingInfoProvider is not None and self.flyingInfoProvider.isFlying)
    isLeftSideFlying = property(lambda self: self.flyingInfoProvider is not None and self.flyingInfoProvider.isLeftSideFlying)
    isRightSideFlying = property(lambda self: self.flyingInfoProvider is not None and self.flyingInfoProvider.isRightSideFlying)
    trackScrollController = property(lambda self: self.__trackScrollCtl)
    wheelsState = property(lambda self: 0)
    burnoutLevel = property(lambda self: 0.0)
    wheelsGameObject = property(lambda self: self.__wheelsGameObject)
    filterRetrievers = property(lambda self: self.__filterRetrievers)
    filterRetrieverGameObjects = property(lambda self: self.__filterRetrieverGameObjects)
    allLodCalculators = property(lambda self: self.__allLodCalculators)
    transmissionSlip = property(lambda self: self._commonSlip)
    transmissionScroll = property(lambda self: self._commonScroll)
    vehicleStickers = property(lambda self: self._vehicleStickers)
    isTurretDetached = property(lambda self: self._isTurretDetached)
    _weaponEnergy = property(lambda self: self.__weaponEnergy)
    filter = AutoProperty()
    areaTriggerTarget = ComponentDescriptor()
    burnoutProcessor = ComponentDescriptor()
    c11nComponent = ComponentDescriptor()
    collisionObstaclesCollector = ComponentDescriptor()
    collisions = ComponentDescriptor()
    crashedTracksController = ComponentDescriptor()
    customEffectManager = ComponentDescriptor()
    detailedEngineState = ComponentDescriptor()
    dirtComponent = ComponentDescriptor()
    engineAudition = ComponentDescriptor()
    flyingInfoProvider = ComponentDescriptor()
    frictionAudition = ComponentDescriptor()
    gearbox = ComponentDescriptor()
    gunLinkedNodesAnimator = ComponentDescriptor()
    gunRecoil = ComponentDescriptor()
    gunRotatorAudition = ComponentDescriptor()
    hullAimingController = ComponentDescriptor()
    leveredSuspension = ComponentDescriptor()
    lodCalculator = ComponentDescriptor()
    shadowManager = ComponentDescriptor()
    siegeEffects = ComponentDescriptor()
    siegeState = ComponentDescriptor()
    suspension = ComponentDescriptor()
    suspensionSound = ComponentDescriptor()
    swingingAnimator = ComponentDescriptor()
    terrainMatKindSensor = ComponentDescriptor()
    tessellationCollisionSensor = ComponentDescriptor()
    trackNodesAnimator = ComponentDescriptor()
    tracks = ComponentDescriptor()
    transform = ComponentDescriptor()
    vehicleTraces = ComponentDescriptor()
    waterSensor = ComponentDescriptor()
    wheelsAnimator = ComponentDescriptor()
    flagComponent = ComponentDescriptor()

    def __init__(self, spaceID):
        ScriptGameObject.__init__(self, spaceID, CgfTankNodes.TANK_ROOT)
        self._vehicle = None
        self.__wheelsGameObject = ScriptGameObject(spaceID, 'Tank.Wheels.Root')
        self.__filter = None
        self.__typeDesc = None
        self.crashedTracksController = None
        self.__currentDamageState = VehicleDamageState()
        self.__currTerrainMatKind = [-1] * MATKIND_COUNT
        self.__currTerrainGroundType = [-1] * MATKIND_COUNT
        self.__terrainEffectMaterialNames = [''] * MATKIND_COUNT
        self._chassisDecal = VehicleDecal(self)
        self.__splodge = None
        self.__boundEffects = None
        self._splineTracks = None
        self.flyingInfoProvider = self.createComponent(Vehicular.FlyingInfoProvider)
        self.__trackScrollCtl = BigWorld.PyTrackScroll()
        self.__trackScrollCtl.setFlyingInfo(DataLinks.createBoolLink(self.flyingInfoProvider, 'isLeftSideFlying'), DataLinks.createBoolLink(self.flyingInfoProvider, 'isRightSideFlying'))
        self.__weaponEnergy = 0.0
        self.__outfit = None
        self.__systemStarted = False
        self.__isAlive = True
        self._isTurretDetached = False
        self.__isObserver = False
        self.__attachments = []
        self.__modelAnimators = []
        self.turretMatrix = None
        self.gunMatrix = None
        self.__allLodCalculators = []
        self._commonScroll = 0.0
        self._commonSlip = 0.0
        self._compoundModel = None
        self.__fashions = None
        self.__filterRetrievers = []
        self.__filterRetrieverGameObjects = []
        self._vehicleStickers = None
        self._vehicleInfo = {}
        self.__vID = 0
        self.__renderMode = None
        self.__frameTimestamp = 0
        self.__periodicTimerID = None
        self.undamagedStateChildren = []
        self.createComponent(VehicleAppearanceComponent, self)
        self._loadingQueue = []
        return

    def prerequisites(self, typeDescriptor, vID, health, isCrewActive, isTurretDetached, outfitCD, renderMode=None):
        self.damageState.update(health, isCrewActive, False)
        self.__typeDesc = typeDescriptor
        self.__vID = vID
        self._isTurretDetached = isTurretDetached
        self.__updateModelStatus()
        self.__outfit = self._prepareOutfit(outfitCD)
        if self.damageState.isCurrentModelUndamaged:
            self.__attachments = camouflages.getAttachments(self.outfit, self.typeDescriptor)
        self.__renderMode = renderMode
        prereqs = self.typeDescriptor.prerequisites(True)
        prereqs.extend(camouflages.getCamoPrereqs(self.outfit, self.typeDescriptor))
        prereqs.extend(camouflages.getModelAnimatorsPrereqs(self.outfit, self.spaceID))
        prereqs.extend(camouflages.getAttachmentsAnimatorsPrereqs(self.__attachments, self.spaceID))
        splineDesc = self.typeDescriptor.chassis.splineDesc
        modelsSet = self.outfit.modelsSet
        if IS_EDITOR:
            modelsSet = self.currentModelsSet
        if splineDesc is not None:
            for _, trackDesc in splineDesc.trackPairs.iteritems():
                prereqs += trackDesc.prerequisites(modelsSet)

        modelsSetParams = self.modelsSetParams
        compoundAssembler = model_assembler.prepareCompoundAssembler(self.typeDescriptor, modelsSetParams, self.spaceID, self.isTurretDetached, renderMode=self.renderMode)
        prereqs.append(compoundAssembler)
        if renderMode == TankRenderMode.OVERLAY_COLLISION:
            self.damageState.update(0, isCrewActive, False)
        collisionAssembler = model_assembler.prepareCollisionAssembler(self.typeDescriptor, self.isTurretDetached, self.spaceID)
        prereqs.append(collisionAssembler)
        skin = modelsSetParams.skin
        if IS_EDITOR:
            skin = self.currentModelsSet
        physicalTracksBuilders = self.typeDescriptor.chassis.physicalTracks
        for name, builders in physicalTracksBuilders.iteritems():
            for index, builder in enumerate(builders):
                prereqs.append(builder.createLoader(self.spaceID, '{0}{1}PhysicalTrack'.format(name, index), skin))

        return prereqs

    def construct(self, isPlayer, resourceRefs):
        self.__isObserver = 'observer' in self.typeDescriptor.type.tags
        self._compoundModel = resourceRefs[self.typeDescriptor.name]
        self.removeComponentByType(GenericComponents.DynamicModelComponent)
        self.createComponent(GenericComponents.DynamicModelComponent, self._compoundModel)
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
        self.collisions = self.createComponent(BigWorld.CollisionComponent, resourceRefs['collisionAssembler'])
        model_assembler.setupCollisions(self.typeDescriptor, self.collisions)
        self._setFashions(fashions, self.isTurretDetached)
        self._setupModels()
        if not isCurrentModelDamaged:
            modelsSet = self.outfit.modelsSet
            if IS_EDITOR:
                modelsSet = self.currentModelsSet
            self._splineTracks = model_assembler.setupSplineTracks(self.fashion, self.typeDescriptor, self.compoundModel, resourceRefs, modelsSet)
            self.crashedTracksController = CrashedTrackController(self.typeDescriptor, self.fashion, modelsSet)
        else:
            self.__trackScrollCtl = None
        self._chassisDecal.create()
        if self.modelsSetParams.state == 'undamaged':
            self.__modelAnimators = camouflages.getModelAnimators(self.outfit, self.typeDescriptor, self.spaceID, resourceRefs, self.compoundModel)
            self.__modelAnimators.extend(camouflages.getAttachmentsAnimators(self.__attachments, self.spaceID, resourceRefs, self.compoundModel))
        self.transform = self.createComponent(GenericComponents.TransformComponent, Math.Vector3(0, 0, 0))
        self.areaTriggerTarget = self.createComponent(Triggers.AreaTriggerTarget)
        self.__filter = model_assembler.createVehicleFilter(self.typeDescriptor)
        compoundModel = self.compoundModel
        if self.isAlive:
            self.detailedEngineState, self.gearbox = model_assembler.assembleDrivetrain(self, isPlayer)
            if not gEffectsDisabled():
                self.customEffectManager = CustomEffectManager(self)
                if self.typeDescriptor.hasSiegeMode:
                    self.siegeEffects = SiegeEffectsController(self, isPlayer)
                model_assembler.assembleVehicleAudition(isPlayer, self)
                self.detailedEngineState.onEngineStart = self._onEngineStart
                self.detailedEngineState.onStateChanged = self.engineAudition.onEngineStateChanged
            if isPlayer:
                turret = self.typeDescriptor.turret
                gunRotatorAudition = self.createComponent(Vehicular.GunRotatorAudition, turret.turretRotatorSoundManual, turret.weight / 1000.0, compoundModel.node(TankPartNames.TURRET))
                gunRotatorAudition.vehicleMatrixLink = self.compoundModel.root
                gunRotatorAudition.damaged = lambda : self.turretDamaged()
                gunRotatorAudition.maxTurretRotationSpeed = lambda : self.maxTurretRotationSpeed()
                self.gunRotatorAudition = gunRotatorAudition
                self.frictionAudition = self.createComponent(Vehicular.FrictionAudition, TANK_FRICTION_EVENT)
        isLodTopPriority = isPlayer
        lodCalcInst = self.createComponent(Vehicular.LodCalculator, DataLinks.linkMatrixTranslation(compoundModel.matrix), True, VEHICLE_PRIORITY_GROUP, isLodTopPriority)
        self.lodCalculator = lodCalcInst
        self.allLodCalculators.append(lodCalcInst)
        lodLink = DataLinks.createFloatLink(lodCalcInst, 'lodDistance')
        lodStateLink = lodCalcInst.lodStateLink
        if IS_EDITOR:
            matrixBinding = None
            changeCamera = None
        else:
            matrixBinding = BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged
            changeCamera = BigWorld.player().inputHandler.onCameraChanged
        self.shadowManager = VehicleShadowManager(compoundModel, matrixBinding, changeCamera)
        if not self.damageState.isCurrentModelDamaged:
            self.__assembleNonDamagedOnly(resourceRefs, isPlayer, lodLink, lodStateLink)
            dirtEnabled = BigWorld.WG_dirtEnabled() and 'HD' in self.typeDescriptor.type.tags
            if dirtEnabled and self.fashions is not None:
                dirtHandlers = [BigWorld.PyDirtHandler(True, compoundModel.node(TankPartNames.CHASSIS).position.y),
                 BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.HULL).position.y),
                 BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.TURRET).position.y),
                 BigWorld.PyDirtHandler(False, compoundModel.node(TankPartNames.GUN).position.y)]
                modelHeight, _ = self.computeVehicleHeight()
                self.dirtComponent = self.createComponent(Vehicular.DirtComponent, dirtHandlers, modelHeight)
                for fashionIdx, _ in enumerate(TankPartNames.ALL):
                    self.fashions[fashionIdx].addMaterialHandler(dirtHandlers[fashionIdx])
                    self.fashions[fashionIdx].addTrackMaterialHandler(dirtHandlers[fashionIdx])

        model_assembler.setupTurretRotations(self)
        self.waterSensor = model_assembler.assembleWaterSensor(self.typeDescriptor, self, lodStateLink, self.spaceID)
        if self.engineAudition is not None:
            self.engineAudition.setIsUnderwaterInfo(DataLinks.createBoolLink(self.waterSensor, 'isUnderWater'))
            self.engineAudition.setIsInWaterInfo(DataLinks.createBoolLink(self.waterSensor, 'isInWater'))
        self.__postSetupFilter()
        compoundModel.setPartBoundingBoxAttachNode(TankPartIndexes.GUN, TankNodeNames.GUN_INCLINATION)
        camouflages.updateFashions(self)
        model_assembler.assembleCustomLogicComponents(self, self.typeDescriptor, self.__attachments, self.__modelAnimators)
        self._createStickers()
        while self._loadingQueue:
            prefab, go, vector, callback = self._loadingQueue.pop()
            CGF.loadGameObjectIntoHierarchy(prefab, go, vector, callback)

        return

    def destroy(self):
        self._vehicleInfo = {}
        self.flagComponent = None
        self._destroySystems()
        fashions = VehiclePartsTuple(None, None, None, None)
        self._setFashions(fashions, self._isTurretDetached)
        self.shadowManager.unregisterCompoundModel(self.compoundModel)
        for go in self.filterRetrieverGameObjects:
            go.destroy()

        self.wheelsGameObject.destroy()
        super(CommonTankAppearance, self).destroy()
        self.__typeDesc = None
        if self.boundEffects is not None:
            self.boundEffects.destroy()
        self._vehicleStickers = None
        self._chassisDecal.destroy()
        self._chassisDecal = None
        self._compoundModel = None
        self._destroyStickers()
        self._loadingQueue = []
        return

    def activate(self):
        typeDescr = self.typeDescriptor
        wheelConfig = typeDescr.chassis.generalWheelsAnimatorConfig
        if self.wheelsAnimator is not None and wheelConfig is not None:
            self.wheelsAnimator.createCollision(wheelConfig, self.collisions)
        super(CommonTankAppearance, self).activate()
        self.wheelsGameObject.activate()
        for go in self.filterRetrieverGameObjects:
            go.activate()

        if not self.isObserver:
            self._chassisDecal.attach()
        if not self.isObserver:
            self._startSystems()
            self.filter.enableLagDetection(not self.damageState.isCurrentModelDamaged)
            if self.__periodicTimerID is not None:
                BigWorld.cancelCallback(self.__periodicTimerID)
            self.__periodicTimerID = BigWorld.callback(PERIODIC_UPDATE_TIME, self.__onPeriodicTimer)
        self.setupGunMatrixTargets(self.filter)
        for lodCalculator in self.allLodCalculators:
            lodCalculator.setupPosition(DataLinks.linkMatrixTranslation(self.compoundModel.matrix))

        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.setEnabled(True)
            modelAnimator.animator.start()

        if hasattr(self.filter, 'placingCompensationMatrix') and self.swingingAnimator is not None:
            self.swingingAnimator.placingCompensationMatrix = self.filter.placingCompensationMatrix
            self.swingingAnimator.worldMatrix = self.compoundModel.matrix
        if self.isObserver:
            self.compoundModel.visible = False
        self._connectCollider()
        self._attachStickers()
        return

    def deactivate(self):
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.setEnabled(False)

        super(CommonTankAppearance, self).deactivate()
        self.shadowManager.unregisterCompoundModel(self.compoundModel)
        self._stopSystems()
        self.wheelsGameObject.deactivate()
        for go in self.filterRetrieverGameObjects:
            go.deactivate()

        self._chassisDecal.detach()
        self._detachStickers()

    def setVehicleInfo(self, vehInfo):
        self._vehicleInfo = vehInfo

    def setupGunMatrixTargets(self, target):
        self.turretMatrix = target.turretMatrix
        self.gunMatrix = target.gunMatrix

    def receiveShotImpulse(self, direction, impulse):
        if not VehicleDamageState.isDamagedModel(self.damageState.modelState):
            self.swingingAnimator.receiveShotImpulse(direction, impulse)
            if self.crashedTracksController is not None:
                self.crashedTracksController.receiveShotImpulse(direction, impulse)
        return

    def recoil(self):
        self._initiateRecoil(TankNodeNames.GUN_INCLINATION, 'HP_gunFire', self.gunRecoil)

    def multiGunRecoil(self, indexes):
        if self.gunAnimators is None:
            return
        else:
            for index in indexes:
                typeDescr = self.typeDescriptor
                gunNodeName = typeDescr.turret.multiGun[index].node
                gunFireNodeName = typeDescr.turret.multiGun[index].gunFire
                gunAnimator = self.gunAnimators[index].findComponentByType(Vehicular.RecoilAnimator)
                self._initiateRecoil(gunNodeName, gunFireNodeName, gunAnimator)

            return

    def computeFullVehicleLength(self):
        vehicleLength = 0.0
        if self.compoundModel is not None:
            hullBB = Math.Matrix(self.compoundModel.getBoundsForPart(TankPartIndexes.HULL))
            vehicleLength = hullBB.applyVector(Math.Vector3(0.0, 0.0, 1.0)).length
        return vehicleLength

    def _initiateRecoil(self, gunNodeName, gunFireNodeName, gunAnimator):
        gunNode = self.compoundModel.node(gunNodeName)
        impulseDir = Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1))
        impulseValue = self.typeDescriptor.gun.impulse
        self.receiveShotImpulse(impulseDir, impulseValue)
        gunAnimator.recoil()
        return impulseDir

    def _connectCollider(self):
        if self.collisions is not None:
            chassisColisionMatrix, gunNodeName = self._vehicleColliderInfo
            if self.isTurretDetached:
                self.collisions.removeAttachment(TankPartNames.getIdx(TankPartNames.TURRET))
                self.collisions.removeAttachment(TankPartNames.getIdx(TankPartNames.GUN))
                collisionData = ((TankPartNames.getIdx(TankPartNames.HULL), self.compoundModel.node(TankPartNames.HULL)), (TankPartNames.getIdx(TankPartNames.CHASSIS), chassisColisionMatrix))
            else:
                collisionData = ((TankPartNames.getIdx(TankPartNames.HULL), self.compoundModel.node(TankPartNames.HULL)),
                 (TankPartNames.getIdx(TankPartNames.TURRET), self.compoundModel.node(TankPartNames.TURRET)),
                 (TankPartNames.getIdx(TankPartNames.CHASSIS), chassisColisionMatrix),
                 (TankPartNames.getIdx(TankPartNames.GUN), self.compoundModel.node(gunNodeName)))
            defaultPartLength = len(TankPartNames.ALL)
            additionalChassisParts = []
            trackPairs = self.typeDescriptor.chassis.trackPairs
            if not trackPairs:
                trackPairs = [None]
            for x in xrange(len(trackPairs) - 1):
                additionalChassisParts.append((defaultPartLength + x, chassisColisionMatrix))

            if additionalChassisParts:
                collisionData += tuple(additionalChassisParts)
            self.collisions.connect(self.id, ColliderTypes.VEHICLE_COLLIDER, collisionData)
        return

    def computeVehicleHeight(self):
        gunLength = 0.0
        height = 0.0
        if self.collisions is not None:
            desc = self.typeDescriptor
            hullBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.HULL))
            turretBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.TURRET))
            gunBB = self.collisions.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN))
            hullTopY = desc.chassis.hullPosition[1] + hullBB[1][1]
            turretTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + turretBB[1][1]
            gunTopY = desc.chassis.hullPosition[1] + desc.hull.turretPositions[0][1] + desc.turret.gunPosition[1] + gunBB[1][1]
            gunLength = math.fabs(gunBB[1][2] - gunBB[0][2])
            height = max(hullTopY, max(turretTopY, gunTopY))
        return (height, gunLength)

    def onWaterSplash(self, waterHitPoint, isHeavySplash):
        pass

    def onUnderWaterSwitch(self, isUnderWater):
        pass

    def getWheelsSteeringMax(self):
        pass

    def _prepareOutfit(self, outfitCD):
        outfitComponent = camouflages.getOutfitComponent(outfitCD)
        return Outfit(component=outfitComponent, vehicleCD=self.typeDescriptor.makeCompactDescr())

    def _setupModels(self):
        self.__isAlive = not self.damageState.isCurrentModelDamaged
        if self.isAlive:
            _, gunLength = self.computeVehicleHeight()
            self.__weaponEnergy = gunLength * self.typeDescriptor.shot.shell.caliber
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
            self._vehicleStickers = VehicleStickers(self.spaceID, self.typeDescriptor, outfit=self.outfit)
            return

    def _destroyStickers(self):
        _logger.debug('Attaching VehicleStickers for vehicleType: %s', self.typeDescriptor)
        self._detachStickers()
        self._vehicleStickers = None
        return

    def _attachStickers(self):
        _logger.debug('Attaching VehicleStickers for vehicle: %s', self._vehicle)
        if self.vehicleStickers is None:
            _logger.error('Failed to attach VehicleStickers. Missing VehicleStickers. Vehicle: %s', self._vehicle)
            return
        else:
            isCurrentModelDamaged = self.damageState.isCurrentModelDamaged
            self.vehicleStickers.alpha = DEFAULT_STICKERS_ALPHA
            self.vehicleStickers.attach(compoundModel=self.compoundModel, isDamaged=isCurrentModelDamaged, showDamageStickers=not isCurrentModelDamaged)
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

    def _startSystems(self):
        if self.flyingInfoProvider is not None:
            self.flyingInfoProvider.setData(self.filter, self.suspension)
        if self.damageState.isCurrentModelDamaged or self.__systemStarted:
            return
        else:
            self.__systemStarted = True
            if self.trackScrollController is not None:
                self.trackScrollController.activate()
                self.trackScrollController.setData(self.filter)
            if self.engineAudition is not None:
                self.engineAudition.setWeaponEnergy(self._weaponEnergy)
                self.engineAudition.attachToModel(self.compoundModel)
            if self.hullAimingController is not None:
                self.hullAimingController.setData(self.filter, self.typeDescriptor)
            if self.detailedEngineState is not None:
                self.detailedEngineState.onGearUpCbk = self.__onEngineStateGearUp
            return

    def _stopSystems(self):
        if self.flyingInfoProvider is not None:
            self.flyingInfoProvider.setData(None, None)
        if self.__systemStarted:
            self.__systemStarted = False
        if self.trackScrollController is not None:
            self.trackScrollController.deactivate()
            self.trackScrollController.setData(None)
        if self.__periodicTimerID is not None:
            BigWorld.cancelCallback(self.__periodicTimerID)
            self.__periodicTimerID = None
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

        if self.__periodicTimerID is not None:
            BigWorld.cancelCallback(self.__periodicTimerID)
            self.__periodicTimerID = None
        self.__modelAnimators = []
        self.filter.enableLagDetection(False)
        for go in self.undamagedStateChildren:
            CGF.removeGameObject(go)

        self.undamagedStateChildren = []
        return

    def _onRequestModelsRefresh(self):
        self.flagComponent = None
        self.__updateModelStatus()
        return

    def __updateModelStatus(self):
        if self.damageState.isCurrentModelUndamaged:
            modelStatus = ModelStatus.NORMAL
        else:
            modelStatus = ModelStatus.CRASHED
        for htManager in self.typeDescriptor.getHitTesterManagers():
            htManager.setStatus(modelStatus)

    def _onEngineStart(self):
        if self.engineAudition is not None:
            self.engineAudition.onEngineStart()
        return

    def __assembleNonDamagedOnly(self, resourceRefs, isPlayer, lodLink, lodStateLink):
        model_assembler.assembleTerrainMatKindSensor(self, lodStateLink, self.spaceID)
        model_assembler.assembleRecoil(self, lodLink)
        model_assembler.assembleMultiGunRecoil(self, lodLink)
        model_assembler.assembleGunLinkedNodesAnimator(self)
        model_assembler.assembleCollisionObstaclesCollector(self, lodStateLink, self.typeDescriptor)
        model_assembler.assembleTessellationCollisionSensor(self, lodStateLink)
        wheelsScroll = None
        wheelsSteering = None
        generalWheelsAnimatorConfig = self.typeDescriptor.chassis.generalWheelsAnimatorConfig
        if generalWheelsAnimatorConfig is not None:
            scrollableWheelsCount = generalWheelsAnimatorConfig.getNonTrackWheelsCount()
            wheelsScroll = []
            for _ in xrange(scrollableWheelsCount):
                retrieverGameObject = ScriptGameObject(self.spaceID)
                retriever = retrieverGameObject.createComponent(NetworkFilters.FloatFilterRetriever)
                wheelsScroll.append(DataLinks.createFloatLink(retriever, 'value'))
                self.filterRetrievers.append(retriever)
                self.filterRetrieverGameObjects.append(retrieverGameObject)

            steerableWheelsCount = generalWheelsAnimatorConfig.getSteerableWheelsCount()
            wheelsSteering = []
            for _ in xrange(steerableWheelsCount):
                retrieverGameObject = ScriptGameObject(self.spaceID)
                retriever = retrieverGameObject.createComponent(NetworkFilters.FloatFilterRetriever)
                wheelsSteering.append(DataLinks.createFloatLink(retriever, 'value'))
                self.filterRetrievers.append(retriever)
                self.filterRetrieverGameObjects.append(retrieverGameObject)

        self.wheelsAnimator = model_assembler.createWheelsAnimator(self, ColliderTypes.VEHICLE_COLLIDER, self.typeDescriptor, lambda : self.wheelsState, wheelsScroll, wheelsSteering, self.splineTracks, lodStateLink)
        if self.customEffectManager is not None:
            self.customEffectManager.setWheelsData(self)
        suspensionLodLink = lodStateLink
        if 'wheeledVehicle' in self.typeDescriptor.type.tags:
            wheeledLodCalculator = self.wheelsGameObject.createComponent(Vehicular.LodCalculator, DataLinks.linkMatrixTranslation(self.compoundModel.matrix), True, WHEELED_CHASSIS_PRIORITY_GROUP, isPlayer)
            self.allLodCalculators.append(wheeledLodCalculator)
            suspensionLodLink = wheeledLodCalculator.lodStateLink
        model_assembler.assembleSuspensionIfNeed(self, suspensionLodLink)
        model_assembler.assembleLeveredSuspensionIfNeed(self, suspensionLodLink)
        self.__assembleSwinging(lodLink)
        model_assembler.assembleBurnoutProcessor(self)
        model_assembler.assembleSuspensionSound(self, lodLink, isPlayer)
        model_assembler.assembleHullAimingController(self)
        self.trackNodesAnimator = model_assembler.createTrackNodesAnimator(self, self.typeDescriptor, lodStateLink)
        model_assembler.assembleTracks(resourceRefs, self.typeDescriptor, self, self.splineTracks, False, lodStateLink)
        model_assembler.assembleVehicleTraces(self, self.filter, lodStateLink)
        return

    def __assembleSwinging(self, lodLink):
        hullNode = self.compoundModel.node(TankPartNames.HULL)
        if hullNode is None:
            _logger.error('Could not create SwingingAnimator: failed to find hull node')
            return
        else:
            self.swingingAnimator = model_assembler.createSwingingAnimator(self, self.typeDescriptor, hullNode.localMatrix, self.compoundModel.matrix, lodLink)
            self.compoundModel.node(TankPartNames.HULL, self.swingingAnimator.animatedMProv)
            if hasattr(self.filter, 'placingCompensationMatrix'):
                self.swingingAnimator.placingCompensationMatrix = self.filter.placingCompensationMatrix
            return

    def __postSetupFilter(self):
        suspensionWorking = self.suspension is not None and self.suspension.hasGroundNodes
        placingOnGround = not (suspensionWorking or self.leveredSuspension is not None)
        self.filter.placingOnGround = placingOnGround
        return

    def __onPeriodicTimer(self):
        timeStamp = BigWorld.wg_getFrameTimestamp()
        if self.__frameTimestamp >= timeStamp:
            self.__periodicTimerID = BigWorld.callback(0.0, self.__onPeriodicTimer)
        else:
            self.__frameTimestamp = timeStamp
            self.__periodicTimerID = BigWorld.callback(PERIODIC_UPDATE_TIME, self.__onPeriodicTimer)
            self._periodicUpdate()

    def _periodicUpdate(self):
        if self._vehicle is None or not self._vehicle.isAlive():
            return
        else:
            self._updateCurrTerrainMatKinds()
            self.__updateEffectsLOD()
            if self.siegeEffects:
                self.siegeEffects.tick()
            if self.customEffectManager:
                self.customEffectManager.update()
            return

    def __updateEffectsLOD(self):
        if self.customEffectManager:
            distanceFromPlayer = self.lodCalculator.lodDistance
            enableExhaust = distanceFromPlayer <= _LOD_DISTANCE_EXHAUST and not self.isUnderwater
            enableTrails = distanceFromPlayer <= _LOD_DISTANCE_TRAIL_PARTICLES and BigWorld.wg_isVehicleDustEnabled()
            self.customEffectManager.enable(enableTrails, EffectSettings.SETTING_DUST)
            self.customEffectManager.enable(enableExhaust, EffectSettings.SETTING_EXHAUST)

    def _stopEffects(self):
        self.boundEffects.stop()

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

    def _updateCurrTerrainMatKinds(self):
        if self.terrainMatKindSensor is None:
            return
        else:
            matKinds = self.terrainMatKindSensor.matKinds
            groundTypes = self.terrainMatKindSensor.groundTypes
            materialsCount = len(matKinds)
            for i in xrange(MATKIND_COUNT):
                matKind = matKinds[i] if i < materialsCount else 0
                groundType = groundTypes[i] if i < materialsCount else 0
                self.terrainMatKind[i] = matKind
                self.terrainGroundType[i] = groundType
                effectIndex = calcEffectMaterialIndex(matKind)
                effectMaterialName = ''
                if effectIndex is not None:
                    effectMaterialName = material_kinds.EFFECT_MATERIALS[effectIndex]
                self.terrainEffectMaterialNames[i] = effectMaterialName

            if self.vehicleTraces is not None:
                self.vehicleTraces.setCurrTerrainMatKinds(self.terrainMatKind[0], self.terrainMatKind[1])
            return

    def onSiegeStateChanged(self, newState, timeToNextMode):
        if self.siegeState is not None:
            self.siegeState.onSiegeStateChanged(newState)
        if self.engineAudition is not None:
            self.engineAudition.onSiegeStateChanged(newState)
        if self.hullAimingController is not None:
            self.hullAimingController.onSiegeStateChanged(newState)
        if self.suspensionSound is not None:
            self.suspensionSound.vehicleState = newState
        if self.siegeEffects is not None:
            self.siegeEffects.onSiegeStateChanged(newState, timeToNextMode)
        enabled = newState == VEHICLE_SIEGE_STATE.ENABLED or newState == VEHICLE_SIEGE_STATE.SWITCHING_ON
        if self.suspension is not None:
            self.suspension.setLiftMode(enabled)
        if self.leveredSuspension is not None:
            self.leveredSuspension.setLiftMode(enabled)
        if self.vehicleTraces is not None:
            self.vehicleTraces.setLiftMode(enabled)
        return

    def changeEngineMode(self, mode, forceSwinging=False):
        if self.detailedEngineState is not None:
            self.detailedEngineState.mode = mode[0]
        if self.trackScrollController is not None:
            self.trackScrollController.setMode(mode)
        return

    def changeSiegeState(self, siegeState):
        if self.engineAudition is not None:
            self.engineAudition.onSiegeStateChanged(siegeState)
        return

    def turretDamaged(self):
        pass

    def maxTurretRotationSpeed(self):
        pass

    def pushToLoadingQueue(self, prefab, go, vector, callback):
        self._loadingQueue.append((prefab,
         go,
         vector,
         callback))

    def _onCameraChanged(self, cameraName, currentVehicleId=None):
        if self.id != BigWorld.player().playerVehicleID:
            return
        isEnabled = not cameraName == 'sniper'
        for modelAnimator in self.__modelAnimators:
            modelAnimator.animator.setEnabled(isEnabled)

    def __onEngineStateGearUp(self):
        if self.customEffectManager is not None:
            self.customEffectManager.onGearUp()
        if self.engineAudition is not None:
            self.engineAudition.onEngineGearUp()
        return

    def __animatorCallback(self, name, time):
        _logger.debug('Callback aquired %s %f', name, time)
        if self.shellAnimator is not None:
            self.shellAnimator.throwShell(self.typeDescriptor.shot.shell.animation)
        return

    def getCurrentModelsSet(self):
        has3DStyle = self.outfit is not None and self.outfit.modelsSet is not None and self.outfit.modelsSet != ''
        return self.outfit.modelsSet if has3DStyle else 'default'

    def __shouldCreatePhysicalDestroyedTracks(self):
        quality = BigWorld.trackPhysicsQuality()
        if BigWorld.isForwardPipeline() or quality >= len(TrackCrashWithDebrisComponent.MAX_DEBRIS_COUNT):
            return False
        maxDebrisCount = TrackCrashWithDebrisComponent.MAX_DEBRIS_COUNT[quality]
        debrisCount = TrackCrashWithDebrisComponent.CURRENT_DEBRIS_COUNT
        return False if debrisCount >= maxDebrisCount and not self._vehicle.isPlayerVehicle else True

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
            if self.crashedTracksController is not None:
                for idx in indices:
                    self.crashedTracksController.addCrashedTrack(isLeft, idx, isSideFlying)

            return
        else:
            modelsSet = self.getCurrentModelsSet()
            for idx in indices:
                track = self.tracks.getTrackGameObject(isLeft, idx)
                track.createComponent(TrackCrashWithDebrisComponent, isLeft, idx, self.typeDescriptor, self.gameObject, self.boundEffects, self.filter, self._vehicle.isPlayerVehicle, shouldCreateDebris, hitPoint, modelsSet)
                if self.crashedTracksController is not None:
                    self.crashedTracksController.addDebrisCrashedTrack(isLeft, idx)

            return

    def _delCrashedTrack(self, isLeft, pairIndex):
        indices = self._getTrackPairIndicesToDestroy(pairIndex)
        foundCrashedTrackWithDebris = False
        if self.tracks is not None:
            for idx in indices:
                track = self.tracks.getTrackGameObject(isLeft, idx)
                if track.isValid():
                    debris = track.findComponentByType(TrackCrashWithDebrisComponent)
                    if debris is not None:
                        track.removeComponent(debris)
                        foundCrashedTrackWithDebris = True
                        if self.crashedTracksController is not None:
                            self.crashedTracksController.delDebrisCrashedTrack(isLeft, idx)

        if not foundCrashedTrackWithDebris and self.crashedTracksController is not None:
            for idx in indices:
                self.crashedTracksController.delCrashedTrack(isLeft, idx)

        return
