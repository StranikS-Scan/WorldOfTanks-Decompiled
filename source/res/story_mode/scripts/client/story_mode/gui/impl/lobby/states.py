# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/states.py
import typing
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeSubLayerState, LobbyStateFlags, LobbyStateDescription
from gui.lobby_state_machine.transitions import HijackTransition
from helpers import dependency
from story_mode.gui.impl.lobby.mission_selection_view import MissionSelectionView
from story_mode.skeletons.story_mode_controller import IStoryModeController

def registerStates(machine):
    machine.addState(StoryModeState())


def registerTransitions(machine):
    from gui.impl.lobby.hangar.states import HangarState
    storyMode = machine.getStateByCls(StoryModeState)
    parent = machine.getStateByCls(StoryModeState).getParent()
    parent.addTransition(HijackTransition(HangarState, _shallNavigateToStoryModeHangar, transitionType=TransitionType.EXTERNAL), storyMode)


@SubScopeSubLayerState.parentOf
class StoryModeState(GuiImplViewLobbyState):
    STATE_ID = 'storyMode'
    VIEW_KEY = ViewKey(MissionSelectionView.LAYOUT_ID)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(StoryModeState, self).__init__(MissionSelectionView, flags=flags | LobbyStateFlags.HANGAR, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.sm_lobby.headerButtons.battle.types.story_mode()))


@dependency.replace_none_kwargs(storyModeCtrl=IStoryModeController)
def _shallNavigateToStoryModeHangar(event, storyModeCtrl=None):
    return storyModeCtrl.isEnabled() and storyModeCtrl.isInPrb()
