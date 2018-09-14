# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/tankStructure.py
import BigWorld
from collections import namedtuple

class ModelStates:
    UNDAMAGED = 'undamaged'
    DESTROYED = 'destroyed'
    EXPLODED = 'exploded'


class TankPartNames:
    CHASSIS = 'chassis'
    HULL = 'hull'
    TURRET = 'turret'
    GUN = 'gun'
    ALL = (CHASSIS,
     HULL,
     TURRET,
     GUN)

    @staticmethod
    def getIdx(name):
        for idx, n in enumerate(TankPartNames.ALL):
            if n == name:
                return idx

        raise Exception('Invalid part name!')


class VehiclePartsTuple(namedtuple('VehiclePartsTuple', TankPartNames.ALL + ('turret2', 'gun2'))):

    def __new__(cls, chassis, hull, turret, gun, turret2=None, gun2=None):
        return super(VehiclePartsTuple, cls).__new__(cls, chassis, hull, turret, gun, turret2, gun2)

    def stripEmpty(self):
        noneIdx = len(self) - 1
        while noneIdx > 0:
            if self[noneIdx] is not None:
                break
            noneIdx -= 1

        return self[0:noneIdx + 1]


class TankPartIndexes:
    CHASSIS = 0
    HULL = 1
    TURRET = 2
    GUN = 3
    ALL = (CHASSIS,
     HULL,
     TURRET,
     GUN)

    @staticmethod
    def getName(idx):
        return TankPartNames.ALL[idx]


class TankNodeNames:
    TRACK_LEFT_FRONT = 'HP_Track_LFront'
    TRACK_LEFT_REAR = 'HP_Track_LRear'
    TRACK_RIGHT_FRONT = 'HP_Track_RFront'
    TRACK_RIGHT_REAR = 'HP_Track_RRear'
    TRACK_LEFT_UP_FRONT = 'HP_TrackUp_LFront'
    TRACK_LEFT_UP_REAR = 'HP_TrackUp_LRear'
    TRACK_RIGHT_UP_FRONT = 'HP_TrackUp_RFront'
    TRACK_RIGHT_UP_REAR = 'HP_TrackUp_RRear'
    GUI = 'HP_gui'
    HULL_SWINGING = 'V'
    TURRET_JOINT = 'HP_turretJoint'
    HULL_FIRE_1 = 'HP_Fire_1'
    GUN_JOINT = 'HP_gunJoint'
    GUN_INCLINATION = 'Gun'
    TRACK_LEFT_MID = 'DM_Track_LMid'
    TRACK_RIGHT_MID = 'DM_Track_RMid'
    CHASSIS_MID_TRAIL = 'DM_Mid_Trail'


UNDAMAGED_SKELETON = VehiclePartsTuple(chassis=[('Tank', ''),
 (TankNodeNames.HULL_SWINGING, 'Tank'),
 (TankNodeNames.GUI, ''),
 (TankNodeNames.TRACK_LEFT_FRONT, ''),
 (TankNodeNames.TRACK_LEFT_REAR, ''),
 (TankNodeNames.TRACK_RIGHT_FRONT, ''),
 (TankNodeNames.TRACK_RIGHT_REAR, '')], hull=[('HP_Fire_1', ''),
 (TankNodeNames.TRACK_LEFT_UP_FRONT, ''),
 (TankNodeNames.TRACK_LEFT_UP_REAR, ''),
 (TankNodeNames.TRACK_RIGHT_UP_FRONT, ''),
 (TankNodeNames.TRACK_RIGHT_UP_REAR, '')], turret=[('HP_gunJoint', '')], gun=[('Gun', ''), ('G', 'Gun'), ('HP_gunFire', 'G')])
CRASHED_SKELETON = VehiclePartsTuple(chassis=[('Tank', ''), ('V', 'Tank'), ('HP_gui', '')], hull=[('HP_Fire_1', '')], turret=[('HP_gunJoint', '')], gun=[])
UNDAMAGED_SKELETON_WHEELED = VehiclePartsTuple(chassis=[('Tank', ''),
 (TankNodeNames.HULL_SWINGING, 'Tank'),
 (TankNodeNames.GUI, ''),
 (TankNodeNames.TRACK_LEFT_FRONT, ''),
 (TankNodeNames.TRACK_LEFT_REAR, ''),
 (TankNodeNames.TRACK_RIGHT_FRONT, ''),
 (TankNodeNames.TRACK_RIGHT_REAR, ''),
 (TankNodeNames.TRACK_LEFT_UP_FRONT, ''),
 (TankNodeNames.TRACK_LEFT_UP_REAR, ''),
 (TankNodeNames.TRACK_RIGHT_UP_FRONT, ''),
 (TankNodeNames.TRACK_RIGHT_UP_REAR, '')], hull=[('HP_Fire_1', ''), ('HP_Fire_2', '')], turret=[('HP_gunJoint', '')], gun=[('Gun', ''), ('G', 'Gun'), ('HP_gunFire', 'G')])

def getUndamagedSkeleton(vehicleDesc):
    exhaustNodes = getExhaustNodesFromDesc(vehicleDesc)
    exhaustNodes = [ (x, '') for x in exhaustNodes ]
    turretJointNode = (vehicleDesc.hull['turretHardPoints'][0], '')
    chassisSkeleton = None
    hullSkeleton = None
    if 'wheeledVehicle' in vehicleDesc.type.tags:
        chassisSkeleton = UNDAMAGED_SKELETON_WHEELED.chassis
        hullSkeleton = UNDAMAGED_SKELETON_WHEELED.hull
    else:
        chassisSkeleton = UNDAMAGED_SKELETON.chassis
        hullSkeleton = UNDAMAGED_SKELETON.hull
    result = VehiclePartsTuple(chassis=chassisSkeleton, hull=hullSkeleton + exhaustNodes + [turretJointNode], turret=UNDAMAGED_SKELETON.turret, gun=UNDAMAGED_SKELETON.gun)
    return result


def getCrashedSkeleton(vehicleDesc):
    turretJointNode = (vehicleDesc.hull['turretHardPoints'][0], '')
    turretJoints = [turretJointNode]
    if 'markI' in vehicleDesc.type.tags:
        turretJoints.append(('HP_turretJoint_02', ''))
    result = VehiclePartsTuple(chassis=CRASHED_SKELETON.chassis, hull=CRASHED_SKELETON.hull + turretJoints, turret=CRASHED_SKELETON.turret, gun=CRASHED_SKELETON.gun)
    return result


def getSkeleton(vehicleDesc, modelStateName):
    return getUndamagedSkeleton(vehicleDesc) if modelStateName == 'undamaged' else getCrashedSkeleton(vehicleDesc)


def getExhaustNodesFromDesc(vehicleDesc):
    vehicleExhaustDescriptor = vehicleDesc.hull['exhaust']
    return vehicleExhaustDescriptor.nodes


def getPartModelsFromDesc(vehicleDesc, modelStateName):
    return VehiclePartsTuple(vehicleDesc.chassis['models'][modelStateName], vehicleDesc.hull['models'][modelStateName], vehicleDesc.turret['models'][modelStateName], vehicleDesc.gun['models'][modelStateName])
