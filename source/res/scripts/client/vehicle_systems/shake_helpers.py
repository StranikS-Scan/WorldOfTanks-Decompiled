# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/shake_helpers.py
import BigWorld
import Math
from aih_constants import ShakeReason
from vehicle_systems.tankStructure import TankNodeNames

def shakePlayerDynamicCamera(vehicle, shakeReason=ShakeReason.OWN_SHOT, gunNodeName=TankNodeNames.GUN_INCLINATION, gunFireNodeName='HP_gunFire'):
    appearance = vehicle.appearance
    if appearance is None or appearance.compoundModel is None:
        return
    else:
        gunNode = appearance.compoundModel.node(gunNodeName)
        gunFireNode = appearance.compoundModel.node(gunFireNodeName)
        if gunFireNode is None or gunNode is None:
            return
        BigWorld.player().inputHandler.onVehicleShaken(vehicle, shakeReason, Math.Matrix(gunFireNode).translation, Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1)), vehicle.typeDescriptor.shot.shell.caliber)
        return


def shakeMultiGunPlayerDynamicCamera(vehicle, multiGunInstance, shakeReason=ShakeReason.OWN_SHOT):
    shakePlayerDynamicCamera(vehicle, shakeReason, multiGunInstance.node, multiGunInstance.gunFire)
