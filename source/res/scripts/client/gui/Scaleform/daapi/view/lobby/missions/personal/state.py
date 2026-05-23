# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/state.py
from __future__ import absolute_import
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SubScopeSubLayerState, ViewLobbyState

def registerStates(machine):
    machine.addState(PersonalMissionsAwardsState())
    machine.addState(PersonalMissionsPageState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(PersonalMissionsPageState))


@SubScopeSubLayerState.parentOf
class PersonalMissionsAwardsState(ViewLobbyState):
    STATE_ID = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS
    VIEW_KEY = ViewKey(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS)

    def registerTransitions(self):
        lsm = self.getMachine()
        from gui.impl.lobby.vehicle_hub import OverviewState
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(PersonalMissionsPageState), record=True)

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.rewards())


@SubScopeSubLayerState.parentOf
class PersonalMissionsPageState(ViewLobbyState):
    STATE_ID = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS
    VIEW_KEY = ViewKey(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS)

    @classmethod
    def goTo(cls, operationID=None, branch=None, chainID=None, missionID=None):
        super(PersonalMissionsPageState, cls).goTo(chainID=chainID, operationID=operationID, branch=branch, eventID=missionID)

    def registerTransitions(self):
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(PersonalMissionsAwardsState), record=True)

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.header.backBtn.descrLabel.operation())
