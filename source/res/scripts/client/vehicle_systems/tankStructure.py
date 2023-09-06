# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/tankStructure.py
from collections import namedtuple

class CgfTankNodes(object):
    TANK_ROOT = 'Tank.Root'


class ModelStates(object):
    UNDAMAGED = 'undamaged'
    DESTROYED = 'destroyed'
    EXPLODED = 'exploded'


ModelsSetParams = namedtuple('ModelsSetParams', ('skin', 'state', 'attachments'))

class TankRenderMode(object):
    NORMAL = 0
    CRASH = 1
    SERVER_COLLISION = 2
    CLIENT_COLLISION = 3
    CRASH_COLLISION = 4
    OVERLAY_COLLISION = 5
    ARMOR_WIDTH_COLLISION = 6
    DISABLE = 7


class TankCollisionPartNames(object):
    CHASSIS = 'chassisCollision'
    HULL = 'hullCollision'
    TURRET = 'turretCollision'
    GUN = 'gunCollision'
    WHEEL = 'wheelCollision'
    ALL = (CHASSIS,
     HULL,
     TURRET,
     GUN)

    @staticmethod
    def getIdx(name):
        for idx, n in enumerate(TankCollisionPartNames.ALL):
            if n == name:
                return idx

        return None


class TankPartNames(object):
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

        return None


class DetachedTurretPartNames(object):
    ALL = (TankPartNames.TURRET, TankPartNames.GUN)

    @staticmethod
    def getIdx(name):
        for idx, n in enumerate(DetachedTurretPartNames.ALL):
            if n == name:
                return idx

        return None


class DetachedTurretPartIndexes(object):
    TURRET = 0
    GUN = 1
    ALL = (TURRET, GUN)

    @staticmethod
    def getName(idx):
        return DetachedTurretPartNames.ALL[idx]


VehiclePartsTuple = namedtuple('VehiclePartsTuple', TankPartNames.ALL)

class TankPartIndexes(object):
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
        return TankPartNames.ALL[idx] if idx < len(TankPartNames.ALL) else None


class TankNodeNames(object):
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
    GUN_RECOIL = 'G'
    TRACK_LEFT_MID = 'DM_Track_LMid'
    TRACK_RIGHT_MID = 'DM_Track_RMid'
    CHASSIS_MID_TRAIL = 'DM_Mid_Trail'


class TankSoundObjectsIndexes(object):
    CHASSIS = 0
    ENGINE = 1
    GUN = 2
    HIT = 3
    COUNT = 4


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
 (TankNodeNames.TRACK_RIGHT_UP_REAR, '')], turret=[('HP_gunJoint', '')], gun=[(TankNodeNames.GUN_INCLINATION, ''), (TankNodeNames.GUN_RECOIL, TankNodeNames.GUN_INCLINATION), ('HP_gunFire', TankNodeNames.GUN_RECOIL)])
CRASHED_SKELETON = VehiclePartsTuple(chassis=[('Tank', ''), ('V', 'Tank'), ('HP_gui', '')], hull=[('HP_Fire_1', '')], turret=[('HP_gunJoint', '')], gun=[])

class ColliderTypes(object):
    DYNAMIC_FLAG = 1
    TANK_FLAG = 2
    HANGAR_FLAG = 4
    PLAYER_FLAG = 8
    DYNAMIC_COLLIDER = DYNAMIC_FLAG
    VEHICLE_COLLIDER = DYNAMIC_FLAG | TANK_FLAG
    PLATOON_VEHICLE_COLLIDER = TANK_FLAG | HANGAR_FLAG
    PLAYER_VEHICLE_COLLIDER = DYNAMIC_FLAG | TANK_FLAG | PLAYER_FLAG
    HANGAR_VEHICLE_COLLIDER = DYNAMIC_FLAG | TANK_FLAG | HANGAR_FLAG
    HANGAR_PLAYER_VEHICLE_COLLIDER = DYNAMIC_FLAG | TANK_FLAG | HANGAR_FLAG | PLAYER_FLAG


def getCrashedSkeleton(vehicleDesc):
    turretJointNode = (vehicleDesc.hull.turretHardPoints[0], '')
    result = VehiclePartsTuple(chassis=CRASHED_SKELETON.chassis, hull=CRASHED_SKELETON.hull + [turretJointNode], turret=CRASHED_SKELETON.turret, gun=CRASHED_SKELETON.gun)
    return result


def getPartModelsFromDesc(vehicleDesc, modelsSetParams):
    skinName = modelsSetParams.skin
    paths = []
    for partName in TankPartNames.ALL:
        part = getattr(vehicleDesc, partName)
        if skinName in part.modelsSets:
            skin = part.modelsSets[skinName]
        else:
            skin = part.models
        path = skin.getPathByStateName(modelsSetParams.state)
        paths.append(path)

    return VehiclePartsTuple(*paths)


def getCollisionModelsFromDesc(vehicleDesc, state):
    paths = []
    for partName in TankPartNames.ALL:
        part = getattr(vehicleDesc, partName)
        if state == TankRenderMode.CLIENT_COLLISION:
            paths.append(part.hitTesterManager.edClientBspModel)
        if state in (TankRenderMode.SERVER_COLLISION, TankRenderMode.ARMOR_WIDTH_COLLISION):
            paths.append(part.hitTesterManager.edServerBspModel)
        if state == TankRenderMode.CRASH_COLLISION:
            if part.hitTesterManager.edCrashBspModel != '':
                paths.append(part.hitTesterManager.edCrashBspModel)
            else:
                paths.append(part.hitTesterManager.edClientBspModel)

    return VehiclePartsTuple(*paths)
