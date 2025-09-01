# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/scheduler.py
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbDispatcherProperty
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.notifications import NotificationPriorityLevel
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController

class WhiteTigerBattleScheduler(BaseScheduler):
    wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, entity):
        super(WhiteTigerBattleScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False
        self._isLeaveRequestSent = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.wtController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.wtController.onPrimeTimeStatusUpdated += self.__update
        self.__show(status, isInit=True)

    def fini(self):
        self.wtController.onPrimeTimeStatusUpdated -= self.__update

    def __update(self, status):
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show(status)
            g_eventDispatcher.updateUI()

    def __show(self, status, isInit=False):
        strRes = R.strings.white_tiger_lobby.notifications
        if not self.__isConfigured:
            SystemMessages.pushMessage(text=backport.text(strRes.notSet()), type=SystemMessages.SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)
        elif not self.__isPrimeTime and status != PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(strRes.primeTime.notAvailable.body()), messageData={'header': backport.text(strRes.primeTime.notAvailable.header())}, type=SystemMessages.SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH)
