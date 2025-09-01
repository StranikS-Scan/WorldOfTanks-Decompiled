# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/states.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

def registerStates(machine):
    machine.addState(ShopState())


def registerTransitions(_):
    pass


@SubScopeSubLayerState.parentOf
class ShopState(SFViewLobbyState):
    STATE_ID = 'shop'
    VIEW_KEY = ViewKey(VIEW_ALIAS.LOBBY_STORE)

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.browser.shop()))
