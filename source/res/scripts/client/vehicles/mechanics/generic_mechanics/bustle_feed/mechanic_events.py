# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/generic_mechanics/bustle_feed/mechanic_events.py
from __future__ import absolute_import
import logging
from events_handler import eventHandler
from helpers.CallbackDelayer import CallbackDelayer
from vehicles.components.component_events import VehicleComponentEventsCoreIntegration
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic, MechanicStatesEvents
from vehicles.mechanics.generic_mechanics.bustle_feed.mechanic_interfaces import IBustleFeedEventsLogic, IBustleFeedListenerLogic
from vehicle_systems.components.vehicle_variable_storage import update as updateVariable
_logger = logging.getLogger(__name__)
_INIT_VAR_VAL = -1

class BustleFeedStatesEvents(MechanicStatesEvents, IBustleFeedEventsLogic):

    def __init__(self, component, tickInterval):
        super(BustleFeedStatesEvents, self).__init__(component, tickInterval)
        self.onReloadTriggered = self._createEvent()

    def processReloadTriggered(self, shell, side, duration):
        self.onReloadTriggered(shell, side, duration)

    def _createCoreIntegration(self):
        return BustleFeedVfxCoreIntegration(self, self._getComponent())


class BustleFeedVfxCoreIntegration(VehicleComponentEventsCoreIntegration, IMechanicStatesListenerLogic, IBustleFeedListenerLogic):

    def __init__(self, events, component):
        self.__component = component
        self.__callbackDelayer = CallbackDelayer()
        super(BustleFeedVfxCoreIntegration, self).__init__(events, component)

    @eventHandler
    def onReloadTriggered(self, shell, side, duration):
        if self.__updateVariables(shell, side):
            self.__callbackDelayer.delayCallback(duration, self.__updateVariablesDelayed, _INIT_VAR_VAL, _INIT_VAR_VAL)

    @eventHandler
    def onEventsContainerDestroy(self, events):
        self.__callbackDelayer.destroy()
        self.__updateVariables(_INIT_VAR_VAL, _INIT_VAR_VAL)
        self.__component = None
        super(BustleFeedVfxCoreIntegration, self).onEventsContainerDestroy(events)
        return

    def __updateVariables(self, shell, side):
        varStorageGO = self.__component.getVariableStorageGO()
        if varStorageGO is not None:
            updateVariable(varStorageGO, 'vehicle/bustleFeed/side', side)
            updateVariable(varStorageGO, 'vehicle/bustleFeed/shell', shell)
            return True
        else:
            _logger.warning('__updateVariables: no GO with VariableStorageComponent')
            return False

    def __updateVariablesDelayed(self, shell, side):
        self.__updateVariables(shell, side)
