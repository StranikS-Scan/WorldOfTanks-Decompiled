# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_results/composer.py
from gui.battle_results.composer import IBattleResultStatsCtrl
from gui.battle_results.components import base
from battle_royale.gui.battle_results import templates
from battle_royale.gui.shared import event_dispatcher

class BattleRoyaleStatsComposer(IBattleResultStatsCtrl):

    def __init__(self, _):
        super(BattleRoyaleStatsComposer, self).__init__()
        self._block = base.StatsBlock(templates.BR_TOTAL_VO_META)
        self._block.addNextComponent(templates.BR_TABS_BLOCK.clone())
        self._block.addNextComponent(templates.BR_TEAM_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.BR_COMMON_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.BR_PERSONAL_STATS_BLOCK.clone())

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self._block.setRecord(results, reusable)

    def getVO(self):
        return self._block.getVO()

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        event_dispatcher.showBattleRoyaleResultsView({'arenaUniqueID': arenaUniqueID})
