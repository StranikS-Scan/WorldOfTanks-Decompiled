# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prb_control/entities/pre_queue/scheduler.py
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from shared_utils import nextTick
from helpers import dependency
from grinch.skeletons.battle_controller import IGrinchController

class GrinchScheduler(BaseScheduler):
    __grinchCtrl = dependency.descriptor(IGrinchController)

    def __init__(self, entity):
        super(GrinchScheduler, self).__init__(entity)
        self._isLeaveRequestSent = False

    def init(self):
        self.__grinchCtrl.onPrimeTimeStatusUpdated += self.__update

    def fini(self):
        self.__grinchCtrl.onPrimeTimeStatusUpdated -= self.__update

    def _doLeave(self):
        if self._entity and self._entity.isInQueue():
            if not self._isLeaveRequestSent:
                self._entity.exitFromQueue()
                self._isLeaveRequestSent = True
            nextTick(self._doLeave)()
        else:
            self.__grinchCtrl.selectRandomMode()
            self._isLeaveRequestSent = False

    def __update(self, status):
        if not self.__grinchCtrl.isEnabled():
            nextTick(self._doLeave)()
        else:
            g_eventDispatcher.updateUI()
