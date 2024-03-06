# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/script_component/DynamicScriptComponent.py
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from shared_utils import nextTick
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

class DynamicScriptComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, *_, **__):
        BigWorld.DynamicScriptComponent.__init__(self)
        if self._isAvatarReady:
            nextTick(makeCallbackWeak(self.__onAvatarReady))()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady
        _logger.debug('%s.__init__. EntityID=%s', self.__class__.__name__, self.entity.id)

    @property
    def _isAvatarReady(self):
        return BigWorld.player().userSeesWorld()

    def onDestroy(self):
        _logger.debug('%s.onDestroy. EntityID=%s', self.__class__.__name__, self.entity.id)
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
        if self._isValid:
            self._onAvatarReady()

    @property
    def _isValid(self):
        return not self.entity.isDestroyed and self in self.entity.dynamicComponents.values()
