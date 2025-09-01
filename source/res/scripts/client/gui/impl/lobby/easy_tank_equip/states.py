# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/states.py
import typing
from frameworks.state_machine import StateFlags
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.easy_tank_equip.easy_tank_equip_view import EasyTankEquipView
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeSubLayerState, LobbyStateDescription

def registerStates(machine):
    machine.addState(EasyTankEquipState())


def registerTransitions(machine):
    pass


@SubScopeSubLayerState.parentOf
class EasyTankEquipState(GuiImplViewLobbyState):
    STATE_ID = 'easyTankEquip'
    VIEW_KEY = ViewKey(R.views.lobby.tanksetup.EasyTankEquipView())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(EasyTankEquipState, self).__init__(EasyTankEquipView, ScopeTemplates.LOBBY_SUB_SCOPE, flags=flags)

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.easyTankEquip()))
