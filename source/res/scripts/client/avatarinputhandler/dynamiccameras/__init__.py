# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/__init__.py
import BigWorld
import Math
from Math import Vector3, Matrix
import math
from AvatarInputHandler import mathUtils
from AvatarInputHandler.Oscillator import Oscillator, NoiseOscillator, RandomNoiseOscillatorFlat, RandomNoiseOscillatorSpherical
from AvatarInputHandler.cameras import readVec3, readFloat, ImpulseReason

def createCrosshairMatrix(offsetFromNearPlane):
    nearPlane = BigWorld.projection().nearPlane
    return mathUtils.createTranslationMatrix(Vector3(0, 0, nearPlane + offsetFromNearPlane))


def createOscillatorFromSection(oscillatorSection, constraintsAsAngle = True):
    constraints = readVec3(oscillatorSection, 'constraints', (0.0, 0.0, 0.0), (175.0, 175.0, 175.0), 10.0)
    if constraintsAsAngle:
        constraints = Vector3((math.radians(constraints.x), math.radians(constraints.y), math.radians(constraints.z)))
    constructorParams = {'oscillator': __getOscillator3dParams,
     'noiseOscillator': __getOscillator3dParams,
     'randomNoiseOscillatorFlat': __getOscillator1dParams,
     'randomNoiseOscillatorSpherical': __getRandomNoiseOscillatorSphericalParams}.get(oscillatorSection.name, __getOscillator3dParams)(oscillatorSection)
    constructor = Oscillator
    if oscillatorSection.name == 'noiseOscillator':
        constructor = NoiseOscillator
    elif oscillatorSection.name == 'randomNoiseOscillatorFlat':
        constructor = RandomNoiseOscillatorFlat
    elif oscillatorSection.name == 'randomNoiseOscillatorSpherical':
        constructor = RandomNoiseOscillatorSpherical
    else:
        constructorParams['constraints'] = constraints
    oscillator = constructor(**constructorParams)
    return oscillator


def __getOscillator3dParams(oscillatorSection):
    return {'mass': readFloat(oscillatorSection, 'mass', 1e-05, 9000, 3.5),
     'stiffness': readVec3(oscillatorSection, 'stiffness', (1e-05, 1e-05, 1e-05), (9000, 9000, 9000), 60.0),
     'drag': readVec3(oscillatorSection, 'drag', (1e-05, 1e-05, 1e-05), (9000, 9000, 9000), 9.0)}


def __getOscillator1dParams(oscillatorSection):
    return {'mass': readFloat(oscillatorSection, 'mass', 1e-05, 9000, 3.5),
     'stiffness': readFloat(oscillatorSection, 'stiffness', 1e-05, 9000, 3.5),
     'drag': readFloat(oscillatorSection, 'drag', 1e-05, 9000, 3.5)}


def __getRandomNoiseOscillatorSphericalParams(oscillatorSection):
    oscillatorParams = __getOscillator1dParams(oscillatorSection)
    oscillatorParams['scaleCoeff'] = readVec3(oscillatorSection, 'scaleCoeff', Vector3(0.0), Vector3(9000), Vector3(1.0))
    return oscillatorParams


class CameraDynamicConfig(dict):
    REASONS_AS_STR = {ImpulseReason.MY_SHOT: 'shot',
     ImpulseReason.ME_HIT: 'hit',
     ImpulseReason.OTHER_SHOT: 'otherShot',
     ImpulseReason.SPLASH: 'splash',
     ImpulseReason.COLLISION: 'collision',
     ImpulseReason.VEHICLE_EXPLOSION: 'vehicleExplosion',
     ImpulseReason.PROJECTILE_HIT: 'projectileHit',
     ImpulseReason.HE_EXPLOSION: 'vehicleExplosion'}

    def readImpulsesConfig(self, rootDataSec):
        self.__readReasonProjection('impulseSensitivities', rootDataSec)
        self.__readReasonProjection('noiseSensitivities', rootDataSec)
        self.__readReasonProjection('impulseLimits', rootDataSec, True)
        self.__readReasonProjection('noiseLimits', rootDataSec, True)

    def __readReasonProjection(self, projectionName, rootDataSec, asMinMax = False):
        self[projectionName] = impulseDict = {}
        projectionDataSec = rootDataSec[projectionName]
        if projectionDataSec is None:
            return
        else:
            for reason, reasonStr in CameraDynamicConfig.REASONS_AS_STR.iteritems():
                reasonLimitSec = projectionDataSec[reasonStr]
                if reasonLimitSec is not None:
                    if asMinMax:
                        impulseDict[reason] = reasonLimitSec.asVector2
                    else:
                        impulseDict[reason] = reasonLimitSec.asFloat

            return

    def adjustImpulse(self, impulse, reason):
        impulseSensitivity = self['impulseSensitivities'].get(reason, 0.0)
        noiseImpulseSensitivity = self['noiseSensitivities'].get(reason, 0.0)
        resultImpulse = impulse * impulseSensitivity
        impulseMinMax = self['impulseLimits'].get(reason, None)
        if impulseMinMax is not None:
            resultImpulse = mathUtils.clampVectorLength(impulseMinMax[0], impulseMinMax[1], resultImpulse)
        noiseMagnitude = impulse.length * noiseImpulseSensitivity
        noiseMinMax = self['noiseLimits'].get(reason, None)
        if noiseMinMax is not None:
            noiseMagnitude = mathUtils.clamp(noiseMinMax[0], noiseMinMax[1], noiseMagnitude)
        return (resultImpulse, noiseMagnitude)


class AccelerationSmoother(object):

    def __setMaxAllowedAcc(self, value):
        self.__accelerationFilter.maxLength = value

    acceleration = property(lambda self: self.__acceleration)
    maxAllowedAcceleration = property(lambda self: self.__accelerationFilter.maxLength, __setMaxAllowedAcc)
    hasChangedDirection = property(lambda self: self.__hasChangedDirection)
    timeLapsed = property(lambda self: self.__timeLapsedSinceDirChange)

    def __init__(self, accelerationFilter, maxAccelerationDuration):
        self.__accelerationFilter = accelerationFilter
        self.__acceleration = Vector3(0)
        self.__prevMovementFlags = 0
        self.__prevVelocity = Vector3(0)
        self.__hasChangedDirection = False
        self.__maxAccelerationDuration = maxAccelerationDuration
        self.__timeLapsedSinceDirChange = 0.0

    def reset(self):
        self.__accelerationFilter.reset()
        self.__acceleration = Vector3(0)
        self.__prevMovementFlags = 0
        self.__hasChangedDirection = False

    def update(self, vehicle, deltaTime):
        curVelocity = vehicle.filter.velocity
        acceleration = vehicle.filter.acceleration
        acceleration = self.__accelerationFilter.add(acceleration)
        movementFlags = vehicle.engineMode[1]
        moveMask = 3
        self.__hasChangedDirection = movementFlags & moveMask ^ self.__prevMovementFlags & moveMask or curVelocity.dot(self.__prevVelocity) <= 0.01
        self.__prevMovementFlags = movementFlags
        self.__prevVelocity = curVelocity
        self.__timeLapsedSinceDirChange += deltaTime
        if self.__hasChangedDirection:
            self.__timeLapsedSinceDirChange = 0.0
        elif self.__timeLapsedSinceDirChange > self.__maxAccelerationDuration:
            invVehMat = Matrix(vehicle.matrix)
            invVehMat.invert()
            accelerationRelativeToVehicle = invVehMat.applyVector(acceleration)
            accelerationRelativeToVehicle.x = 0.0
            accelerationRelativeToVehicle.z = 0.0
            acceleration = Matrix(vehicle.matrix).applyVector(accelerationRelativeToVehicle)
        self.__acceleration = acceleration
        return acceleration
