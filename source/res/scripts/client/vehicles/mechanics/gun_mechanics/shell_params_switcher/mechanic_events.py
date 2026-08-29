# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/shell_params_switcher/mechanic_events.py
from __future__ import absolute_import
import typing
from cache import last_cached_method
from cgf_events import gun_events
from events_handler import eventHandler
from vehicles.components.component_events import VehicleComponentEventsCoreIntegration
from vehicles.mechanics.mechanic_states import MechanicStatesEvents, IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.gun_mechanics.shell_params_switcher import IShellParamsSwitcherMechanicState

class ShellParamsSwitcherStatesEvents(MechanicStatesEvents):

    def _createCoreIntegration(self):
        return ShellParamsSwitcherStatesCoreIntegration(self, self._getComponent())


class ShellParamsSwitcherStatesCoreIntegration(VehicleComponentEventsCoreIntegration, IMechanicStatesListenerLogic):

    @eventHandler
    def onStatePrepared(self, state):
        self.__postShellParamsSwitcherChangedEvent(state.isActive, state.lastActiveShotTimestamp)

    @eventHandler
    def onStateObservation(self, state):
        self.__postShellParamsSwitcherChangedEvent(state.isActive, state.lastActiveShotTimestamp)

    @last_cached_method()
    def __postShellParamsSwitcherChangedEvent(self, isActive, lastActiveShotTimestamp):
        gun_events.postVehicularVariablesChangedEvent(self._spaceID, self._vehicleID, self._slotName, {'vehicle/gun/shellParamsSwitcher/isActive': isActive,
         'vehicle/gun/shellParamsSwitcher/lastActiveShotTimestamp': lastActiveShotTimestamp})
