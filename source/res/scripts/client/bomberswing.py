# Embedded file name: scripts/client/BombersWing.py
from collections import namedtuple
import math
from helpers.CallbackDelayer import CallbackDelayer
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from items import vehicles
import BigWorld
import ResMgr
from Math import Vector3
import SoundGroups
import FMOD
CurveControlPoint = namedtuple('CurveControlPoint', ['position', 'direction', 'time'])
BomberDesc = namedtuple('BomberDesc', ['modelName',
 'soundEvent',
 'initPointA',
 'initPointB'])
AREA_LENGTH_SCALE_FACTOR = 0.05
_INITIAL_RETREAT_SHIFT = 200.0
_RETREAT_SUBDIVISION_FACTOR = 10
_MINIMAL_RETREAT_HEIGHT = 25
_MINIMAL_RETREAT_VELOCITY_FACTOR = 0.5
_GRAVITY = 9.81

class Bomber(object):
    ROLL_SPEED = math.radians(45)
    timeOffset = property(lambda self: self.__desc.timeOffset)
    motor = property(lambda self: self.__motor)

    def __init__(self, desc):
        self.__desc = desc
        self.__model = None
        BigWorld.loadResourceListBG((self.__desc.modelName,), self.__onModelLoaded)
        self.__motor = BigWorld.PyTimedWarplaneMotor(self.__desc.initPointA, self.__desc.initPointB, Bomber.ROLL_SPEED)
        self.__sound = None
        self.__destroyed = False
        return

    def destroy(self):
        self.__destroyed = True
        if self.__model:
            if self.__motor and self.__motor in self.__model.motors:
                self.__model.delMotor(self.__motor)
            if self.__model in BigWorld.models():
                BigWorld.delModel(self.__model)
        self.__model = None
        self.__motor = None
        if self.__sound:
            self.__sound.stop()
        self.__sound = None
        return

    def __onModelLoaded(self, resourceRefs):
        if self.__destroyed:
            return
        if self.__desc.modelName not in resourceRefs.failedIDs:
            self.__model = resourceRefs[self.__desc.modelName]
            self.__onFlightStarted()
        else:
            LOG_ERROR('Could not load model %s' % self.__desc.modelName)

    def __onFlightStarted(self):
        if self.__model:
            BigWorld.addModel(self.__model)
            if self.__motor:
                self.__model.addMotor(self.__motor)
            self.__playSound()

    def __onAttackEnded(self, position, velocity):
        self.startAttack(False)

    def __playSound(self):
        if self.__desc and self.__desc.soundEvent:
            try:
                self.__sound = SoundGroups.g_instance.getSound3D(self.__model.root, self.__desc.soundEvent)
                self.__sound.play()
            except:
                self.__sound = None
                LOG_CURRENT_EXCEPTION()

        return

    def startAttack(self, isAttacking):
        if self.__sound is None:
            return
        else:
            if FMOD.enabled:
                self.__sound.setParameterByName('bombing', 1 if isAttacking else 0)
            return

    def addControlPoint(self, position, velocity, time, attackEnded = False):
        callback = None
        if attackEnded:
            callback = self.__onAttackEnded
        self.__motor.addTrajectoryPoint(position, velocity, time, callback)
        return


class BombersWing(CallbackDelayer):
    withdrawn = property(lambda self: self.__withdrawn)

    def __init__(self, equipmentID, wingControlPoints):
        CallbackDelayer.__init__(self)
        self.__withdrawn = False
        self.__bombers = []
        modelName, soundEvent = self.__readData(equipmentID)
        speed = self.__calculateSpeed(wingControlPoints[0], wingControlPoints[1])
        flatVectors = map(self.__calculateDirAndNorm, (wingControlPoints[0].direction, wingControlPoints[1].direction))
        times = map(self.__convertTime, (wingControlPoints[0].time, wingControlPoints[1].time))
        for offset in self.__offsets:
            points = []
            for i in xrange(2):
                point = wingControlPoints[i]
                realOffset = self.__calculateOffset(offset, flatVectors[i])
                points.append(CurveControlPoint(point.position + realOffset, speed * point.direction, times[i]))

            bomberDesc = BomberDesc(modelName, soundEvent, points[0], points[1])
            self.__bombers.append(Bomber(bomberDesc))

    def destroy(self):
        CallbackDelayer.destroy(self)
        for bomber in self.__bombers:
            bomber.destroy()

    def __convertTime(self, time):
        diff = BigWorld.serverTime() - BigWorld.time()
        return time - diff

    def __calculateDirAndNorm(self, direction):
        flatDir = Vector3(direction.x, 0.0, direction.z)
        flatDir.normalise()
        flatNorm = Vector3(direction.z, 0.0, -direction.x)
        flatNorm.normalise()
        return (flatDir, flatNorm)

    def __calculateOffset(self, offset, flatDirAndNorm):
        return offset[2] * flatDirAndNorm[0] + offset[0] * flatDirAndNorm[1]

    def __calculateSpeed(self, start, finish):
        return (finish.position - start.position).length / (finish.time - start.time)

    def __readData(self, equipmentID):
        self.__equipment = equipment = vehicles.g_cache.equipments()[equipmentID]
        self.__offsets = zip(equipment.antepositions, [0.0] * len(equipment.antepositions), equipment.lateropositions)
        self.__fixedSpeed = equipment.speed
        self.__areaLength = equipment.areaLength * AREA_LENGTH_SCALE_FACTOR
        return (equipment.modelName, equipment.soundEvent)

    def __onFlightComplete(self):
        self.__withdrawn = True
        self.destroy()

    def addControlPoint(self, curveControlPoints, bombing):
        speed = self.__calculateSpeed(curveControlPoints[0], curveControlPoints[1]) if not bombing else self.__fixedSpeed
        point = curveControlPoints[1]
        bombingTime = self.__convertTime(point.time)
        endOfBombingTime = 0.0
        retreatPath = []
        if bombing:
            endOfBombingTime = bombingTime + self.__areaLength / self.__fixedSpeed
            ascendPath = curveControlPoints[1].position - curveControlPoints[0].position
            ascendPath.y = -ascendPath.y
            descendTime = curveControlPoints[1].time - curveControlPoints[0].time
            retreatPath.append((ascendPath, endOfBombingTime + descendTime))
        bomberSpeed = speed * point.direction
        for bomber, offset in zip(self.__bombers, self.__offsets):
            realOffset = self.__calculateOffset(offset, self.__calculateDirAndNorm(point.direction))
            bomberPosition = point.position + realOffset
            bomber.addControlPoint(bomberPosition, bomberSpeed, bombingTime)
            if bombing:
                bomber.startAttack(True)
                bomberPosition += point.direction * self.__areaLength
                bomber.addControlPoint(bomberPosition, bomberSpeed, endOfBombingTime, True)
                retreatPath = self.__generateRetreatTrajectory(curveControlPoints[0].position.y, bomberPosition, point.direction, endOfBombingTime)
                for bomberRetreatPosition, retreatVelocity, bomberTime in retreatPath:
                    bomber.addControlPoint(bomberRetreatPosition, retreatVelocity, bomberTime, True)

                self.delayCallback(retreatPath[-1].time - BigWorld.time(), self.__onFlightComplete)

    def __generateRetreatTrajectory(self, idealFlightHeight, bombingEndPosition, bombingDir, bombingEndTime):
        clientArena = BigWorld.player().arena
        endTrajectoryPosition = clientArena.collideWithSpaceBB(bombingEndPosition, bombingEndPosition + bombingDir * 9000.0)
        segmentLength = (endTrajectoryPosition - bombingEndPosition).length / _RETREAT_SUBDIVISION_FACTOR
        firstRetreatPoint = Vector3(bombingEndPosition + bombingDir * _INITIAL_RETREAT_SHIFT)
        positions = [firstRetreatPoint]
        positions += [ firstRetreatPoint + bombingDir * (segmentLength * (idx + 1)) for idx in xrange(_RETREAT_SUBDIVISION_FACTOR - 1) ]
        positions.append(endTrajectoryPosition - bombingDir * min(segmentLength * 0.1, 50.0))
        positions.append(endTrajectoryPosition + bombingDir * 100)
        retreatHeight = _MINIMAL_RETREAT_HEIGHT
        minFlightHeight = idealFlightHeight
        for position in positions:
            zeroHeightPos = Vector3(position)
            zeroHeightPos.y = 0
            collRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, zeroHeightPos + (0, 1000, 0), zeroHeightPos + (0, -1000, 0), 18)
            if collRes is not None:
                minFlightHeight = max(collRes[0].y + retreatHeight, minFlightHeight)
            else:
                minFlightHeight = max(position.y, minFlightHeight)
            position.y = minFlightHeight

        for idx in xrange(len(positions) - 1):
            positions[idx].y = (positions[idx].y + positions[idx + 1].y) / 2.0

        result = self.__generateRetreatPoints(bombingEndPosition, bombingEndTime, positions)
        return result

    def __generateRetreatPoints(self, bombingEndPosition, bombingEndTime, positions):
        result = []
        defaultSpeed = self.__fixedSpeed
        prevPosition = bombingEndPosition
        prevSpeed = defaultSpeed
        prevSpeedSq = prevSpeed * prevSpeed
        prevPointTime = bombingEndTime
        for idx, position in enumerate(positions):
            distDelta = (position - prevPosition).length
            velocityDir = position - prevPosition
            velocityDir /= distDelta
            heightDelta = position.y - prevPosition.y
            speedSq = 2 * (prevSpeed * prevSpeed * 0.5 - _GRAVITY * heightDelta)
            speed = defaultSpeed * _MINIMAL_RETREAT_VELOCITY_FACTOR
            if speedSq / prevSpeedSq >= _MINIMAL_RETREAT_VELOCITY_FACTOR * _MINIMAL_RETREAT_VELOCITY_FACTOR:
                speed = math.sqrt(speedSq)
            flightVelocity = velocityDir * speed
            flightTime = 2 * distDelta / (speed + prevSpeed)
            pointTime = prevPointTime + flightTime
            result.append(CurveControlPoint(position, flightVelocity, pointTime))
            prevPosition = position
            prevSpeed = speed
            prevSpeedSq = prevSpeed * prevSpeed
            prevPointTime = pointTime

        return result
