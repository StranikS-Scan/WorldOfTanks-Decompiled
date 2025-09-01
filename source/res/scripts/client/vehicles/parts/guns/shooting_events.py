# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/shooting_events.py
import typing
import weakref
from Event import EventManager, LateEvent, SafeEvent
from vehicles.components.component_events import ComponentEvents
from vehicles.parts.guns.guns_interfaces import IGunShootingEvents
if typing.TYPE_CHECKING:
    from vehicles.parts.guns.guns_interfaces import IGunComponent

class GunShootingEvents(ComponentEvents, IGunShootingEvents):

    def __init__(self, component):
        super(GunShootingEvents, self).__init__()
        self.__component = weakref.proxy(component)
        self.__isAppearanceReady = False
        self.__eventsManager = EventManager()
        self.onAppearanceReady = LateEvent(self.__lateAppearanceReady, self.__eventsManager)
        self.onDiscreteShot = SafeEvent(self.__eventsManager)
        self.onMultiShot = SafeEvent(self.__eventsManager)

    def destroy(self):
        self.__component = None
        self.__eventsManager.clear()
        super(GunShootingEvents, self).destroy()
        return

    def processAppearanceReady(self):
        self.__isAppearanceReady = True
        self.onAppearanceReady()

    def processDiscreteShot(self, gunIndex):
        self.onDiscreteShot(gunIndex)

    def processMultiShot(self, gunIndexes):
        self.onMultiShot(gunIndexes)

    def __lateAppearanceReady(self, handler):
        if self.__isAppearanceReady:
            handler()
