# Embedded file name: scripts/client/FlockExotic.py
import BigWorld
import math
from Vehicle import Vehicle
import random
import Math
from debug_utils import LOG_CURRENT_EXCEPTION
from Flock import FlockLike
from AvatarInputHandler.CallbackDelayer import CallbackDelayer
import TriggersManager

class FlockTriggersListener(TriggersManager.ITriggerListener):
    triggerListener = None
    flocks = set()

    @staticmethod
    def addTrigger(**args):
        if FlockTriggersListener.triggerListener is None:
            FlockTriggersListener.triggerListener = FlockTriggersListener()
            TriggersManager.g_manager.addListener(FlockTriggersListener.triggerListener)
        id = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.EXOTIC_FLOCK, **args)
        FlockTriggersListener.flocks.add(id)
        return

    @staticmethod
    def removeAll():
        if TriggersManager.g_manager is None:
            return
        else:
            for flockId in FlockTriggersListener.flocks:
                TriggersManager.g_manager.delTrigger(flockId)

            TriggersManager.g_manager.delListener(FlockTriggersListener.triggerListener)
            FlockTriggersListener.triggerListener = None
            FlockTriggersListener.flocks = set()
            return

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.EXOTIC_FLOCK:
            args['onTrigger']()

    def onTriggerDeactivated(self, args):
        pass


class FlockExotic(BigWorld.Entity, FlockLike, CallbackDelayer):
    __TRIGGER_CHECK_PERIOD = 1

    def __init__(self):
        BigWorld.Entity.__init__(self)
        FlockLike.__init__(self)
        CallbackDelayer.__init__(self)
        self.__checkTriggerCallbackId = None
        self.__respawnCallbackId = None
        self.flightAngleMin = math.radians(self.flightAngleMin)
        self.flightAngleMax = math.radians(self.flightAngleMax)
        if self.flightAngleMin < 0:
            self.flightAngleMin += math.ceil(abs(self.flightAngleMin) / (math.pi * 2)) * math.pi * 2
        elif self.flightAngleMin > math.pi * 2:
            self.flightAngleMin -= math.floor(self.flightAngleMin / (math.pi * 2)) * math.pi * 2
        self.__active = False
        self.__isTriggered = False
        return

    def prerequisites(self):
        return self._getModelsToLoad()

    def __createMotor(self, positionStart, positionEnd, speed, flightTime):
        time1 = BigWorld.time()
        time2 = time1 + self.accelerationTime
        time3 = time1 + flightTime
        initSpeed = speed * random.uniform(self.initSpeedRandom[0], self.initSpeedRandom[1])
        controlPoint1 = (positionStart, initSpeed, time1)
        controlPoint2 = (positionStart + (initSpeed + speed) / 2.0, speed, time2)
        motor = BigWorld.PyTimedWarplaneMotor(controlPoint1, controlPoint2, 0.0)
        motor.addTrajectoryPoint(positionEnd, speed, time3)
        return motor

    def onEnterWorld(self, prereqs):
        self._loadModels(prereqs)
        for model in self.models:
            model.visible = False

        self.__respawnCallbackId = BigWorld.callback(self.respawnTime, self.__respawnTrigger)
        self._switchSounds(False)
        FlockTriggersListener.addTrigger(position=self.position, onTrigger=self.__onTrigger, radius=self.explosionRadius)

    def onLeaveWorld(self):
        FlockTriggersListener.removeAll()
        self.models = []
        if self.__checkTriggerCallbackId is not None:
            BigWorld.cancelCallback(self.__checkTriggerCallbackId)
            self.__checkTriggerCallbackId = None
        if self.__respawnCallbackId is not None:
            BigWorld.cancelCallback(self.__respawnCallbackId)
            self.__respawnCallbackId = None
        FlockLike.destroy(self)
        CallbackDelayer.destroy(self)
        return

    def name(self):
        return 'FlockExotic'

    def __checkTrigger(self):
        self.__checkTriggerCallbackId = None
        for id, entity in BigWorld.entities.items():
            if isinstance(entity, Vehicle):
                distanceVec = self.position - entity.position
                distanceVec.y = 0
                if distanceVec.lengthSquared <= self.triggerRadius * self.triggerRadius:
                    if not self.__isTriggered:
                        self.__onTrigger()
                        self.__isTriggered = True
                        return
                else:
                    self.__isTriggered = False

        self.__checkTriggerCallbackId = BigWorld.callback(FlockExotic.__TRIGGER_CHECK_PERIOD, self.__checkTrigger)
        return

    def __respawnTrigger(self):
        self.__respawnCallbackId = None
        self.__checkTriggerCallbackId = BigWorld.callback(FlockExotic.__TRIGGER_CHECK_PERIOD, self.__checkTrigger)
        self.__active = True
        return

    def __getRandomSpawnPos(self):
        randHeight = random.uniform(0, self.spawnHeight)
        randAngle = random.uniform(0, 2 * math.pi)
        randRadius = random.uniform(0, self.spawnRadius)
        return Math.Vector3(randRadius * math.cos(randAngle), randHeight, randRadius * math.sin(randAngle)) + self.position

    def __getRandomTargetPos(self, startPos):
        randHeight = random.uniform(0, self.flightHeight)
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
        if not self.__active:
            return
        else:
            flightTime = None
            for model in self.models:
                model.visible = True
                model.position = self.__getRandomSpawnPos()
                targetPos = self.__getRandomTargetPos(model.position)
                dir = targetPos - model.position
                dirLength = dir.length
                speed = self.speed * random.uniform(self.speedRandom[0], self.speedRandom[1])
                if dirLength > 0:
                    velocity = dir * speed / dirLength
                else:
                    velocity = Math.Vector3(0, speed, 0)
                flightTime = dirLength / velocity.length
                motor = self.__createMotor(model.position, targetPos, velocity, flightTime)
                model.addMotor(motor)

            if flightTime is not None:
                self.delayCallback(flightTime, self.__onFlightEnd)
                self._switchSounds(True)
                self.__active = False
            return

    def __onFlightEnd(self):
        self._switchSounds(False)
        for model in self.models:
            model.motors = ()
            model.position = self.position
            model.visible = False

        self.__respawnCallbackId = BigWorld.callback(self.respawnTime, self.__respawnTrigger)
