# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/scheduler.py
from adisp import process
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction, CreatePrbEntityCtx
from gui.prb_control.entities.base.unit.ctx import LeaveUnitCtx, BattleQueueUnitCtx
from gui.prb_control.entities.event.pre_queue.scheduler import EventScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE, FUNCTIONAL_FLAG

class EventSquadScheduler(EventScheduler):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _doLeave(self):
        if self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander():
                ctx = BattleQueueUnitCtx('prebattle/battle_queue', 0)
                ctx.selectVehInvID = 0
                self._entity.doBattleQueue(ctx, self._leave)
            else:
                self._doSelect(PREBATTLE_ACTION_NAME.RANDOM)
        else:
            self._doSelect(PREBATTLE_ACTION_NAME.RANDOM)

    def _leave(self):
        ctx = CreatePrbEntityCtx(CTRL_ENTITY_TYPE.PREQUEUE, 0, flags=0)
        g_eventDispatcher.loadHangar()
        dialog = self._entity.getConfirmDialogMeta(LeaveUnitCtx(flags=FUNCTIONAL_FLAG.EVENT))
        self._entity.storage.suspend()
        self._entity.leave(ctx)
        if dialog is not None:
            self._showLeave(dialog)
        return

    @process
    def _showLeave(self, dialog):
        yield dialog

    @process
    def _doSelect(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))
