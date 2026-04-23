# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/temperature/common/mechanic_events.py
from __future__ import absolute_import
import typing
from cache import last_cached_method
from cgf_events import gun_events
from events_handler import eventHandler
from vehicles.components.component_events import VehicleComponentEventsCoreIntegration
from vehicles.mechanics.mechanic_states import MechanicStatesEvents, IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.gun_mechanics.temperature.common.mechanic_interfaces import ITemperatureMechanicState

class TemperatureStatesEvents(MechanicStatesEvents):

    def _createCoreIntegration(self):
        return TemperatureStatesCoreIntegration(self, self._getComponent())


class TemperatureStatesCoreIntegration(VehicleComponentEventsCoreIntegration, IMechanicStatesListenerLogic):

    @eventHandler
    def onStatePrepared(self, state):
        self.__postTemperatureChangedEvent(state.temperatureProgress)

    @eventHandler
    def onStateTick(self, state):
        self.__postTemperatureChangedEvent(state.temperatureProgress)

    @last_cached_method()
    def __postTemperatureChangedEvent(self, temperatureProgress):
        gun_events.postVehicularVariablesChangedEvent(self._spaceID, self._vehicleID, self._slotName, {'vehicle/gun/temperature': temperatureProgress})
