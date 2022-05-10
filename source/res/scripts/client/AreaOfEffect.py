# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AreaOfEffect.py
from functools import partial
import math
import random
import BigWorld
import AnimationSequence
import CGF
import GenericComponents
import Math
import CombatSelectedArea
import math_utils
from ProjectileMover import collideDynamicAndStatic
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MarkersManagerEvent
from helpers import dependency
from ids_generators import SequenceIDGenerator
from items import vehicles
from items.artefacts import AoeEffects, AreaShow
from skeletons.gui.battle_session import IBattleSessionProvider

class AreaOfEffect(BigWorld.Entity):
    SHOT_HEIGHT = 100.0
    MAX_SHOTS = 1000
    GRAVITY = 9.8
    SHELL_VELOCITY = (0, -500, 0)
    MAX_LAG = 0.5
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _idGen = SequenceIDGenerator()

    def __init__(self):
        super(AreaOfEffect, self).__init__()
        self._sequences = []
        self._callbacks = {}
        self._areas = {}
        self.__areaGO = None
        self._equipment = vehicles.g_cache.equipments()[self.equipmentID]
        self.salvo = BigWorld.PySalvo(self.MAX_SHOTS, 0, -self.SHOT_HEIGHT)
        return

    def prerequisites(self):
        prereqs = []
        if self._equipment.areaVisual:
            prereqs.append(self._equipment.areaVisual)
        for effect in self._equipment.effects.itervalues():
            if not effect:
                continue
            for sequence in effect['sequences']:
                prereqs.append(AnimationSequence.Loader(sequence, self.spaceID))

        return prereqs

    def playEffect(self, effectType, position, radius):
        effect = self._equipment.effects.get(effectType)
        if not effect:
            return
        else:
            delayOffset = 0
            for _ in xrange(effect['repeatCount']):
                playID = self._idGen.next()
                play = partial(self._play, playID, effect, position)
                self._callbacks[playID] = BigWorld.callback(delayOffset, play)
                delayOffset += effect['repeatDelay']

            if effect['areaColor']:
                area = CombatSelectedArea.CombatSelectedArea()
                area.setup(position, Math.Vector3(0, 0, 0), Math.Vector2(radius * 2, radius * 2), CombatSelectedArea.DEFAULT_RADIUS_MODEL, effect['areaColor'], None)
                areaID = self._idGen.next()
                self._areas[areaID] = area
            return

    def onEnterWorld(self, prereqs):
        timeOffset = BigWorld.serverTime() - self.launchTime
        if timeOffset < self.MAX_LAG:
            self.playEffect(AoeEffects.START, self.position, self._equipment.areaRadius)
        self._showArea()
        if self._isMarkersManagerReady:
            self._showMarker()
        else:
            g_eventBus.addListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)

    def onLeaveWorld(self):
        g_eventBus.removeListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        for callbackID in self._callbacks.itervalues():
            BigWorld.cancelCallback(callbackID)

        self._callbacks = {}
        self.__destroyAreaGameObject()
        for area in self._areas.itervalues():
            area.destroy()

        self._areas = {}
        for animator in self._sequences:
            if animator:
                animator.stop()

        self._sequences = []
        self._equipment = None
        return

    def _play(self, playID, effect, targetPosition):
        self._callbacks.pop(playID)
        altitude = Math.Vector3(0, self.SHOT_HEIGHT, 0)
        if effect['offsetDeviation']:
            radius = random.uniform(0, effect['offsetDeviation'])
            angle = random.uniform(0, 2 * math.pi)
            offset = Math.Vector3(radius * math.cos(angle), 0, radius * math.sin(angle))
            targetPosition = targetPosition + offset
        if effect['groundRaycast']:
            startPoint = targetPosition + altitude
            endPoint = targetPosition - altitude
            collisionPoint = collideDynamicAndStatic(startPoint, endPoint, ())
            if collisionPoint:
                targetPosition = collisionPoint[0]
        if effect['shotEffects']:
            shotEffect = random.choice(effect['shotEffects'])
            effectsIndex = vehicles.g_cache.shotEffectsIndexes[shotEffect]
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            artilleryID = effectsDescr.get('artilleryID')
            if artilleryID is not None:
                self.salvo.addProjectile(artilleryID, self.GRAVITY, targetPosition + altitude, self.SHELL_VELOCITY)
        if effect['sequences']:
            sequenceID, sequenceData = random.choice(effect['sequences'].items())
            matrix = Math.Matrix()
            matrix.setRotateY(self.yaw)
            matrix.setScale(sequenceData['scale'])
            matrix.translation = targetPosition
            loader = AnimationSequence.Loader(sequenceID, self.spaceID)
            animator = loader.loadSync()
            animator.bindToWorld(matrix)
            animator.speed = 1
            animator.loopCount = 1
            animator.start()
            self._sequences.append(animator)
        return

    def _areaDestroy(self, areaID):
        self.__destroyAreaGameObject()
        self._callbacks.pop(areaID)
        area = self._areas.pop(areaID)
        area.destroy()

    @property
    def _isMarkersManagerReady(self):
        return self.sessionProvider.shared.areaMarker._gui.getMarkers2DPlugin()

    def _onMarkersCreated(self, event):
        g_eventBus.removeListener(MarkersManagerEvent.MARKERS_CREATED, self._onMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self._showMarker()

    @property
    def _adjustedDelay(self):
        timeOffset = BigWorld.serverTime() - self.launchTime
        return self._equipment.delay - timeOffset

    @property
    def _direction(self):
        return Math.Matrix(self.matrix).applyToAxis(2)

    def _showArea(self):
        areaTimeout = self._adjustedDelay
        if self._equipment.areaShow == AreaShow.ALWAYS:
            areaTimeout += self._equipment.duration
        areaVisual = self._equipment.areaVisual
        if areaVisual and areaTimeout > 0:
            areaSize = Math.Vector2(self._equipment.areaWidth, self._equipment.areaLength)
            areaColor = self._equipment.areaColor
            area = CombatSelectedArea.CombatSelectedArea()
            area.setup(self.position, self._direction, areaSize, areaVisual, areaColor, None)
            area.enableAccurateCollision(self._equipment.areaAccurateCollision)
            area.enableWaterCollision(True)
            areaID = self._idGen.next()
            self._areas[areaID] = area
            self._callbacks[areaID] = BigWorld.callback(areaTimeout, partial(self._areaDestroy, areaID))
            if self._equipment.areaUsedPrefab:
                CGF.loadGameObjectIntoHierarchy(self._equipment.areaUsedPrefab, self.entityGameObject, Math.Vector3(), self.__areaGameObjectLoaded)
        return

    def _showMarker(self):
        delay = self.strikeTime - BigWorld.serverTime()
        equipmentsCtrl = self.sessionProvider.shared.equipments
        if equipmentsCtrl and delay > 0:
            equipmentsCtrl.showMarker(self._equipment, self.position, self._direction, delay)

    def __areaGameObjectLoaded(self, gameObject):
        self.__areaGO = gameObject
        t = gameObject.findComponentByType(GenericComponents.TransformComponent)
        floatEpsilon = 0.001
        xScale = self._equipment.areaWidth * 0.5
        zScale = self._equipment.areaLength * 0.5
        t.transform = math_utils.createSRTMatrix(Math.Vector3(xScale, 1.0, zScale), (0.0, 0.0, 0.0), (0.0, floatEpsilon, 0.0))

    def __destroyAreaGameObject(self):
        if self.__areaGO is not None:
            CGF.removeGameObject(self.__areaGO)
        self.__areaGO = None
        return
