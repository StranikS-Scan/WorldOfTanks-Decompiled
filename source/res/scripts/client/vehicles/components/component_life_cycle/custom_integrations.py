# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_life_cycle/custom_integrations.py
import typing
import logging
from events_handler import eventHandler
from vehicles.components.component_events import ComponentListener
from vehicles.components.component_life_cycle.life_cycle_interfaces import IComponentLifeCycleListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.components.component_life_cycle.life_cycle_interfaces import ILifeCycleComponent, IComponentLifeCycleEvents
_logger = logging.getLogger(__name__)

class ComponentLifeCycleLogger(ComponentListener, IComponentLifeCycleListenerLogic):

    @eventHandler
    def onComponentParamsCollected(self, component):
        _logger.debug('onComponentParamsCollected %s', component)
        super(ComponentLifeCycleLogger, self).onComponentParamsCollected(component)

    @eventHandler
    def onComponentEventsDestroy(self, events):
        _logger.debug('onComponentEventsDestroy %s', events)
        super(ComponentLifeCycleLogger, self).onComponentEventsDestroy(events)
