# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/player_notifications/siege_mode/camera_shaker.py
import BigWorld
import Math
from constants import VEHICLE_SIEGE_STATE
from vehicle_systems.tankStructure import TankNodeNames

class SiegeModeCameraShaker(object):
    SIEGE_CAMERA_IMPULSE = 0.05

    @staticmethod
    def shake(_, newState, __):
        if newState not in VEHICLE_SIEGE_STATE.SWITCHING:
            return
        else:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is None:
                return
            nodeGunJoint = vehicle.model.node(TankNodeNames.GUN_JOINT)
            typeDescriptor = vehicle.typeDescriptor
            if typeDescriptor.hasAutoSiegeMode or typeDescriptor.isTwinGunVehicle or nodeGunJoint is None:
                return
            handler = BigWorld.player().inputHandler
            matrix = Math.Matrix(vehicle.model.matrix)
            impulseDir = -matrix.applyToAxis(2)
            impulsePosition = Math.Matrix(nodeGunJoint).translation
            handler.onSpecificImpulse(impulsePosition, impulseDir * SiegeModeCameraShaker.SIEGE_CAMERA_IMPULSE, 'sniper')
            return
