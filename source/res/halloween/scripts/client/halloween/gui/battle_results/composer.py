# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_results/composer.py
from gui.battle_results.composer import IStatsComposer
from halloween.gui.battle_results import templates
from halloween.gui.battle_results.templates import HW_TOTAL_RESULTS_BLOCK
from halloween.gui.shared import event_dispatcher

class HalloweenBattleStatsComposer(IStatsComposer):

    def __init__(self, _):
        super(HalloweenBattleStatsComposer, self).__init__()
        self._block = HW_TOTAL_RESULTS_BLOCK.clone()
        self._block.addNextComponent(templates.HW_COMMON_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.HW_TEAMS_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.HW_QUESTS_PROGRESS_STATS_BLOCK.clone())

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self._block.setRecord(results, reusable)

    def getVO(self):
        return self._block.getVO()

    def popAnimation(self):
        pass

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        event_dispatcher.showBattleHalloweenResultsView({'arenaUniqueID': arenaUniqueID})
