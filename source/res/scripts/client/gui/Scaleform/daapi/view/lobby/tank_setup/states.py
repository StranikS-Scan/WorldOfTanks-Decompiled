# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/states.py
import logging
import typing
from WeakMethod import WeakMethodProxy
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.lobby_state_machine.states import SubScopeTopLayerState, SFViewLobbyState, TopScopeTopLayerState, LobbyState, LobbyStateDescription
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from helpers.dependency import replace_none_kwargs
from skeletons.gui.app_loader import IAppLoader
from wg_async import wg_async, BrokenPromiseError
if typing.TYPE_CHECKING:
    from gui.impl.lobby.tank_setup.ammunition_setup.base import BaseAmmunitionSetupView
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(LegacyAmmunitionState())
    machine.addState(LegacyAmmunitionConfirmationState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(LegacyAmmunitionState))


@replace_none_kwargs(appLoader=IAppLoader)
def _getAmmunitionSubView(appLoader=None):
    app = appLoader.getApp()
    view = app.containerManager.getViewByKey(LegacyAmmunitionState.VIEW_KEY)
    return None if not view else view.injectedView


@SubScopeTopLayerState.parentOf
class LegacyAmmunitionState(SFViewLobbyState):
    STATE_ID = 'legacyAmmunition'
    VIEW_KEY = ViewKey(VIEW_ALIAS.AMMUNITION_SETUP_VIEW)

    def registerTransitions(self):
        lsm = self.getMachine()
        self.addGuardTransition(lsm.getStateByCls(LegacyAmmunitionConfirmationState), WeakMethodProxy(self._hasChanges))

    def _hasChanges(self, _):
        ammunitionSubView = _getAmmunitionSubView()
        return ammunitionSubView.hasChanged() if ammunitionSubView else False


@TopScopeTopLayerState.parentOf
class LegacyAmmunitionConfirmationState(LobbyState):
    STATE_ID = 'legacyAmmuntionConfirmLeave'

    def getNavigationDescription(self):
        return None

    @wg_async
    def _onEntered(self, event):
        super(LegacyAmmunitionConfirmationState, self)._onEntered(event)
        ammunitionSubView = _getAmmunitionSubView()
        if not ammunitionSubView:
            self.__continueOriginalNavigation(event)
            return
        try:
            proceed = yield ammunitionSubView.canQuit()
            if proceed:
                self.__continueOriginalNavigation(event)
            else:
                self.goBack()
        except BrokenPromiseError:
            _logger.debug('%s dialog closed without user decision.', self.__class__.__name__)

    def __continueOriginalNavigation(self, event):
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.CLOSE_VIEW), EVENT_BUS_SCOPE.LOBBY)
        self.getMachine().post(event)
