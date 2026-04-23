# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/wheeled_dash/mechanic_interfaces.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import IClientEventsContainer
if typing.TYPE_CHECKING:
    from constants import WheeledDashDirection

class IWheeledDashEventsLogic(object):
    onImpulseStarted = None


class IWheeledDashListenerLogic(object):

    def onImpulseStarted(self, direction):
        pass


class IWheeledDashEvents(IClientEventsContainer, IWheeledDashEventsLogic):
    pass
