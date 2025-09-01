# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/currency_reserves/states.py
import typing
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeTopLayerState, LobbyStateDescription
from gui.impl.gen import R
from gui.impl.lobby.currency_reserves.currency_reserves_view import CurrencyReservesView

def registerStates(machine):
    machine.addState(CurrencyReservesState())


def registerTransitions(machine):
    currencyReserves = machine.getStateByCls(CurrencyReservesState)
    machine.addNavigationTransitionFromParent(currencyReserves)


@SubScopeTopLayerState.parentOf
class CurrencyReservesState(GuiImplViewLobbyState):
    STATE_ID = 'currencyReserves'
    VIEW_KEY = ViewKey(R.views.lobby.currency_reserves.CurrencyReserves())

    def __init__(self):
        super(CurrencyReservesState, self).__init__(CurrencyReservesView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.currency_reserves()))
