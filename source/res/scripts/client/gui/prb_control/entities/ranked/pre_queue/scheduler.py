# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/scheduler.py
from gui.impl import backport
from gui.impl.gen import R
from gui import SystemMessages
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.prime_time_constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedScheduler(BaseScheduler):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, entity):
        super(RankedScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    def init(self):
        status, _, _ = self.rankedController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.rankedController.onGameModeStatusUpdated += self.__update
        self.__show(isInit=True)

    def fini(self):
        self.rankedController.onGameModeStatusUpdated -= self.__update

    def __update(self, status):
        if not self.rankedController.isAvailable():
            self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show()
            g_eventDispatcher.updateUI()

    def __show(self, isInit=False):
        if not self.__isConfigured:
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.ranked.notification.notSet()), type=SystemMessages.SM_TYPE.RankedBattlesNotSet)
        elif not self.__isPrimeTime:
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.ranked.notification.primeTime()), type=SystemMessages.SM_TYPE.PrimeTime)
        elif not isInit:
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.ranked.notification.available()), type=SystemMessages.SM_TYPE.RankedBattlesAvailable)
