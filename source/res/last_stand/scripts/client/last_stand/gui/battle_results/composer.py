# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_results/composer.py
import BigWorld
from gui import SystemMessages
from gui.battle_results.composer import IBattleResultStatsCtrl
from gui.prb_control import prbEntityProperty
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from last_stand.gui.battle_results import templates
from last_stand.gui.shared import event_dispatcher

def showErrorMessage():
    SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.queue.isInQueue()), type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.HIGH)


class LastStandBattleStatsComposer(IBattleResultStatsCtrl):

    def __init__(self, _):
        super(LastStandBattleStatsComposer, self).__init__()
        self._block = templates.LS_TOTAL_RESULTS_BLOCK.clone()

    @prbEntityProperty
    def prbEntity(self):
        return None

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
        if LastStandBattleStatsComposer.prbEntity.isInQueue():
            BigWorld.callback(0, showErrorMessage)
            return
        event_dispatcher.showBattleResult(arenaUniqueID)
