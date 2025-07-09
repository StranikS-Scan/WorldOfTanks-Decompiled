# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_variable_storage.py
import typing
import enum
import logging
import Math
from cgf_modules.variable_components import VariableStorageComponent
from constants import VEHICLE_CLASSES, VEHICLE_CLASS_INDICES
from vehicle_systems.tankStructure import TankPartIndexes
if typing.TYPE_CHECKING:
    import CGF
    from Vehicle import Vehicle
    from common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
    from items.vehicles import VehicleDescriptor
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


def createForRoot(vehicle):
    vehicle.entityGameObject.removeComponentByType(VariableStorageComponent)
    varStorage = vehicle.entityGameObject.createComponent(VariableStorageComponent)
    vehDescr = vehicle.typeDescriptor
    vehType = set(VEHICLE_CLASSES).intersection(vehDescr.type.tags).pop()
    vehTypeIdx = VEHICLE_CLASS_INDICES[vehType]
    varStorage.setVarVal(VehicleRootVars.TYPE.value, vehTypeIdx)
    varStorage.setVarVal(VehicleRootVars.MAX_HEALTH.value, vehicle.maxHealth)


def createForGun(appearance, gunGO):
    gunGO.removeComponentByType(VariableStorageComponent)
    storageComponent = gunGO.createComponent(VariableStorageComponent)
    shellDescr = appearance.typeDescriptor.shot.shell
    gunDescr = appearance.typeDescriptor.gun
    gunBB = Math.Matrix(appearance.compoundModel.getBoundsForPart(TankPartIndexes.GUN))
    gunLength = gunBB.applyVector(Math.Vector3(0.0, 0.0, 1.0)).length
    storageComponent.setVarVal(VehicleGunVars.MUZZLE_BRAKE.value, gunDescr.muzzleBrake.value)
    storageComponent.setVarVal(VehicleGunVars.GUN_LENGTH.value, gunLength)
    storageComponent.setVarVal(VehicleGunVars.GUN_CALIBER.value, shellDescr.caliber)


def update(go, varName, value):
    varStorage = go.findComponentByType(VariableStorageComponent)
    if not varStorage:
        _logger.error("Can't find variable storage for: %s", go.name)
        return
    varStorage.setVarVal(varName, value)
