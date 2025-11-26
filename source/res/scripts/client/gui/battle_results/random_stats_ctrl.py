# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/random_stats_ctrl.py
import typing
from soft_exception import SoftException
from gui.battle_results.pbs_helpers.common import pushNoBattleResultsDataMessage
from gui.battle_results.stats_ctrl import IBattleResultStatsCtrl, BattleResults
from gui.shared.event_dispatcher import showRandomBattleResultsWindow
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo

class RandomBattleResultStatsCtrl(IBattleResultStatsCtrl):

    def __init__(self, _):
        self._battleResults = None
        return

    @property
    def ctrlImplType(self):
        return self.CTRL_IMPL_TYPE_GAMEFACE

    def clear(self):
        self._battleResults = None
        return

    def getVO(self):
        raise SoftException('Unsupported method')

    def setResults(self, results, reusable):
        self._battleResults = BattleResults(results, reusable)

    def getResults(self):
        return self._battleResults

    def onResultsPosted(self, arenaUniqueID):
        if self._battleResults:
            bonusType = self._battleResults.reusable.bonusType
            showRandomBattleResultsWindow(arenaUniqueID, bonusType)
            return
        pushNoBattleResultsDataMessage()

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None
