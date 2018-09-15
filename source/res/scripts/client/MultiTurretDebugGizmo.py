# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MultiTurretDebugGizmo.py
import BigWorld
import Math
from Flock import DebugGizmo, DebugLine

class MultiturretDebugGizmo(object):

    def __init__(self):
        super(MultiturretDebugGizmo, self).__init__()
        self.__gizmos = {}
        self.__lines = {}

    def createGizmo(self, name, position=None):
        gizmo = DebugGizmo()
        self.__gizmos[name] = gizmo
        if position is not None:
            self.updateGizmoPosition(name, position)
        return

    def updateGizmoPosition(self, name, newPos):
        if name not in self.__gizmos:
            return
        gizmo = self.__gizmos[name]
        positionMatrix = Math.Matrix()
        positionMatrix.translation = newPos
        gizmo.motor.signal = positionMatrix

    def createLine(self, index, startPos, endPos):
        line = DebugLine(startPos, endPos)
        self.__lines[index] = line

    def updateLine(self, index, startPos, endPos):
        if index not in self.__lines:
            return
        line = self.__lines[index]
        line.set(startPos, endPos)


g_multiTurretDebugGizmo = MultiturretDebugGizmo()
