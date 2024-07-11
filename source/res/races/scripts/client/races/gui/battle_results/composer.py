# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/battle_results/composer.py
from collections import namedtuple
from gui.battle_results import templates
from gui.battle_results.composer import StatsComposer
from races.gui.shared import event_dispatcher
BattleResult = namedtuple('BattleResult', ('results', 'reusable'))

class RacesEventBattleStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(RacesEventBattleStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self.battleResults = None
        return

    def getVO(self):
        return self.battleResults

    def setResults(self, results, reusable):
        self.battleResults = BattleResult(results=results, reusable=reusable)

    @staticmethod
    def onShowResults(arenaUniqueID):
        pass

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        event_dispatcher.showRacesBattleResultView(arenaUniqueID)
