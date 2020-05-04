# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AttackBomber.py
import math
import BigWorld
import CombatSelectedArea
from AnimatedScene import AnimatedScene
from Math import Vector3, Vector2
from items import vehicles

class AttackBomber(AnimatedScene):
    MAX_DIST = 1000
    SKIP_FLAGS = 18
    STRIKE_LINES = (-1, 1)
    LINE_WIDTH = 5.0

    def __init__(self):
        super(AttackBomber, self).__init__()
        self._attackCallbackId = None
        self._areas = []
        self._equipment = vehicles.g_cache.equipments()[self.equipmentID]
        return

    def onEnterWorld(self, prereqs):
        super(AttackBomber, self).onEnterWorld(prereqs)
        self._attackCallbackId = BigWorld.callback(self.delay, self._carpetBombing)

    def onLeaveWorld(self):
        if self._attackCallbackId:
            BigWorld.cancelCallback(self._attackCallbackId)
        for area in self._areas:
            area.destroy()

        self._equipment = None
        super(AttackBomber, self).onLeaveWorld()
        return

    def playEffect(self, position):
        if self._equipment.shotAreaColor:
            shotRadius = self._equipment.areaWidth / 4
            area = CombatSelectedArea.CombatSelectedArea()
            area.setup(position, Vector3(0, 0, 0), Vector2(shotRadius * 2.4, shotRadius * 2.4), CombatSelectedArea.DEFAULT_RADIUS_MODEL, self._equipment.shotAreaColor, None)
            self._areas.append(area)
        return

    def _carpetBombing(self):
        self._attackCallbackId = None
        equipment = self._equipment
        shellDescr = vehicles.getItemByCompactDescr(equipment.shellCompactDescr)
        shotEffect = vehicles.g_cache.shotEffects[shellDescr.effectsIndex]
        airstrikeID = shotEffect.get('airstrikeID')
        if airstrikeID is None:
            return
        else:
            height = equipment.heights[1]
            flatDir = Vector3(math.sin(self.yaw), 0, math.cos(self.yaw))
            direction = Vector3(flatDir.x, -height / equipment.shootingDistance, flatDir.z)
            direction.normalise()
            velocity = flatDir * equipment.speed
            areaLength = equipment.areaLength
            shootingPoint = self.position - flatDir * (areaLength / 2 + equipment.shootingDistance) + (0, height, 0)
            beginExplosionPos = BigWorld.wg_collideSegment(self.spaceID, shootingPoint, shootingPoint + direction * self.MAX_DIST, self.SKIP_FLAGS)
            if beginExplosionPos is None:
                return
            beginExplosionPos = beginExplosionPos.closestPoint
            endShootingPoint = shootingPoint + flatDir * areaLength
            endExplosionPos = BigWorld.wg_collideSegment(self.spaceID, endShootingPoint, endShootingPoint + direction * self.MAX_DIST, self.SKIP_FLAGS)
            if endExplosionPos is None:
                endExplosionPos = beginExplosionPos + flatDir * areaLength
            else:
                endExplosionPos = endExplosionPos.closestPoint
            areaLength = beginExplosionPos.flatDistTo(endExplosionPos)
            lateral = flatDir * Vector3(0, 1, 0) * self.LINE_WIDTH
            bombsPerLength = int(math.ceil(float(equipment.bombsNumber) / len(self.STRIKE_LINES)))
            if bombsPerLength == 1:
                beginExplosionPos = beginExplosionPos + flatDir * (areaLength / 2)
            for line in self.STRIKE_LINES:
                BigWorld.PyGroundEffectManager().playAirstrike(airstrikeID, beginExplosionPos + lateral * line, velocity, self.LINE_WIDTH, areaLength, 1, bombsPerLength * 2)

            return
