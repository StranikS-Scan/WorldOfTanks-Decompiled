# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/periodic_battles/prb_control/entity.py
from gui.impl import backport
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint
from gui.prb_control.settings import PRE_QUEUE_JOIN_ERRORS
from gui.periodic_battles.models import PrimeTimeStatus
from gui import SystemMessages

class PeriodicEntryPoint(PreQueueEntryPoint):
    _RES_ROOT = None
    _controller = None

    def select(self, ctx, callback=None):
        status, _, _ = self._controller.getPrimeTimeStatus()
        if status == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(backport.text(self._RES_ROOT.notification.notAvailable()), type=SystemMessages.SM_TYPE.Error)
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(PeriodicEntryPoint, self).select(ctx, callback)
            return
