# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/script_component/DynamicScriptComponent.py
import BigWorld
from debug_utils import LOG_DEBUG
from PlayerEvents import g_playerEvents
from shared_utils import nextTick

class DynamicScriptComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, *_, **__):
        BigWorld.DynamicScriptComponent.__init__(self)
        if self._isAvatarReady:
            nextTick(self._onAvatarReady)()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady
        LOG_DEBUG('%s.__init__. EntityID=%s' % (self.__class__.__name__, self.entity.id))

    @property
    def _isAvatarReady(self):
        return BigWorld.player().userSeesWorld()

    def onDestroy(self):
        LOG_DEBUG('%s.onDestroy. EntityID=%s' % (self.__class__.__name__, self.entity.id))
        g_playerEvents.onAvatarReady -= self.__onAvatarReady

    def onLeaveWorld(self):
        self.onDestroy()

    @property
    def spaceID(self):
        return self.entity.spaceID

    @property
    def keyName(self):
        return next((name for name, value in self.entity.dynamicComponents.iteritems() if value == self))

    def _onAvatarReady(self):
        pass

    def __onAvatarReady(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self._onAvatarReady()
