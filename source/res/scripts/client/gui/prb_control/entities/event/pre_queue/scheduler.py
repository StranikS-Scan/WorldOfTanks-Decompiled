# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/scheduler.py
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class EventScheduler(BaseScheduler):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, entity):
        super(EventScheduler, self).__init__(entity)
        self.__isPrimeTime = False
        self.__isConfigured = False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def init(self):
        status, _, _ = self.gameEventController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__isConfigured = status != PrimeTimeStatus.NOT_SET
        self.gameEventController.onPrimeTimeStatusUpdated += self.__update
        self.__show(status, isInit=True)

    def fini(self):
        self.gameEventController.onPrimeTimeStatusUpdated -= self.__update

    def __update(self, status):
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        isConfigured = status != PrimeTimeStatus.NOT_SET
        if isPrimeTime != self.__isPrimeTime or isConfigured != self.__isConfigured:
            self.__isPrimeTime = isPrimeTime
            self.__isConfigured = isConfigured
            self.__show(status)
            g_eventDispatcher.updateUI()

    def __show(self, status, isInit=False):
        strRes = R.strings.event.notifications
        if not self.__isConfigured:
            SystemMessages.pushMessage(text=backport.text(strRes.notSet()), type=SystemMessages.SM_TYPE.Warning, priority=NotificationPriorityLevel.HIGH)
        elif not self.__isPrimeTime and status != PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(strRes.primeTime.notAvailable.body()), messageData={'header': backport.text(strRes.primeTime.notAvailable.header())}, type=SystemMessages.SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH)
