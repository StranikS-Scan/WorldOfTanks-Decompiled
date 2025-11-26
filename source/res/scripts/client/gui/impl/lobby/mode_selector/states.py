# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/states.py
import typing
from frameworks.state_machine import StateFlags
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.battle_session_view import BattleSessionView
from gui.impl.lobby.mode_selector.mode_selector_view import ModeSelectorView
from gui.lobby_state_machine.states import SubScopeTopLayerState, GuiImplViewLobbyState, LobbyState, LobbyStateFlags, LobbyStateDescription
from gui.prb_control.events_dispatcher import g_eventDispatcher

def registerStates(machine):
    machine.addState(ModeSelectorState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(ModeSelectorState))


@SubScopeTopLayerState.parentOf
class ModeSelectorState(LobbyState):
    STATE_ID = 'modeSelector'

    @classmethod
    def goTo(cls, provider=None, subSelectorCallback=None):
        super(ModeSelectorState, cls).goTo(provider=provider, subSelectorCallback=subSelectorCallback)

    def registerStates(self):
        self.addChildState(EntryState(LobbyStateFlags.INITIAL))
        self.addChildState(BattleSessionState())

    def registerTransitions(self):
        entry = self.getMachine().getStateByCls(EntryState)
        battleSession = self.getMachine().getStateByCls(BattleSessionState)
        entry.addNavigationTransition(battleSession, record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.mode_selector()))


@ModeSelectorState.parentOf
class EntryState(GuiImplViewLobbyState):
    STATE_ID = 'entry'
    VIEW_KEY = ViewKey(R.views.lobby.mode_selector.ModeSelectorView())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(EntryState, self).__init__(ModeSelectorView, flags=flags, scope=ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__isNavigationVisible = True

    def getNavigationDescription(self):
        title = backport.text(R.strings.pages.titles.mode_selector()) if self.__isNavigationVisible else u''
        return LobbyStateDescription(title=title)

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.pages.titles.mode_selector())

    def _onEntered(self, event):
        self.__isNavigationVisible = event.params.get('subSelectorCallback') is None
        super(EntryState, self)._onEntered(event)
        return


@ModeSelectorState.parentOf
class BattleSessionState(GuiImplViewLobbyState):
    STATE_ID = 'battleSession'
    VIEW_KEY = ViewKey(BattleSessionView.LAYOUT_ID)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(BattleSessionState, self).__init__(BattleSessionView, flags=flags, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.mode_selector.window.battleSession.title()))

    def _onEntered(self, event):
        super(BattleSessionState, self)._onEntered(event)
        g_eventDispatcher.addSpecBattlesToCarousel()

    def _onExited(self):
        g_eventDispatcher.removeSpecBattlesFromCarousel()
        super(BattleSessionState, self)._onExited()
