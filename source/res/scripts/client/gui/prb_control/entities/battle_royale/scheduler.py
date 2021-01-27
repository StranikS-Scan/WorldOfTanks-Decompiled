# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/scheduler.py
from gui.impl import backport
from gui.impl.gen import R
from gui import SystemMessages
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.prime_time_constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IEventProgressionController

class RoyaleScheduler(BaseScheduler):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def __init__(self, entity):
        super(RoyaleScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    def init(self):
        status, _, _ = self.__eventProgression.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__eventProgression.onPrimeTimeStatusUpdatedAddEvent(self.__update)

    def fini(self):
        self.__eventProgression.onPrimeTimeStatusUpdatedRemoveEvent(self.__update)

    def __update(self, status):
        if not self.__eventProgression.modeIsEnabled():
            return
        isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        if isPrimeTime != self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            if not isPrimeTime:
                SystemMessages.pushMessage(backport.text(R.strings.system_messages.royale.notification.primeTime()), type=SystemMessages.SM_TYPE.PrimeTime)
            g_eventDispatcher.updateUI()
