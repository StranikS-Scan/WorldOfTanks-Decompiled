# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_results/composer.py
import BigWorld
from gui import SystemMessages
from gui.battle_results.composer import IStatsComposer
from historical_battles.gui.shared import event_dispatcher
from historical_battles.gui.battle_results import templates

def _showMessage():
    SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')


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
        if HistoryBattleStatsComposer._canNavigate():
            event_dispatcher.showHBBattleResult(arenaUniqueID)

    @staticmethod
    def _canNavigate():
        from gui.prb_control.dispatcher import g_prbLoader
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            BigWorld.callback(0.0, _showMessage)
            return False
        else:
            return True
