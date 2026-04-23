# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/squad/scheduler.py
from adisp import adisp_process
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from historical_battles.gui.prb_control.entities.pre_queue.scheduler import HistoricalBattleScheduler
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

class HistoricalBattleSquadScheduler(HistoricalBattleScheduler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _doLeave(self):
        if self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander():
                self._entity.exitFromQueue()
        else:
            self._doSelect(PREBATTLE_ACTION_NAME.RANDOM)

    @adisp_process
    def _doSelect(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))
