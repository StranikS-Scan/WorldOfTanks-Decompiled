# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/states.py
from battle_royale.gui.impl.lobby.views.pre_battle import PreBattleView
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyStateDescription

def registerStates(lsm):
    lsm.addState(BattleRoyaleTournamentQueueState())


def registerTransitions(_):
    pass


@BattleQueueContainerState.parentOf
class BattleRoyaleTournamentQueueState(GuiImplViewLobbyState):
    STATE_ID = 'battleRoyaleTournamentBattleQueue'
    VIEW_KEY = ViewKey(R.views.battle_royale.lobby.views.PreBattleView())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(BattleRoyaleTournamentQueueState, self).__init__(PreBattleView, ScopeTemplates.LOBBY_SUB_SCOPE, flags=flags)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.waiting.prebattle.battle_queue()))
