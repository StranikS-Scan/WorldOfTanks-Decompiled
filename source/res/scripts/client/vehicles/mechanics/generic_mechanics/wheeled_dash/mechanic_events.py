# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/wheeled_dash/mechanic_events.py
from __future__ import absolute_import
from events_containers.common.containers import ClientEventsContainer
from vehicles.mechanics.generic_mechanics.wheeled_dash.mechanic_interfaces import IWheeledDashEventsLogic

class WheeledDashStateEvents(ClientEventsContainer, IWheeledDashEventsLogic):

    def __init__(self):
        super(WheeledDashStateEvents, self).__init__()
        self.onImpulseStarted = self._createEvent()
