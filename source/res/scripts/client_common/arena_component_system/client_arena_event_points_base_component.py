# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/client_arena_event_points_base_component.py
from client_arena_component_system import ClientArenaComponent

class EventPointsBaseComponent(ClientArenaComponent):
    eventPointBase = property(lambda self: self.__eventPointBase)

    def __init__(self, componentSystem):
        super(EventPointsBaseComponent, self).__init__(componentSystem)
        self.__eventPointBase = None
        return

    def destroy(self):
        super(EventPointsBaseComponent, self).destroy()
        self.__eventPointBase = None
        return

    def init(self, eventPointBase):
        self.__eventPointBase = eventPointBase

    def clear(self):
        self.__eventPointBase = None
        return

    def isInitialized(self):
        return self.__eventPointBase is not None

    @property
    def radius(self):
        return self.__eventPointBase.radius

    @property
    def position(self):
        return self.__eventPointBase.position
