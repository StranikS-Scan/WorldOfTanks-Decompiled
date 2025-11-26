# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/br_helpers/utils.py
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from battle_royale.gui.impl.lobby.views.states import BattleRoyaleBattleResultsState

def isBattleResultsStateEntered():
    state = getLobbyStateMachine().getStateByCls(BattleRoyaleBattleResultsState)
    return state and state.isEntered()
