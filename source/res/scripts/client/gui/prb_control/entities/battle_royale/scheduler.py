# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/scheduler.py
from gui.impl import backport
from gui.impl.gen import R
from gui import SystemMessages
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class RoyaleScheduler(BaseScheduler):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, entity):
        super(RoyaleScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    def init(self):
        status, _, _ = self.__battleRoyaleController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.__update

    def fini(self):
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.__update

    def __update(self, status):
        if not self.__battleRoyaleController.isEnabled():
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        if isPrimeTime != self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            if not isPrimeTime:
                SystemMessages.pushMessage(backport.text(R.strings.system_messages.royale.notification.primeTime()), type=SystemMessages.SM_TYPE.PrimeTime, messageData={'title': backport.text(R.strings.system_messages.royale.notification.primeTime.title())})
            g_eventDispatcher.updateUI()
