# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/mode_selector/states.py
from __future__ import absolute_import
from frameworks.state_machine import StateFlags
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from fun_random.gui.impl.lobby.mode_selector.fun_sub_selector_view import FunModeSubSelectorView
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.states import ModeSelectorState, EntryState
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyStateDescription
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams

def registerStates(machine):
    machine.addState(FunRandomSubSelectorState())


def registerTransitions(machine):
    pass


@ModeSelectorState.parentOf
class FunRandomSubSelectorState(GuiImplViewLobbyState):
    STATE_ID = 'fun_random_sub_selector'
    VIEW_KEY = ViewKey(R.views.fun_random.lobby.feature.FunRandomModeSubSelector())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FunRandomSubSelectorState, self).__init__(FunModeSubSelectorView, flags=flags, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

    def registerTransitions(self):
        machine = self.getMachine()
        entry = machine.getStateByCls(EntryState)
        funSubSelector = machine.getStateByCls(FunRandomSubSelectorState)
        entry.addNavigationTransition(funSubSelector, record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(FunAssetPacksMixin.getModeUserName())

    def _getViewLoadCtx(self, event):
        return {}

    def _getViewLoadParams(self, event):
        return GuiImplViewLoadParams(self.VIEW_KEY.alias, self._viewImplClass, self._scope, event.params.get('parent'))
