# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_results/composer.py
from gui.battle_results.composer import RegularStatsComposer
from white_tiger.gui.shared.event_dispatcher import showBattleResultsWindow

class WhiteTigerBattleStatsComposer(RegularStatsComposer):

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        showBattleResultsWindow(arenaUniqueID)
