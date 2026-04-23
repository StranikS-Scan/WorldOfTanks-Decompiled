# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/propellant_gun/mechanic_events.py
from __future__ import absolute_import
import typing
from cache import last_cached_method
from cgf_events import gun_events
from events_handler import eventHandler
from vehicles.components.component_events import VehicleComponentEventsCoreIntegration
from vehicles.mechanics.mechanic_states import MechanicStatesEvents, IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.gun_mechanics.propellant_gun.mechanic_interfaces import IPropellantGunMechanicState

class PropellantStatesEvents(MechanicStatesEvents):

    def _createCoreIntegration(self):
        return PropellantStatesCoreIntegration(self, self._getComponent())


class PropellantStatesCoreIntegration(VehicleComponentEventsCoreIntegration, IMechanicStatesListenerLogic):

    @eventHandler
    def onStatePrepared(self, state):
        self.__postPropellantChangedEvent(state.lastShotTimestamp, state.lastShotCharge)

    @eventHandler
    def onStateObservation(self, state):
        self.__postPropellantChangedEvent(state.lastShotTimestamp, state.lastShotCharge)

    @last_cached_method()
    def __postPropellantChangedEvent(self, lastShotTimestamp, lastShotCharge):
        gun_events.postVehicularVariablesChangedEvent(self._spaceID, self._vehicleID, self._slotName, {'vehicle/gun/lastSingleShotTimeServer': lastShotTimestamp,
         'vehicle/gun/lastShotPropellantProgress': lastShotCharge})
