# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wot_plus/states.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SFViewLobbyState, TopScopeTopLayerState, LobbyStateDescription
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

def registerStates(machine):
    machine.addState(WotPlusInfoState())


def registerTransitions(_):
    pass


@TopScopeTopLayerState.parentOf
class WotPlusInfoState(SFViewLobbyState):
    STATE_ID = 'wotPlusInfo'
    VIEW_KEY = ViewKey(VIEW_ALIAS.WOT_PLUS_INFO_VIEW)

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(backport.text(R.strings.pages.titles.browser.wotplus_info()))
