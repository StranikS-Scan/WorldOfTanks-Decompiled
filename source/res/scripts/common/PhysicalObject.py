# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/PhysicalObject.py
import BigWorld
import weakref

class PhysicalObject(BigWorld.Entity):

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.proxy = weakref.proxy(self)

    def receiveExplosion(self, hitPoint, explosionRadius, armorDamage, shotEffectsIndex, shellCompactDescr, entityID):
        pass

    def onCollisionWithVehicle(self, otherID, selfPt, otherPt, normal, impulse, kineticEnergy, stress, selfSpeed, otherSpeed):
        pass
