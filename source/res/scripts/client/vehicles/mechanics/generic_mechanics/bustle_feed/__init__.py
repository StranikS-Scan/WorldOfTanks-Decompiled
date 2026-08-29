# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/bustle_feed/__init__.py
from __future__ import absolute_import
import typing
from constants import SERVER_TICK_LENGTH
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.generic_mechanics.bustle_feed.mechanic_events import BustleFeedStatesEvents
from vehicles.mechanics.generic_mechanics.bustle_feed.mechanic_models import BustleFeedComponentParams, BustleFeedState, BustleFeedAmmoState, BustleFeedAmmoMode
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states.mechanic_interfaces import IMechanicStatesComponent
__all__ = ('BustleFeedStatesEvents', 'BustleFeedComponentParams', 'BustleFeedState', 'BustleFeedAmmoState', 'BustleFeedAmmoMode', 'DEFAULT_BUSTLE_FEED_PARAMS', 'createBustleFeedStatesEvents')
DEFAULT_BUSTLE_FEED_PARAMS = BustleFeedComponentParams(0, (), 1.0)

@activateEventsContainer()
def createBustleFeedStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    return BustleFeedStatesEvents(component, tickInterval)
