# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_containers/components/life_cycle/events.py
from __future__ import absolute_import
import typing
import weakref
from events_containers.common.containers import ClientEventsContainer
from events_containers.components.common import ClientComponentEventsDebugger
from events_containers.components.life_cycle.interfaces import IComponentLifeCycleEventsLogic
if typing.TYPE_CHECKING:
    from events_containers.components.life_cycle.interfaces import ILifeCycleComponent, IComponentLifeCycleListener

class ComponentLifeCycleEvents(ClientEventsContainer, IComponentLifeCycleEventsLogic):

    def __init__(self, component):
        super(ComponentLifeCycleEvents, self).__init__()
        self.__componentRef = weakref.ref(component)
        self.__isParamsCollected = False
        self.onComponentParamsCollected = self._createLateEvent(self.__lateParamsCollected)
        self.onComponentDestroyed = self._createEvent()

    def destroy(self):
        self.onComponentDestroyed(self._getComponent())
        self.__componentRef, self.__isParamsCollected = None, False
        super(ComponentLifeCycleEvents, self).destroy()
        return

    def lateSubscribe(self, listener):
        self.__lateParamsCollected(listener.onComponentParamsCollected)
        super(ComponentLifeCycleEvents, self).lateSubscribe(listener)

    def processParamsCollected(self):
        self.__isParamsCollected = True
        self.onComponentParamsCollected(self._getComponent().getComponentParams())

    def _createEventsDebugger(self):
        return ComponentLifeCycleEventsDebugger(self, self._getComponent())

    def _getComponent(self):
        return self.__componentRef() if self.__componentRef is not None else None

    def __lateParamsCollected(self, handler):
        if self.__isParamsCollected and self._getComponent() is not None:
            handler(self._getComponent().getComponentParams())
        return


class ComponentLifeCycleEventsDebugger(ClientComponentEventsDebugger):
    _EVENTS_DEBUG_PREFIX = 'COMPONENT_LC'

    def onComponentDestroyed(self, _):
        self.onDestroyed()
