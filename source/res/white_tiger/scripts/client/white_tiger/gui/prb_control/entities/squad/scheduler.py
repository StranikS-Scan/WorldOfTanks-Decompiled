# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/scheduler.py
from adisp import adisp_process
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from white_tiger.gui.prb_control.entities.pre_queue.scheduler import WhiteTigerBattleScheduler
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from helpers import dependency
from shared_utils import nextTick

class WhiteTigerSquadScheduler(WhiteTigerBattleScheduler):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def _doLeave(self):
        if self._entity and self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander() and not self._isLeaveRequestSent:
                self._entity.exitFromQueue()
                self._isLeaveRequestSent = True
            nextTick(self._doLeave)()
        else:
            self._doSelect(PREBATTLE_ACTION_NAME.RANDOM)
            self._isLeaveRequestSent = False

    @adisp_process
    def _doSelect(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))
