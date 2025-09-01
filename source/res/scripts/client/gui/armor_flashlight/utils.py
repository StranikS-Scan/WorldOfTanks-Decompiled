# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/armor_flashlight/utils.py
import typing
from items import vehicles
from vehicle_systems.tankStructure import TankPartNames
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
    from items.components.shared_components import MaterialInfo

def _convertMatInfo(matInfo):
    return (matInfo.kind,
     matInfo.armor if matInfo.armor is not None else 0.0,
     matInfo.vehicleDamageFactor,
     matInfo.useHitAngle | matInfo.mayRicochet << 1 | matInfo.collideOnceOnly << 2 | matInfo.checkCaliberForRicochet << 3 | matInfo.checkCaliberForHitAngleNorm << 4 | bool(matInfo.extra) << 5)


def getAllMatInfos(typeDescriptor):
    partDescriptors = {TankPartNames.CHASSIS: typeDescriptor.chassis,
     TankPartNames.HULL: typeDescriptor.hull,
     TankPartNames.TURRET: typeDescriptor.turret,
     TankPartNames.GUN: typeDescriptor.gun}
    materialsAll = {}
    for partName, partDesc in partDescriptors.items():
        materialList = [ _convertMatInfo(matInfo) for matInfo in partDesc.materials.itervalues() ]
        materialsAll[partName] = materialList

    if typeDescriptor.type.isWheeledVehicle:
        for key, matInfo in typeDescriptor.chassis.wheelsArmor.iteritems():
            materialsAll[key] = [_convertMatInfo(matInfo)]

    commonMaterials = [ _convertMatInfo(matInfo) for matInfo in vehicles.g_cache.commonConfig['materials'].itervalues() ]
    materialsAll['common'] = commonMaterials
    return materialsAll
