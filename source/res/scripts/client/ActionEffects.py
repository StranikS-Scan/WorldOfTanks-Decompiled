# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ActionEffects.py
from functools import partial
import math
import random
import BigWorld
import AnimationSequence
import Math
import CombatSelectedArea
from ProjectileMover import collideDynamicAndStatic
from ids_generators import SequenceIDGenerator
from items import vehicles
_SHOT_HEIGHT = 100.0
_MAX_SHOTS = 1000
_GRAVITY = 9.8
_VELOCITY = (0, -500, 0)

class ActionEffects(BigWorld.Entity):
    _idGen = SequenceIDGenerator()

    def __init__(self):
        super(ActionEffects, self).__init__()
        self._sequences = []
        self._callbacks = {}
        self._areas = []
        self._equipment = vehicles.g_cache.equipments()[self.equipmentID]
        self._shotSize = self._equipment.areaRadius / math.sqrt(self._equipment.shotsNumber) * 2.5
        self.salvo = BigWorld.PySalvo(_MAX_SHOTS, 0, -_SHOT_HEIGHT)

    def prerequisites(self):
        prereqs = []
        for effect in self._equipment.effects.itervalues():
            if not effect:
                continue
            for sequence in effect['sequences']:
                prereqs.append(AnimationSequence.Loader(sequence, self.spaceID))

        return prereqs

    def playEffect(self, effectType, position):
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

            if self._equipment.shotAreaColor and effectType == 'action':
                area = CombatSelectedArea.CombatSelectedArea()
                area.setup(position, Math.Vector3(0, 0, 0), Math.Vector2(self._shotSize, self._shotSize), CombatSelectedArea.DEFAULT_RADIUS_MODEL, self._equipment.shotAreaColor, None)
                self._areas.append(area)
            return

    def onEnterWorld(self, prereqs):
        self.playEffect('start', self.position)

    def onLeaveWorld(self):
        for callbackID in self._callbacks.itervalues():
            BigWorld.cancelCallback(callbackID)

        for area in self._areas:
            area.destroy()

        for animator in self._sequences:
            if animator:
                animator.stop()

        self._sequences = []
        self._equipment = None
        return

    def _play(self, playID, effect, targetPosition):
        if effect['offsetDeviation']:
            radius = random.uniform(0, effect['offsetDeviation'])
            angle = random.uniform(0, 2 * math.pi)
            offset = Math.Vector3(radius * math.cos(angle), 0, radius * math.sin(angle))
            targetPosition = targetPosition + offset
        if effect['shotEffects']:
            shotEffect = random.choice(effect['shotEffects'])
            effectsIndex = vehicles.g_cache.shotEffectsIndexes[shotEffect]
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            artilleryID = effectsDescr.get('artilleryID')
            if artilleryID is not None:
                shotPosition = targetPosition + (0, _SHOT_HEIGHT, 0)
                self.salvo.addProjectile(artilleryID, _GRAVITY, shotPosition, _VELOCITY)
        if effect['sequences']:
            matrix = Math.Matrix()
            matrix.translation = self._getGroundPosition(targetPosition) if effect['groundRaycast'] else targetPosition
            sequenceID = random.choice(effect['sequences'])
            loader = AnimationSequence.Loader(sequenceID, self.spaceID)
            animator = loader.loadSync()
            animator.bindToWorld(matrix)
            animator.speed = 1
            animator.loopCount = 1
            animator.start()
            self._sequences.append(animator)
        self._callbacks.pop(playID)
        return

    def _getGroundPosition(self, position):
        start = position + (0, _SHOT_HEIGHT, 0)
        end = position + (0, -_SHOT_HEIGHT, 0)
        colPoint = collideDynamicAndStatic(start, end, ())
        return colPoint[0] if colPoint else position
