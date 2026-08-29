# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/br_helpers/utils.py
from __future__ import absolute_import
from battle_royale.gui.impl.gen.view_models.views.lobby.enums import SubMode, CoinType
from battle_royale.gui.impl.lobby.views.states import BattleRoyaleBattleResultsState
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

def isBattleResultsStateEntered():
    state = getLobbyStateMachine().getStateByCls(BattleRoyaleBattleResultsState)
    return state and state.isEntered()


@dependency.replace_none_kwargs(battleRoyaleController=IBattleRoyaleController)
def setEventInfo(model, battleRoyaleController=None):
    if battleRoyaleController.isStPatrick():
        subMode = SubMode.STPATRICK
        coinType = CoinType.STPCOIN
    else:
        subMode = SubMode.DEFAULT
        coinType = CoinType.BRCOIN
    model.setSubMode(subMode)
    model.setCoinType(coinType)
