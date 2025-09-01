# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/states.py
import typing
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
from gui.Scaleform.daapi.view.lobby.vehicle_compare.states import VehicleCompareState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.lobby_state_machine.states import LobbyState, SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.blueprints.states import BlueprintState
from helpers.dependency import replace_none_kwargs
from skeletons.gui.shared import IItemsCache

def registerStates(machine):
    machine.addState(TechtreeState())
    machine.addState(ResearchState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(TechtreeState))
    machine.addNavigationTransitionFromParent(machine.getStateByCls(ResearchState))


@SubScopeSubLayerState.parentOf
class TechtreeState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.LOBBY_TECHTREE
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_TECHTREE)

    def registerStates(self):
        self.addChildState(DefaultTechtreeState(flags=StateFlags.INITIAL))
        self.addChildState(BlueprintTechtreeState())

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import ModulesState
        machine = self.getMachine()
        researchState = machine.getStateByCls(ResearchState)
        blueprintState = machine.getStateByCls(BlueprintState)
        blueprintTechTree = machine.getStateByCls(BlueprintTechtreeState)
        defaultTechTree = machine.getStateByCls(DefaultTechtreeState)
        machine.addNavigationTransitionFromParent(defaultTechTree)
        machine.addNavigationTransitionFromParent(blueprintTechTree)
        defaultTechTree.addGuardTransition(defaultTechTree, WeakMethodProxy(self._targetsTechtreeState))
        blueprintTechTree.addGuardTransition(blueprintTechTree, WeakMethodProxy(self._targetsTechtreeState))
        defaultTechTree.addNavigationTransition(defaultTechTree, transitionType=TransitionType.EXTERNAL)
        defaultTechTree.addNavigationTransition(researchState, record=True)
        blueprintTechTree.addNavigationTransition(researchState, record=True)
        blueprintTechTree.addNavigationTransition(blueprintState, record=True)
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


@TechtreeState.parentOf
class BlueprintTechtreeState(LobbyState):
    STATE_ID = 'blueprint'

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub.states import VehicleHubState, OverviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        lsm.getStateByCls(VehicleHubState).addNavigationTransition(self)

    def getBackNavigationDescription(self, params):
        nation = params.get('nation')
        return backport.text(R.strings.menu.viewHeader.backBtn.descrLabel.techtree.dyn(nation).blueprints())

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.techtree.blueprints()))


@SubScopeSubLayerState.parentOf
class ResearchState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.LOBBY_RESEARCH
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_RESEARCH)

    def registerTransitions(self):
        machine = self.getMachine()
        blueprint = machine.getStateByCls(BlueprintState)
        vehiclePostProgression = machine.getStateByCls(VehiclePostProgressionState)
        vehCompare = machine.getStateByCls(VehicleCompareState)
        self.addNavigationTransition(blueprint, record=True)
        self.addNavigationTransition(vehiclePostProgression, record=True)
        self.addNavigationTransition(vehCompare, record=True)

    def _getViewLoadCtx(self, event):
        return {'ctx': {'rootCD': event.params['rootCD']}}

    def serializeParams(self):
        from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
        return {'rootCD': ResearchItemsData.getRootCD()}

    @replace_none_kwargs(itemsCache=IItemsCache)
    def getBackNavigationDescription(self, params, itemsCache=None):
        vehicle = itemsCache.items.getItemByCD(params['rootCD'])
        return backport.text(R.strings.menu.viewHeader.backBtn.descrLabel.research(), tankName=vehicle.shortUserName)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.research()))
