# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EmptyEntity.py
import BigWorld

class EmptyEntity(BigWorld.Entity):

    def __init__(self):
        super(EmptyEntity, self).__init__()
        self.filter = BigWorld.AvatarFilter()

    def onLeaveWorld(self):
        pass
