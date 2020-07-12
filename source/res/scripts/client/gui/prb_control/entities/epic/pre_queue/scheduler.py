# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/pre_queue/scheduler.py
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventProgressionController

class EpicMetaScheduler(BaseScheduler):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def __init__(self, entity):
        super(EpicMetaScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isCycle = False

    def init(self):
        status, _, _ = self.__eventProgression.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        season = self.__eventProgression.getCurrentSeason()
        if season is not None:
            self.__isCycle = season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp())
        self.__eventProgression.onPrimeTimeStatusUpdatedAddEvent(self.__update)
        return

    def fini(self):
        self.__eventProgression.onPrimeTimeStatusUpdatedRemoveEvent(self.__update)

    def __update(self, status):
        hasCurrentSeason = self.__eventProgression.getCurrentSeason() is not None
        if not self.__eventProgression.modeIsEnabled() or self.__eventProgression.isFrozen() or not hasCurrentSeason:
            self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
            return
        else:
            isPrimeTime = status == PrimeTimeStatus.AVAILABLE
            time = time_utils.getCurrentLocalServerTimestamp()
            isCycle = self.__eventProgression.getCurrentSeason().hasActiveCycle(time)
            if isPrimeTime != self.__isPrimeTime or isCycle != self.__isCycle:
                self.__isPrimeTime = isPrimeTime
                self.__isCycle = isCycle
                g_eventDispatcher.updateUI()
            return
