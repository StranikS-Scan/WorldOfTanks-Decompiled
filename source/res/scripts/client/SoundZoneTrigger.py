# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SoundZoneTrigger.py
import BigWorld
import Math
from math import cos
from math import sin

class SoundZoneTrigger(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        alpha = self.direction.x
        centerShift = Math.Vector2(0.0, self.Size[1] * 0.5)
        x1 = centerShift[0] * cos(alpha) - centerShift[1] * sin(alpha)
        y1 = centerShift[0] * sin(alpha) + centerShift[1] * cos(alpha)
        center = Math.Vector2(self.position.x, self.position.z) + Math.Vector2(x1, y1)
        BigWorld.addSoundZoneTrigger(center, self.Size, alpha, self.ZoneEnter, self.ZoneExit, self.Reverb, self.ReverbLevel)

    def destroy(self):
        pass
