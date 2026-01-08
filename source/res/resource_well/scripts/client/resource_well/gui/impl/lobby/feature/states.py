# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/states.py
from __future__ import absolute_import
from typing import Optional
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import VehiclePreviewState as BaseVehiclePreviewState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.states import HangarState
from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
from gui.lobby_state_machine.states import SubScopeSubLayerState, LobbyStateDescription, ViewLobbyState
from resource_well.gui.shared.event_dispatcher import openInfoPageScreen

def registerStates(machine):
    machine.addState(ProgressionState())
    machine.addState(ProgressionCompletedState())
    machine.addState(VehiclePreviewState())


def registerTransitions(machine):
    from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
    hangar = machine.getStateByCls(HangarState)
    progressionState = machine.getStateByCls(ProgressionState)
    completedState = machine.getStateByCls(ProgressionCompletedState)
    progressionState.addNavigationTransition(completedState)
    machine.addNavigationTransitionFromParent(completedState)
    machine.addNavigationTransitionFromParent(progressionState)
    vehiclePreviewState = machine.getStateByCls(VehiclePreviewState)
    progressionState.addNavigationTransition(vehiclePreviewState, record=True)
    hangar.addNavigationTransition(progressionState)
    hangar.addNavigationTransition(completedState)
    shop = machine.getStateByCls(ShopState)
    shop.addNavigationTransition(progressionState, record=True)
    shop.addNavigationTransition(completedState, record=True)


class BaseProgressionState(ViewLobbyState):

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.resource_well.mainView.navbar.backBtn())

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.resource_well.mainView.navbar.title()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=openInfoPageScreen, tooltipBody=backport.text(R.strings.resource_well.tooltips.mainView.info_tip.body())),))


@SubScopeSubLayerState.parentOf
class ProgressionState(BaseProgressionState):
    STATE_ID = 'resourceWell/progression'
    VIEW_KEY = ViewKey(VIEW_ALIAS.RESOURCE_WELL_PROGRESSION)


@SubScopeSubLayerState.parentOf
class ProgressionCompletedState(BaseProgressionState):
    STATE_ID = 'resourceWell/completed'
    VIEW_KEY = ViewKey(VIEW_ALIAS.RESOURCE_WELL_COMPLETED_PROGRESSION)


@SubScopeSubLayerState.parentOf
class VehiclePreviewState(BaseVehiclePreviewState):
    STATE_ID = VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW)

    def _getViewLoadCtx(self, event):
        params = super(VehiclePreviewState, self)._getViewLoadCtx(event)
        params['ctx'].update({'rewardID': event.params.get('rewardID', None),
         'numberStyle': event.params.get('numberStyle', None)})
        return params

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.vehicle_hub()))
