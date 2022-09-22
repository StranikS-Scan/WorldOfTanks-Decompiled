# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EmptyEntity.py
import BigWorld
from cgf_script.entity_dyn_components import BWEntitiyComponentTracker

class EmptyEntity(BigWorld.Entity, BWEntitiyComponentTracker):

    def __init__(self):
        super(EmptyEntity, self).__init__()
        self.filter = BigWorld.AvatarFilter()

    def onLeaveWorld(self):
        pass

    def drawEdge(self):
        pass

    def removeEdge(self):
        pass

    def isAlive(self):
        return False
