# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/fun_stats_controller.py
from __future__ import absolute_import
import typing
from fun_random.gui.battle_results.pbs_helpers import getEventID
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.shared.event_dispatcher import showFunRandomBattleResults
from gui.battle_results.pbs_helpers.common import pushNoBattleResultsDataMessage
from gui.battle_results.stats_ctrl import IBattleResultStatsCtrl, BattleResults
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo

class FunBattleResultStatsCtrl(IBattleResultStatsCtrl, FunSubModesWatcher):

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

    def getResults(self):
        return self._battleResults

    def setResults(self, results, reusable):
        self._battleResults = BattleResults(results, reusable)

    def onResultsPosted(self, arenaUniqueID):
        if self._battleResults and self._funRandomCtrl.isEnabled():
            subModeID = getEventID(self._battleResults.reusable)
            subMode = self.getSubMode(subModeID)
            if subMode is not None and subMode.isAvailable():
                showFunRandomBattleResults(arenaUniqueID, subMode.getSubModeImpl())
                return
        pushNoBattleResultsDataMessage()
        return

    @staticmethod
    def onShowResults(arenaUniqueID):
        return None
