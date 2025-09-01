# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily_experience/states.py
import typing
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.lobby.daily_experience.daily_experience_view import DailyExperienceView
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeTopLayerState, LobbyStateDescription
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

def registerStates(machine):
    machine.addState(DailyExperienceState())


def registerTransitions(machine):
    state = machine.getStateByCls(DailyExperienceState)
    machine.addNavigationTransitionFromParent(state)


@SubScopeTopLayerState.parentOf
class DailyExperienceState(GuiImplViewLobbyState):
    STATE_ID = 'dailyExperience'
    VIEW_KEY = ViewKey(R.views.lobby.account_dashboard.DailyExperienceView())

    def __init__(self):
        super(DailyExperienceState, self).__init__(DailyExperienceView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.daily_experience()))
