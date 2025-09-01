# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/states.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.gen import R
from gui.impl.lobby.clan_supply.main_view import MainView
from gui.lobby_state_machine.states import SubScopeSubLayerState, GuiImplViewLobbyState

def registerStates(machine):
    machine.addState(ClanSupplyState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(ClanSupplyState))


@SubScopeSubLayerState.parentOf
class ClanSupplyState(GuiImplViewLobbyState):
    STATE_ID = 'clanSupply'
    VIEW_KEY = ViewKey(R.views.lobby.clan_supply.ClanSupply())

    def __init__(self):
        super(ClanSupplyState, self).__init__(MainView, ScopeTemplates.LOBBY_SUB_SCOPE)

    @classmethod
    def goTo(cls, tabId, **params):
        super(ClanSupplyState, cls).goTo(tabId=tabId, **params)

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import OverviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
