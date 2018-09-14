# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/model_assembler.py
from AvatarInputHandler import mathUtils
import BigWorld
from CustomEffectManager import CustomEffectManager
from VehicleAppearance import VehicleDamageState
import constants
from helpers import gEffectsDisabled
from vehicle_systems.tankStructure import getPartModelsFromDesc, getSkeleton, TankNodeNames, TankPartNames
import Vehicular
import WWISE
from vehicle_systems.components.siegeEffectsController import SiegeEffectsController
from vehicle_systems.components.suspension_controller import SuspensionController

def prepareCompoundAssembler(vehicleDesc, modelStateName, spaceID, isTurretDetached=False):
    if constants.IS_DEVELOPMENT and modelStateName not in VehicleDamageState.MODEL_STATE_NAMES:
        raise Exception('Invalid modelStateName %s, must be in %s' % (modelStateName, VehicleDamageState.MODEL_STATE_NAMES))
    if spaceID is None:
        spaceID = BigWorld.player().spaceID
    partModels = getPartModelsFromDesc(vehicleDesc, modelStateName)
    chassis, hull, turret, gun = partModels
    assembler = BigWorld.CompoundAssembler()
    assembler.addRootPart(chassis, TankPartNames.CHASSIS)
    assembler.emplacePart(hull, 'V', TankPartNames.HULL)
    turretJointName = vehicleDesc.hull['turretHardPoints'][0]
    assembler.addNodeAlias(turretJointName, TankNodeNames.TURRET_JOINT)
    if not isTurretDetached:
        assembler.addPart(turret, turretJointName, TankPartNames.TURRET)
        assembler.addPart(gun, TankNodeNames.GUN_JOINT, TankPartNames.GUN)
    cornerPoint = vehicleDesc.chassis['topRightCarryingPoint']
    assembler.addNode(TankNodeNames.TRACK_LEFT_MID, TankPartNames.CHASSIS, mathUtils.createTranslationMatrix((-cornerPoint[0], 0, 0)))
    assembler.addNode(TankNodeNames.TRACK_RIGHT_MID, TankPartNames.CHASSIS, mathUtils.createTranslationMatrix((cornerPoint[0], 0, 0)))
    assembler.addNode(TankNodeNames.CHASSIS_MID_TRAIL, TankPartNames.CHASSIS)
    assembler.assemblerName = vehicleDesc.name
    assembler.spaceID = spaceID
    return assembler


def createGunAnimator(vehicleDesc, basisMatrix=None, lodLink=None):
    recoilDescr = vehicleDesc.gun['recoil']
    gunAnimator = Vehicular.RecoilAnimator(recoilDescr['backoffTime'], recoilDescr['returnTime'], recoilDescr['amplitude'], recoilDescr['lodDist'])
    if basisMatrix is not None:
        gunAnimator.basisMatrix = basisMatrix
    gunAnimator.lodLink = lodLink
    return gunAnimator


def createSwingingAnimator(vehicleDesc, basisMatrix=None, worldMProv=None, lodLink=None):
    swingingAnimator = Vehicular.SwingingAnimator()
    swingingAnimator.basisMatrix = basisMatrix
    swingingCfg = vehicleDesc.hull['swinging']
    pp = tuple((p * m for p, m in zip(swingingCfg['pitchParams'], (0.9, 1.88, 0.3, 4.0, 1.0, 1.0))))
    swingingAnimator.setupPitchSwinging(*pp)
    swingingAnimator.setupRollSwinging(*swingingCfg['rollParams'])
    swingingAnimator.setupShotSwinging(swingingCfg['sensitivityToImpulse'])
    swingingAnimator.maxMovementSpeed = vehicleDesc.physics['speedLimits'][0]
    swingingAnimator.lodSetting = swingingCfg['lodDist']
    swingingAnimator.worldMatrix = worldMProv if worldMProv is not None else mathUtils.createIdentityMatrix()
    swingingAnimator.lodLink = lodLink
    return swingingAnimator


def createLeveredSuspension(compoundModel, vehicleDescriptor, lodStateLink):
    leveredSuspensionConfig = vehicleDescriptor.chassis['leveredSuspension']
    if leveredSuspensionConfig is None:
        return
    else:
        leveredSuspension = Vehicular.LeveredSuspension(compoundModel, leveredSuspensionConfig.levers, leveredSuspensionConfig.interpolationSpeedMul)
        leveredSuspension.setupLodLink(lodStateLink)
        leveredSuspension.setupLodSettings(leveredSuspensionConfig.lodSettings)
        return leveredSuspension


def assembleLeveredSuspensionIfNeed(appearance, lodStateLink):
    appearance.leveredSuspension = createLeveredSuspension(appearance.compoundModel, appearance.typeDescriptor, lodStateLink)


def assembleRecoil(appearance, lodLink):
    gunAnimatorNode = appearance.compoundModel.node(TankNodeNames.GUN_RECOIL)
    localGunMatrix = gunAnimatorNode.localMatrix
    appearance.gunRecoil = gunRecoil = createGunAnimator(appearance.typeDescriptor, localGunMatrix, lodLink)
    gunRecoilMProv = gunRecoil.animatedMProv
    appearance.compoundModel.node(TankNodeNames.GUN_RECOIL, gunRecoilMProv)
    appearance.fashions.gun.inclinationMatrix = appearance.gunMatrix
    appearance.fashions.gun.gunLocalMatrix = gunRecoilMProv


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
        suspensionSoundParams = siegeVehicleDescr.chassis.get('hullAimingSound', None)
        if suspensionSoundParams is None:
            return
        sounds = suspensionSoundParams['sounds']
        lodDist = suspensionSoundParams['lodDist']
        if sounds is None or lodDist is None:
            return
        model = appearance.compoundModel
        if model is None:
            return
        hullNode = model.node(TankPartNames.HULL)
        if hullNode is None:
            return
        suspensionSound = Vehicular.SuspensionSound(appearance.id)
        for sound in sounds:
            if isPlayer:
                suspensionSound.setSoundsForState(sound.state, sound.PC)
            suspensionSound.setSoundsForState(sound.state, sound.NPC)

        suspensionSound.bodyMatrix = None
        suspensionSound.lodLink = lodLink
        suspensionSound.lodSetting = lodDist
        appearance.suspensionSound = suspensionSound
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
    vehicleFilter.hullLocalPosition = typeDescriptor.chassis['hullPosition']
    vehicleFilter.vehicleWidth = typeDescriptor.chassis['topRightCarryingPoint'][0] * 2
    vehicleFilter.maxMove = typeDescriptor.physics['speedLimits'][0] * 2.0
    vehicleFilter.vehicleMinNormalY = typeDescriptor.physics['minPlaneNormalY']
    for p1, p2, p3 in typeDescriptor.physics['carryingTriangles']:
        vehicleFilter.addTriangle((p1[0], 0, p1[1]), (p2[0], 0, p2[1]), (p3[0], 0, p3[1]))

    vehicleFilter.forceGroundPlacingMatrix(typeDescriptor.isPitchHullAimingAvailable)
    return vehicleFilter
