# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_music_stage/camera_descriptor.py
import Math

class CameraDescriptor(object):
    __slots__ = ('initMatrix', 'yawConstraints', 'pitchConstraints', 'distanceConstraints', 'fov', 'isCentered')

    def __init__(self, initMatrix=Math.Matrix(), yawConstraints=Math.Vector2(), pitchConstraints=Math.Vector2(), distanceConstraints=Math.Vector2(), fov=120, isCentered=False):
        super(CameraDescriptor, self).__init__()
        self.initMatrix = Math.Matrix(initMatrix)
        self.yawConstraints = Math.Vector2(yawConstraints)
        self.pitchConstraints = Math.Vector2(pitchConstraints)
        self.distanceConstraints = Math.Vector2(distanceConstraints)
        self.fov = fov
        self.isCentered = isCentered
