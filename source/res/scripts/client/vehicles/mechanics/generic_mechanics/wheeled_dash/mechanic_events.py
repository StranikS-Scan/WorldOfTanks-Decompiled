# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/wheeled_dash/mechanic_events.py
from __future__ import absolute_import
from events_containers.common.containers import ClientEventsContainer, ClientEventsContainerDebugger
from vehicles.mechanics.generic_mechanics.wheeled_dash.mechanic_interfaces import IWheeledDashEventsLogic

class WheeledDashMiscEvents(ClientEventsContainer, IWheeledDashEventsLogic):

    def __init__(self):
        super(WheeledDashMiscEvents, self).__init__()
        self.onImpulseStarted = self._createEvent()

    def _createEventsDebugger(self):
        return WheeledDashMiscEventsDebugger(self)


class WheeledDashMiscEventsDebugger(ClientEventsContainerDebugger):
    IGNORED_EVENTS = ClientEventsContainerDebugger.IGNORED_EVENTS + ('onImpulseStarted',)
    _EVENTS_DEBUG_PREFIX = 'WHEELED_DASH_MISC'
