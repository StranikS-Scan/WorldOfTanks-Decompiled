# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/states.py
import typing
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.profile.ProfilePage import ProfilePage

def registerStates(machine):
    machine.addState(ServiceRecordState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(ServiceRecordState))


@SubScopeSubLayerState.parentOf
class ServiceRecordState(SFViewLobbyState):
    STATE_ID = VIEW_ALIAS.LOBBY_PROFILE
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_PROFILE)
    __appLoader = dependency.descriptor(IAppLoader)

    def registerTransitions(self):
        from gui.impl.lobby.vehicle_hub import OverviewState, ModulesState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(ModulesState), record=True)

    def serializeParams(self):
        view = self.getMachine().getRelatedView(self)
        tabId = view.tabId
        return {'ctx': {'selectedAlias': tabId}} if tabId else {}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.service_record()))
