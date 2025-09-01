# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/shake_helpers.py
import typing
import BigWorld
import Math
from aih_constants import ShakeReason
from vehicle_systems.tankStructure import TankNodeNames
if typing.TYPE_CHECKING:
    from items.components.gun_installation_components import GunInstallationSlot
    from Vehicle import Vehicle

def shakePlayerDynamicCamera(vehicle, gunInstallationSlot, shakeReason=ShakeReason.OWN_SHOT, gunNodeName=TankNodeNames.GUN_INCLINATION, gunFireNodeName='HP_gunFire'):
    appearance = vehicle.appearance
    if appearance is None or appearance.compoundModel is None:
        return
    else:
        gunNode = appearance.compoundModel.node(gunNodeName)
        gunFireNode = appearance.compoundModel.node(gunFireNodeName)
        if gunFireNode is None or gunNode is None:
            return
        BigWorld.player().inputHandler.onVehicleShaken(vehicle, shakeReason, Math.Matrix(gunFireNode).translation, Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1)), gunInstallationSlot.gun.effectsCaliber, withEvents=gunInstallationSlot.isMainInstallation())
        return


def shakeMultiGunPlayerDynamicCamera(vehicle, gunInstallationSlot, gunIndex, shakeReason=ShakeReason.OWN_SHOT):
    multiGun = gunInstallationSlot.gun.multiGun
    if multiGun is not None:
        0 <= gunIndex < len(multiGun) and shakePlayerDynamicCamera(vehicle, gunInstallationSlot, shakeReason, multiGun[gunIndex].node, multiGun[gunIndex].gunFire)
    else:
        shakePlayerDynamicCamera(vehicle, gunInstallationSlot, shakeReason)
    return


def shakeMultiGunsPlayerDynamicCamera(vehicle, gunInstallationSlot, gunIndexes, shakeReason=ShakeReason.OWN_SHOT):
    for gunIndex in gunIndexes:
        shakeMultiGunPlayerDynamicCamera(vehicle, gunInstallationSlot, gunIndex, shakeReason)
