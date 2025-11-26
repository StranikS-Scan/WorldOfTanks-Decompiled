# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/states.py
import logging
import typing
from CurrentVehicle import g_currentVehicle
from frameworks.state_machine import StateFlags
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.easy_tank_equip.easy_tank_equip_view import EasyTankEquipView
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeSubLayerState, LobbyStateDescription
from helpers.events_handler import EventsHandler
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(EasyTankEquipState())


def registerTransitions(machine):
    pass


@SubScopeSubLayerState.parentOf
class EasyTankEquipState(GuiImplViewLobbyState, EventsHandler):
    STATE_ID = 'easyTankEquip'
    VIEW_KEY = ViewKey(R.views.lobby.tanksetup.EasyTankEquipView())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(EasyTankEquipState, self).__init__(EasyTankEquipView, ScopeTemplates.LOBBY_SUB_SCOPE, flags=flags)

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.easyTankEquip()))

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onVehicleChanged),)

    def _onEntered(self, event):
        self._subscribe()
        super(EasyTankEquipState, self)._onEntered(event)

    def _onExited(self):
        super(EasyTankEquipState, self)._onExited()
        self._unsubscribe()

    def __onVehicleChanged(self):
        _logger.info('Vehicle changed while in EasyTankEquipState, navigating back')
        self.goBack()
