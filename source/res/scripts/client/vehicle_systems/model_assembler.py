# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/model_assembler.py
import math
from collections import namedtuple
from soft_exception import SoftException
from AvatarInputHandler import mathUtils
import BigWorld
from CustomEffectManager import CustomEffectManager
from items.components.shared_components import LodSettings
from vehicle_systems.vehicle_damage_state import VehicleDamageState
import constants
from helpers import gEffectsDisabled
from vehicle_systems.tankStructure import getPartModelsFromDesc, TankNodeNames, TankPartNames, TankPartIndexes
import Vehicular
import DataLinks
import WWISE
from vehicle_systems.components.siegeEffectsController import SiegeEffectsController
from vehicle_systems.components.suspension_controller import SuspensionController
from items.components import shared_components, component_constants
import debug_utils
import material_kinds
import Math
from helpers import DecalMap
import WoT
DEFAULT_MAX_LOD_PRIORITY = None
_INFINITY = 10000
_PHYSICAL_TRACKS_MAX_DISTANCE = 60
_PHYSICAL_TRACKS_MAX_COUNT = 5
_PHYSICAL_TRACKS_LOD_SETTINGS = LodSettings(_PHYSICAL_TRACKS_MAX_DISTANCE, _PHYSICAL_TRACKS_MAX_COUNT)
_SPLINE_TRACKS_MAX_COUNT = 5
_AREA_LOD_FOR_NONSIMPLE_TRACKS = 50

def prepareCompoundAssembler(vehicleDesc, modelsSetParams, spaceID, isTurretDetached=False):
    if constants.IS_DEVELOPMENT and modelsSetParams.state not in VehicleDamageState.MODEL_STATE_NAMES:
        raise SoftException('Invalid modelStateName %s, must be in %s' % (modelsSetParams.state, VehicleDamageState.MODEL_STATE_NAMES))
    if spaceID is None:
        spaceID = BigWorld.player().spaceID
    partModels = getPartModelsFromDesc(vehicleDesc, modelsSetParams)
    chassis, hull, turret, gun = partModels
    assembler = BigWorld.CompoundAssembler()
    assembler.addRootPart(chassis, TankPartNames.CHASSIS)
    assembler.emplacePart(hull, 'V', TankPartNames.HULL)
    turretJointName = vehicleDesc.hull.turretHardPoints[0]
    assembler.addNodeAlias(turretJointName, TankNodeNames.TURRET_JOINT)
    if not isTurretDetached:
        assembler.addPart(turret, turretJointName, TankPartNames.TURRET)
        assembler.addPart(gun, TankNodeNames.GUN_JOINT, TankPartNames.GUN)
    cornerPoint = vehicleDesc.chassis.topRightCarryingPoint
    assembler.addNode(TankNodeNames.TRACK_LEFT_MID, TankPartNames.CHASSIS, mathUtils.createTranslationMatrix((-cornerPoint[0], 0, 0)))
    assembler.addNode(TankNodeNames.TRACK_RIGHT_MID, TankPartNames.CHASSIS, mathUtils.createTranslationMatrix((cornerPoint[0], 0, 0)))
    assembler.addNode(TankNodeNames.CHASSIS_MID_TRAIL, TankPartNames.CHASSIS)
    assembler.assemblerName = vehicleDesc.name
    assembler.spaceID = spaceID
    return assembler


def createGunAnimator(vehicleDesc, basisMatrix=None, lodLink=None):
    recoilDescr = vehicleDesc.gun.recoil
    gunAnimator = Vehicular.RecoilAnimator(recoilDescr.backoffTime, recoilDescr.returnTime, recoilDescr.amplitude, recoilDescr.lodDist)
    if basisMatrix is not None:
        gunAnimator.basisMatrix = basisMatrix
    gunAnimator.lodLink = lodLink
    return gunAnimator


def createSwingingAnimator(vehicleDesc, basisMatrix=None, worldMProv=None, lodLink=None):
    swingingAnimator = Vehicular.SwingingAnimator()
    swingingAnimator.basisMatrix = basisMatrix
    swingingCfg = vehicleDesc.hull.swinging
    pp = tuple((p * m for p, m in zip(swingingCfg.pitchParams, (0.9, 1.88, 0.3, 4.0, 1.0, 1.0))))
    swingingAnimator.setupPitchSwinging(*pp)
    swingingAnimator.setupRollSwinging(*swingingCfg.rollParams)
    swingingAnimator.setupShotSwinging(swingingCfg.sensitivityToImpulse)
    swingingAnimator.maxMovementSpeed = vehicleDesc.physics['speedLimits'][0]
    swingingAnimator.lodSetting = swingingCfg.lodDist
    swingingAnimator.worldMatrix = worldMProv if worldMProv is not None else mathUtils.createIdentityMatrix()
    swingingAnimator.lodLink = lodLink
    return swingingAnimator


def createSuspension(compoundModel, vehicleDescriptor, lodStateLink, collisionObstaclesCollector, tessellationCollisionSensor):
    groundNodesConfig = vehicleDescriptor.chassis.groundNodes
    groundNodeGroups = groundNodesConfig.groups
    groundNodes = groundNodesConfig.nodes
    hasGroundNodes = len(groundNodeGroups) or len(groundNodes)
    if not hasGroundNodes:
        return None
    else:
        suspension = Vehicular.Suspension(compoundModel, tessellationCollisionSensor, TankPartIndexes.CHASSIS)
        for groundGroup in groundNodeGroups:
            nodes = _createNodeNameListByTemplate(groundGroup.startIndex, groundGroup.template, groundGroup.count)
            suspension.addGroundNodesGroup(nodes, groundGroup.isLeft, groundGroup.minOffset, groundGroup.maxOffset)

        for groundNode in groundNodes:
            suspension.addGroundNode(groundNode.name, groundNode.isLeft, groundNode.minOffset, groundNode.maxOffset)

        trackParams = vehicleDescriptor.chassis.trackParams
        suspension.setParameters(trackParams.thickness)
        suspension.setLodLink(lodStateLink)
        suspension.setLodSettings(shared_components.LodSettings(vehicleDescriptor.chassis.wheels.lodDist, DEFAULT_MAX_LOD_PRIORITY))
        suspension.setCollisionObstaclesCollector(collisionObstaclesCollector)
        return suspension


def assembleSuspensionIfNeed(appearance, lodStateLink):
    appearance.suspension = createSuspension(appearance.compoundModel, appearance.typeDescriptor, lodStateLink, appearance.collisionObstaclesCollector, appearance.tessellationCollisionSensor)


def createLeveredSuspension(compoundModel, vehicleDescriptor, lodStateLink):
    leveredSuspensionConfig = vehicleDescriptor.chassis.leveredSuspension
    if leveredSuspensionConfig is None:
        return
    else:
        leveredSuspension = Vehicular.LeveredSuspension(compoundModel, leveredSuspensionConfig.levers, leveredSuspensionConfig.interpolationSpeedMul)
        leveredSuspension.setupLodLink(lodStateLink)
        leveredSuspension.setupLodSettings(leveredSuspensionConfig.lodSettings)
        return leveredSuspension


def assembleLeveredSuspensionIfNeed(appearance, lodStateLink):
    appearance.leveredSuspension = createLeveredSuspension(appearance.compoundModel, appearance.typeDescriptor, lodStateLink)


def createWheelsAnimator(compoundModel, typeDescriptor, splineTracks, f=None, lodStateLink=None):
    wheelsConfig = typeDescriptor.chassis.wheels
    wheelsAnimator = Vehicular.WheelsAnimator(compoundModel)
    for group in wheelsConfig.groups:
        nodes = _createNodeNameListByTemplate(group.startIndex, group.template, group.count)
        wheelsAnimator.addWheelGroup(group.isLeft, group.radius, nodes)

    for wheel in wheelsConfig.wheels:
        wheelsAnimator.addWheel(wheel.isLeft, wheel.radius, wheel.nodeName, wheel.isLeading, wheel.leadingSyncAngle)

    if splineTracks is not None:
        wheelsAnimator.setSplineTrackMovementData(splineTracks.left, splineTracks.right)
    wheelsAnimator.setLodLink(lodStateLink)
    wheelsAnimator.setLodSettings(shared_components.LodSettings(typeDescriptor.chassis.wheels.lodDist, DEFAULT_MAX_LOD_PRIORITY))
    if f is not None:
        wheelsAnimator.setMovementInfo(f.movementInfo)
    return wheelsAnimator


def createTrackNodesAnimator(compoundModel, typeDescriptor, wheelsDataProvider=None, lodStateLink=None):
    trackNodesConfig = typeDescriptor.chassis.trackNodes
    trackParams = typeDescriptor.chassis.trackParams
    if not trackNodesConfig:
        return
    else:
        trackNodesAnimator = Vehicular.TrackNodesAnimator(compoundModel, TankNodeNames.HULL_SWINGING)
        if trackParams is not None:
            trackNodesAnimator.setParameters(trackParams.thickness, trackParams.gravity, trackParams.maxAmplitude, trackParams.maxOffset)
        for trackNode in trackNodesConfig.nodes:
            leftSibling = '' if trackNode.leftNodeName is None else trackNode.leftNodeName
            rightSibling = '' if trackNode.rightNodeName is None else trackNode.rightNodeName
            trackNodesAnimator.addTrackNode(trackNode.name, trackNode.isLeft, trackNode.initialOffset, leftSibling, rightSibling, (trackNode.damping,
             trackNode.elasticity,
             trackNode.forwardElasticityCoeff,
             trackNode.backwardElasticityCoeff))

        trackNodesAnimator.setWheelsDataProvider(wheelsDataProvider)
        trackNodesAnimator.setLodLink(lodStateLink)
        trackNodesAnimator.setLodSettings(shared_components.LodSettings(typeDescriptor.chassis.wheels.lodDist, DEFAULT_MAX_LOD_PRIORITY))
        return trackNodesAnimator


def assembleVehicleTraces(appearance, f, lodStateLink=None):
    vehicleTraces = Vehicular.VehicleTraces()
    tracesConfig = appearance.typeDescriptor.chassis.traces
    textures = {}
    for matKindName, texId in DecalMap.g_instance.getTextureSet(tracesConfig.textureSet).iteritems():
        if matKindName != 'bump':
            for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[matKindName]:
                textures[matKind] = texId

    vehicleTraces.setTrackTraces(tracesConfig.bufferPrefs, textures, tracesConfig.centerOffset, tracesConfig.size, appearance.typeDescriptor.chassis.topRightCarryingPoint[1] * 2)
    vehicleTraces.setCompound(appearance.compoundModel)
    isLeftFlying = DataLinks.createBoolLink(appearance.flyingInfoProvider, 'isLeftSideFlying')
    isRightFlying = DataLinks.createBoolLink(appearance.flyingInfoProvider, 'isRightSideFlying')
    vehicleTraces.setFlyingInfo(isLeftFlying, isRightFlying)
    vehicleTraces.setLodLink(lodStateLink)
    vehicleTraces.setLodSettings(shared_components.LodSettings(tracesConfig.lodDist, DEFAULT_MAX_LOD_PRIORITY))
    vehicleTraces.setMovementInfo(f.movementInfo)
    appearance.vehicleTraces = vehicleTraces


def assembleRecoil(appearance, lodLink):
    gunAnimatorNode = appearance.compoundModel.node(TankNodeNames.GUN_RECOIL)
    localGunMatrix = gunAnimatorNode.localMatrix
    appearance.gunRecoil = gunRecoil = createGunAnimator(appearance.typeDescriptor, localGunMatrix, lodLink)
    gunRecoilMProv = gunRecoil.animatedMProv
    appearance.compoundModel.node(TankNodeNames.GUN_RECOIL, gunRecoilMProv)


def assembleGunLinkedNodesAnimator(appearance):
    drivingJoints = appearance.typeDescriptor.gun.drivenJoints
    if drivingJoints is not None:
        appearance.gunLinkedNodesAnimator = Vehicular.LinkedNodesPitchAnimator(appearance.compoundModel, drivingJoints)
    return


def assembleSuspensionController(appearance):
    if not (appearance.typeDescriptor.hasSiegeMode and appearance.typeDescriptor.isPitchHullAimingAvailable):
        return
    appearance.suspensionController = SuspensionController()


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
        suspensionSound = Vehicular.SuspensionSound(appearance.id)
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


def assembleTerrainMatKindSensor(appearance, lodStateLink):
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
    sensor = appearance.terrainMatKindSensor = Vehicular.TerrainMatKindSensor(compoundModel.root, localPoints, scanLength, BigWorld.player().spaceID)
    sensor.setLodLink(lodStateLink)
    sensor.setLodSettings(shared_components.LodSettings(TERRAIN_MAT_KIND_SENSOR_LOD_DIST, TERRAIN_MAT_KIND_SENSOR_MAX_PRIORITY))


def assembleVehicleAudition(isPlayer, appearance):
    PLAYER_UPDATE_PERIOD = 0.1
    NPC_UPDATE_PERIOD = 0.25
    typeDescriptor = appearance.typeDescriptor
    engineEventName = typeDescriptor.engine.sounds.getWWPlayerSound(isPlayer)
    chassisEventName = typeDescriptor.chassis.sounds.getWWPlayerSound(isPlayer)
    vehicleData = (typeDescriptor.physics['enginePower'] / component_constants.HP_TO_WATTS, typeDescriptor.physics['weight'], typeDescriptor.physics['rotationSpeedLimit'])
    vehicleAudition = Vehicular.VehicleAudition(appearance.id, isPlayer, vehicleData, engineEventName, chassisEventName)
    vehicleAudition.setEffectMaterialsInfo(lambda : appearance.terrainEffectMaterialNames)
    vehicleAudition.setSpeedInfo(lambda : appearance.filter.angularSpeed, lambda : appearance.filter.strafeSpeed)
    vehicleAudition.setTrackScrollInfo(lambda : appearance.leftTrackScroll, lambda : appearance.rightTrackScroll, lambda : appearance.customEffectManager.getParameter('deltaL'), lambda : appearance.customEffectManager.getParameter('deltaR'))
    vehicleAudition.setIsFlyingInfo(DataLinks.createBoolLink(appearance.flyingInfoProvider, 'isFlying'))
    if typeDescriptor.type.siegeModeParams is not None:
        soundStateChange = typeDescriptor.type.siegeModeParams['soundStateChange']
        vehicleAudition.setSiegeSoundEvents(soundStateChange.on if soundStateChange.on is not None else '', soundStateChange.off if soundStateChange.off is not None else '')
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


def createEffects(appearance):
    if gEffectsDisabled():
        appearance.customEffectManager = None
        return
    else:
        appearance.customEffectManager = CustomEffectManager(appearance)
        if not appearance.typeDescriptor.hasSiegeMode:
            return
        appearance.siegeEffects = SiegeEffectsController(appearance)
        return


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


def _createNodeNameListByTemplate(startIndex, template, count):
    return [ '%s%d' % (template, i) for i in range(startIndex, startIndex + count) ]


_ROOT_NODE_NAME = 'V'
SplineTracks = namedtuple('SplineTracks', ('left', 'right'))

def setupSplineTracks(fashion, vDesc, chassisModel, prereqs):
    splineDesc = vDesc.chassis.splineDesc
    resultTracks = None
    if splineDesc is not None:
        leftSpline = None
        rightSpline = None
        segmentModelLeft = segmentModelRight = segment2ModelLeft = segment2ModelRight = None
        modelName = splineDesc.segmentModelLeft
        try:
            segmentModelLeft = prereqs[modelName]
        except Exception:
            debug_utils.LOG_ERROR("can't load track segment model <%s>" % modelName)

        modelName = splineDesc.segmentModelRight
        try:
            segmentModelRight = prereqs[modelName]
        except Exception:
            debug_utils.LOG_ERROR("can't load track segment model <%s>" % modelName)

        modelName = splineDesc.segment2ModelLeft
        if modelName is not None:
            try:
                segment2ModelLeft = prereqs[modelName]
            except Exception:
                debug_utils.LOG_ERROR("can't load track segment 2 model <%s>" % modelName)

        modelName = splineDesc.segment2ModelRight
        if modelName is not None:
            try:
                segment2ModelRight = prereqs[modelName]
            except Exception:
                debug_utils.LOG_ERROR("can't load track segment 2 model <%s>" % modelName)

        if segmentModelLeft is not None and segmentModelRight is not None:
            identityMatrix = Math.Matrix()
            identityMatrix.setIdentity()
            if splineDesc.leftDesc is not None:
                leftSpline = BigWorld.wg_createSplineTrack(fashion, chassisModel, splineDesc.leftDesc, splineDesc.segmentLength, segmentModelLeft, splineDesc.segmentOffset, segment2ModelLeft, splineDesc.segment2Offset, _ROOT_NODE_NAME, splineDesc.atlasUTiles, splineDesc.atlasVTiles)
            if splineDesc.rightDesc is not None:
                rightSpline = BigWorld.wg_createSplineTrack(fashion, chassisModel, splineDesc.rightDesc, splineDesc.segmentLength, segmentModelRight, splineDesc.segmentOffset, segment2ModelRight, splineDesc.segment2Offset, _ROOT_NODE_NAME, splineDesc.atlasUTiles, splineDesc.atlasVTiles)
            fashion.setSplineTrack(leftSpline, rightSpline)
        resultTracks = SplineTracks(leftSpline, rightSpline)
    return resultTracks


def assembleWaterSensor(vehicleDesc, appearance, lodStateLink):
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
     BigWorld.player().spaceID)
    sensor = Vehicular.WaterSensor(sensorConfig)
    sensor.sensorPlaneLink = appearance.compoundModel.root
    sensor.speedLink = DataLinks.createFloatLink(appearance.filter, 'averageSpeed')
    sensor.onWaterSplash = appearance.onWaterSplash
    sensor.onUnderWaterSwitch = appearance.onUnderWaterSwitch
    sensor.setLodLink(lodStateLink)
    sensor.setLodSettings(shared_components.LodSettings(WATER_SENSOR_LOD_DIST, WATER_SENSOR_MAX_PRIORITY))
    return sensor


def assembleDetailedEngineState(compoundModel, vehicleFilter, typeDescriptor, isPlayerVehicle):
    PLAYER_UPDATE_PERIOD = 0.1
    NPC_UPDATE_PERIOD = 0.25
    engineState = Vehicular.DetailedEngineState()
    engineState.vehicleSpeedLink = DataLinks.createFloatLink(vehicleFilter, 'averageSpeed')
    engineState.rotationSpeedLink = DataLinks.createFloatLink(vehicleFilter, 'averageRotationSpeed')
    engineState.vehicleMatrixLink = compoundModel.root
    speed_limits_0 = typeDescriptor.physics['speedLimits'][0]
    speed_limits_1 = typeDescriptor.physics['speedLimits'][1]
    rpm_min = typeDescriptor.engine.rpm_min
    rpm_max = typeDescriptor.engine.rpm_max
    rotation_speed_limit = typeDescriptor.physics['rotationSpeedLimit']
    max_climb_angle = math.acos(typeDescriptor.physics['minPlaneNormalY'])
    engineState.setVehicleParams(speed_limits_0, speed_limits_1, rotation_speed_limit, max_climb_angle, rpm_min, rpm_max, isPlayerVehicle)
    if isPlayerVehicle:
        p = BigWorld.player()
        engineState.physicRPMLink = lambda : WoT.unpackAuxVehiclePhysicsData(p.ownVehicleAuxPhysicsData)[5]
        engineState.physicGearLink = lambda : BigWorld.player().ownVehicleGear
    else:
        engineState.physicRPMLink = None
        engineState.physicGearLink = None
    engineState.updatePeriod = PLAYER_UPDATE_PERIOD if isPlayerVehicle else NPC_UPDATE_PERIOD
    return engineState


def subscribeEngineAuditionToEngineState(engineAudition, engineState):
    engineState.onEngineStart = engineAudition.onEngineStart
    engineState.onStateChanged = engineAudition.onEngineStateChanged


def setupTracksFashion(vehicleDesc, fashion):
    tracksCfg = vehicleDesc.chassis.tracks
    fashion.setTracksLod(tracksCfg.lodDist)
    fashion.setTracksMaterials(tracksCfg.leftMaterial, tracksCfg.rightMaterial)


def __assembleSimpleTracks(vehicleDesc, fashion, wheelsAnimator, tracks):
    tracksCfg = vehicleDesc.chassis.tracks
    left = Vehicular.SimpleTrack(True, tracksCfg.leftMaterial, fashion, wheelsAnimator)
    right = Vehicular.SimpleTrack(False, tracksCfg.rightMaterial, fashion, wheelsAnimator)
    meterToTexScale = tracksCfg.textureScale
    left.meterToTexScale = meterToTexScale
    right.meterToTexScale = meterToTexScale
    lodSettings = LodSettings(_INFINITY, DEFAULT_MAX_LOD_PRIORITY)
    tracks.addTrackComponent(True, left, lodSettings)
    tracks.addTrackComponent(False, right, lodSettings)


def __assemblePhysicalTracks(resourceRefs, appearance, tracks, instantWarmup):
    inited = True
    leftTrack = resourceRefs['leftPhysicalTrack'] if resourceRefs.has_key('leftPhysicalTrack') else None
    rightTrack = resourceRefs['rightPhysicalTrack'] if resourceRefs.has_key('rightPhysicalTrack') else None
    if leftTrack is not None:
        leftTrack.init(appearance.compoundModel, appearance.wheelsAnimator, appearance.collisionObstaclesCollector, appearance.tessellationCollisionSensor, instantWarmup)
        if leftTrack.inited:
            appearance.fashion.setPhysicalTrack(leftTrack)
            tracks.addTrackComponent(True, leftTrack, _PHYSICAL_TRACKS_LOD_SETTINGS)
        else:
            inited = False
    else:
        inited = False
    if rightTrack is not None:
        rightTrack.init(appearance.compoundModel, appearance.wheelsAnimator, appearance.collisionObstaclesCollector, appearance.tessellationCollisionSensor, instantWarmup)
        if rightTrack.inited:
            appearance.fashion.setPhysicalTrack(rightTrack)
            tracks.addTrackComponent(False, rightTrack, _PHYSICAL_TRACKS_LOD_SETTINGS)
        else:
            inited = False
    else:
        inited = False
    return inited


def __assembleSplineTracks(vehicleDesc, appearance, splineTracksImpl, tracks):
    if splineTracksImpl is None:
        return
    else:
        lodDist = vehicleDesc.chassis.splineDesc.lodDist
        lodSettings = LodSettings(lodDist, _SPLINE_TRACKS_MAX_COUNT)
        if splineTracksImpl[0] is not None:
            leftSplineTrack = Vehicular.SplineTrack(splineTracksImpl[0], appearance.compoundModel)
            tracks.addTrackComponent(True, leftSplineTrack, lodSettings)
        if splineTracksImpl[1] is not None:
            rightSplineTrack = Vehicular.SplineTrack(splineTracksImpl[1], appearance.compoundModel)
            tracks.addTrackComponent(False, rightSplineTrack, lodSettings)
        return


def assembleTracks(resourceRefs, vehicleDesc, appearance, splineTracksImpl, instantWarmup, lodLink=None):
    tracks = Vehicular.VehicleTracks(appearance.compoundModel, TankPartIndexes.CHASSIS, _AREA_LOD_FOR_NONSIMPLE_TRACKS)
    appearance.tracks = tracks
    if not __assemblePhysicalTracks(resourceRefs, appearance, tracks, instantWarmup):
        __assembleSplineTracks(vehicleDesc, appearance, splineTracksImpl, tracks)
    __assembleSimpleTracks(vehicleDesc, appearance.fashion, appearance.wheelsAnimator, tracks)
    vehicleFilter = getattr(appearance, 'filter', None)
    if vehicleFilter is not None:
        tracks.leftTrack.setupScrollLink(DataLinks.createFloatLink(vehicleFilter, 'leftTrackScroll'))
        tracks.rightTrack.setupScrollLink(DataLinks.createFloatLink(vehicleFilter, 'rightTrackScroll'))
    if lodLink is None:
        lodLink = Vehicular.getDummyLodLink()
    tracks.setLodLink(lodLink)
    crashedTracksController = getattr(appearance, 'crashedTracksController', None)
    if crashedTracksController is not None:
        crashedTracksController.baseTracksComponent = tracks
    return


def assembleCollisionObstaclesCollector(appearance, lodStateLink):
    collisionObstaclesCollector = Vehicular.CollisionObstaclesCollector(appearance.compoundModel, BigWorld.player().spaceID)
    if lodStateLink is not None:
        collisionObstaclesCollector.setLodLink(lodStateLink)
        collisionObstaclesCollector.setLodSettings(shared_components.LodSettings(appearance.typeDescriptor.chassis.wheels.lodDist, DEFAULT_MAX_LOD_PRIORITY))
        groundNodesConfig = appearance.typeDescriptor.chassis.groundNodes
        groundNodeGroups = groundNodesConfig.groups
        groundNodes = groundNodesConfig.nodes
        hasGroundNodes = len(groundNodeGroups) or len(groundNodes)
        if not hasGroundNodes:
            collisionObstaclesCollector.disable()
    appearance.collisionObstaclesCollector = collisionObstaclesCollector
    return


def assembleTessellationCollisionSensor(appearance, lodStateLink):
    tessellationCollisionSensor = Vehicular.TessellationCollisionSensor(appearance.compoundModel, TankPartIndexes.CHASSIS)
    if lodStateLink is not None:
        tessellationCollisionSensor.setLodLink(lodStateLink)
        tessellationCollisionSensor.setLodSettings(shared_components.LodSettings(appearance.typeDescriptor.chassis.wheels.lodDist, DEFAULT_MAX_LOD_PRIORITY))
        groundNodesConfig = appearance.typeDescriptor.chassis.groundNodes
        groundNodeGroups = groundNodesConfig.groups
        groundNodes = groundNodesConfig.nodes
        hasGroundNodes = len(groundNodeGroups) or len(groundNodes)
        if not hasGroundNodes:
            tessellationCollisionSensor.disable()
    appearance.tessellationCollisionSensor = tessellationCollisionSensor
    return
