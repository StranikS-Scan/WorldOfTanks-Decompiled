# Embedded file name: scripts/client/Flock.py
from AvatarInputHandler import mathUtils
import BigWorld
import helpers
import Math
import ResMgr
import math
import random
import BattleReplay
import Settings
import SoundGroups
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from Math import Vector3
import FMOD
ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/environment_effects.xml'

class DebugGizmo:

    def __init__(self, spaceID, modelName = 'helpers/models/position_gizmo.model'):
        self.model = BigWorld.Model(modelName)
        BigWorld.addModel(self.model, spaceID)
        self.motor = BigWorld.Servo(Math.Matrix())
        self.model.addMotor(self.motor)

    def visible(self, show):
        self.model.visible = show

    def attachTo(self, model):
        self.motor.signal = model.matrix

    def attachToPosition(self, pos):
        self.model.motors = ()
        self.model.position = pos


class DebugLine(object):

    def _setThickness(self, value):
        self.__thickness = value

    thickness = property(lambda self: self.__thickness, _setThickness)

    def __init__(self, start, end):
        self.model = BigWorld.Model('helpers/models/unit_cube.model')
        self.motor = BigWorld.Servo(Math.Matrix())
        self.model.addMotor(self.motor)
        self.__thickness = 0.1
        self.set(start, end)
        BigWorld.addModel(self.model)

    def set(self, start, end):
        self.start = start
        self.end = end
        direction = end - start
        m = mathUtils.createSRTMatrix((self.__thickness, self.__thickness, direction.length), (direction.yaw, direction.pitch, 0), start + direction / 2)
        m.preMultiply(mathUtils.createTranslationMatrix(Vector3(-0.5, -0.5, -0.5)))
        self.motor.signal = m


class DebugPolyLine(object):

    def __init__(self):
        self.lines = []

    def set(self, points):
        idx = 0
        for curP, nextP in zip(points, points[1:]):
            if idx == len(self.lines):
                self.lines.append(DebugLine(curP, nextP))
            else:
                self.lines[idx].set(curP, nextP)
                self.lines[idx].model.visible = True
            idx += 1

        while idx < len(self.lines):
            self.lines[idx].model.visible = False
            idx += 1


class FlockLike:
    __SoundNames = None
    MAX_DIST_SQ = 10000

    def __init__(self):
        if FlockLike.__SoundNames is None:
            FlockLike.__SoundNames = {}
            flockDataSect = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/birds')
            for value in flockDataSect.values():
                modelName = value.readString('modelName', '')
                if FMOD.enabled:
                    soundName = value.readString('sound', '')
                if modelName != '' and soundName != '':
                    FlockLike.__SoundNames[modelName] = soundName

        self.__sound = None
        return

    def destroy(self):
        self.__sound = None
        return

    def _getModelsToLoad(self):
        list = []
        modelNames = [self.modelName]
        if self.modelName2 != '':
            modelNames.append(self.modelName2)
        for i in xrange(0, self.modelCount):
            list.append(random.choice(modelNames))

        return list

    def _loadModels(self, prereqs):
        try:
            firstModel = True
            for modelId in prereqs.keys():
                if modelId in prereqs.failedIDs:
                    LOG_ERROR('Failed to load flock model: %s' % modelId)
                    continue
                model = prereqs[modelId]
                model.outsideOnly = 1
                model.moveAttachments = True
                self.addModel(model)
                if firstModel:
                    self._addSound(model)
                    firstModel = False
                animSpeed = random.uniform(self.animSpeedMin, self.animSpeedMax)
                model.actionScale = animSpeed
                model.action('FlockAnimAction')()

        except Exception:
            LOG_CURRENT_EXCEPTION()

    def _addSound(self, model):
        if not model.sources:
            return
        else:
            modelName = model.sources[0]
            soundName = FlockLike.__SoundNames.get(modelName, None)
            if soundName is None or soundName == '':
                return
            try:
                self.__sound = SoundGroups.g_instance.getSound3D(model.root, soundName)
                if self.__sound is not None:
                    self.__sound.play()
            except Exception:
                LOG_CURRENT_EXCEPTION()
                return

            return

    def _delSound(self):
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound = None
        return


class Flock(BigWorld.Entity, FlockLike):
    STRATEGY_USUAL_FLY = 0
    STRATEGY_FLY_AROUND_CW = 1
    STRATEGY_FLY_AROUND_CCW = 2
    HEIGHT_CHANGE_DECISION_COUNT = 3
    HEIGHT_CHANGE_SPEED_MULTIPLIER = 1.1
    HEIGHT_DISPERSION_CORRIDOR = 0.05
    CIRCLE_FLIGHT_ABOVE = 0.5
    CIRCLE_FLIGHT_PROBABILITY = 0.25
    __SoundNames = None

    def __init__(self):
        BigWorld.Entity.__init__(self)
        FlockLike.__init__(self)
        self.__decisionCallbackId = None
        self.__decisionCount = 0
        return

    def prerequisites(self):
        return self._getModelsToLoad()

    def onEnterWorld(self, prereqs):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        self._loadModels(prereqs)
        if len(self.models) > 0:
            self._addSound(self.models[0])
        self.__decisionStrategy = self.__doUsualFly
        if self.flyAroundCenter != Flock.STRATEGY_USUAL_FLY:
            self.__setupFlyAroundCenter()
        self.filter = BigWorld.BoidsFilter()
        self.filter.speed = self.speedAtBottom
        self.filter.yprSpeed = Vector3(self.yawSpeed, self.pitchSpeed, self.rollSpeed)
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
        newPosition.y = (self.minHeight + self.maxHeight) / 2.0
        self.physics.teleport(newPosition)
        self.__makeDecision()

    def onLeaveWorld(self):
        self.models = []
        if self.__decisionCallbackId is not None:
            BigWorld.cancelCallback(self.__decisionCallbackId)
        self.__decisionStrategy = None
        FlockLike.destroy(self)
        return

    def set_state(self, oldState):
        pass

    def boidsLanded(self):
        pass

    def name(self):
        return 'Flock'

    def __setupFlyAroundCenter(self):
        self.__decisionStrategy = self.__doAroundCenterFly
        self.deadZoneRadius = self.radius
        for boid in self.models:
            boid.position = Vector3(0.0, 0.0, self.deadZoneRadius)
            if self.flyAroundCenter == Flock.STRATEGY_FLY_AROUND_CW:
                boid.yaw = math.pi / 2.0
            else:
                boid.yaw = -math.pi / 2.0

    def __doUsualFly(self):
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
        randAngle = random.uniform(0.0, 2.0 * math.pi)
        newPosition = Math.Vector3(self.middlePosition.x + randRadius * math.cos(randAngle), randY, self.middlePosition.z + randRadius * math.sin(randAngle))
        self.physics.teleport(newPosition)

    def __doAroundCenterFly(self):
        randY = random.uniform(self.minHeight, self.maxHeight)
        self.physics.teleport(Math.Vector3(self.middlePosition.x, randY, self.middlePosition.z))

    def __makeDecision(self):
        self.__decisionCallbackId = BigWorld.callback(self.decisionTime, self.__makeDecision)
        self.__decisionCount += 1
        self.__decisionStrategy()
