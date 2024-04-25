# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_results/composer.py
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from historical_battles.gui.shared import event_dispatcher
from historical_battles.gui.battle_results import templates
from gui.battle_results.composer import ComposerFactory, IStatsComposer

@ComposerFactory.registerForBonusTypes(*ARENA_BONUS_TYPE.HB_RANGE)
class HistoryBattleStatsComposer(IStatsComposer):

    def __init__(self, _):
        super(HistoryBattleStatsComposer, self).__init__()
        self._block = templates.HB_TOTAL_RESULTS_BLOCK.clone()

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self._block.setRecord(results, reusable)

    def getVO(self):
        return self._block.getVO()

    def popAnimation(self):
        return None

    @staticmethod
    def onShowResults(arenaUniqueID):
        pass

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        event_dispatcher.showHistoricalBattleResultView(arenaUniqueID)
