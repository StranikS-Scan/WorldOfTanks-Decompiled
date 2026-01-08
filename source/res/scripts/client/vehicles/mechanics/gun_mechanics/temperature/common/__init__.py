# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/common/__init__.py
from __future__ import absolute_import
import typing
from constants import SERVER_TICK_LENGTH
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.gun_mechanics.temperature.common.mechanic_interfaces import ITemperatureComponentParams, ITemperatureMechanicState
from vehicles.mechanics.gun_mechanics.temperature.common.mechanic_events import TemperatureStatesEvents
from vehicles.mechanics.gun_mechanics.temperature.common.mechanic_models import TemperatureComponentParams, TemperatureMechanicState
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
__all__ = ('ITemperatureComponentParams', 'ITemperatureMechanicState', 'TemperatureComponentParams', 'TemperatureMechanicState', 'TemperatureStatesEvents', 'createTemperatureStatesEvents')

@activateEventsContainer()
def createTemperatureStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    return TemperatureStatesEvents(component, tickInterval)
