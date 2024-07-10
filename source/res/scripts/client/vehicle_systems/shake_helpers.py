# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/shake_helpers.py
import BigWorld
import Math
from aih_constants import ShakeReason
from vehicle_systems.tankStructure import TankNodeNames

def shakePlayerDynamicCamera(vehicle, shakeReason=ShakeReason.OWN_SHOT, gunFireNodeName='HP_gunFire'):
    appearance = vehicle.appearance
    if appearance is None or appearance.compoundModel is None:
        return
    else:
        gunFireNode = appearance.compoundModel.node(gunFireNodeName)
        gunNode = appearance.compoundModel.node(TankNodeNames.GUN_INCLINATION)
        if gunFireNode is None or gunNode is None:
            return
        BigWorld.player().inputHandler.onVehicleShaken(vehicle, shakeReason, Math.Matrix(gunFireNode).translation, Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1)), vehicle.typeDescriptor.shot.shell.caliber)
        return


def shakeVehicleModel(vehicle, percent=1.0):
    appearance = vehicle.appearance
    if appearance is None or appearance.compoundModel is None:
        return
    else:
        gunNode = appearance.compoundModel.node(TankNodeNames.GUN_INCLINATION)
        appearance.receiveShotImpulse(Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1)), appearance.typeDescriptor.gun.impulse * percent)
        return
