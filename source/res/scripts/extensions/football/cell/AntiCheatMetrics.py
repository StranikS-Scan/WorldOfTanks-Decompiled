# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/cell/AntiCheatMetrics.py
from Math import Vector3

class OPTIONS:
    PRECISION = 0.001
    DEBUG = False


def fuzzyEquals(a, b, t=OPTIONS.PRECISION):
    return abs(a - b) < t


def fuzzyIsZero(a, t=OPTIONS.PRECISION):
    return abs(a) < t


class Distribution(object):

    def __init__(self, data):
        self.__data = data
        if not data:
            data[:] = [0] * len(self.BINS)

    BINS = ()

    def accumulate(self, value):
        data = self.__data
        for i, maxValue in enumerate(self.BINS):
            if value <= maxValue:
                data[i] += 1
                break


class PositionSimilarityMetrics(Distribution):
    BINS = (2.265,
     4.53,
     11.325000000000001,
     float('+inf'))

    def __init__(self, data):
        Distribution.__init__(self, data)

    def tick(self, position, otherPosition):
        self.accumulate(otherPosition.distTo(position))


class MovementSimilarityDistribution(Distribution):
    BINS = (0.001,
     0.01,
     0.1,
     1.0,
     5.0,
     float('+inf'))

    def __init__(self, data):
        Distribution.__init__(self, data)

    def isAnyMoving(self, delta, otherDelta):
        return not fuzzyIsZero(delta.length) and not fuzzyIsZero(otherDelta.length)


class MovementSimilarityMetricsLinear(MovementSimilarityDistribution):

    def __init__(self, data):
        MovementSimilarityDistribution.__init__(self, data)

    def tick(self, delta, otherDelta):
        self.accumulate(round(abs(delta.lengthSquared - otherDelta.lengthSquared), 3))


class MovementSimilarityMetrics(MovementSimilarityDistribution):

    def __init__(self, data):
        MovementSimilarityDistribution.__init__(self, data)

    def tick(self, delta, otherDelta):
        if self.isAnyMoving(delta, otherDelta):
            self.accumulate((delta - otherDelta).length)


class Forwarders:

    @staticmethod
    def ballAndAimPosition(prevVehiclePosition, prevAimPosition, prevBallPosition, vehiclePosition, aimPosition, ballPosition):
        return (ballPosition, aimPosition)

    @staticmethod
    def ballAndAimMovement(prevVehiclePosition, prevAimPosition, prevBallPosition, vehiclePosition, aimPosition, ballPosition):
        return (ballPosition - prevBallPosition, aimPosition - prevAimPosition)


class AntiCheatMetricsCollector(object):
    METRICS = ((PositionSimilarityMetrics, Forwarders.ballAndAimPosition), (MovementSimilarityMetricsLinear, Forwarders.ballAndAimMovement), (MovementSimilarityMetrics, Forwarders.ballAndAimMovement))

    def __init__(self, data):
        self.__data = data
        if not data:
            data['args'] = (Vector3(), Vector3(), Vector3())
            data['metrics'] = tuple(([] for _ in AntiCheatMetricsCollector.METRICS))
        self.__metrics = tuple(((constructor(data['metrics'][i]), forwarder) for i, (constructor, forwarder) in enumerate(AntiCheatMetricsCollector.METRICS)))

    def tick(self, *args):
        data = self.__data
        forwarded = data['args'] + args
        data['args'] = args
        for metric, forwarder in self.__metrics:
            metric.tick(*forwarder(*forwarded))

    @property
    def allMetrics(self):
        return self.__data['metrics']
