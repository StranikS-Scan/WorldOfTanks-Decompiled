# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/scheduler.py
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters.windows import SwitchPeripheryRankedCtx
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, i18n
from skeletons.gui.game_control import IRankedBattlesController

class RankedScheduler(BaseScheduler):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, entity):
        super(RankedScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    def init(self):
        status, _ = self.rankedController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PRIME_TIME_STATUS.AVAILABLE
        self.rankedController.onUpdated += self.__reset
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__update))
        self.startNotification()
        self.__show()

    def fini(self):
        self.stopNotification()
        self.clearNotification()
        self.rankedController.onUpdated -= self.__reset

    def __reset(self, *args):
        self.startNotification()
        self.__update()

    def __getTimer(self):
        """
        Gets the prime time update time
        """
        _, timeLeft = self.rankedController.getPrimeTimeStatus()
        return timeLeft + 1

    def __update(self):
        """
        Process update
        """
        if not self.rankedController.isAvailable():
            self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))
            return
        status, _ = self.rankedController.getPrimeTimeStatus()
        isPrimeTime = status == PRIME_TIME_STATUS.AVAILABLE
        if isPrimeTime != self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            self.__show()
            g_eventDispatcher.updateUI()

    def __show(self):
        """
        Show UI elements: system message, window
        """
        if not self.__isPrimeTime:
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.RANKED_NOTIFICATION_PRIMETIME), type=SystemMessages.SM_TYPE.PrimeTime)
            if self.rankedController.hasAnyPeripheryWithPrimeTime():
                g_eventDispatcher.showSwitchPeripheryWindow(ctx=SwitchPeripheryRankedCtx(), isModal=False)
