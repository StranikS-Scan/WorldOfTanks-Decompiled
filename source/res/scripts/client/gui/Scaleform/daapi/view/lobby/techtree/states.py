# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/states.py
from __future__ import absolute_import
import typing
from WeakMethod import WeakMethodProxy
from frameworks_common.state_machine import StateFlags
from frameworks_common.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.vehicle_compare.states import VehicleCompareState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.lobby_state_machine.states import LobbyState, SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from gui.impl import backport
from gui.impl.gen import R

def registerStates(machine):
    machine.addState(TechtreeState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(TechtreeState))


@SubScopeSubLayerState.parentOf
class TechtreeState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.LOBBY_TECHTREE
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_TECHTREE)

    def registerStates(self):
        self.addChildState(DefaultTechtreeState(flags=StateFlags.INITIAL))

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import ModulesState
        machine = self.getMachine()
        defaultTechTree = machine.getStateByCls(DefaultTechtreeState)
        machine.addNavigationTransitionFromParent(defaultTechTree)
        defaultTechTree.addGuardTransition(defaultTechTree, WeakMethodProxy(self._targetsTechtreeState))
        defaultTechTree.addNavigationTransition(defaultTechTree, transitionType=TransitionType.EXTERNAL)
        defaultTechTree.addNavigationTransition(machine.getStateByCls(ModulesState), record=True)

    def _targetsTechtreeState(self, event):
        return event.targetStateID == self.getStateID()

    def _getViewLoadCtx(self, event):
        return {'ctx': {'nation': event.params['nation']}}

    def serializeParams(self):
        return {'nation': SelectedNation.getName()}


@TechtreeState.parentOf
class DefaultTechtreeState(LobbyState):
    STATE_ID = 'default'

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub.states import VehicleHubState, OverviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(VehicleCompareState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        lsm.getStateByCls(VehicleHubState).addNavigationTransition(self)

    def getBackNavigationDescription(self, params):
        nation = params.get('nation')
        return backport.text(R.strings.menu.viewHeader.backBtn.descrLabel.techtree.dyn(nation)())

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.techtree()))
