# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_results/composer.py
import BigWorld
from gui import SystemMessages
from white_tiger.gui.shared.event_dispatcher import showBattleResultsWindow
from gui.battle_results.composer import IStatsComposer
from white_tiger.gui.battle_results import templates as wt_templates
from gui.battle_results.components import base

def _showMessage():
    SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')


class WhiteTigerStatsComposer(IStatsComposer):

    def __init__(self, _):
        super(WhiteTigerStatsComposer, self).__init__()
        self._block = wt_templates.WT_TOTAL_RESULTS_BLOCK.clone()

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self._block.addNextComponent(base.DirectStatsItem('results', results))
        self._block.addNextComponent(base.DirectStatsItem('reusable', reusable))
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
        if WhiteTigerStatsComposer._canNavigate():
            showBattleResultsWindow(arenaUniqueID)

    @staticmethod
    def _canNavigate():
        from gui.prb_control.dispatcher import g_prbLoader
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            BigWorld.callback(0.0, _showMessage)
            return False
        else:
            return True
