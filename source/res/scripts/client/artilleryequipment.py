# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArtilleryEquipment.py
import math_utils
import BigWorld

class ArtilleryEquipment(BigWorld.UserDataObject):
    launchVelocity = property(lambda self: self.__launchVelocity)

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        launchDir = math_utils.createRotationMatrix((self.__dict__['yaw'], self.__dict__['pitch'], 0)).applyToAxis(2)
        launchDir.normalise()
        self.__launchVelocity = launchDir * self.speed
