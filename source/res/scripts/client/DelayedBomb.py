# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DelayedBomb.py
import BigWorld
import CGF
import GenericComponents
import Math
from debug_utils import LOG_DEBUG_DEV
_ADDITIONAL_PITCH = 0.8

class DelayedBomb(BigWorld.Entity):

    def __init__(self):
        super(DelayedBomb, self).__init__()
        LOG_DEBUG_DEV('DelayedBomb created: ID=', self.id)
        self.gameObject = None
        self.isLeaveWorldBeforeLoadGO = False
        return

    def onEnterWorld(self, *args):
        LOG_DEBUG_DEV('DelayedBomb onEnterWorld: ID=', self.id)
        CGF.loadGameObject(self.prefab, self.spaceID, self.position, self._postLoadCallback)

    def _postLoadCallback(self, gameObject):
        if self.isLeaveWorldBeforeLoadGO:
            gameObject.deactivate()
            CGF.removeGameObject(gameObject)
            return
        trComp = gameObject.findComponentByType(GenericComponents.TransformComponent)
        trComp.scale = Math.Vector3(self.size, self.size, self.size)
        trComp.rotation = Math.Vector3(self.hitYaw, self.hitPitch + _ADDITIONAL_PITCH, 0)
        self.gameObject = gameObject

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('DelayedBomb onLeaveWorld: ID=', self.id)
        if self.gameObject is not None:
            self.gameObject.deactivate()
            CGF.removeGameObject(self.gameObject)
            self.gameObject = None
        else:
            self.isLeaveWorldBeforeLoadGO = True
        return
