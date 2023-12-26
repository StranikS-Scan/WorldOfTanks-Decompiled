# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/model_assembler.py
import math
from collections import namedtuple
import logging
import Vehicular
import DataLinks
import WWISE
import BigWorld
import Math
import WoT
import material_kinds
import CGF
import GenericComponents
from constants import IS_DEVELOPMENT, IS_EDITOR, IS_UE_EDITOR
from skeletons.gui.shared.utils import IHangarSpace
from soft_exception import SoftException
import math_utils
from helpers import DecalMap, dependency
from items.components import shared_components, component_constants
from vehicle_systems.vehicle_damage_state import VehicleDamageState
from vehicle_systems.tankStructure import getPartModelsFromDesc, getCollisionModelsFromDesc, TankNodeNames, TankPartNames, TankPartIndexes, TankRenderMode, TankCollisionPartNames, TankSoundObjectsIndexes
from vehicle_systems.components.hull_aiming_controller import HullAimingController
_logger = logging.getLogger(__name__)
DEFAULT_MAX_LOD_PRIORITY = None
_INFINITY = 10000
_PHYSICAL_TRACKS_MAX_DISTANCE = 60
_PHYSICAL_TRACKS_MAX_COUNT = 5
_PHYSICAL_TRACKS_LOD_SETTINGS = shared_components.LodSettings(_PHYSICAL_TRACKS_MAX_DISTANCE, _PHYSICAL_TRACKS_MAX_COUNT)
_SPLINE_TRACKS_MAX_COUNT = 5
_AREA_LOD_FOR_NONSIMPLE_TRACKS = 50
_WHEEL_TO_TRACE_RATIO = 0.75
_DEFAULT_LOD_INDEX = 0

def __getWheelsRiseTime(vehicleDesc):
    wheelsRiseTime = 0.0
    chassisXPhysics = vehicleDesc.type.xphysics['chassis'][vehicleDesc.chassis.name]
    if 'wheelRiseSpeed' in chassisXPhysics:
        wheelRiseSpeed = chassisXPhysics['wheelRiseSpeed']
        if wheelRiseSpeed > 0.0:
            wheelsRiseTime = 1.0 / wheelRiseSpeed
    return wheelsRiseTime


def prepareCollisionAssembler(vehicleDesc, isTurretDetached, worldID):
    hitTestersByPart = {TankPartNames.CHASSIS: vehicleDesc.chassis.hitTester,
     TankPartNames.HULL: vehicleDesc.hull.hitTester}
    if not isTurretDetached:
        hitTestersByPart[TankPartNames.TURRET] = vehicleDesc.turret.hitTester
        hitTestersByPart[TankPartNames.GUN] = vehicleDesc.gun.hitTester
    bspModels = []
    for partName, hitTester in hitTestersByPart.iteritems():
        partId = TankPartNames.getIdx(partName)
        bspModel = (partId, hitTester.bspModelName)
        bspModels.append(bspModel)

    trackPairs = vehicleDesc.chassis.trackPairs[1:]
    for idx, trackPair in enumerate(trackPairs):
        totalDefaultParts = len(TankPartNames.ALL)
        bspModels.append((totalDefaultParts + idx, trackPair.hitTester.bspModelName))

    assembler = BigWorld.CollisionAssembler(tuple(bspModels), worldID)
    return assembler


def collisionIdxToTrackPairIdx(collisionIdx, typeDesc):
    leftBound = len(TankPartNames.ALL)
    rightBound = leftBound + len(typeDesc.chassis.trackPairs) - 1
    return collisionIdx - leftBound if leftBound < collisionIdx <= rightBound else None


def trackPairIdxToCollisionIdx(trackPairIdx):
    return len(TankPartNames.ALL) + trackPairIdx


def setupCollisions(vehicleDesc, collisions):
    hitTestersByPart = {TankPartNames.CHASSIS: vehicleDesc.chassis.hitTester,
     TankPartNames.HULL: vehicleDesc.hull.hitTester,
     TankPartNames.TURRET: vehicleDesc.turret.hitTester,
     TankPartNames.GUN: vehicleDesc.gun.hitTester}
    for partName, hitTester in hitTestersByPart.iteritems():
        partID = TankPartNames.getIdx(partName)
        hitTester.bbox = collisions.getBoundingBox(partID)
        if not hitTester.bbox:
            _logger.error("Couldn't find bounding box for the part '%s' (collisions=%s)", partName, collisions)

    trackPairs = vehicleDesc.chassis.trackPairs[1:]
    for idx, trackPair in enumerate(trackPairs):
        trackPair.hitTester.bbox = collisions.getBoundingBox(trackPairIdxToCollisionIdx(idx))
        if not trackPair.hitTester.bbox:
            _logger.error("Couldn't find bounding box for the track pair '%i' (collisions=%s)", idx, collisions)


def prepareCompoundAssembler(vehicleDesc, modelsSetParams, spaceID, isTurretDetached=False, lodIdx=_DEFAULT_LOD_INDEX, skipMaterials=False, renderMode=None):
    if IS_DEVELOPMENT and modelsSetParams.state not in VehicleDamageState.MODEL_STATE_NAMES:
        raise SoftException('Invalid modelStateName %s, must be in %s' % (modelsSetParams.state, VehicleDamageState.MODEL_STATE_NAMES))
    if spaceID is None:
        spaceID = BigWorld.player().spaceID
    assembler = BigWorld.CompoundAssembler()
    attachModels(assembler, vehicleDesc, modelsSetParams, isTurretDetached, renderMode)
    if renderMode == TankRenderMode.OVERLAY_COLLISION:
        attachModels(assembler, vehicleDesc, modelsSetParams, isTurretDetached, TankRenderMode.SERVER_COLLISION, True)
    cornerPoint = vehicleDesc.chassis.topRightCarryingPoint
    assembler.addNode(TankNodeNames.TRACK_LEFT_MID, TankPartNames.CHASSIS, math_utils.createTranslationMatrix((-cornerPoint[0], 0, 0)))
    assembler.addNode(TankNodeNames.TRACK_RIGHT_MID, TankPartNames.CHASSIS, math_utils.createTranslationMatrix((cornerPoint[0], 0, 0)))
    assembler.addNode(TankNodeNames.CHASSIS_MID_TRAIL, TankPartNames.CHASSIS)
    assembler.name = vehicleDesc.name
    assembler.spaceID = spaceID
    assembler.lodIdx = lodIdx
    assembler.skipMaterials = skipMaterials
    return assembler


def attachModels(assembler, vehicleDesc, modelsSetParams, isTurretDetached, renderMode=None, overlayCollision=False):
    collisionState = renderMode in (TankRenderMode.CLIENT_COLLISION,
     TankRenderMode.SERVER_COLLISION,
     TankRenderMode.CRASH_COLLISION,
     TankRenderMode.ARMOR_WIDTH_COLLISION)
    if collisionState:
        partModels = getCollisionModelsFromDesc(vehicleDesc, renderMode)
    else:
        partModels = getPartModelsFromDesc(vehicleDesc, modelsSetParams)
    chassis, hull, turret, gun = partModels
    partNames = TankPartNames
    if overlayCollision:
        partNames = TankCollisionPartNames
    if not overlayCollision:
        assembler.addRootPart(chassis, TankPartNames.CHASSIS)
    else:
        assembler.addPart(chassis, TankPartNames.CHASSIS, TankCollisionPartNames.CHASSIS)
    if collisionState:
        trackPairs = vehicleDesc.chassis.trackPairs[1:]
        for idx, trackPair in enumerate(trackPairs):
            assembler.addPart(trackPair.hitTester.bspModelName, partNames.CHASSIS, 'trackPair' + str(idx + 1))

    if collisionState and vehicleDesc.isWheeledVehicle:
        for i, wheel in enumerate(vehicleDesc.chassis.wheels.wheels):
            bspPath = ''
            if renderMode == TankRenderMode.CLIENT_COLLISION:
                bspPath = wheel.hitTesterManager.edClientBspModel
            elif renderMode in (TankRenderMode.SERVER_COLLISION, TankRenderMode.ARMOR_WIDTH_COLLISION):
                bspPath = wheel.hitTesterManager.edServerBspModel
            if bspPath:
                assembler.addNode(wheel.nodeName, partNames.CHASSIS, math_utils.createTranslationMatrix(wheel.position))
                assembler.emplacePart(bspPath, wheel.nodeName, TankCollisionPartNames.WHEEL + str(i))

    if collisionState and not overlayCollision:
        assembler.addNode('V', TankPartNames.CHASSIS, math_utils.createTranslationMatrix(vehicleDesc.chassis.hullPosition))
    if not overlayCollision:
        assembler.emplacePart(hull, 'V', partNames.HULL)
    else:
        assembler.addPart(hull, 'V', partNames.HULL)
    turretJointName = vehicleDesc.hull.turretHardPoints[0]
    assembler.addNodeAlias(turretJointName, TankNodeNames.TURRET_JOINT)
    if not isTurretDetached:
        if collisionState and not overlayCollision:
            assembler.addNode(turretJointName, 'V', math_utils.createRTMatrix(Math.Vector3(0, vehicleDesc.hull.turretPitches[0], 0), vehicleDesc.hull.turretPositions[0]))
        assembler.addPart(turret, turretJointName, partNames.TURRET)
        if collisionState and not overlayCollision:
            assembler.addNode(TankNodeNames.GUN_JOINT, TankPartNames.TURRET, math_utils.createRTMatrix(Math.Vector3(0, vehicleDesc.turret.gunJointPitch, 0), vehicleDesc.turret.gunPosition))
        assembler.addPart(gun, TankNodeNames.GUN_JOINT, partNames.GUN)
        if modelsSetParams.state == 'undamaged':
            for attachment in modelsSetParams.attachments:
                if attachment.attachmentLogic == 'prefab':
                    continue
                assembler.addPart(attachment.modelName, attachment.attachNode, attachment.partNodeAlias, attachment.transform)


def createGunAnimator(gameObject, vehicleDesc, basisMatrix=None, lodLink=None):
    recoilDescr = vehicleDesc.gun.recoil
    gunAnimator = gameObject.createComponent(Vehicular.RecoilAnimator, recoilDescr.backoffTime, recoilDescr.returnTime, recoilDescr.amplitude, recoilDescr.lodDist)
    if basisMatrix is not None:
        gunAnimator.basisMatrix = basisMatrix
    gunAnimator.lodLink = lodLink
    return gunAnimator


def createSwingingAnimator(gameObject, vehicleDesc, basisMatrix, worldMProv=None, lodLink=None):
    swingingAnimator = gameObject.createComponent(Vehicular.SwingingAnimator)
    swingingAnimator.basisMatrix = basisMatrix
    swingingCfg = vehicleDesc.hull.swinging
    pp = tuple((p * m for p, m in zip(swingingCfg.pitchParams, (0.9, 1.88, 0.3, 4.0, 1.0, 1.0))))
    swingingAnimator.setupPitchSwinging(*pp)
    swingingAnimator.setupRollSwinging(*swingingCfg.rollParams)
    swingingAnimator.setupShotSwinging(swingingCfg.sensitivityToImpulse)
    swingingAnimator.maxMovementSpeed = vehicleDesc.physics['speedLimits'][0]
    swingingAnimator.lodSetting = swingingCfg.lodDist
    swingingAnimator.worldMatrix = worldMProv if worldMProv is not None else math_utils.createIdentityMatrix()
    swingingAnimator.lodLink = lodLink
    return swingingAnimator


def createSuspension(appearance, vehicleDescriptor, lodStateLink):
    suspension = None
    try:
        compoundModel = appearance.compoundModel
        collisionObstaclesCollector = appearance.collisionObstaclesCollector
        tessellationCollisionSensor = appearance.tessellationCollisionSensor
        wheelsDataProvider = appearance.wheelsAnimator
        groundNodesConfig = vehicleDescriptor.chassis.groundNodes
        groundNodeGroups = groundNodesConfig.groups
        groundNodes = groundNodesConfig.nodes
        hasGroundNodes = len(groundNodeGroups) or len(groundNodes)
        if not hasGroundNodes:
            return
        siegeSwitchOnTime = 0.0
        siegeSwitchOffTime = 0.0
        if vehicleDescriptor.type.siegeModeParams is not None:
            siegeSwitchOnTime = vehicleDescriptor.type.siegeModeParams['switchOnTime']
            siegeSwitchOffTime = vehicleDescriptor.type.siegeModeParams['switchOffTime']
        if vehicleDescriptor.isWheeledVehicle:
            siegeSwitchOnTime = siegeSwitchOffTime = __getWheelsRiseTime(vehicleDescriptor)
        suspension = appearance.createComponent(Vehicular.Suspension, compoundModel, tessellationCollisionSensor, wheelsDataProvider, TankPartIndexes.CHASSIS, siegeSwitchOnTime, siegeSwitchOffTime, groundNodesConfig.activePostmortem, vehicleDescriptor.isWheeledVehicle)
        for groundGroup in groundNodeGroups:
            nodes = _createNameListByTemplate(groundGroup.startIndex, groundGroup.nodesTemplate, groundGroup.nodesCount)
            wheels = ['']
            if groundGroup.affectedWheelsTemplate is not None:
                wheels = _createNameListByTemplate(groundGroup.startIndex, groundGroup.affectedWheelsTemplate, groundGroup.nodesCount)
            suspension.addGroundNodesGroup(nodes, groundGroup.isLeft, groundGroup.minOffset, groundGroup.maxOffset, wheels, groundGroup.collisionSamplesCount, groundGroup.hasLiftMode)

        for groundNode in groundNodes:
            suspension.addGroundNode(groundNode.nodeName, groundNode.isLeft, groundNode.minOffset, groundNode.maxOffset, groundNode.affectedWheelName, groundNode.collisionSamplesCount, groundNode.hasLiftMode)

        if vehicleDescriptor.chassis.trackSplineParams is not None:
            trackSplineParams = vehicleDescriptor.chassis.trackSplineParams
            suspension.setParameters(trackSplineParams.thickness)
        else:
            suspension.setParameters(0.0)
        suspension.setLodLink(lodStateLink)
        lodSettings = groundNodesConfig.lodSettings
        if lodSettings is None:
            lodSettings = shared_components.LodSettings(vehicleDescriptor.chassis.chassisLodDistance, DEFAULT_MAX_LOD_PRIORITY)
        suspension.setLodSettings(lodSettings)
        suspension.setCollisionObstaclesCollector(collisionObstaclesCollector)
        collisionObstaclesCollector.setActivePostmortem(groundNodesConfig.activePostmortem)
        tessellationCollisionSensor.setActivePostmortem(groundNodesConfig.activePostmortem)
        return suspension
    except BigWorld.AssetException:
        _logger.error('Failed to create Suspension', exc_info=True)
        if suspension is not None:
            appearance.removeComponent(suspension)
        return

    return


def assembleSuspensionIfNeed(appearance, lodStateLink):
    appearance.suspension = createSuspension(appearance, appearance.typeDescriptor, lodStateLink)


def createLeveredSuspension(appearance, vehicleDescriptor, lodStateLink):
    compoundModel = appearance.compoundModel
    tessellationCollisionSensor = appearance.tessellationCollisionSensor
    wheelsDataProvider = appearance.wheelsAnimator
    leveredSuspensionConfig = vehicleDescriptor.chassis.leveredSuspension
    if leveredSuspensionConfig is None:
        return
    else:
        siegeSwitchOnTime = 0.0
        siegeSwitchOffTime = 0.0
        if vehicleDescriptor.type.siegeModeParams is not None:
            siegeSwitchOnTime = vehicleDescriptor.type.siegeModeParams['switchOnTime']
            siegeSwitchOffTime = vehicleDescriptor.type.siegeModeParams['switchOffTime']
        if vehicleDescriptor.isWheeledVehicle:
            siegeSwitchOnTime = siegeSwitchOffTime = __getWheelsRiseTime(vehicleDescriptor)
        leveredSuspension = appearance.createComponent(Vehicular.LeveredSuspension, compoundModel, leveredSuspensionConfig.levers, leveredSuspensionConfig.interpolationSpeedMul, tessellationCollisionSensor, wheelsDataProvider, siegeSwitchOnTime, siegeSwitchOffTime, leveredSuspensionConfig.activePostmortem)
        leveredSuspension.setupLodLink(lodStateLink)
        leveredSuspension.setupLodSettings(leveredSuspensionConfig.lodSettings)
        tessellationCollisionSensor.setActivePostmortem(leveredSuspensionConfig.activePostmortem)
        return leveredSuspension


def assembleLeveredSuspensionIfNeed(appearance, lodStateLink):
    appearance.leveredSuspension = createLeveredSuspension(appearance, appearance.typeDescriptor, lodStateLink)


def createWheelsAnimator(appearance, colliderType, typeDescriptor, wheelsState, wheelsScroll, wheelsSteering, splineTracks, lodStateLink=None):
    return createGeneralWheelsAnimator(appearance, colliderType, typeDescriptor, wheelsState, wheelsScroll, wheelsSteering, lodStateLink) if typeDescriptor.chassis.generalWheelsAnimatorConfig is not None else createTankWheelsAnimator(appearance, typeDescriptor, splineTracks, lodStateLink)


def createGeneralWheelsAnimator(appearance, colliderType, typeDescriptor, wheelsState, wheelsScroll, wheelsSteering, lodStateLink=None):
    config = typeDescriptor.chassis.generalWheelsAnimatorConfig
    generalWheelsAnimator = appearance.createComponent(Vehicular.GeneralWheelsAnimator, config, appearance.compoundModel, colliderType, wheelsState, wheelsScroll, wheelsSteering, appearance.id)
    generalWheelsAnimator.setLodLink(lodStateLink)
    generalWheelsAnimator.setLodSettings(shared_components.LodSettings(typeDescriptor.chassis.chassisLodDistance, DEFAULT_MAX_LOD_PRIORITY))
    generalWheelsAnimator.connectVehicleFashion(appearance.fashion)
    return generalWheelsAnimator


def createTankWheelsAnimator(appearance, typeDescriptor, splineTracks, lodStateLink=None):
    wheelsAnimator = None
    try:
        compoundModel = appearance.compoundModel
        f = appearance.filter
        wheelsConfig = typeDescriptor.chassis.wheels
        wheelsAnimator = appearance.createComponent(Vehicular.TankWheelsAnimator, compoundModel)
        for group in wheelsConfig.groups:
            nodes = _createNameListByTemplate(group.startIndex, group.template, group.count)
            wheelsAnimator.addWheelGroup(group.isLeft, group.radius, nodes)

        for wheel in wheelsConfig.wheels:
            wheelsAnimator.addWheel(wheel.isLeft, wheel.radius, wheel.nodeName, wheel.isLeading, wheel.leadingSyncAngle)

        if splineTracks is not None and splineTracks.left and splineTracks.right:
            wheelsAnimator.setSplineTrackMovementData(splineTracks.left[0], splineTracks.right[0])
        wheelsAnimator.setLodLink(lodStateLink)
        wheelsAnimator.setLodSettings(shared_components.LodSettings(typeDescriptor.chassis.chassisLodDistance, DEFAULT_MAX_LOD_PRIORITY))
        if f is not None:
            wheelsAnimator.setMovementInfo(f.movementInfo)
        return wheelsAnimator
    except BigWorld.AssetException:
        _logger.error('Failed to create TankWheelsAnimator', exc_info=True)
        if wheelsAnimator is not None:
            appearance.removeComponent(wheelsAnimator)
        return

    return


def createTrackNodesAnimator(appearance, typeDescriptor, lodStateLink=None):
    trackNodesAnimator = None
    try:
        compoundModel = appearance.compoundModel
        wheelsDataProvider = appearance.wheelsAnimator
        trackNodesConfig = typeDescriptor.chassis.trackNodes
        trackSplineParams = typeDescriptor.chassis.trackSplineParams
        if not trackNodesConfig:
            return
        trackNodesAnimator = appearance.createComponent(Vehicular.TrackNodesAnimator, compoundModel, TankNodeNames.HULL_SWINGING)
        if trackSplineParams is not None:
            trackNodesAnimator.setParameters(trackSplineParams.thickness, trackSplineParams.gravity, trackSplineParams.maxAmplitude, trackSplineParams.maxOffset)
        for trackNode in trackNodesConfig.nodes:
            leftSibling = '' if trackNode.leftNodeName is None else trackNode.leftNodeName
            rightSibling = '' if trackNode.rightNodeName is None else trackNode.rightNodeName
            trackNodesAnimator.addTrackNode(trackNode.name, trackNode.isLeft, trackNode.initialOffset, leftSibling, rightSibling, (trackNode.damping,
             trackNode.elasticity,
             trackNode.forwardElasticityCoeff,
             trackNode.backwardElasticityCoeff))

        trackNodesAnimator.setWheelsDataProvider(wheelsDataProvider)
        trackNodesAnimator.setLodLink(lodStateLink)
        trackNodesAnimator.setLodSettings(shared_components.LodSettings(typeDescriptor.chassis.chassisLodDistance, DEFAULT_MAX_LOD_PRIORITY))
        return trackNodesAnimator
    except BigWorld.AssetException:
        _logger.error('Failed to create TrackNodesAnimator', exc_info=True)
        if trackNodesAnimator is not None:
            appearance.removeComponent(trackNodesAnimator)
        return

    return


def assembleVehicleTraces(appearance, f, lodStateLink=None):
    vehicleTraces = appearance.createComponent(Vehicular.VehicleTraces)
    chassisConfig = appearance.typeDescriptor.chassis
    tracesConfig = chassisConfig.traces
    textures = {}
    for matKindName, texId in DecalMap.g_instance.getTextureSet(tracesConfig.textureSet).iteritems():
        if matKindName != 'bump':
            for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[matKindName]:
                textures[matKind] = texId

    vehicleTraces.setTrackTextures(textures)
    vehicleTraces.setCompound(appearance.compoundModel)
    if chassisConfig.generalWheelsAnimatorConfig is None:
        wrOffset = Math.Vector2(tracesConfig.centerOffset, 0)
        wlOffset = Math.Vector2(-tracesConfig.centerOffset, 0)
        length = appearance.typeDescriptor.chassis.topRightCarryingPoint[1] * 2
        vehicleTraces.addTrackTrace('', wrOffset, tracesConfig.size, length, tracesConfig.bufferPrefs, False)
        vehicleTraces.addTrackTrace('', wlOffset, tracesConfig.size, length, tracesConfig.bufferPrefs, False)
    else:
        traceConfigs = appearance.wheelsAnimator.getTraceConfigs()
        for trace in traceConfigs:
            vehicleTraces.addTrackTrace('', trace[0], tracesConfig.size, trace[1], tracesConfig.bufferPrefs, False)

    isLeftFlying = DataLinks.createBoolLink(appearance.flyingInfoProvider, 'isLeftSideFlying')
    isRightFlying = DataLinks.createBoolLink(appearance.flyingInfoProvider, 'isRightSideFlying')
    vehicleTraces.setFlyingInfo(isLeftFlying, isRightFlying)
    vehicleTraces.setLodLink(lodStateLink)
    vehicleTraces.setLodSettings(shared_components.LodSettings(tracesConfig.lodDist, DEFAULT_MAX_LOD_PRIORITY))
    vehicleTraces.setMovementInfo(f.movementInfo)
    vehicleTraces.setActivePostmortem(tracesConfig.activePostmortem)
    appearance.vehicleTraces = vehicleTraces
    return


def assembleRecoil(appearance, lodLink):
    gunAnimatorNode = appearance.compoundModel.node(TankNodeNames.GUN_RECOIL)
    localGunMatrix = gunAnimatorNode.localMatrix
    appearance.gunRecoil = gunRecoil = createGunAnimator(appearance, appearance.typeDescriptor, localGunMatrix, lodLink)
    gunRecoilMProv = gunRecoil.animatedMProv
    appearance.compoundModel.node(TankNodeNames.GUN_RECOIL, gunRecoilMProv)


def createMultiGunRecoils(appearance, lodLink, gunNodes):
    animators = []
    for gunInstance in gunNodes:
        gunNodeName = gunInstance.node
        gunAnimatorNode = appearance.compoundModel.node(gunNodeName)
        if gunAnimatorNode is not None:
            gameObject = CGF.GameObject(appearance.spaceID, 'Multigun recoil ' + gunNodeName)
            gameObject.createComponent(GenericComponents.HierarchyComponent, appearance.gameObject)
            localGunMatrix = gunAnimatorNode.localMatrix
            gunRecoil = createGunAnimator(gameObject, appearance.typeDescriptor, localGunMatrix, lodLink)
            animators.append(gameObject)
            gunRecoilMProv = gunRecoil.animatedMProv
            appearance.compoundModel.node(gunNodeName, gunRecoilMProv)

    return None if not animators else animators


def assembleMultiGunRecoil(appearance, lodLink):
    multiGun = appearance.typeDescriptor.turret.multiGun
    if multiGun is not None:
        appearance.gunAnimators = createMultiGunRecoils(appearance, lodLink, multiGun)
    return


def assembleGunLinkedNodesAnimator(appearance):
    skin = appearance.modelsSetParams.skin
    drivingJoints = appearance.typeDescriptor.gun.drivenJoints or {}
    drivingJoints = drivingJoints.get(skin, drivingJoints.get('default', None))
    if drivingJoints is not None:
        appearance.gunLinkedNodesAnimator = appearance.createComponent(Vehicular.LinkedNodesPitchAnimator, appearance.compoundModel, drivingJoints)
    return


def assembleHullAimingController(appearance):
    if not (appearance.typeDescriptor.hasSiegeMode and appearance.typeDescriptor.isPitchHullAimingAvailable):
        return
    appearance.hullAimingController = HullAimingController()


def assembleSuspensionSound(appearance, lodLink, isPlayer):
    if not WWISE.WW_isInitialised():
        return
    elif not appearance.typeDescriptor.hasSiegeMode:
        return
    else:
        siegeVehicleDescr = appearance.typeDescriptor.siegeVehicleDescr
        if siegeVehicleDescr is None:
            return
        suspensionSoundParams = siegeVehicleDescr.chassis.hullAimingSound
        if suspensionSoundParams is None:
            return
        model = appearance.compoundModel
        if model is None:
            return
        hullNode = model.node(TankPartNames.HULL)
        if hullNode is None:
            return
        suspensionSound = appearance.createComponent(Vehicular.SuspensionSound, appearance.id)
        suspensionSound.setSoundObject(appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.CHASSIS))
        for sound in suspensionSoundParams.sounds:
            if isPlayer:
                suspensionSound.setSoundsForState(sound.state, sound.underLimitSounds.PC, sound.overLimitSounds.PC)
            suspensionSound.setSoundsForState(sound.state, sound.underLimitSounds.NPC, sound.overLimitSounds.NPC)

        suspensionSound.bodyMatrix = None
        suspensionSound.angleLimitValue = suspensionSoundParams.angleLimitValue
        suspensionSound.lodLink = lodLink
        suspensionSound.lodSetting = suspensionSoundParams.lodDist
        suspensionSound.vehicleMatrix = appearance.filter.groundPlacingMatrix
        suspensionSound.bodyMatrix = appearance.filter.bodyMatrix
        appearance.suspensionSound = suspensionSound
        return


def assembleTerrainMatKindSensor(appearance, lodStateLink, spaceID):
    TERRAIN_MAT_KIND_SENSOR_LOD_DIST = 100.0
    TERRAIN_MAT_KIND_SENSOR_MAX_PRIORITY = 15
    compoundModel = appearance.compoundModel
    invertedOrigin = Math.Matrix(compoundModel.matrix)
    leftNodeMatrix = Math.Matrix(compoundModel.node(TankNodeNames.TRACK_LEFT_MID))
    rightNodeMatrix = Math.Matrix(compoundModel.node(TankNodeNames.TRACK_RIGHT_MID))
    leftNodeMatrix.postMultiply(invertedOrigin)
    rightNodeMatrix.postMultiply(invertedOrigin)
    scanLength = 4.0
    offset = Math.Vector3(0.0, scanLength * 0.5, 0.0)
    localPoints = (leftNodeMatrix.translation + offset, rightNodeMatrix.translation + offset, Math.Vector3(0.0, 0.0, 0.0) + offset)
    sensor = appearance.terrainMatKindSensor = appearance.createComponent(Vehicular.TerrainMatKindSensor, compoundModel.root, localPoints, scanLength)
    sensor.setLodLink(lodStateLink)
    sensor.setLodSettings(shared_components.LodSettings(TERRAIN_MAT_KIND_SENSOR_LOD_DIST, TERRAIN_MAT_KIND_SENSOR_MAX_PRIORITY))


def assembleVehicleAudition(isPlayer, appearance):
    PLAYER_UPDATE_PERIOD = 0.1
    NPC_UPDATE_PERIOD = 0.25
    typeDescriptor = appearance.typeDescriptor
    engineEventName = typeDescriptor.engine.sounds.getEvents()
    chassisEventName = typeDescriptor.chassis.sounds.getEvents()
    wheeledVehicle = False
    if typeDescriptor.chassis.generalWheelsAnimatorConfig is not None:
        wheeledVehicle = typeDescriptor.chassis.generalWheelsAnimatorConfig.isWheeledVehicle()
    if wheeledVehicle:
        vehicleData = (typeDescriptor.physics['enginePower'] / component_constants.HP_TO_WATTS,
         typeDescriptor.physics['weight'],
         typeDescriptor.physics['rotationSpeedLimit'],
         engineEventName,
         chassisEventName,
         ('wheel_vehicle_wheel_repaired', 'wheel_vehicle_wheel_metal_repaired'),
         ('wheel_vehicle_wheel_damaged', 'wheel_vehicle_wheel_metal_damaged'),
         'RTPC_ext_client_rpm_rel',
         'RTPC_ext_client_rpm_abs')
    else:
        vehicleData = (typeDescriptor.physics['enginePower'] / component_constants.HP_TO_WATTS,
         typeDescriptor.physics['weight'],
         typeDescriptor.physics['rotationSpeedLimit'],
         engineEventName,
         chassisEventName,
         ('repair_treads',),
         ('brakedown_treads',),
         '',
         '')
    vehicleAudition = appearance.createComponent(Vehicular.VehicleAudition, appearance.id, isPlayer, vehicleData)
    vehicleAudition.setEffectMaterialsInfo(lambda : appearance.terrainEffectMaterialNames)
    vehicleAudition.setSpeedInfo(lambda : appearance.filter.angularSpeed, lambda : appearance.filter.strafeSpeed)
    vehicleAudition.setTracksInfo(lambda : appearance.transmissionScroll, lambda : appearance.transmissionSlip, lambda : appearance.getWheelsSteeringMax(), DataLinks.createBoolLink(appearance.flyingInfoProvider, 'isFlying'))
    if typeDescriptor.type.siegeModeParams is not None:
        soundStateChange = typeDescriptor.type.siegeModeParams['soundStateChange']
        vehicleAudition.setSiegeSoundEvents(soundStateChange.isEngine, soundStateChange.on if isPlayer else soundStateChange.npcOn, soundStateChange.off if isPlayer else soundStateChange.npcOff)
    vehicleAudition.setDetailedEngineState(appearance.detailedEngineState)
    vehicleAudition.setUpdatePeriod(PLAYER_UPDATE_PERIOD if isPlayer else NPC_UPDATE_PERIOD)
    appearance.engineAudition = vehicleAudition
    return


def setupTurretRotations(appearance):
    compoundModel = appearance.compoundModel
    compoundModel.node(TankPartNames.TURRET, appearance.turretMatrix)
    if not appearance.damageState.isCurrentModelDamaged:
        compoundModel.node(TankNodeNames.GUN_INCLINATION, appearance.gunMatrix)
    else:
        compoundModel.node(TankPartNames.GUN, appearance.gunMatrix)
    if appearance.renderMode == TankRenderMode.OVERLAY_COLLISION:
        compoundModel.node(TankCollisionPartNames.TURRET, appearance.turretMatrix)
        compoundModel.node(TankCollisionPartNames.GUN, appearance.gunMatrix)


def createVehicleFilter(typeDescriptor):
    vehicleFilter = BigWorld.WGVehicleFilter()
    vehicleFilter.hullLocalPosition = typeDescriptor.chassis.hullPosition
    vehicleFilter.vehicleWidth = typeDescriptor.chassis.topRightCarryingPoint[0] * 2
    vehicleFilter.maxMove = typeDescriptor.physics['speedLimits'][0] * 2.0
    vehicleFilter.vehicleMinNormalY = typeDescriptor.physics['minPlaneNormalY']
    for p1, p2, p3 in typeDescriptor.physics['carryingTriangles']:
        vehicleFilter.addTriangle((p1[0], 0, p1[1]), (p2[0], 0, p2[1]), (p3[0], 0, p3[1]))

    vehicleFilter.forceGroundPlacingMatrix(typeDescriptor.isPitchHullAimingAvailable)
    return vehicleFilter


def _createNameListByTemplate(startIndex, template, count):
    return [ '%s%d' % (template, i) for i in range(startIndex, startIndex + count) ]


_ROOT_NODE_NAME = 'V'
SplineTracks = namedtuple('SplineTracks', ('left', 'right'))

def setupSplineTracks(fashion, vDesc, chassisModel, prereqs, modelsSet):
    splineDesc = vDesc.chassis.splineDesc
    resultTracks = None
    if splineDesc is None:
        return resultTracks
    else:
        leftSpline = []
        rightSpline = []
        for idx, trackDesc in splineDesc.trackPairs.iteritems():
            segmentModelLeft = segmentModelRight = segment2ModelLeft = segment2ModelRight = None
            modelName = trackDesc.segmentModelLeft(modelsSet)
            try:
                segmentModelLeft = prereqs[modelName]
            except Exception:
                _logger.error("can't load track segment model '%s'", modelName)

            modelName = trackDesc.segmentModelRight(modelsSet)
            try:
                segmentModelRight = prereqs[modelName]
            except Exception:
                _logger.error("can't load track segment model '%s'", modelName)

            modelName = trackDesc.segment2ModelLeft(modelsSet)
            if modelName is not None:
                try:
                    segment2ModelLeft = prereqs[modelName]
                except Exception:
                    _logger.error("can't load track segment 2 model '%s'", modelName)

            modelName = trackDesc.segment2ModelRight(modelsSet)
            if modelName is not None:
                try:
                    segment2ModelRight = prereqs[modelName]
                except Exception:
                    _logger.error("can't load track segment 2 model '%s'", modelName)

            if segmentModelLeft is not None and segmentModelRight is not None:
                identityMatrix = Math.Matrix()
                identityMatrix.setIdentity()
                if not chassisModel.isValid():
                    _logger.error('chassisModel is not valid')
                    return
                track = BigWorld.wg_createSplineTrack(chassisModel, trackDesc.leftDesc, idx, trackDesc.segmentLength, segmentModelLeft, trackDesc.segmentOffset, segment2ModelLeft, trackDesc.segment2Offset, _ROOT_NODE_NAME, trackDesc.atlasUTiles, trackDesc.atlasVTiles)
                if track is not None:
                    leftSpline.append(track)
                track = BigWorld.wg_createSplineTrack(chassisModel, trackDesc.rightDesc, idx, trackDesc.segmentLength, segmentModelRight, trackDesc.segmentOffset, segment2ModelRight, trackDesc.segment2Offset, _ROOT_NODE_NAME, trackDesc.atlasUTiles, trackDesc.atlasVTiles)
                if track is not None:
                    rightSpline.append(track)

        if len(leftSpline) != len(rightSpline) or not leftSpline:
            return
        fashion.setSplineTracks(leftSpline + rightSpline)
        resultTracks = SplineTracks(leftSpline, rightSpline)
        return resultTracks


def assembleWaterSensor(vehicleDesc, appearance, lodStateLink, spaceID):
    MIN_DEPTH_FOR_HEAVY_SPLASH = 0.5
    WATER_SENSOR_LOD_DIST = 150.0
    WATER_SENSOR_MAX_PRIORITY = 15
    turretOffset = vehicleDesc.chassis.hullPosition + vehicleDesc.hull.turretPositions[0]
    trPoint = vehicleDesc.chassis.topRightCarryingPoint
    lightVelocityThreshold = vehicleDesc.type.collisionEffectVelocities['waterContact']
    heavyVelocityThreshold = vehicleDesc.type.heavyCollisionEffectVelocities['waterContact']
    sensorConfig = (turretOffset,
     trPoint,
     lightVelocityThreshold,
     heavyVelocityThreshold,
     MIN_DEPTH_FOR_HEAVY_SPLASH,
     spaceID)
    sensor = appearance.createComponent(Vehicular.WaterSensor, sensorConfig)
    sensor.sensorPlaneLink = appearance.compoundModel.root
    sensor.speedLink = DataLinks.createFloatLink(appearance.filter, 'averageSpeed')
    sensor.onWaterSplash = appearance.onWaterSplash
    sensor.onUnderWaterSwitch = appearance.onUnderWaterSwitch
    sensor.setLodLink(lodStateLink)
    sensor.setLodSettings(shared_components.LodSettings(WATER_SENSOR_LOD_DIST, WATER_SENSOR_MAX_PRIORITY))
    return sensor


def assembleDrivetrain(appearance, isPlayerVehicle):
    vehicleFilter = appearance.filter
    typeDescriptor = appearance.typeDescriptor
    PLAYER_UPDATE_PERIOD = 0.1
    NPC_UPDATE_PERIOD = 0.25
    engineState = appearance.createComponent(Vehicular.DetailedEngineState)
    siegeState = appearance.createComponent(Vehicular.SiegeState)
    appearance.siegeState = siegeState
    engineState.vehicleSpeedLink = DataLinks.createFloatLink(vehicleFilter, 'averageSpeed')
    engineState.rotationSpeedLink = DataLinks.createFloatLink(vehicleFilter, 'averageRotationSpeed')
    engineState.vehicleMatrixLink = appearance.compoundModel.root
    speed_limits_0 = typeDescriptor.physics['speedLimits'][0]
    speed_limits_1 = typeDescriptor.physics['speedLimits'][1]
    rpm_min = typeDescriptor.engine.rpm_min
    rpm_max = typeDescriptor.engine.rpm_max
    rotation_speed_limit = typeDescriptor.physics['rotationSpeedLimit']
    max_climb_angle = math.acos(typeDescriptor.physics['minPlaneNormalY'])
    engineState.setVehicleParams(speed_limits_0, speed_limits_1, rotation_speed_limit, max_climb_angle, rpm_min, rpm_max, isPlayerVehicle)
    wheeledVehicle = False
    if typeDescriptor.chassis.generalWheelsAnimatorConfig is not None:
        wheeledVehicle = typeDescriptor.chassis.generalWheelsAnimatorConfig.isWheeledVehicle()
    if wheeledVehicle and isPlayerVehicle:
        gearShiftMap = (((1e-05, rpm_min * 1.2, rpm_max * 0.98),
          (0.15 * speed_limits_0, rpm_min * 1.7, rpm_max * 0.98),
          (0.5 * speed_limits_0, rpm_min * 2.2, rpm_max * 0.98),
          (0.7 * speed_limits_0, rpm_max * 0.7, rpm_max * 0.9)), ((0.01, rpm_min * 1.2, rpm_max * 0.98),))
        gearbox = appearance.createComponent(Vehicular.GearBox, speed_limits_0, speed_limits_1, rpm_min, rpm_max, gearShiftMap)
        gearbox.engineModeLink = DataLinks.createIntLink(engineState, 'mode')
        gearbox.vehicleSpeedLink = DataLinks.createFloatLink(vehicleFilter, 'averageSpeed')
        gearbox.flyingLink = DataLinks.createBoolLink(appearance.flyingInfoProvider, 'isFlying')
    else:
        gearbox = None
    if isPlayerVehicle:
        if gearbox is not None:
            engineState.physicRPMLink = lambda : gearbox.rpm
            engineState.physicGearLink = lambda : gearbox.gear
        elif not IS_EDITOR:
            p = BigWorld.player()
            engineState.physicRPMLink = lambda : WoT.unpackAuxVehiclePhysicsData(p.ownVehicleAuxPhysicsData)[5]
            engineState.physicGearLink = lambda : BigWorld.player().ownVehicleGear
    else:
        engineState.physicRPMLink = None
        engineState.physicGearLink = None
    engineState.updatePeriod = PLAYER_UPDATE_PERIOD if isPlayerVehicle else NPC_UPDATE_PERIOD
    return (engineState, gearbox)


def subscribeEngineAuditionToEngineState(engineAudition, engineState):
    engineState.onEngineStart = engineAudition.onEngineStart
    engineState.onStateChanged = engineAudition.onEngineStateChanged


def setupTracksFashion(vehicleDesc, fashion):
    tracksCfg = vehicleDesc.chassis.tracks
    if tracksCfg is not None:
        leftMaterials = []
        rightMaterials = []
        for value in tracksCfg.trackPairs.values():
            leftMaterials.append(value.leftMaterial)
            rightMaterials.append(value.rightMaterial)

        fashion.setTracksMaterials(leftMaterials, rightMaterials)
    return


def assembleSimpleTracks(vehicleDesc, fashion, wheelsDataProvider, tracks):
    tracksCfg = vehicleDesc.chassis.tracks
    if tracksCfg is None:
        return
    else:
        leftTracks = []
        rightTracks = []
        for i in xrange(len(tracksCfg.trackPairs)):
            left = (Vehicular.SimpleTrack,
             True,
             i,
             tracksCfg.trackPairs[i].leftMaterial,
             fashion,
             wheelsDataProvider,
             tracksCfg.trackPairs[i].textureScale)
            right = (Vehicular.SimpleTrack,
             False,
             i,
             tracksCfg.trackPairs[i].rightMaterial,
             fashion,
             wheelsDataProvider,
             tracksCfg.trackPairs[i].textureScale)
            leftTracks.append(left)
            rightTracks.append(right)

        lodSettings = shared_components.LodSettings(_INFINITY, DEFAULT_MAX_LOD_PRIORITY)
        tracks.addTrackComponent(True, leftTracks, lodSettings)
        tracks.addTrackComponent(False, rightTracks, lodSettings)
        return


def assembleSizePhysicalTrack(resourceRefs, resourceFormat, isLeft, trackPairsCount, appearance, tracks, instantWarmup, setupOnlyThickness=False):
    if appearance.wheelsAnimator is None:
        return False
    else:
        try:
            inited = True
            allTracks = []
            for i in xrange(trackPairsCount):
                name = resourceFormat.format(i)
                trackBuilder = resourceRefs[name] if resourceRefs.has_key(name) else None
                if trackBuilder is not None and trackBuilder.isValid() and not setupOnlyThickness:
                    trackData = (Vehicular.PhysicalTrack,
                     trackBuilder,
                     appearance.compoundModel,
                     appearance.wheelsAnimator,
                     appearance.collisionObstaclesCollector,
                     appearance.tessellationCollisionSensor,
                     appearance.fashion,
                     instantWarmup)
                    allTracks.append(trackData)
                if trackBuilder is not None:
                    go = tracks.getTrackGameObject(isLeft, i)
                    compositeTrack = go.findComponentByType(Vehicular.CompositeTrack)
                    compositeTrack.trackThickness = trackBuilder.trackThickness
                inited = False

            if allTracks:
                tracks.addTrackComponent(isLeft, allTracks, _PHYSICAL_TRACKS_LOD_SETTINGS)
        except ValueError as e:
            _logger.error('Failure on physical track creation: %s', e)
            inited = False

        return inited


def assemblePhysicalTracks(resourceRefs, trackPairsCount, appearance, tracks, instantWarmup, setupOnlyThickness=False):
    inited = True
    inited = inited and assembleSizePhysicalTrack(resourceRefs, 'left{0}PhysicalTrack', True, trackPairsCount, appearance, tracks, instantWarmup, setupOnlyThickness)
    inited = inited and assembleSizePhysicalTrack(resourceRefs, 'right{0}PhysicalTrack', False, trackPairsCount, appearance, tracks, instantWarmup, setupOnlyThickness)
    return inited


def assembleSplineTracks(vehicleDesc, appearance, splineTracksImpl, tracks):
    if splineTracksImpl is None:
        return
    else:
        lodDist = vehicleDesc.chassis.splineDesc.lodDist
        lodSettings = shared_components.LodSettings(lodDist, _SPLINE_TRACKS_MAX_COUNT)
        leftSplineTracks = []
        rightSplineTracks = []
        for left, right in zip(splineTracksImpl[0], splineTracksImpl[1]):
            leftSplineTracks.append((Vehicular.SplineTrack,
             left,
             appearance.compoundModel,
             appearance.wheelsAnimator))
            rightSplineTracks.append((Vehicular.SplineTrack,
             right,
             appearance.compoundModel,
             appearance.wheelsAnimator))

        if leftSplineTracks:
            tracks.addTrackComponent(True, leftSplineTracks, lodSettings)
        if rightSplineTracks:
            tracks.addTrackComponent(False, rightSplineTracks, lodSettings)
        return


def assembleTracks(resourceRefs, vehicleDesc, appearance, splineTracksImpl, instantWarmup, lodLink=None):
    trackPairsCount = 0
    tracksCfg = vehicleDesc.chassis.tracks
    if tracksCfg is not None:
        trackPairsCount = len(tracksCfg.trackPairs)
    tracks = Vehicular.VehicleTracks(appearance.gameObject, appearance.compoundModel, TankPartIndexes.CHASSIS, _AREA_LOD_FOR_NONSIMPLE_TRACKS, trackPairsCount)
    appearance.tracks = tracks
    assemblePhysicalTracks(resourceRefs, trackPairsCount, appearance, tracks, instantWarmup)
    assembleSplineTracks(vehicleDesc, appearance, splineTracksImpl, tracks)
    assembleSimpleTracks(vehicleDesc, appearance.fashion, appearance.wheelsAnimator, tracks)
    vehicleFilter = getattr(appearance, 'filter', None)
    if vehicleFilter is not None:
        tracks.setTrackScrollLink(DataLinks.createFloatLink(vehicleFilter, 'leftTrackScroll'), DataLinks.createFloatLink(vehicleFilter, 'rightTrackScroll'))
    if appearance.wheelsAnimator and appearance.wheelsAnimator.scrollLinksRequired:
        tracks.collectConnectedWheels(appearance.wheelsAnimator)
        tracks.sendWheelScrollLinks(appearance.wheelsAnimator)
    if lodLink is None:
        lodLink = Vehicular.getDummyLodLink()
    tracks.setLodLink(lodLink)
    crashedTracksController = getattr(appearance, 'crashedTracksController', None)
    if crashedTracksController is not None:
        crashedTracksController.baseTracksComponent = tracks
    return


def assembleCollisionObstaclesCollector(appearance, lodStateLink, desc):
    isWheeledVehicle = 'wheeledVehicle' in desc.type.tags
    collisionObstaclesCollector = appearance.createComponent(Vehicular.CollisionObstaclesCollector, appearance.compoundModel, appearance.spaceID, isWheeledVehicle)
    if lodStateLink is not None:
        collisionObstaclesCollector.setLodLink(lodStateLink)
        collisionObstaclesCollector.setLodSettings(shared_components.LodSettings(appearance.typeDescriptor.chassis.chassisLodDistance, DEFAULT_MAX_LOD_PRIORITY))
    appearance.collisionObstaclesCollector = collisionObstaclesCollector
    return


def assembleTessellationCollisionSensor(appearance, lodStateLink):
    tessellationCollisionSensor = appearance.createComponent(Vehicular.TessellationCollisionSensor, appearance.compoundModel, TankPartIndexes.CHASSIS)
    if lodStateLink is not None:
        tessellationCollisionSensor.setLodLink(lodStateLink)
        tessellationCollisionSensor.setLodSettings(shared_components.LodSettings(appearance.typeDescriptor.chassis.chassisLodDistance, DEFAULT_MAX_LOD_PRIORITY))
    appearance.tessellationCollisionSensor = tessellationCollisionSensor
    return


def assembleBurnoutProcessor(appearance):
    burnoutAnimation = appearance.typeDescriptor.hull.burnoutAnimation
    if burnoutAnimation is None:
        return
    else:
        burnoutProcessor = appearance.createComponent(Vehicular.BurnoutProcessor, appearance.compoundModel, appearance.swingingAnimator, lambda : appearance.burnoutLevel, burnoutAnimation.accumImpulseMag, burnoutAnimation.dischargeImpulseMag, burnoutAnimation.timeToAccumImpulse)
        appearance.burnoutProcessor = burnoutProcessor
        return


def assembleCustomLogicComponents(appearance, typeDescriptor, attachments, modelAnimators):
    assemblers = [('flagAnimation', __assembleAnimationFlagComponent), ('prefab', __assemblePrefabComponent)]
    for assemblerName, assembler in assemblers:
        for attachment in attachments:
            if attachment.attachmentLogic == assemblerName:
                assembler(appearance, attachment, attachments, modelAnimators)

    for prefab in typeDescriptor.chassis.prefabs:
        loadAppearancePrefab(prefab, appearance)

    for prefab in typeDescriptor.hull.prefabs:
        loadAppearancePrefab(prefab, appearance)

    for prefab in typeDescriptor.turret.prefabs:
        loadAppearancePrefab(prefab, appearance)

    for prefab in typeDescriptor.gun.prefabs:
        loadAppearancePrefab(prefab, appearance)


def __assembleAnimationFlagComponent(appearance, attachment, attachments, modelAnimators):
    mainAnimator = None
    for i, modelAnimator in enumerate(modelAnimators):
        if modelAnimator.attachmentPartNode == attachment.partNodeAlias:
            mainAnimator = modelAnimators.pop(i)
            break

    if mainAnimator is None:
        return False
    else:
        flagParts = tuple((a.partNodeAlias for a in attachments if a.attachmentLogic == 'flagPart'))
        appearance.flagComponent = appearance.createComponent(Vehicular.FlagComponent, mainAnimator.animator, mainAnimator.node, TankPartNames.TURRET, (attachment.partNodeAlias,) + flagParts)
        if appearance.filter is not None:
            appearance.flagComponent.vehicleSpeedLink = DataLinks.createFloatLink(appearance.filter, 'averageSpeed')
            appearance.flagComponent.allowTransparency(True)
        return True


def loadAppearancePrefab(prefab, appearance, posloadCallback=None):

    def _onLoaded(gameObject):
        appearance.undamagedStateChildren.append(gameObject)
        if IS_UE_EDITOR:
            gameObject.removeComponentByType(GenericComponents.DynamicModelComponent)
        gameObject.createComponent(GenericComponents.RedirectorComponent, appearance.gameObject)
        gameObject.createComponent(GenericComponents.DynamicModelComponent, appearance.compoundModel)
        if posloadCallback:
            posloadCallback(gameObject)

    if appearance.compoundModel:
        CGF.loadGameObjectIntoHierarchy(prefab, appearance.gameObject, Math.Vector3(0, 0, 0), _onLoaded)
    else:
        appearance.pushToLoadingQueue(prefab, appearance.gameObject, Math.Vector3(0, 0, 0), _onLoaded)


def __assemblePrefabComponent(appearance, attachment, _, __):
    if not IS_UE_EDITOR:
        hangar = dependency.instance(IHangarSpace)
        modelName = attachment.hangarModelName if attachment.hangarModelName and hangar.inited else attachment.modelName
        loadAppearancePrefab(modelName, appearance)
    else:
        loadAppearancePrefab(attachment.modelName, appearance)
