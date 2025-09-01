# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_life_cycle/__init__.py
from vehicles.components.component_life_cycle.custom_integrations import ComponentLifeCycleLogger
from vehicles.components.component_life_cycle.life_cycle_events import ComponentLifeCycleEvents
from vehicles.components.component_life_cycle.life_cycle_interfaces import ILifeCycleComponent, IComponentLifeCycleEvents, IComponentLifeCycleListener, IComponentLifeCycleListenerLogic
__all__ = ('ILifeCycleComponent', 'IComponentLifeCycleEvents', 'IComponentLifeCycleListener', 'IComponentLifeCycleListenerLogic', 'ComponentLifeCycleEvents', 'ComponentLifeCycleLogger', 'createComponentLifeCycleEvents')

def createComponentLifeCycleEvents(component):
    componentLifeCycleEvents = ComponentLifeCycleEvents(component)
    ComponentLifeCycleLogger().subscribeTo(componentLifeCycleEvents)
    return componentLifeCycleEvents
