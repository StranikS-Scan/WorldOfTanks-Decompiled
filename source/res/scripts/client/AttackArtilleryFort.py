# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AttackArtilleryFort.py
import Math
from AreaOfEffect import AreaOfEffect

class AttackArtilleryFort(AreaOfEffect):

    @property
    def _direction(self):
        return Math.Vector3(1, 0, 0)
