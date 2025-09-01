# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/states.py
from __future__ import absolute_import
import typing
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SubScopeSubLayerState, ViewLobbyState, LobbyStateDescription

def registerStates(machine):
    machine.addState(VehicleCompareState())
    machine.addState(VehicleCompareConfiguratorState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(VehicleCompareState))
    machine.addNavigationTransitionFromParent(machine.getStateByCls(VehicleCompareConfiguratorState))


@SubScopeSubLayerState.parentOf
class VehicleCompareState(ViewLobbyState):
    STATE_ID = VIEW_ALIAS.VEHICLE_COMPARE
    VIEW_KEY = ViewKey(VIEW_ALIAS.VEHICLE_COMPARE)

    def registerTransitions(self):
        machine = self.getMachine()
        configurator = machine.getStateByCls(VehicleCompareConfiguratorState)
        self.addNavigationTransition(configurator, record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.vehicle_compare()))


@SubScopeSubLayerState.parentOf
class VehicleCompareConfiguratorState(ViewLobbyState):
    STATE_ID = VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR
    VIEW_KEY = ViewKey(VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(VehicleCompareConfiguratorState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
        machine = self.getMachine()
        vehiclePostProgression = machine.getStateByCls(VehiclePostProgressionState)
        self.addNavigationTransition(vehiclePostProgression, record=True)

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.vehicle_compare_configuration()))

    def _onEntered(self, event):
        super(VehicleCompareConfiguratorState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        super(VehicleCompareConfiguratorState, self)._onExited()
        self.__cachedParams = {}

    def _getViewLoadCtx(self, event):
        return {'ctx': {'index': event.params['index']}}
