# Embedded file name: scripts/client/AvatarInputHandler/mathUtils.py
import functools
import BigWorld
import Math
from Math import Vector2, Vector3, Matrix
import random
import math

def createIdentityMatrix():
    result = Matrix()
    result.setIdentity()
    return result


def createRotationMatrix(rotation):
    result = Matrix()
    result.setRotateYPR(rotation)
    return result


def createTranslationMatrix(translation):
    result = Matrix()
    result.setTranslate(translation)
    return result


def createRTMatrix(rotation, translation):
    result = Matrix()
    result.setRotateYPR(rotation)
    result.translation = translation
    return result


def createSRTMatrix(scale, rotation, translation):
    scaleMatrix = Matrix()
    scaleMatrix.setScale(scale)
    result = Matrix()
    result.setRotateYPR(rotation)
    result.translation = translation
    result.preMultiply(scaleMatrix)
    return result


clamp = lambda minVal, maxVal, val: if val < minVal:
minVal(maxVal if val > maxVal else val)

def clampVector3(minVal, maxVal, val):
    return Vector3(clamp(minVal.x, maxVal.x, val.x), clamp(minVal.y, maxVal.y, val.y), clamp(minVal.z, maxVal.z, val.z))


def clampVectorLength(minLength, maxLength, vector):
    length = vector.length
    if not almostZero(length):
        if minLength > length:
            return vector / length * minLength
        if maxLength is not None and maxLength < length:
            return vector / length * maxLength
    return vector * 1.0


def matrixScale(vector, scaleCoeff):
    return Vector3(vector.x * scaleCoeff.x, vector.y * scaleCoeff.y, vector.z * scaleCoeff.z)


def almostZero(val, epsilon = 0.0004):
    return -epsilon < val < epsilon


def lerp(a, b, t):
    return a + (b - a) * t


def squareIn(a, b, t):
    return a + (b - a) * t * t


def squareOut(a, b, t):
    return a + (b - a) * (-t * t + 2 * t)


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
        raise duration > 0.0 or AssertionError
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
    def exponentialEasing(start, end, duration):
        func = lambda a, b, t: b + (a - b) * math.pow(0.0001, t)
        return Easing(start, end, func, duration)


class MatrixProviders:

    @staticmethod
    def product(a, b):
        m = Math.MatrixProduct()
        m.a = a
        m.b = b
        return m


class RandomVectors:

    @staticmethod
    def random2(magnitude = 1.0, randomGenerator = None):
        if randomGenerator is None:
            randomGenerator = random
        u = randomGenerator.random()
        yaw = 2 * math.pi * u
        return Vector2(math.sin(yaw) * magnitude, math.cos(yaw) * magnitude)

    @staticmethod
    def random3Flat(magnitude = 1.0, randomGenerator = None):
        randomVec2 = RandomVectors.random2(magnitude, randomGenerator)
        return Vector3(randomVec2.x, 0.0, randomVec2.y)

    @staticmethod
    def random3(magnitude = 1.0, randomGenerator = None):
        if randomGenerator is None:
            randomGenerator = random
        u = randomGenerator.random()
        v = randomGenerator.random()
        yaw = 2 * math.pi * u
        pitch = math.acos(2 * v - 1)
        sin = math.sin(pitch)
        return Vector3(math.sin(yaw) * sin * magnitude, math.cos(pitch) * magnitude, math.cos(yaw) * sin * magnitude)


class FIRFilter(object):

    def __init__(self, coeffs = None):
        self.coeffs = coeffs
        self.values = [ Vector3(0) for x in xrange(len(self.coeffs)) ]
        self.__id = 0
        self.value = Vector3(0)

    def reset(self):
        self.values = [ Vector3(0) for x in xrange(len(self.coeffs)) ]
        self.__id = 0

    def add(self, value):
        self.values[self.__id] = value
        self.value = Vector3(0)
        for id, coeff in enumerate(self.coeffs):
            self.value += self.values[self.__id - id] * coeff

        self.__id += 1
        if self.__id >= len(self.values):
            self.__id = 0
        return self.value


class SMAFilter(FIRFilter):

    def __init__(self, length):
        FIRFilter.__init__(self, [ 1.0 / length for x in xrange(length) ])


class LowPassFilter(object):

    def __init__(self, alpha):
        self.value = Vector3(0)
        self.alpha = alpha

    def reset(self):
        self.value = Vector3(0)

    def add(self, value):
        self.value = value * self.alpha + (1 - self.alpha) * self.value
        return self.value


class RangeFilter(object):
    value = property(lambda self: self.filter.value)

    def __init__(self, minThreshold, maxLength, cutOffThreshold, filter):
        self.minThreshold = minThreshold
        self.maxLength = maxLength
        self.cutOffThreshold = cutOffThreshold
        self.filter = filter

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
