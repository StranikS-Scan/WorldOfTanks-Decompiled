# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/entity_world_object.py
from __future__ import absolute_import
import BigWorld

class EntityWorldObject(BigWorld.Entity):

    def __init__(self):
        self.worldObject = None
        return

    def onEnterWorld(self, *args):
        self.worldObject = self._loadWorldObject()

    def onLeaveWorld(self):
        if self.worldObject is not None:
            self.worldObject.deactivate()
            self.worldObject.destroy()
            self.worldObject.stopLoading = True
            self.worldObject = None
        return

    def _loadWorldObject(self):
        raise NotImplementedError

    def _registerWorldObject(self, worldObject):
        self.worldObject = worldObject
        self.worldObject.setMotor(self.matrix)
        self.worldObject.activate()
