# Embedded file name: scripts/client/AvatarInputHandler/Oscillator.py
import math
import random
import sys
import BigWorld
import Math
from Math import Vector3, Matrix
from AvatarInputHandler import mathUtils
from AvatarInputHandler.mathUtils import matrixScale

class IOscillator(object):

    def __init__(self):
        self.deviation = Vector3(0, 0, 0)
        self.velocity = Vector3(0, 0, 0)
        self.externalForce = Vector3(0, 0, 0)

    def reset(self):
        self.deviation = Vector3(0, 0, 0)
        self.velocity = Vector3(0, 0, 0)
        self.externalForce = Vector3(0, 0, 0)

    def applyImpulse(self, impulse):
        pass


class Oscillator(IOscillator):
    _STEP_LENGTH = 1.0 / 60

    def __init__(self, mass, stiffness, drag, constraints):
        IOscillator.__init__(self)
        self.mass = mass
        self.stiffness = Vector3(stiffness)
        self.drag = Vector3(drag)
        self.constraints = Vector3(constraints)
        self.deviation = Vector3(0, 0, 0)
        self.velocity = Vector3(0, 0, 0)
        self.externalForce = Vector3(0, 0, 0)

    def update(self, dt):
        remainedDt = dt
        remainedDt = mathUtils.clamp(0.0, Oscillator._STEP_LENGTH * 3, remainedDt)
        while remainedDt > 0.0:
            deltaTime = Oscillator._STEP_LENGTH
            if deltaTime > remainedDt:
                deltaTime = remainedDt
            remainedDt -= deltaTime
            force = self.__calcForce()
            acc = force / self.mass
            self.velocity += acc * deltaTime
            self.deviation += self.velocity * deltaTime
            unclampedPos = self.deviation
            self.deviation = mathUtils.clampVector3(-self.constraints, self.constraints, self.deviation)
            if unclampedPos.x != self.deviation.x:
                self.velocity.x = 0.0
            if unclampedPos.y != self.deviation.y:
                self.velocity.y = 0.0
            if unclampedPos.z != self.deviation.z:
                self.velocity.z = 0.0

    def applyImpulse(self, impulse):
        velocity = impulse / self.mass
        self.velocity += velocity

    def __calcForce(self):
        return self.externalForce - matrixScale(self.deviation, self.stiffness) - matrixScale(self.velocity, self.drag)


class OscillationsSolver(object):
    period = property(lambda self: 2 * math.pi / self.__omega)

    def __init__(self, mass, stiffnesss, drag):
        self.mass = mass
        self.stiffness = stiffnesss
        self.drag = drag
        sqr = self.drag / (2 * self.mass)
        self.__omega = math.sqrt(self.stiffness / self.mass - sqr * sqr)

    def calcDeviation(self, v0, t):
        return math.exp(-self.drag * t / (2 * self.mass)) * v0 * math.sin(self.__omega * t) / self.__omega


class CompoundOscillator(IOscillator):

    def __setExternalForce(self, value):
        self.__source.externalForce = value

    externalForce = property(lambda self: self.__source.externalForce, __setExternalForce)

    def __init__(self, sourceOscillator, relaxationOscillator):
        self.__source = sourceOscillator
        self.__relaxation = relaxationOscillator
        IOscillator.__init__(self)

    def reset(self):
        IOscillator.reset(self)
        self.__source.reset()
        self.__relaxation.reset()

    def applyImpulse(self, impulse):
        self.__source.applyImpulse(impulse)

    def update(self, dt):
        self.__source.update(dt)
        self.__relaxation.deviation = self.deviation - self.__source.deviation
        self.__relaxation.update(dt)
        self.deviation = self.__source.deviation + self.__relaxation.deviation
        self.velocity = self.__source.velocity + self.__relaxation.velocity


class RandomNoiseOscillator(IOscillator):

    def __init__(self, mass, stiffness, drag, randomGoalPointFunc, restEpsilon = 0.001):
        IOscillator.__init__(self)
        self.__oscillationsSolver = OscillationsSolver(mass, stiffness, drag)
        self.restEpsilon = restEpsilon
        self.__time = 0.0
        self.__startVelocity = 0.0
        self.__prevDeviationGoal = Vector3(0)
        self.__deviationGoal = Vector3(0)
        self.__generator = random.Random()
        self.__initialSeed = random.random() * sys.maxint
        self.__randomGoalPointFunc = randomGoalPointFunc

    def reset(self):
        IOscillator.reset(self)
        self.__time = 0.0
        self.__startVelocity = 0.0

    def update(self, dt):
        self.__time += dt
        halfPeriod = self.__oscillationsSolver.period / 2
        prevGoalTime = int(self.__time / halfPeriod) * halfPeriod
        curGoalTime = (int(self.__time / halfPeriod) + 1) * halfPeriod
        prevGoalDev = self.__getDeviation(-halfPeriod / 2 + prevGoalTime)
        curGoalDev = self.__getDeviation(-halfPeriod / 2 + curGoalTime)
        dir = curGoalDev - prevGoalDev
        dist = abs(dir)
        if self.__time > halfPeriod:
            interpolationCoeff = 1 - ((curGoalDev - self.__getDeviation(-halfPeriod / 2 + self.__time)) / dir if dist > 0.001 else 0.0)
        else:
            interpolationCoeff = 1 - ((curGoalDev - self.__getDeviation(self.__time * 0.5)) / dir if dist > 0.001 else 0.0)
        prevGoalPoint = self.__getGoalPoint(prevGoalTime, prevGoalDev)
        curGoalPoint = self.__getGoalPoint(curGoalTime, curGoalDev)
        self.deviation = prevGoalPoint + (curGoalPoint - prevGoalPoint) * interpolationCoeff

    def applyImpulse(self, impulse):
        if abs(self.deviation.length) > self.restEpsilon:
            return
        self.__startVelocity = impulse.length / self.__oscillationsSolver.mass
        self.__time = 0.0
        self.__initialSeed = random.random() * sys.maxint

    def __getDeviation(self, t):
        if t < 0:
            return 0.0
        return self.__oscillationsSolver.calcDeviation(self.__startVelocity, t)

    def __getGoalPoint(self, t, deviation):
        seed = hash(self.__initialSeed + t)
        self.__generator.seed(seed)
        return self.__randomGoalPointFunc(deviation, self.__generator)


def RandomNoiseOscillatorFlat(mass, stiffness, drag, restEpsilon = 0.01):
    return RandomNoiseOscillator(mass, stiffness, drag, mathUtils.RandomVectors.random3Flat, restEpsilon)


def RandomNoiseOscillatorSpherical(mass, stiffness, drag, scaleCoeff = Vector3(1.0, 1.0, 1.0), restEpsilon = 0.01):
    randomFunc = lambda deviation, generator: matrixScale(mathUtils.RandomVectors.random3(deviation, generator), scaleCoeff)
    return RandomNoiseOscillator(mass, stiffness, drag, randomFunc, restEpsilon)


class NoiseOscillator(IOscillator):

    def __init__(self, mass, stiffness, drag, restEpsilon = 0.001):
        IOscillator.__init__(self)
        self.mass = mass
        self.stiffness = Vector3(stiffness)
        self.drag = Vector3(drag)
        self.deviation = Vector3(0, 0, 0)
        self.velocity = Vector3(0, 0, 0)
        self.externalForce = Vector3(0, 0, 0)
        self.__time = 0.0
        self.__startVelocity = Vector3(0, 0, 0)
        self.restEpsilon = restEpsilon
        sqr = self.drag / (2 * self.mass)
        self.__omega = Vector3(math.sqrt(self.stiffness.x / self.mass - sqr.x * sqr.x), math.sqrt(self.stiffness.y / self.mass - sqr.y * sqr.y), math.sqrt(self.stiffness.z / self.mass - sqr.z * sqr.z))

    def reset(self):
        IOscillator.reset(self)
        self.__time = 0.0
        self.__startVelocity = Vector3(0)

    def update(self, dt):
        self.__time += dt
        self.deviation = Vector3(self.__calcDeviation(self.__startVelocity.x, self.drag.x, self.mass, self.__omega.x, self.__time), self.__calcDeviation(self.__startVelocity.y, self.drag.y, self.mass, self.__omega.y, self.__time), self.__calcDeviation(self.__startVelocity.z, self.drag.z, self.mass, self.__omega.z, self.__time))

    def __calcDeviation(self, v0, drag, mass, omega, t):
        return math.exp(-drag * t / (2 * mass)) * v0 * math.sin(omega * t) / omega

    def applyImpulse(self, impulse):
        if abs(self.deviation.length) > self.restEpsilon:
            return
        self.__startVelocity = impulse / self.mass
        self.__time = 0.0


class HarmonicOscillator(object):

    def __init__(self, amplitude, frequency):
        self.__amplitude = amplitude
        self.__omega = 2 * math.pi * frequency
        self.__time = 0.0
        self.__nextAmplitude = amplitude
        self.__amplitudeChangeVelocity = 0.0
        self.deviation = 0.0

    def changeAmplitude(self, amplitude, changeTime):
        if mathUtils.almostZero(self.__nextAmplitude - amplitude):
            return
        self.__nextAmplitude = amplitude
        if changeTime <= 0.0001:
            self.__amplitude = amplitude
            self.__amplitudeChangeVelocity = 0.0
            return
        self.__amplitudeChangeVelocity = (self.__nextAmplitude - self.__amplitude) / changeTime

    def reset(self):
        self.deviation = 0.0
        self.__time = 0.0

    def update(self, dt):
        self.__time += dt
        prevDelta = self.__nextAmplitude - self.__amplitude
        self.__amplitude += self.__amplitudeChangeVelocity * dt
        if prevDelta * (self.__nextAmplitude - self.__amplitude) <= 0.0:
            self.__amplitude = self.__nextAmplitude
            self.__amplitudeChangeVelocity = 0.0
        self.deviation = self.__amplitude * math.sin(self.__omega * self.__time)
