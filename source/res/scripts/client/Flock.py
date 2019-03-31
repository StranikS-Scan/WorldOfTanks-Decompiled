# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Flock.py
# Compiled at: 2011-12-19 13:56:37
import BigWorld
import Math
import math
import random
import BattleReplay

class Flock(BigWorld.Entity):
    HEIGHT_CHANGE_DECISION_COUNT = 3
    HEIGHT_CHANGE_SPEED_MULTIPLIER = 1.1
    HEIGHT_DISPERSION_CORRIDOR = 0.05
    CIRCLE_FLIGHT_ABOVE = 0.5
    CIRCLE_FLIGHT_PROBABILITY = 0.25

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.__decisionCallbackId = None
        self.__decisionCount = 0
        return

    def prerequisites(self):
        list = []
        for i in xrange(0, self.modelCount):
            list.append(self.modelName)

        return list

    def onEnterWorld(self, prereqs):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        boidModels = prereqs.values()
        for model in boidModels:
            model.outsideOnly = 1
            self.addModel(model)
            model.FlockAnimAction(random.uniform(self.animSpeedMin, self.animSpeedMax))

        self.__decisionStrategy = self.__doUsualFly
        if self.flyAroundCenter:
            self.__decisionStrategy = self.__doAroundCenterFly
            self.deadZoneRadius = self.radius
        self.filter = BigWorld.BoidsFilter()
        self.filter.speed = self.speedAtBottom
        self.filter.yawSpeed = self.yawSpeed
        self.filter.deadZonePosition = self.position
        self.filter.deadZoneRadius = self.deadZoneRadius
        self.middlePosition = Math.Vector3()
        self.minHeight = self.position.y
        self.maxHeight = self.minHeight + self.height
        for boid in self.models:
            boid.visible = True

        self.middlePosition = Math.Vector3(self.position)
        self.physics = 0
        newPosition = Math.Vector3(self.position)
        newPosition.y = (self.minHeight + self.maxHeight) / 2
        self.physics.teleport(newPosition)
        self.__makeDecision()

    def onLeaveWorld(self):
        self.models = []
        if self.__decisionCallbackId is not None:
            BigWorld.cancelCallback(self.__decisionCallbackId)
        return

    def set_state(self, oldState):
        pass

    def boidsLanded(self):
        pass

    def name(self):
        pass

    def __doUsualFly(self):
        randY = self.position.y
        flightZoneHeight = self.maxHeight - self.minHeight
        if self.__decisionCount >= Flock.HEIGHT_CHANGE_DECISION_COUNT:
            randY = random.uniform(self.minHeight, self.maxHeight)
            heightFraction = (randY - self.minHeight) / flightZoneHeight
            self.filter.speed = self.speedAtBottom + (self.speedAtTop - self.speedAtBottom) * heightFraction
            self.__decisionCount = 0
        else:
            heightFraction = (self.position.y - self.minHeight) / flightZoneHeight
            if heightFraction >= Flock.CIRCLE_FLIGHT_ABOVE and random.random() <= Flock.CIRCLE_FLIGHT_PROBABILITY:
                return
            self.filter.speed = self.speedAtBottom + (self.speedAtTop - self.speedAtBottom) * heightFraction
            randY = self.position.y + random.uniform(-flightZoneHeight * Flock.HEIGHT_DISPERSION_CORRIDOR, flightZoneHeight * Flock.HEIGHT_DISPERSION_CORRIDOR)
            if randY < self.minHeight:
                randY = self.minHeight
            elif randY > self.maxHeight:
                randY = self.maxHeight
        randRadius = random.uniform(self.deadZoneRadius, self.radius)
        randAngle = random.uniform(0, 2 * math.pi)
        newPosition = Math.Vector3(self.middlePosition.x + randRadius * math.cos(randAngle), randY, self.middlePosition.z + randRadius * math.sin(randAngle))
        self.physics.teleport(newPosition)

    def __doAroundCenterFly(self):
        randY = random.uniform(self.minHeight, self.maxHeight)
        self.physics.teleport(Math.Vector3(self.middlePosition.x, randY, self.middlePosition.z))

    def __makeDecision(self):
        self.__decisionCallbackId = BigWorld.callback(self.decisionTime, self.__makeDecision)
        self.__decisionCount += 1
        self.__decisionStrategy()
