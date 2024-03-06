# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SoundZoneTrigger.py
import BigWorld
import CGF
import Math
from GenericComponents import TransformComponent
from Triggers import SquareAreaComponent
from Sound import SoundZoneComponent
import math_utils
VISUALISE_ZONE = False

class SoundZoneTrigger(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        self.__gameObject = CGF.GameObject(BigWorld.player().spaceID or BigWorld.camera().spaceID, 'SoundZoneTrigger')
        self.__gameObject.setStatic(True)
        position = math_utils.createRTMatrix(Math.Vector3(self.direction.z, self.direction.y, self.direction.x), self.position)
        self.__gameObject.createComponent(TransformComponent, position)
        self.__gameObject.createComponent(SoundZoneComponent, self.ZoneEnter, self.ZoneExit, self.Reverb, '', self.ReverbLevel, self.VolumeDeviation)
        v = Math.Vector3(self.Size.x, self.Size.y, self.Size.z) * 0.5
        self.__gameObject.createComponent(SquareAreaComponent, -v, v)
        self.__gameObject.activate()
        if VISUALISE_ZONE:
            self.model = BigWorld.Model('objects/misc/bbox/unit_cube_1m_proxy.model')
            BigWorld.player().addModel(self.model)
            motor = BigWorld.Servo(Math.Matrix())
            self.model.addMotor(motor)
            motor.signal = math_utils.createSRTMatrix(Math.Vector3(self.Size.x, self.Size.y, self.Size.z), Math.Vector3(self.direction.z, self.direction.y, self.direction.x), self.position)

    def destroy(self):
        self.__gameObject.destroy()
        self.__gameObject = None
        return
