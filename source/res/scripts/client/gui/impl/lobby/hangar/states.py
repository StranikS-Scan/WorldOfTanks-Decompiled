# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/states.py
from __future__ import absolute_import
import logging
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import generateBasicHangarStateClasses, generateBasicLoadoutStateClasses
from gui.lobby_state_machine.states import SubScopeSubLayerState, SFViewLobbyState, LobbyStateFlags
from gui.lobby_state_machine.transitions import HijackTransition
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(HangarState())
    machine.addState(LegacyHangarState())
    machine.addState(LoadoutState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(HangarState), transitionType=TransitionType.EXTERNAL)


@SubScopeSubLayerState.parentOf
class LegacyHangarState(SFViewLobbyState, IPrbListener):
    STATE_ID = VIEW_ALIAS.LEGACY_LOBBY_HANGAR
    VIEW_KEY = ViewKey(VIEW_ALIAS.LEGACY_LOBBY_HANGAR)
    __LEGACY_HANGAR_MODE_FLAGS = {FUNCTIONAL_FLAG.E_SPORT,
     FUNCTIONAL_FLAG.EVENT,
     FUNCTIONAL_FLAG.RANKED,
     FUNCTIONAL_FLAG.TOURNAMENT,
     FUNCTIONAL_FLAG.MAPBOX}

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LegacyHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    def registerTransitions(self):
        self.getParent().addTransition(HijackTransition(HangarState, WeakMethodProxy(self._shouldHijack), transitionType=TransitionType.EXTERNAL), self)

    @classmethod
    def addLegacyHangarFunctionalFlag(cls, flag):
        cls.__LEGACY_HANGAR_MODE_FLAGS.add(flag)

    def _shouldHijack(self, event):
        if event.targetStateID != HangarState.STATE_ID:
            return False
        prbFlags = self.prbEntity.getModeFlags()
        return any((bool(prbFlags & flag) for flag in self.__LEGACY_HANGAR_MODE_FLAGS))


HangarState, DefaultHangarState, AllVehiclesState = generateBasicHangarStateClasses(SubScopeSubLayerState, R.invalid)
LoadoutState, LoadoutConfirmState, LoadoutSectionState, ShellsLoadoutState, EquipmentLoadoutState, InstructionsLoadoutState, ConsumablesLoadoutState = generateBasicLoadoutStateClasses(HangarState, R.invalid)
