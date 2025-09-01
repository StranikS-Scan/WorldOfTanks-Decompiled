# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/states.py
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.lobby_state_machine.states import SubScopeSubLayerState, ViewLobbyState
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

def registerStates(machine):
    machine.addState(MissionsState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(MissionsState))


@SubScopeSubLayerState.parentOf
class MissionsState(ViewLobbyState):
    STATE_ID = 'missions'
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_MISSIONS)
    __appLoader = dependency.descriptor(IAppLoader)

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import OverviewState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)

    def serializeParams(self):
        ctx = {}
        app = self.__appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        if view:
            ctx['tab'] = view.getCurrentTabAlias()
        return {'ctx': ctx}
