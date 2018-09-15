# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/matrix_factory.py
import BigWorld
import Math
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui.battle_control.avatar_getter import getInputHandler
from gui.battle_control.battle_constants import VEHICLE_LOCATION

def makeVehicleEntityMP(vehicle):
    provider = Math.WGTranslationOnlyMP()
    provider.source = vehicle.matrix
    return provider


def makeVehicleEntityMPCopy(vehicle):
    provider = Math.WGTranslationOnlyMP()
    provider.source = Math.Matrix(vehicle.matrix)
    return provider


def makePositionMP(position):
    provider = Math.WGReplayAwaredSmoothTranslationOnlyMP()
    matrix = Math.Matrix()
    matrix.setTranslate(position)
    provider.source = matrix
    return provider


def getEntityMatrix(entityID):
    try:
        return BigWorld.entities[entityID].matrix
    except AttributeError:
        LOG_CURRENT_EXCEPTION()
        return None

    return None


def getVehicleMPAndLocation(vehicleID, positions):
    vehicle = BigWorld.entities.get(vehicleID)
    location = VEHICLE_LOCATION.UNDEFINED
    provider = None
    if vehicle is not None and vehicle.isStarted:
        provider = makeVehicleEntityMP(vehicle)
        location = VEHICLE_LOCATION.AOI
    elif vehicleID in positions:
        provider = makePositionMP(positions[vehicleID])
        location = VEHICLE_LOCATION.FAR
    return (provider, location)


def makeVehicleMPByLocation(vehicleID, location, positions):
    provider = None
    if location in (VEHICLE_LOCATION.AOI, VEHICLE_LOCATION.AOI_TO_FAR):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is not None and vehicle.isStarted:
            if location == VEHICLE_LOCATION.AOI_TO_FAR:
                provider = makeVehicleEntityMPCopy(vehicle)
            else:
                provider = makeVehicleEntityMP(vehicle)
        else:
            LOG_WARNING('Entity of vehicle is not found to given location', vehicleID, location)
    elif location == VEHICLE_LOCATION.FAR:
        if vehicleID in positions:
            provider = makePositionMP(positions[vehicleID])
        else:
            LOG_WARNING('Position of vehicle is not found in the arena.positions', vehicleID, location)
    return provider


def convertToLastSpottedVehicleMP(matrix):
    converted = Math.WGReplayAwaredSmoothTranslationOnlyMP()
    converted.source = Math.Matrix(matrix.source)
    return converted


def makeArcadeCameraMatrix():
    matrix = Math.WGCombinedMP()
    matrix.translationSrc = BigWorld.player().getOwnVehicleMatrix()
    matrix.rotationSrc = BigWorld.camera().invViewMatrix
    return matrix


def makeStrategicCameraMatrix():
    matrix = Math.WGStrategicAreaViewMP()
    matrix.source = BigWorld.camera().invViewMatrix
    matrix.baseScale = (1.0, 1.0)
    return matrix


def makeArtyAimPointMatrix():
    """Makes combined matrix where translation is position of aiming,
    rotation and scale is camera position.
    
    :return: instance of Math.WGCombinedMP
    """
    provider = Math.WGCombinedMP()
    rotationMatrix = Math.WGStrategicAreaViewMP()
    rotationMatrix.source = BigWorld.camera().invViewMatrix
    rotationMatrix.baseScale = (1.0, 1.0)
    handler = getInputHandler()
    if handler is not None:
        translationMatrix = handler.ctrl.camera.aimingSystem.aimMatrix
    else:
        translationMatrix = Math.Matrix()
    provider.translationSrc = translationMatrix
    provider.rotationSrc = rotationMatrix
    return provider


def makeDefaultCameraMatrix():
    return BigWorld.camera().invViewMatrix


def makePostmortemCameraMatrix():
    """Makes a camera matrix for postmortem mode, which position component is inferred from active vehicle and rotation
    component matches the 3D camera orientation. If the active vehicle changes (for example, during a view switch, the
    matrix is updated accordingly.
    """
    matrix = Math.WGCombinedMP()
    translationSrc = Math.WGTranslationOnlyMP()
    translationSrc.source = BigWorld.player().consistentMatrices.attachedVehicleMatrix
    matrix.translationSrc = translationSrc
    matrix.rotationSrc = BigWorld.camera().invViewMatrix
    return matrix


def makeAttachedVehicleMatrix():
    """Makes a matrix which is consistent with active vehicle, if the vehicle changes (for example, during a view
    switch), the matrix is updated accordingly.
    """
    return BigWorld.player().consistentMatrices.attachedVehicleMatrix


def makeOwnVehicleMatrix():
    """Makes a matrix which is consistent with player vehicle, even if the vehicle itself is destroyed.
    """
    return BigWorld.player().consistentMatrices.ownVehicleMatrix
