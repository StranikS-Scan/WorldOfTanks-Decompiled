# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/model_assembler.py
from AvatarInputHandler import mathUtils
import BigWorld
from VehicleUtils import VehicleDamageState
import constants
from vehicle_systems.tankStructure import getPartModelsFromDesc, getSkeleton, TankNodeNames, TankPartNames
MARK_NODES_POSTFIX = '_02'

def _addMarkTurret(assembler, turretModel, gunModel, skeleton):
    turretModel = turretModel.replace('01', '02')
    gunModel = gunModel.replace('01', '02')
    assembler.addPart(turretModel, 'HP_turretJoint_02', TankPartNames.TURRET, skeleton.turret, mathUtils.createIdentityMatrix())
    assembler.addPart(gunModel, TankNodeNames.GUN_JOINT, TankPartNames.GUN, skeleton.gun, mathUtils.createIdentityMatrix())
    renameNodes = [ x[0] for x in skeleton.turret ] + [TankPartNames.TURRET] + [ x[0] for x in skeleton.gun ] + [TankPartNames.GUN]
    for nodeName in renameNodes:
        assembler.renameNode(nodeName, nodeName + MARK_NODES_POSTFIX)


def prepareCompoundAssembler(vehicleDesc, modelStateName, spaceID, isTurretDetached=False):
    if constants.IS_DEVELOPMENT and modelStateName not in VehicleDamageState.MODEL_STATE_NAMES:
        raise Exception('Invalid modelStateName %s, must be in %s' % (modelStateName, VehicleDamageState.MODEL_STATE_NAMES))
    if spaceID is None:
        spaceID = BigWorld.player().spaceID
    partModels = getPartModelsFromDesc(vehicleDesc, modelStateName)
    chassis, hull, turret, gun = (partModels.chassis,
     partModels.hull,
     partModels.turret,
     partModels.gun)
    assembler = BigWorld.CompoundAssembler()
    skeleton = getSkeleton(vehicleDesc, modelStateName)
    assembler.addRootPart(chassis, TankPartNames.CHASSIS, skeleton.chassis, mathUtils.createIdentityMatrix())
    assembler.emplacePart(hull, 'V', TankPartNames.HULL, skeleton.hull)
    turretJointName = vehicleDesc.hull['turretHardPoints'][0]
    assembler.renameNode(turretJointName, TankNodeNames.TURRET_JOINT)
    if not isTurretDetached:
        if 'markI' in vehicleDesc.type.tags:
            _addMarkTurret(assembler, turret, gun, skeleton)
        assembler.addPart(turret, TankNodeNames.TURRET_JOINT, TankPartNames.TURRET, skeleton.turret, mathUtils.createIdentityMatrix())
        assembler.addPart(gun, TankNodeNames.GUN_JOINT, TankPartNames.GUN, skeleton.gun, mathUtils.createIdentityMatrix())
    cornerPoint = vehicleDesc.chassis['topRightCarryingPoint']
    assembler.addDummyNode(TankPartNames.CHASSIS, TankNodeNames.TRACK_LEFT_MID, mathUtils.createTranslationMatrix((-cornerPoint[0], 0, 0)))
    assembler.addDummyNode(TankPartNames.CHASSIS, TankNodeNames.TRACK_RIGHT_MID, mathUtils.createTranslationMatrix((cornerPoint[0], 0, 0)))
    assembler.addDummyNode(TankPartNames.CHASSIS, TankNodeNames.CHASSIS_MID_TRAIL)
    assembler.assemblerName = vehicleDesc.name
    assembler.spaceID = spaceID
    return assembler


def createGunAnimator(vehicleDesc, basisMatrix=None, lodLink=None):
    recoilDescr = vehicleDesc.gun['recoil']
    gunAnimator = BigWorld.RecoilAnimator(recoilDescr['backoffTime'], recoilDescr['returnTime'], recoilDescr['amplitude'], recoilDescr['lodDist'])
    if basisMatrix is not None:
        gunAnimator.basisMatrix = basisMatrix
    gunAnimator.lodLink = lodLink
    return gunAnimator


def createSwingingAnimator(vehicleDesc, basisMatrix=None, worldMProv=None, lodLink=None):
    swingingAnimator = BigWorld.SwingingAnimator()
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
