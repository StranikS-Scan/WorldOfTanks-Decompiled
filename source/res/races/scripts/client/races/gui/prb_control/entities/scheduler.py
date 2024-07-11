# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/prb_control/entities/scheduler.py
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.game_control import IRacesBattleController

class RacesScheduler(BaseScheduler):
    __racesBattleController = dependency.descriptor(IRacesBattleController)

    def __init__(self, entity):
        super(RacesScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    def init(self):
        status, _, _ = self.__racesBattleController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__racesBattleController.onPrimeTimeStatusUpdated += self.__update

    def fini(self):
        self.__racesBattleController.onPrimeTimeStatusUpdated -= self.__update

    def __update(self, status):
        if not self.__racesBattleController.isEnabled:
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        if isPrimeTime != self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            if not isPrimeTime:
                SystemMessages.pushMessage(backport.text(R.strings.system_messages.royale.notification.primeTime()), type=SystemMessages.SM_TYPE.PrimeTime, messageData={'title': backport.text(R.strings.system_messages.royale.notification.primeTime.title())})
            g_eventDispatcher.updateUI()
