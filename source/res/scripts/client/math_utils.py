# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/math_utils.py
import random
import math
import Math
from Math import Vector2, Vector3

def createIdentityMatrix():
    return Math.createIdentityMatrix()


def createRotationMatrix(rotation):
    return Math.createRotationMatrix(rotation)


def createTranslationMatrix(translation):
    return Math.createTranslationMatrix(translation)


def createRTMatrix(rotation, translation):
    return Math.createRTMatrix(rotation, translation)


def createSRTMatrix(scale, rotation, translation):
    return Math.createSRTMatrix(scale, rotation, translation)


def setTranslation(matrix, translation):
    matrix.translation = translation


clamp = lambda minVal, maxVal, val: (minVal if val < minVal else maxVal if val > maxVal else val)
clamp01 = lambda val: clamp(0.0, 1.0, val)

def clampVector3(minVal, maxVal, val):
    return Math.clampVector3(minVal, maxVal, val)


def clampVectorLength(minLength, maxLength, vector):
    if isinstance(minLength, Math.Vector2):
        return Math.clampVector2Length(minLength, maxLength, vector)
    if isinstance(minLength, Math.Vector3):
        return Math.clampVector3Length(minLength, maxLength, vector)
    return Math.clampVector4Length(minLength, maxLength, vector) if isinstance(minLength, Math.Vector4) else vector * 1.0


def clampIndex(items, value):
    return clamp(0, len(items) - 1, value)


def matrixScale(vector, scaleCoeff):
    return Math.matrixScale(vector, scaleCoeff)


def almostZero(val, epsilon=0.0004):
    return -epsilon < val < epsilon


def lerp(a, b, t):
    return a + (b - a) * t


def squareIn(a, b, t):
    return a + (b - a) * t * t


def squareOut(a, b, t):
    return a + (b - a) * (-t * t + 2 * t)


def linearTween(t, c, d):
    return c * t / d


def easeInQuad(t, c, d):
    t /= d
    return c * t * t


def easeOutQuad(t, c, d):
    t /= d
    return -c * t * (t - 2.0)


def easeInOutQuad(t, c, d):
    t /= d / 2.0
    if t < 1.0:
        return c / 2.0 * t * t
    t -= 1.0
    return -c / 2.0 * (t * (t - 2.0) - 1.0)


def easeInCubic(t, c, d):
    t /= d
    return c * t * t * t


def easeOutCubic(t, c, d):
    t /= d
    t -= 1.0
    return c * (t * t * t + 1.0)


def easeInOutCubic(t, c, d):
    t /= d / 2.0
    if t < 1.0:
        return c / 2.0 * t * t * t
    t -= 2.0
    return c / 2.0 * (t * t * t + 2.0)


def easeInQuart(t, c, d):
    t /= d
    return c * t * t * t * t


def easeOutQuart(t, c, d):
    t /= d
    t -= 1.0
    return -c * (t * t * t * t - 1.0)


def easeInOutQuart(t, c, d):
    t /= d / 2.0
    if t < 1.0:
        return c / 2.0 * t * t * t * t
    t -= 2.0
    return -c / 2.0 * (t * t * t * t - 2.0)


def easeInQuint(t, c, d):
    t /= d
    return c * t * t * t * t * t


def easeOutQuint(t, c, d):
    t /= d
    t -= 1.0
    return c * (t * t * t * t * t + 1.0)


def easeInOutQuint(t, c, d):
    t /= d / 2.0
    if t < 1.0:
        return c / 2.0 * t * t * t * t * t
    t -= 2.0
    return c / 2.0 * (t * t * t * t * t + 2.0)


def easeInSine(t, c, d):
    return -c * math.cos(t / d * (math.pi / 2.0)) + c


def easeOutSine(t, c, d):
    return c * math.sin(t / d * (math.pi / 2.0))


def easeInOutSine(t, c, d):
    return -c / 2.0 * (math.cos(math.pi * t / d) - 1.0)


def easeInExpo(t, c, d):
    return c * math.pow(2.0, 10.0 * (t / d - 1.0))


def easeOutExpo(t, c, d):
    return c * (-math.pow(2.0, -10.0 * t / d) + 1.0)


def easeInOutExpo(t, c, d):
    t /= d / 2.0
    if t < 1.0:
        return c / 2.0 * math.pow(2.0, 10.0 * (t - 1.0))
    t -= 1.0
    return c / 2.0 * (-math.pow(2.0, -10.0 * t) + 2.0)


def easeInCirc(t, c, d):
    t /= d
    return -c * (math.sqrt(1.0 - t * t) - 1.0)


def easeOutCirc(t, c, d):
    t /= d
    t -= 1.0
    return c * math.sqrt(1.0 - t * t)


def easeInOutCirc(t, c, d):
    t /= d / 2.0
    if t < 1.0:
        return -c / 2.0 * (math.sqrt(1.0 - t * t) - 1.0)
    t -= 2.0
    return c / 2.0 * (math.sqrt(1.0 - t * t) + 1)


def squareInOut(a, b, t):
    if t <= 0.5:
        return 2.0 * t * t
    t -= 0.5
    return 2.0 * t * (1.0 - t) + 0.5


class Easing(object):
    value = property(lambda self: self.__value)
    a = property(lambda self: self.__a)
    b = property(lambda self: self.__b)
    t = property(lambda self: self.__t)
    stopped = property(lambda self: self.__stopped)

    def __init__(self, a, b, interpolationFunc, duration):
        self.__func = interpolationFunc
        self.reset(a, b, duration)

    def reset(self, a, b, duration):
        self.__a = a
        self.__b = b
        self.__t = 0.0
        self.__duration = duration
        self.__value = a
        self.__stopped = False

    def update(self, deltaTime):
        self.__t += deltaTime / self.__duration
        if self.__t > 1.0:
            self.__t = 1.0
            self.__stopped = True
            self.__value = self.__b
        else:
            self.__value = self.__func(self.__a, self.__b, self.__t)
        return self.__value

    @staticmethod
    def linearEasing(a, b, duration):
        return Easing(a, b, lerp, duration)

    @staticmethod
    def squareEasing(a, b, duration):
        return Easing(a, b, squareOut, duration)

    @staticmethod
    def squareEasingInOut(start, end, duration):
        return Easing(start, end, squareInOut, duration)

    @staticmethod
    def exponentialEasing(start, end, duration):
        func = lambda a, b, t: b + (a - b) * math.pow(0.0001, t)
        return Easing(start, end, func, duration)


class MatrixProviders(object):

    @staticmethod
    def product(a, b):
        m = Math.MatrixProduct()
        m.a = a
        m.b = b
        return m


class RandomVectors(object):

    @staticmethod
    def random2(magnitude=1.0, randomGenerator=None):
        if randomGenerator is None:
            randomGenerator = random
        u = randomGenerator.random()
        yaw = 2 * math.pi * u
        return Vector2(math.sin(yaw) * magnitude, math.cos(yaw) * magnitude)

    @staticmethod
    def random3Flat(magnitude=1.0, randomGenerator=None):
        randomVec2 = RandomVectors.random2(magnitude, randomGenerator)
        return Vector3(randomVec2.x, 0.0, randomVec2.y)

    @staticmethod
    def random3(magnitude=1.0, randomGenerator=None):
        if randomGenerator is None:
            randomGenerator = random
        u = randomGenerator.random()
        v = randomGenerator.random()
        yaw = 2 * math.pi * u
        pitch = math.acos(2 * v - 1)
        sin = math.sin(pitch)
        return Vector3(math.sin(yaw) * sin * magnitude, math.cos(pitch) * magnitude, math.cos(yaw) * sin * magnitude)


class FIRFilter(object):

    def __init__(self, coeffs=None):
        self.coeffs = coeffs
        self.values = [ Vector3(0) for _ in xrange(len(self.coeffs)) ]
        self.__id = 0
        self.value = Vector3(0)

    def reset(self):
        self.values = [ Vector3(0) for _ in xrange(len(self.coeffs)) ]
        self.__id = 0

    def add(self, value):
        self.values[self.__id] = value
        self.value = Vector3(0)
        for cID, coeff in enumerate(self.coeffs):
            self.value += self.values[self.__id - cID] * coeff

        self.__id += 1
        if self.__id >= len(self.values):
            self.__id = 0
        return self.value


class SMAFilter(FIRFilter):

    def __init__(self, length):
        FIRFilter.__init__(self, [ 1.0 / length for _ in xrange(length) ])


class LowPassFilter(object):

    def __init__(self, alpha, defaultValue):
        self.value = defaultValue
        self.alpha = alpha
        self.__default = defaultValue

    def reset(self):
        self.value = self.__default

    def add(self, value):
        self.value = value * self.alpha + (1 - self.alpha) * self.value
        return self.value


class RangeFilter(object):
    value = property(lambda self: self.filter.value)

    def __init__(self, minThreshold, maxLength, cutOffThreshold, f):
        self.minThreshold = minThreshold
        self.maxLength = maxLength
        self.cutOffThreshold = cutOffThreshold
        self.filter = f

    def reset(self):
        self.filter.reset()

    def add(self, value):
        valueLength = value.length
        valueToAdd = Vector3(value)
        if valueLength < self.minThreshold or valueLength >= self.cutOffThreshold:
            valueToAdd *= 0.0
        if valueLength > self.maxLength:
            valueToAdd *= self.maxLength / valueLength
        return self.filter.add(valueToAdd)


def reduceToPI(inAngle):
    outAngle = math.fmod(inAngle, 2.0 * math.pi)
    if outAngle >= math.pi:
        outAngle -= 2.0 * math.pi
    elif outAngle <= -math.pi:
        outAngle += 2.0 * math.pi
    return outAngle


def reduceTo2PI(inAngle):
    outAngle = math.fmod(inAngle, 2.0 * math.pi)
    if outAngle < 0.0:
        outAngle += 2.0 * math.pi
    return outAngle


class VectorConstant(object):
    Vector2Zero = Math.Vector2(0.0, 0.0)
    Vector2One = Math.Vector2(1.0, 1.0)
    Vector2I = Math.Vector2(1.0, 0.0)
    Vector2J = Math.Vector2(0.0, 1.0)
    Vector3Zero = Math.Vector3(0.0, 0.0, 0.0)
    Vector3One = Math.Vector3(1.0, 1.0, 1.0)
    Vector3I = Math.Vector3(1.0, 0.0, 0.0)
    Vector3J = Math.Vector3(0.0, 1.0, 0.0)
    Vector3K = Math.Vector3(0.0, 0.0, 1.0)
    Vector4Zero = Math.Vector4(0.0, 0.0, 0.0, 0.0)
    Vector4One = Math.Vector4(1.0, 1.0, 1.0, 1.0)
    Vector4I = Math.Vector4(1.0, 0.0, 0.0, 0.0)
    Vector4J = Math.Vector4(0.0, 1.0, 0.0, 0.0)
    Vector4L = Math.Vector4(0.0, 0.0, 0.0, 1.0)


def normalizeAngle(angle):
    return angle - 2 * math.pi * math.floor(angle / (2 * math.pi))


def isNearlyEqualFloat(a, b, epsilon=1e-05):
    return abs(a - b) < epsilon


def isNearlyZeroFloat(a, epsilon=1e-05):
    return isNearlyEqualFloat(a, 0.0, epsilon)


def rotateVector3(vec, angles, axis):
    return vec * math.cos(angles) + vec * axis * math.sin(angles) + axis * vec.dot(axis) * (1 - math.cos(angles))
