# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/states.py
import typing
from frameworks.state_machine import StateFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.vehicle_hub import OverviewState
from gui.impl.lobby.vehicle_hub.states import VehicleHubState
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyStateDescription, SubScopeSubLayerState
from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from open_bundle.gui.impl.lobby.main_view import MainView
from open_bundle.gui.shared.event_dispatcher import showIntro
from open_bundle.helpers.resources import getTextResource
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

def registerStates(machine):
    machine.addState(OpenBundleState())


def registerTransitions(machine):
    openBundleState = machine.getStateByCls(OpenBundleState)
    machine.addNavigationTransitionFromParent(openBundleState)
    openBundleState.addNavigationTransition(machine.getStateByCls(StylePreviewState), record=True)
    openBundleState.addNavigationTransition(machine.getStateByCls(OverviewState), record=True)
    machine.getStateByCls(VehicleHubState).addNavigationTransition(openBundleState)


@SubScopeSubLayerState.parentOf
class OpenBundleState(GuiImplViewLobbyState):
    STATE_ID = 'openBundle'
    VIEW_KEY = ViewKey(R.views.open_bundle.mono.lobby.main())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(OpenBundleState, self).__init__(MainView, flags=flags, scope=ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__params = {}

    def getNavigationDescription(self):
        text = R.strings.open_bundle_lobby_default.bundle.name_uppercased
        if self.__params.get('bundleID') is not None:
            text = getTextResource(self.__params.get('bundleID'), ('bundle', 'name_uppercased'))
        return LobbyStateDescription(title=backport.text(text()), infos=(LobbyStateDescription.Info(tooltipBody=backport.text(R.strings.open_bundle_lobby_default.tooltips.header.info()), onMoreInfoRequested=lambda : showIntro(self.__params.get('bundleID'))),))

    def serializeParams(self):
        return {'bundleID': self.__params.get('bundleID')}

    def _onEntered(self, event):
        super(OpenBundleState, self)._onEntered(event)
        self.__params = event.params
