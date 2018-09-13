# Embedded file name: scripts/client/FlockExotic.py
import BigWorld
import math
from Vehicle import Vehicle
import random
import Math
from debug_utils import LOG_CURRENT_EXCEPTION
from Flock import FlockLike

class FlockExotic(BigWorld.Entity, FlockLike):
    __TRIGGER_CHECK_PERIOD = 1

    def __init__(self):
        BigWorld.Entity.__init__(self)
        FlockLike.__init__(self)
        self.__checkTriggerCallbackId = None
        self.__respawnCallbackId = None
        self.__motors = []
        self.flightAngleMin = math.radians(self.flightAngleMin)
        self.flightAngleMax = math.radians(self.flightAngleMax)
        if self.flightAngleMin < 0:
            self.flightAngleMin += math.ceil(abs(self.flightAngleMin) / (math.pi * 2)) * math.pi * 2
        elif self.flightAngleMin > math.pi * 2:
            self.flightAngleMin -= math.floor(self.flightAngleMin / (math.pi * 2)) * math.pi * 2
        return

    def prerequisites(self):
        return self._getModelsToLoad()

    def __createMotors(self):
        del self.__motors[:]
        for i in xrange(self.modelCount):
            motor = BigWorld.LinearHomer()
            self.__motors.append(motor)
            motorMatrix = Math.Matrix()
            motorMatrix.setIdentity()
            motor.target = motorMatrix
            motor.acceleration = 0
            motor.proximity = 0.5

    def onEnterWorld(self, prereqs):
        self._loadModels(prereqs)
        for model in self.models:
            model.visible = False

        self.__createMotors()
        self.__respawnCallbackId = BigWorld.callback(self.respawnTime, self.__respawnTrigger)
        self._switchSounds(False)

    def onLeaveWorld(self):
        self.models = []
        if self.__checkTriggerCallbackId is not None:
            BigWorld.cancelCallback(self.__checkTriggerCallbackId)
            self.__checkTriggerCallbackId = None
        if self.__respawnCallbackId is not None:
            BigWorld.cancelCallback(self.__respawnCallbackId)
            self.__respawnCallbackId = None
        FlockLike.destroy(self)
        return

    def name(self):
        return 'FlockExotic'

    def __checkTrigger(self):
        self.__checkTriggerCallbackId = None
        isTriggered = False
        for id, entity in BigWorld.entities.items():
            if isinstance(entity, Vehicle):
                distanceVec = self.position - entity.position
                distanceVec.y = 0
                if distanceVec.lengthSquared <= self.triggerRadius * self.triggerRadius:
                    self.__onTrigger()
                    isTriggered = True
                    break

        if not isTriggered:
            self.__checkTriggerCallbackId = BigWorld.callback(FlockExotic.__TRIGGER_CHECK_PERIOD, self.__checkTrigger)
        return

    def __respawnTrigger(self):
        self.__respawnCallbackId = None
        self.__checkTriggerCallbackId = BigWorld.callback(FlockExotic.__TRIGGER_CHECK_PERIOD, self.__checkTrigger)
        return

    def __getRandomSpawnPos(self):
        randHeight = random.uniform(0, self.spawnHeight)
        randAngle = random.uniform(0, 2 * math.pi)
        randRadius = random.uniform(0, self.spawnRadius)
        return Math.Vector3(randRadius * math.cos(randAngle), randHeight, randRadius * math.sin(randAngle)) + self.position

    def __getRandomTargetPos(self, startPos):
        randHeight = random.uniform(0, self.flightHeight)
        arc = 0
        arc = self.flightAngleMax - self.flightAngleMin
        if self.flightAngleMax < self.flightAngleMin:
            arc = 2 * math.pi - abs(arc)
        randAngle = random.uniform(self.flightAngleMin, self.flightAngleMin + arc)
        dir = Math.Vector3(self.flightRadius * math.cos(randAngle), self.flightOffsetFromOrigin + randHeight, self.flightRadius * math.sin(randAngle)) + self.position
        dir = dir - startPos
        dir.normalise()
        dir *= self.speed * self.lifeTime
        return startPos + dir

    def __onTrigger(self):
        for model, motor in zip(self.models, self.__motors):
            model.visible = True
            model.position = self.__getRandomSpawnPos()
            model.addMotor(motor)
            targetPos = self.__getRandomTargetPos(model.position)
            motor.target.setTranslate(targetPos)
            dir = targetPos - model.position
            dirLength = dir.length
            if dirLength > 0:
                dir *= self.speed / dirLength
                motor.velocity = dir
            else:
                motor.velocity = Math.Vector3(0, self.speed, 0)

        if len(self.__motors) > 0:
            self.__motors[0].proximityCallback = self.__onFlightEnd
        self._switchSounds(True)

    def __onFlightEnd(self):
        self._switchSounds(False)
        for model in self.models:
            model.motors = ()
            model.position = self.position
            model.visible = False

        self.__respawnCallbackId = BigWorld.callback(self.respawnTime, self.__respawnTrigger)
