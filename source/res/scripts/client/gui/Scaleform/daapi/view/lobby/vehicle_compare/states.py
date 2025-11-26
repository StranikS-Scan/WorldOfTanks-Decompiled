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
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket

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
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import VehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import TradeInVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import RentalVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import HeroTankPreviewState
        machine = self.getMachine()
        self.addNavigationTransition(machine.getStateByCls(VehicleCompareConfiguratorState), record=True)
        self.addNavigationTransition(machine.getStateByCls(VehiclePreviewState), record=True)
        self.addNavigationTransition(machine.getStateByCls(TradeInVehiclePreviewState), record=True)
        self.addNavigationTransition(machine.getStateByCls(RentalVehiclePreviewState), record=True)
        self.addNavigationTransition(machine.getStateByCls(HeroTankPreviewState), record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.vehicle_compare()))

    def _onEntered(self, event):
        super(VehicleCompareState, self)._onEntered(event)
        if not self.comparisonBasket.isAvailable():
            showHangar()


@SubScopeSubLayerState.parentOf
class VehicleCompareConfiguratorState(ViewLobbyState):
    STATE_ID = VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR
    VIEW_KEY = ViewKey(VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

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
        if not self.comparisonBasket.isAvailable():
            showHangar()

    def _onExited(self):
        super(VehicleCompareConfiguratorState, self)._onExited()
        self.__cachedParams = {}

    def _getViewLoadCtx(self, event):
        return {'ctx': {'index': event.params['index']}}
