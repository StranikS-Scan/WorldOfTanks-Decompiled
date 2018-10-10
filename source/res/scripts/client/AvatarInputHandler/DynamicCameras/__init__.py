# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/__init__.py
import math
from collections import namedtuple
import BigWorld
import Math
from Math import Vector3, Matrix
from AvatarInputHandler import mathUtils
from AvatarInputHandler.cameras import readVec3, readFloat, ImpulseReason
from helpers.CallbackDelayer import TimeDeltaMeter

def createCrosshairMatrix(offsetFromNearPlane):
    nearPlane = BigWorld.projection().nearPlane
    return mathUtils.createTranslationMatrix(Vector3(0, 0, nearPlane + offsetFromNearPlane))


def createOscillatorFromSection(oscillatorSection, constraintsAsAngle=True):
    constraints = readVec3(oscillatorSection, 'constraints', (0.0, 0.0, 0.0), (175.0, 175.0, 175.0), 10.0)
    if constraintsAsAngle:
        constraints = Vector3((math.radians(constraints.x), math.radians(constraints.y), math.radians(constraints.z)))
    constructorParams = {'oscillator': __getOscillatorParams,
     'noiseOscillator': __getNoiseOscillatorParams,
     'randomNoiseOscillatorFlat': __getRandomNoiseOscillatorFlatParams,
     'randomNoiseOscillatorSpherical': __getRandomNoiseOscillatorSphericalParams}.get(oscillatorSection.name, __getOscillatorParams)(oscillatorSection)
    oscillator = None
    if oscillatorSection.name == 'noiseOscillator':
        oscillator = Math.PyNoiseOscillator(*constructorParams)
    elif oscillatorSection.name == 'randomNoiseOscillatorFlat':
        oscillator = Math.PyRandomNoiseOscillatorFlat(*constructorParams)
    elif oscillatorSection.name == 'randomNoiseOscillatorSpherical':
        oscillator = Math.PyRandomNoiseOscillatorSpherical(*constructorParams)
    else:
        constructorParams.append(constraints)
        oscillator = Math.PyOscillator(*constructorParams)
    return oscillator


def __getOscillatorParams(oscillatorSection):
    return [readFloat(oscillatorSection, 'mass', 1e-05, 9000, 3.5), readVec3(oscillatorSection, 'stiffness', (1e-05, 1e-05, 1e-05), (9000, 9000, 9000), 60.0), readVec3(oscillatorSection, 'drag', (1e-05, 1e-05, 1e-05), (9000, 9000, 9000), 9.0)]


def __getNoiseOscillatorParams(oscillatorSection):
    return [readFloat(oscillatorSection, 'mass', 1e-05, 9000, 3.5), readVec3(oscillatorSection, 'stiffness', (1e-05, 1e-05, 1e-05), (9000, 9000, 9000), 60.0), readVec3(oscillatorSection, 'drag', (1e-05, 1e-05, 1e-05), (9000, 9000, 9000), 9.0)]


def __getRandomNoiseOscillatorFlatParams(oscillatorSection):
    return [readFloat(oscillatorSection, 'mass', 1e-05, 9000, 3.5), readFloat(oscillatorSection, 'stiffness', 1e-05, 9000, 3.5), readFloat(oscillatorSection, 'drag', 1e-05, 9000, 3.5)]


def __getRandomNoiseOscillatorSphericalParams(oscillatorSection):
    oscillatorParams = __getRandomNoiseOscillatorFlatParams(oscillatorSection)
    oscillatorParams.append(readVec3(oscillatorSection, 'scaleCoeff', Vector3(0.0), Vector3(9000), Vector3(1.0)))
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

    def __readReasonProjection(self, projectionName, rootDataSec, asMinMax=False):
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
        try:
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
        except Exception:
            return Math.Vector3(0.0, 0.0, 0.0)


class DynamicCameraInterpolator(TimeDeltaMeter):
    DataProvider = namedtuple('CameraTransitionDataProvider', ['start',
     'end',
     'interpolate',
     'set'])
    isInitialized = property(lambda self: self.__initialized)
    active = property(lambda self: self.__active)
    progress = property(lambda self: 0.0 if self.__interpolationState is not None else self.__interpolationState.time)

    def __init__(self):
        TimeDeltaMeter.__init__(self)
        self.__initialized = False
        self.__active = False
        self.__interpolationState = None
        self.__duration = None
        self.__numItems = None
        self.__startValueGetters = None
        self.__endValueGetters = None
        self.__customInterpolatorFuncs = None
        self.__setters = None
        self.__interpolatedValues = None
        return

    def setup(self, duration, dataProviders):
        self.__active = False
        self.__duration = duration
        self.__interpolationState = mathUtils.Easing.squareEasingInOut(0.0, 1.0, duration)
        self.__numItems = len(dataProviders)
        self.__interpolatedValues = [ None for _ in range(self.__numItems) ]
        self.__startValueGetters = []
        self.__endValueGetters = []
        self.__customInterpolatorFuncs = []
        self.__setters = []
        memberToListMap = {'start': self.__startValueGetters,
         'end': self.__endValueGetters,
         'interpolate': self.__customInterpolatorFuncs,
         'set': self.__setters}
        for memberName, _ in memberToListMap.iteritems():
            for dataProvider in dataProviders:
                memberToListMap[memberName].append(getattr(dataProvider, memberName))

        self.measureDeltaTime()
        self.__initialized = True
        return

    def start(self):
        self.tick()

    def tick(self):
        dt = self.measureDeltaTime()
        self.__active = not self.__interpolationState.stopped
        if self.__active:
            lerpValue = self.__interpolationState.update(dt)
            for idx in range(self.__numItems):
                lerpFunc = self.__customInterpolatorFuncs[idx]
                start = self.__startValueGetters[idx]()
                end = self.__endValueGetters[idx]()
                self.__interpolatedValues[idx] = lerpFunc(start, end, lerpValue) if lerpFunc is not None else mathUtils.lerp(start, end, lerpValue)

            for idx in range(self.__numItems):
                self.__setters[idx](self.__interpolatedValues[idx])

        self.__active = not self.__interpolationState.stopped
        return self.__active

    def reset(self):
        self.__interpolationState.reset(self.__interpolationState.a, self.__interpolationState.b, self.__duration)
        self.measureDeltaTime()
        self.__active = False
