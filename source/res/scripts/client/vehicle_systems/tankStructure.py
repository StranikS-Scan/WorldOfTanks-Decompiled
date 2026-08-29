# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/tankStructure.py
import typing
import logging
import Math
from collections import namedtuple
from constants import VehiclePartName
if typing.TYPE_CHECKING:
    from BigWorld import CollisionComponent
    from typing import Union, Iterable, Sized, Optional
    AABB = typing.Tuple[Math.Vector3, Math.Vector3]
_logger = logging.getLogger(__name__)

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
    CHASSIS = VehiclePartName.CHASSIS
    HULL = VehiclePartName.HULL
    TURRET = VehiclePartName.TURRET
    GUN = VehiclePartName.GUN
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

    @staticmethod
    def getActualNodeNameByPartName(partName, isAlive=True):
        return TankNodeNames.GUN_INCLINATION if isAlive and partName == TankPartNames.GUN else partName


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
        return TankPartNames.ALL[idx] if 0 <= idx < len(TankPartNames.ALL) else None


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
    GUN_RECOIL_L = 'G_L'
    GUN_RECOIL_R = 'G_R'
    GUN_FIRE = 'HP_gunFire'
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


def getVehicleAABB(collisions):
    enclosingAABB = (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0))
    for index in TankPartIndexes.ALL:
        aabb = collisions.getBoundingBox(index)
        enclosingAABB[0].x = min(enclosingAABB[0].x, aabb[0].x)
        enclosingAABB[0].y = min(enclosingAABB[0].y, aabb[0].y)
        enclosingAABB[0].z = min(enclosingAABB[0].z, aabb[0].z)
        enclosingAABB[1].x = max(enclosingAABB[1].x, aabb[1].x)
        enclosingAABB[1].y = max(enclosingAABB[1].y, aabb[1].y)
        enclosingAABB[1].z = max(enclosingAABB[1].z, aabb[1].z)

    return enclosingAABB


def selectItemByTankSize(tankSizeLowerBounds, items, default=None, aabb=None):
    if not tankSizeLowerBounds:
        _logger.error('tankSizeLowerBounds cannot be empty or None.')
    if not items:
        _logger.error('items cannot be empty or None.')
    if not aabb:
        if default:
            return default
        return items[-1]
    maxDimension = max(abs(aabb[1].x - aabb[0].x), abs(aabb[1].y - aabb[0].y), abs(aabb[1].z - aabb[0].z))
    if len(tankSizeLowerBounds) != len(items):
        _logger.error('tankSizeLowerBounds (%r) and items (%r) have to be equally sized.', tankSizeLowerBounds, items)
    sizesWithItems = list(zip(tankSizeLowerBounds, items))
    sizesWithItems.sort(key=lambda sizeWithItem: sizeWithItem[0])
    largestPassingItem = sizesWithItems[0][1]
    for tankSizeLowerBound, item in sizesWithItems:
        if maxDimension < tankSizeLowerBound:
            break
        largestPassingItem = item

    return largestPassingItem
