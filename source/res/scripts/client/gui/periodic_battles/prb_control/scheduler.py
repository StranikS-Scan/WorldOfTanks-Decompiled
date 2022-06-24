# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/periodic_battles/prb_control/scheduler.py
from gui.impl import backport
from gui import SystemMessages
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.periodic_battles.models import PrimeTimeStatus

class PeriodicScheduler(BaseScheduler):
    _RES_ROOT = None
    _controller = None

    def __init__(self, entity):
        super(PeriodicScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    def init(self):
        status, _, _ = self._controller.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self._controller.onGameModeStatusUpdated += self._update
        self.__show(isInit=True)

    def fini(self):
        self._controller.onGameModeStatusUpdated -= self._update

    def _update(self, status):
        if not self._controller.isAvailable():
            self._doLeave()
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show()
            g_eventDispatcher.updateUI()

    def _doLeave(self):
        self._entity.leave(LeavePreQueueCtx(waitingID='prebattle/leave'))

    def __show(self, isInit=False):
        if not self._controller.isBattlesPossible():
            return
        if not self.__isConfigured:
            SystemMessages.pushMessage(backport.text(self._RES_ROOT.notification.notSet()), type=SystemMessages.SM_TYPE.PeriodicBattlesNotSet, messageData={'title': backport.text(self._RES_ROOT.notification.notSet.title())})
        elif not self.__isPrimeTime:
            SystemMessages.pushMessage(backport.text(self._RES_ROOT.notification.primeTime()), type=SystemMessages.SM_TYPE.PrimeTime, messageData={'title': backport.text(self._RES_ROOT.notification.primeTime.title())})
        elif not isInit:
            SystemMessages.pushMessage(backport.text(self._RES_ROOT.notification.available()), type=SystemMessages.SM_TYPE.PeriodicBattlesAvailable, messageData={'title': backport.text(self._RES_ROOT.notification.available.title())})
