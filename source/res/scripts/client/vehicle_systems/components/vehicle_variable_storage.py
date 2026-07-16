# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_variable_storage.py
import typing
import enum
import logging
import Math
import CGF
from cgf_modules.variable_components import VariableStorageComponent
from constants import VEHICLE_CLASSES, VEHICLE_CLASS_INDICES
from vehicle_systems.tankStructure import TankPartIndexes
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
    from vehicle_appearance.common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
    from items.vehicles import VehicleDescriptor
    from items.vehicle_items import Gun, Shell
    from cgf_modules.variable_components import VariableType
    TAppearance = typing.Union[HangarVehicleAppearance, CommonTankAppearance, None]
_logger = logging.getLogger(__name__)

class VehicleRootVars(enum.Enum):
    TYPE = 'vehicle/type'
    MAX_HEALTH = 'vehicle/maxHealth'


class VehicleGunVars(enum.Enum):
    MUZZLE_BRAKE = 'vehicle/gun/muzzleBrake'
    GUN_LENGTH = 'vehicle/gun/gunLength'
    GUN_CALIBER = 'vehicle/gun/caliber'
    TIME_BETWEEN_SHOTS = 'vehicle/gun/timeBetweenShots'


def createForRoot(vehicle, queue=None):
    vehicleObject = vehicle.entityGameObject
    queue = queue or CGF.CommandQueue(vehicleObject.spaceID)
    vehDescr = vehicle.typeDescriptor
    vehType = set(VEHICLE_CLASSES).intersection(vehDescr.type.tags).pop()
    vehTypeIdx = VEHICLE_CLASS_INDICES[vehType]
    vars = [(VehicleRootVars.TYPE.value, vehTypeIdx), (VehicleRootVars.MAX_HEALTH.value, vehicle.maxHealth)]
    queue.removeComponent(vehicleObject, VariableStorageComponent)
    queue.createComponent(vehicleObject, VariableStorageComponent, vars)


def createForGun(appearance, gunGO):
    queue = CGF.CommandQueue(gunGO.spaceID)
    shellDescr = appearance.typeDescriptor.shot.shell
    gunDescr = appearance.typeDescriptor.gun
    gunBB = Math.Matrix(appearance.compoundModel.getBoundsForPart(TankPartIndexes.GUN))
    gunLength = gunBB.applyVector(Math.Vector3(0.0, 0.0, 1.0)).length
    timeBetweenShots = gunDescr.clip[1] if 'clip' in gunDescr.tags else gunDescr.reloadTime
    vars = [(VehicleGunVars.MUZZLE_BRAKE.value, gunDescr.muzzleBrake.value),
     (VehicleGunVars.GUN_LENGTH.value, gunLength),
     (VehicleGunVars.GUN_CALIBER.value, shellDescr.caliber),
     (VehicleGunVars.TIME_BETWEEN_SHOTS.value, timeBetweenShots)]
    queue.removeComponent(gunGO, VariableStorageComponent)
    queue.createComponent(gunGO, VariableStorageComponent, vars)


def update(go, varName, value):
    varStorage = go.findWrite(VariableStorageComponent)
    if not varStorage:
        _logger.error("Can't find variable storage for: %s", go.name)
        return
    varStorage.modify(go, varName, value)
