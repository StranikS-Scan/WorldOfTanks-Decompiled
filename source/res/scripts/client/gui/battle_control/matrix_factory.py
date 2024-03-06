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
        entity = BigWorld.entities.get(entityID)
        if entity:
            return entity.matrix
        return None
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


def makeVehicleTurretMatrixMP():
    matrixProvider = Math.WGCombinedMP()
    vehicleMatrix = BigWorld.player().consistentMatrices.attachedVehicleMatrix
    matrixProvider.translationSrc = vehicleMatrix
    localTransform = Math.MatrixProduct()
    localTransform.a = BigWorld.player().consistentMatrices.ownVehicleTurretMProv
    localTransform.b = vehicleMatrix
    matrixProvider.rotationSrc = localTransform
    return matrixProvider


def makeStrategicCameraMatrix():
    provider = Math.WGCombinedMP()
    handler = getInputHandler()
    aimMatrix = Math.Matrix()
    if handler is not None:
        aimingSystem = handler.ctrl.camera.aimingSystem
        if aimingSystem is not None:
            aimMatrix = handler.ctrl.camera.aimingSystem.aimMatrix
    relativeMatrix = Math.WGRelatedToTargetMP()
    relativeMatrix.source = BigWorld.camera().invViewMatrix
    relativeMatrix.target = aimMatrix
    cameraMatrix = Math.WGStrategicAreaViewMP()
    cameraMatrix.source = relativeMatrix
    cameraMatrix.baseScale = (1.0, 1.0)
    provider.translationSrc = aimMatrix
    provider.rotationSrc = cameraMatrix
    return provider


def makeDefaultCameraMatrix():
    return BigWorld.camera().invViewMatrix


def makePostmortemCameraMatrix():
    matrix = Math.WGCombinedMP()
    translationSrc = Math.WGTranslationOnlyMP()
    translationSrc.source = BigWorld.player().consistentMatrices.attachedVehicleMatrix
    matrix.translationSrc = translationSrc
    matrix.rotationSrc = BigWorld.camera().invViewMatrix
    return matrix


def makeAttachedVehicleMatrix():
    return BigWorld.player().consistentMatrices.attachedVehicleMatrix


def makeOwnVehicleMatrix():
    return BigWorld.player().consistentMatrices.ownVehicleMatrix
