# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/scheduler.py
from gui.prb_control.entities.event.pre_queue.scheduler import EventScheduler
from shared_utils import nextTick

class EventSquadScheduler(EventScheduler):

    def _doLeave(self):
        if self._entity.getFlags().isInQueue():
            if self._entity.getPlayerInfo().isCommander():
                self._entity.exitFromQueue()
            nextTick(self._doLeave)()
        else:
            self._showRandomHangar()
