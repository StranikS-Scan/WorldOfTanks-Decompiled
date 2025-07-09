# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/gun_info.py
import typing
import Vehicular
from vehicle_systems.vehicle_composition import VehicleSlots
if typing.TYPE_CHECKING:
    import CGF
    from items import vehicle_items
    from common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
    TAppearance = typing.Union[HangarVehicleAppearance, CommonTankAppearance, None]

def createGunInfo(gunGO, turretDescr, gunDescr):
    prefab = gunDescr.prefabEffects.prefab if gunDescr.prefabEffects is not None else ''
    if turretDescr.multiGun:
        gunFireSlots = [ gunData.gunFire for gunData in turretDescr.multiGun ]
        shotPrefabs = [ prefab for _ in turretDescr.multiGun ]
    else:
        gunFireSlots = [VehicleSlots.GUN_FIRE.value]
        shotPrefabs = [prefab]
    gunGO.removeComponentByType(Vehicular.GunEffectsInfoComponent)
    gunGO.createComponent(Vehicular.GunEffectsInfoComponent, gunFireSlots, shotPrefabs)
    return
