# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/scheduler.py
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class EventScheduler(BaseScheduler):
    _gameEventController = dependency.descriptor(IGameEventController)

    def init(self):
        self._gameEventController.onEventUpdated += self._onEventUpdated

    def fini(self):
        self._gameEventController.onEventUpdated -= self._onEventUpdated

    def _onEventUpdated(self, *_):
        if not self._gameEventController.isEnabled():
            self._doLeave()

    def _doLeave(self):
        self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
