# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_life_cycle/life_cycle_events.py
import typing
import weakref
from Event import LateEvent, SafeEvent
from vehicles.components.component_events import ComponentEvents
from vehicles.components.component_life_cycle.life_cycle_interfaces import IComponentLifeCycleEventsLogic
if typing.TYPE_CHECKING:
    from vehicles.components.component_life_cycle.life_cycle_interfaces import ILifeCycleComponent, IComponentLifeCycleListener

class ComponentLifeCycleEvents(ComponentEvents, IComponentLifeCycleEventsLogic):

    def __init__(self, component):
        super(ComponentLifeCycleEvents, self).__init__()
        self.__component = weakref.proxy(component)
        self.onComponentParamsCollected = LateEvent(self.__lateParamsCollected, self._eventsManager)
        self.onComponentDestroyed = SafeEvent(self._eventsManager)

    def destroy(self):
        self.__component = None
        self.onComponentDestroyed()
        super(ComponentLifeCycleEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self.__lateParamsCollected(listener.onComponentParamsCollected)
        listener.subscribeTo(self)

    def processParamsCollected(self):
        self.onComponentParamsCollected(self.__component)

    def __lateParamsCollected(self, handler):
        if self.__component is not None:
            handler(self.__component)
        return
