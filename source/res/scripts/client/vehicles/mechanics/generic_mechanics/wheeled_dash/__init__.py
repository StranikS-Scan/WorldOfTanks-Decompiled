# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/wheeled_dash/__init__.py
from __future__ import absolute_import
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.generic_mechanics.wheeled_dash.mechanic_interfaces import IWheeledDashListenerLogic, IWheeledDashEvents
from vehicles.mechanics.generic_mechanics.wheeled_dash.mechanic_events import WheeledDashMiscEvents
__all__ = ('IWheeledDashListenerLogic', 'IWheeledDashEvents', 'createWheeledDashMiscEvents')

@activateEventsContainer()
def createWheeledDashMiscEvents():
    return WheeledDashMiscEvents()
