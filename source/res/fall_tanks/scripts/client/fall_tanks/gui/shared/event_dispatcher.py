# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/shared/event_dispatcher.py
from gui.impl.gen import R
from fun_random.gui.shared.event_dispatcher import showFunRandomBattleResultsWindow

def showFallTanksBattleResults(arenaUniqueID):
    from fall_tanks.gui.impl.lobby.fall_tanks_battle_results_view import FallTanksBattleResultsView
    layoutID = R.views.fall_tanks.lobby.FallTanksBattleResultsView()
    showFunRandomBattleResultsWindow(arenaUniqueID, FallTanksBattleResultsView, layoutID)
