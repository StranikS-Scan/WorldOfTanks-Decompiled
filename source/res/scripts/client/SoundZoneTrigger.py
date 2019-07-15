# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SoundZoneTrigger.py
import BigWorld
import Math
import math_utils
VISUALISE_ZONE = False

class SoundZoneTrigger(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        BigWorld.addSoundZoneTrigger(self.position, Math.Vector3(self.direction.z, self.direction.y, self.direction.x), Math.Vector3(self.Size.x, self.Size.y, self.Size.z), self.ZoneEnter, self.ZoneExit, self.Reverb, self.ReverbLevel, self.VolumeDeviation)
        if VISUALISE_ZONE:
            self.model = BigWorld.Model('objects/misc/bbox/unit_cube_1m_proxy.model')
            BigWorld.player().addModel(self.model)
            motor = BigWorld.Servo(Math.Matrix())
            self.model.addMotor(motor)
            motor.signal = math_utils.createSRTMatrix(Math.Vector3(self.Size.x, self.Size.y, self.Size.z), Math.Vector3(self.direction.z, self.direction.y, self.direction.x), self.position)

    def destroy(self):
        pass
