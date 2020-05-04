# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/scheduler.py
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class EventScheduler(BaseScheduler):
    _eventsCache = dependency.descriptor(IEventsCache)

    def init(self):
        self._eventsCache.onSyncCompleted += self._onSyncCompleted

    def fini(self):
        self._eventsCache.onSyncCompleted -= self._onSyncCompleted

    def _onSyncCompleted(self, *_):
        if not self._eventsCache.isEventEnabled():
            self._doLeave()

    def _doLeave(self):
        self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
