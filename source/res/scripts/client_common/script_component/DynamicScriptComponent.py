# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/script_component/DynamicScriptComponent.py
import BigWorld
from events_handler import EventsHandler
from events_handler import EventsQuery
import PlayerEvents

class DynamicScriptComponent(BigWorld.DynamicScriptComponent, EventsHandler, EventsQuery):

    def __init__(self):
        BigWorld.DynamicScriptComponent.__init__(self)
        self._subscribeToEvents(self.__getEntityEvents())
        if hasattr(self, 'onAvatarReady'):
            if BigWorld.player().userSeesWorld():
                self.onAvatarReady()
            else:
                PlayerEvents.g_playerEvents.onAvatarReady += self.__onAvatarReady

    def __onAvatarReady(self):
        PlayerEvents.g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.onAvatarReady()

    def onDestroy(self):
        self._unsubscribeFromEvents(self.__getEntityEvents())
        PlayerEvents.g_playerEvents.onAvatarReady -= self.__onAvatarReady

    def onLeaveWorld(self):
        self.onDestroy()

    @property
    def spaceID(self):
        return self.entity.spaceID

    @property
    def keyName(self):
        return next((name for name, value in self.entity.dynamicComponents.iteritems() if value == self))

    def __getEntityEvents(self):
        return self._getEvents(self.entity)
