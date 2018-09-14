# Embedded file name: scripts/client/CombatEquipmentManager.py
from AvatarInputHandler import mathUtils
import BigWorld
import Math
from Math import Vector2, Vector3
import functools
import math
from helpers.CallbackDelayer import CallbackDelayer
import BombersWing
import Flock
from constants import IS_DEVELOPMENT
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_WARNING, LOG_ERROR
import CombatSelectedArea
from gui.battle_control import g_sessionProvider
from items import vehicles
import items
import BattleReplay
_ENABLE_DEBUG_DRAW = False
_ENABLE_DEBUG_LOG = False

class _DebugFrontLine(CallbackDelayer):

    @staticmethod
    def launch(beginExplosionPos, endExplosionPos, areaWidth, velocity):
        _DebugFrontLine(beginExplosionPos, endExplosionPos, areaWidth, velocity)

    def __init__(self, beginExplosionPos, endExplosionPos, areaWidth, velocity):
        CallbackDelayer.__init__(self)
        self.model = BigWorld.Model('helpers/models/unit_cube.model')
        BigWorld.addModel(self.model)
        self.model.position = beginExplosionPos
        linearHomer = BigWorld.LinearHomer()
        self.model.addMotor(linearHomer)
        linearHomer.align = mathUtils.createSRTMatrix((areaWidth, 5, 1), (0.0, 0, 0), Vector3(0, 0, 0))
        linearHomer.acceleration = 0
        linearHomer.velocity = velocity
        linearHomer.target = mathUtils.createTranslationMatrix(endExplosionPos)
        linearHomer.proximityCallback = self.__onDeath

    def __onDeath(self):
        BigWorld.delModel(self.model)


class CombatEquipmentManager(object):

    def testArtyStrike(self, id = 33, offset = Vector3(0, 0, 0)):
        if not IS_DEVELOPMENT:
            return
        else:
            p = Vector3(BigWorld.camera().position)
            d = BigWorld.camera().direction
            collRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, p, p + d * 1000, 18, lambda matKind, collFlags, itemId, chunkId: collFlags & 8)
            if collRes is None:
                return
            strikePos = collRes[0]
            vDir = Vector2(d.x, d.z)
            vDir.normalise()
            self.setEquipmentApplicationPoint(id, strikePos + offset, vDir)
            return

    def __init__(self):
        self.__callbackDelayer = CallbackDelayer()
        self.__selectedAreas = {}
        self.__wings = {}
        if _ENABLE_DEBUG_DRAW:
            self.debugPolyLine = Flock.DebugPolyLine()
            self.debugPoints = []
            self.debugDirs = []

    def onBecomePlayer(self):
        pass

    def onBecomeNonPlayer(self):
        for area in self.__selectedAreas.itervalues():
            area.destroy()

        for wing in self.__wings.itervalues():
            wing.destroy()

        self.__callbackDelayer.destroy()
        self.__selectedAreas = {}
        self.__wings = {}

    def updateBomberTrajectory(self, equipmentID, team, curTime, curPos, curDir, nextTime, nextPos, nextDir, isDroppingPoint):
        if _ENABLE_DEBUG_LOG:
            LOG_DEBUG('===== updateBomberTrajectory =====')
            LOG_DEBUG(equipmentID, team)
            LOG_DEBUG(curPos, curDir, curTime)
            LOG_DEBUG(nextPos, nextDir, nextTime)
            LOG_DEBUG(isDroppingPoint)
        moveDir = nextPos - curPos
        moveDir.normalise()
        nextDir3d = Vector3(nextDir.x, moveDir.y, nextDir.y)
        nextDir3d.normalise()
        startP = BombersWing.CurveControlPoint(curPos, Vector3(curDir.x, 0, curDir.y), curTime)
        nextP = BombersWing.CurveControlPoint(nextPos, nextDir3d, nextTime)
        points = (startP, nextP)
        wingID = (team, equipmentID)
        wing = self.__wings.get(wingID)
        if wing is None or wing.withdrawn:
            if wing is not None:
                wing.destroy()
            self.__wings[wingID] = BombersWing.BombersWing(equipmentID, points)
            if _ENABLE_DEBUG_DRAW:
                self.debugPoints.append(curPos)
                self.debugDirs.append(curDir)
        else:
            wing.addControlPoint(points, isDroppingPoint)
        if _ENABLE_DEBUG_DRAW:
            self.debugPoints.append(nextPos)
            self.debugDirs.append(nextDir)
            self.debugPoints.append(nextPos + Vector3(nextDir.x, 0, nextDir.y) * 10)
            self.debugPoints.append(nextPos)
            self.debugPolyLine.set(self.debugPoints)
        return

    def showHittingArea(self, equipmentID, pos, dir, time):
        if _ENABLE_DEBUG_LOG:
            LOG_DEBUG('===== showHittingArea =====')
            LOG_DEBUG(equipmentID)
            LOG_DEBUG(pos, dir, time)
        correctedCoords = tuple((int(x * 1000.0) for x in pos.tuple()))
        areaUID = (int(equipmentID), correctedCoords)
        if areaUID in self.__selectedAreas:
            return
        eq = vehicles.g_cache.equipments()[equipmentID]
        if BattleReplay.isPlaying():
            BigWorld.callback(0.0, functools.partial(self.__showMarkerCallback, eq, pos, dir, time, areaUID))
        else:
            self.__showMarkerCallback(eq, pos, dir, time, areaUID)

    def __delayedAreaDestroy(self, areaUID):
        area = self.__selectedAreas.pop(areaUID, None)
        if area is not None:
            area.destroy()
        return

    def __showMarkerCallback(self, eq, pos, dir, time, areaUID):
        timer = round(time - BigWorld.serverTime())
        area = self.__selectedAreas.pop(areaUID, None)
        if area is not None:
            area.destroy()
        self.__selectedAreas[areaUID] = self.createEquipmentSelectedArea(pos, dir, eq)
        self.__callbackDelayer.delayCallback(timer, functools.partial(self.__delayedAreaDestroy, areaUID))
        g_sessionProvider.getEquipmentsCtrl().showMarker(eq, pos, dir, timer)
        return

    @staticmethod
    def __calcBombsDistribution(bombsCnt, areaWidth, areaLength):
        coeff = areaWidth / areaLength
        bombsPerWidth = math.sqrt(bombsCnt * coeff)
        bombsPerLength = bombsPerWidth / coeff
        return (bombsPerWidth, bombsPerLength)

    def showCarpetBombing(self, equipmentID, pos, dir, time):
        if _ENABLE_DEBUG_LOG:
            LOG_DEBUG('===== showCarpetBombing =====')
            LOG_DEBUG(equipmentID)
            LOG_DEBUG(pos, dir, time)
        bombEquipment = vehicles.g_cache.equipments()[equipmentID]
        shellDescr = items.vehicles.getDictDescr(bombEquipment.shellCompactDescr)
        shotEffect = vehicles.g_cache.shotEffects[shellDescr['effectsIndex']]
        airstrikeID = shotEffect.get('airstrikeID')
        if airstrikeID is None:
            LOG_ERROR('EquipmentID %s has no airstrike shot effect settings' % equipmentID)
            return
        else:
            areaWidth, areaLength = bombEquipment.areaWidth, bombEquipment.areaLength
            if _ENABLE_DEBUG_LOG:
                LOG_DEBUG('Ideal', areaWidth, areaLength)
            beginExplosionPos = BigWorld.wg_collideSegment(BigWorld.player().spaceID, pos, pos + dir * 1000.0, 18)
            if beginExplosionPos is None:
                return
            beginExplosionPos = beginExplosionPos[0]
            flatDir = Vector3(dir)
            flatDir.y = 0.0
            flatDir.normalise()
            endDropPoint = pos + flatDir * (areaLength * bombEquipment.waveFraction)
            endExplosionPos = BigWorld.wg_collideSegment(BigWorld.player().spaceID, endDropPoint, endDropPoint + dir * 1000.0, 18)
            if endExplosionPos is None:
                endExplosionPos = beginExplosionPos + flatDir * (areaLength * bombEquipment.waveFraction)
            else:
                endExplosionPos = endExplosionPos[0]
            areaLength = beginExplosionPos.flatDistTo(endExplosionPos)
            averageBombCount = bombEquipment.bombsNumber
            bombsPerWidth, bombsPerLength = CombatEquipmentManager.__calcBombsDistribution(averageBombCount, areaWidth, areaLength)
            delay = time - BigWorld.serverTime()
            explosionVelocity = flatDir * bombEquipment.speed
            partialAirstrikeFunc = functools.partial(BigWorld.PyGroundEffectManager().playAirstrike, airstrikeID, beginExplosionPos, explosionVelocity, areaWidth, areaLength, math.ceil(bombsPerWidth), math.ceil(bombsPerLength))
            if _ENABLE_DEBUG_LOG:
                LOG_DEBUG('delta', delay)
                LOG_DEBUG('pos, dir', pos, dir)
                LOG_DEBUG('Params for artyStrike effect', airstrikeID, beginExplosionPos, flatDir, areaWidth, areaLength, bombsPerWidth, bombsPerLength)
            if delay < 0.0:
                partialAirstrikeFunc()
            else:
                self.__callbackDelayer.delayCallback(delay, partialAirstrikeFunc)
            if _ENABLE_DEBUG_DRAW:
                self.debugStartLine = Flock.DebugLine(pos, beginExplosionPos)
                self.debugEndLine = Flock.DebugLine(endDropPoint, endExplosionPos)
                self.__callbackDelayer.delayCallback(delay, functools.partial(_DebugFrontLine.launch, beginExplosionPos, endExplosionPos, areaWidth, explosionVelocity))
            return

    def setEquipmentApplicationPoint(self, equipmentID, point, direction):
        myTeam = BigWorld.player().team
        wingID = (myTeam, equipmentID)
        wing = self.__wings.get(wingID)
        if wing is not None:
            wing.destroy()
            del self.__wings[wingID]
        self.cell.setEquipmentApplicationPoint(equipmentID, point, direction)
        return

    @staticmethod
    def createEquipmentSelectedArea(pos, dir, equipment):
        area = CombatSelectedArea.CombatSelectedArea()
        size = Math.Vector2(equipment.areaWidth, equipment.areaLength)
        visual = equipment.areaVisual
        color = equipment.areaColor
        marker = equipment.areaMarker
        if visual is None:
            visual = CombatSelectedArea.DEFAULT_RADIUS_MODEL
        if color is None:
            color = CombatSelectedArea.COLOR_WHITE
        if marker is None:
            pass
        area.setup(pos, dir, size, visual, color, marker)
        return area
