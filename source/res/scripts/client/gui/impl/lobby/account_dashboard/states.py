# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/states.py
import typing
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from gui.impl.gen import R
from gui.impl.lobby.account_dashboard.account_dashboard_view import AccountDashboardView

def registerStates(machine):
    machine.addState(AccountDashboardState())


def registerTransitions(machine):
    accountDashboard = machine.getStateByCls(AccountDashboardState)
    machine.addNavigationTransitionFromParent(accountDashboard)


@SubScopeSubLayerState.parentOf
class AccountDashboardState(GuiImplViewLobbyState):
    STATE_ID = 'accountDashboard'
    VIEW_KEY = ViewKey(R.views.lobby.account_dashboard.AccountDashboard())

    def __init__(self):
        super(AccountDashboardState, self).__init__(AccountDashboardView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.account_dashboard()))
