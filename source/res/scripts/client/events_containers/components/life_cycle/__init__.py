# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_containers/components/life_cycle/__init__.py
from __future__ import absolute_import
import typing
from events_containers.common.container_wrappers import activateEventsContainer
from events_containers.components.life_cycle.events import ComponentLifeCycleEvents
from events_containers.components.life_cycle.interfaces import ILifeCycleComponent, IComponentLifeCycleEvents, IComponentLifeCycleListener, IComponentLifeCycleListenerLogic
__all__ = ('ILifeCycleComponent', 'IComponentLifeCycleEvents', 'IComponentLifeCycleListener', 'IComponentLifeCycleListenerLogic', 'ComponentLifeCycleEvents', 'isLifeCycleComponent', 'createComponentLifeCycleEvents')

def isLifeCycleComponent(component):
    return isinstance(component, ILifeCycleComponent)


@activateEventsContainer()
def createComponentLifeCycleEvents(component, **_):
    return ComponentLifeCycleEvents(component)
