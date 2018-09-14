# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/model_assembler.py
from AvatarInputHandler import mathUtils
import BigWorld
from VehicleAppearance import VehicleDamageState
import VehicleEffects
import constants
from vehicle_systems.tankStructure import getPartModelsFromDesc, getSkeleton, TankNodeNames, TankPartNames

def prepareCompoundAssembler(vehicleDesc, modelStateName, spaceID, isTurretDetached=False):
    if constants.IS_DEVELOPMENT and modelStateName not in VehicleDamageState.MODEL_STATE_NAMES:
        raise Exception('Invalid modelStateName %s, must be in %s' % (modelStateName, VehicleDamageState.MODEL_STATE_NAMES))
    if spaceID is None:
        spaceID = BigWorld.player().spaceID
    partModels = getPartModelsFromDesc(vehicleDesc, modelStateName)
    chassis, hull, turret, gun = partModels
    assembler = BigWorld.CompoundAssembler()
    skeleton = getSkeleton(vehicleDesc, modelStateName)
    assembler.addRootPart(chassis, TankPartNames.CHASSIS, skeleton.chassis, mathUtils.createIdentityMatrix())
    assembler.emplacePart(hull, 'V', TankPartNames.HULL, skeleton.hull)
    turretJointName = vehicleDesc.hull['turretHardPoints'][0]
    assembler.renameNode(turretJointName, TankNodeNames.TURRET_JOINT)
    if not isTurretDetached:
        assembler.addPart(turret, TankNodeNames.TURRET_JOINT, TankPartNames.TURRET, skeleton.turret, mathUtils.createIdentityMatrix())
        assembler.addPart(gun, TankNodeNames.GUN_JOINT, TankPartNames.GUN, skeleton.gun, mathUtils.createIdentityMatrix())
    cornerPoint = vehicleDesc.chassis['topRightCarryingPoint']
    assembler.addDummyNode(TankPartNames.CHASSIS, TankNodeNames.TRACK_LEFT_MID, mathUtils.createTranslationMatrix((-cornerPoint[0], 0, 0)))
    assembler.addDummyNode(TankPartNames.CHASSIS, TankNodeNames.TRACK_RIGHT_MID, mathUtils.createTranslationMatrix((cornerPoint[0], 0, 0)))
    assembler.addDummyNode(TankPartNames.CHASSIS, TankNodeNames.CHASSIS_MID_TRAIL)
    assembler.assemblerName = vehicleDesc.name
    assembler.spaceID = spaceID
    return assembler


def createGunAnimator(vehicleDesc, basisMatrix=None):
    recoilDescr = vehicleDesc.gun['recoil']
    gunAnimator = BigWorld.RecoilAnimator(recoilDescr['backoffTime'], recoilDescr['returnTime'], recoilDescr['amplitude'], recoilDescr['lodDist'])
    if basisMatrix is not None:
        gunAnimator.basisMatrix = basisMatrix
    return gunAnimator


def createSwingingAnimator(vehicleDesc, basisMatrix=None, worldMProv=None):
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
    return swingingAnimator
