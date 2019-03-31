# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/OfflineEntity.py
# Compiled at: 2009-11-30 20:10:57
import BigWorld

class OfflineEntity(BigWorld.Entity):

    def __init__(self):
        pass

    def prerequisites(self):
        return []

    def onEnterWorld(self, prereqs):
        BigWorld.addShadowEntity(self)

    def onLeaveWorld(self):
        BigWorld.delShadowEntity(self)
