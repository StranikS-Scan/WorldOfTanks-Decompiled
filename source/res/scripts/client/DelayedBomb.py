# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DelayedBomb.py
import BigWorld
import CGF
import GenericComponents
import Math
from constants import ArtilleryZoneType
from debug_utils import LOG_DEBUG_DEV
from items import vehicles
_ADDITIONAL_PITCH = 0.8
_DELAYED_BOMB_PREFAB = 'content/CGFPrefabs/Battle/Consumables/bomb.prefab'

class DelayedBomb(BigWorld.Entity):

    def __init__(self):
        super(DelayedBomb, self).__init__()
        LOG_DEBUG_DEV('DelayedBomb created: ID=', self.id)
        self.player = BigWorld.player()
        self.gameObject = None
        self.isLeaveWorldBeforeLoadGO = False
        return

    def onEnterWorld(self, *args):
        LOG_DEBUG_DEV('DelayedBomb onEnterWorld: ID=', self.id)
        CGF.loadGameObject(_DELAYED_BOMB_PREFAB, self.spaceID, self.position, self._postLoadCallback)
        prayer = BigWorld.player()
        if not prayer:
            return
        shellDescr = vehicles.getItemByCompactDescr(self.shellCompDescr)
        delayedShellDescr = vehicles.getItemByCompactDescr(shellDescr.type.delayedShell)
        self.player.addArtilleryShotZone(self.shotID, shellDescr.type.explosionDelay, self.position, delayedShellDescr.type.explosionRadius, ArtilleryZoneType.FRIENDLY if self.team == self.player.team else ArtilleryZoneType.EXPLOSION)

    def _postLoadCallback(self, gameObject):
        if not self.inWorld:
            CGF.removeGameObject(gameObject)
            if self.player:
                self.player.removeArtilleryShotZone(self.shotID)
            return
        trComp = gameObject.findComponentByType(GenericComponents.TransformComponent)
        size = vehicles.getItemByCompactDescr(self.shellCompDescr).type.size
        trComp.scale = Math.Vector3(size, size, size)
        trComp.rotation = Math.Vector3(self.yaw, self.pitch + _ADDITIONAL_PITCH, 0)
        self.gameObject = gameObject

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('DelayedBomb onLeaveWorld: ID=', self.id)
        if self.gameObject is not None:
            CGF.removeGameObject(self.gameObject)
            self.gameObject = None
            if self.player:
                self.player.removeArtilleryShotZone(self.shotID)
        else:
            self.isLeaveWorldBeforeLoadGO = True
        return
