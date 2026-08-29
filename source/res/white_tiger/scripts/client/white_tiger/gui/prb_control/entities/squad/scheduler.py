# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/scheduler.py
from adisp import adisp_process
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from white_tiger.gui.prb_control.entities.pre_queue.scheduler import WhiteTigerScheduler

class WhiteTigerSquadScheduler(WhiteTigerScheduler):

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
