# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/scheduler.py
from adisp import process
from constants import PREBATTLE_TYPE
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.unit.ctx import LeaveUnitCtx
from gui.prb_control.entities.event.pre_queue.scheduler import EventScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG

class EventSquadScheduler(EventScheduler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _doLeave(self):
        if self._entity.getFlags().isInQueue():
            self._showLeaveDialog()
            if self._entity.getPlayerInfo().isCommander():
                self._entity.exitFromQueue()
            else:
                self._doSelect(PREBATTLE_ACTION_NAME.RANDOM)
        else:
            self._doSelect(PREBATTLE_ACTION_NAME.RANDOM)

    def _showLeaveDialog(self):
        g_eventDispatcher.loadHangar()
        return self._entity.getConfirmDialogMeta(LeaveUnitCtx(flags=FUNCTIONAL_FLAG.EVENT, entityType=PREBATTLE_TYPE.EVENT))

    @process
    def _doSelect(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))
