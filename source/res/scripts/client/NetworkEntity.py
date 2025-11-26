# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NetworkEntity.py
import CGF
import BigWorld
from debug_utils import LOG_DEBUG_DEV

class NetworkEntity(BigWorld.Entity):
    ignoreEntityGOSync = True

    def __init__(self):
        super(NetworkEntity, self).__init__()
        self.entityGameObject = None
        return

    def onEnterWorld(self, _):
        if CGF.addNetworkEntity(self.spaceID, self, self.unique_id, self.prefab_path):
            direction = (self.yaw, self.pitch, self.roll)
            LOG_DEBUG_DEV('New NetworkEntity [{}][{}] position {} rotation {} scale {}'.format(self.id, self.unique_id, self.position, direction, self.scale))

    def onLeaveWorld(self):
        if self.entityGameObject and self.prefab_path:
            CGF.removeGameObject(self.entityGameObject)
        self.entityGameObject = None
        if CGF.removeNetworkEntity(self.spaceID, self, self.unique_id):
            LOG_DEBUG_DEV('Removed NetworkEntity [{}]'.format(self.id))
        return

    @property
    def gameObject(self):
        return self.entityGameObject

    @property
    def isConnected(self):
        return self.entityGameObject is not None

    def onDynamicComponentCreated(self, component):
        if not self.isConnected:
            return
        self.__processAddComponent(self.entityGameObject, component)

    def onDynamicComponentDestroyed(self, component):
        if not self.isConnected:
            return
        self.__processRemoveComponent(self.entityGameObject, component)

    @staticmethod
    def __processAddComponent(go, component):
        if not go.isValid():
            return
        else:
            existing = go.findComponentByType(type(component))
            if existing is None:
                go.addComponent(component)
            return

    @staticmethod
    def __processRemoveComponent(go, component):
        if not go.isValid():
            return
        existing = go.findComponentByType(type(component))
        if existing is component:
            go.removeComponent(component)
