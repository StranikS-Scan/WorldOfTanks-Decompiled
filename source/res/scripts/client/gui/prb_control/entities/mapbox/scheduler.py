# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/mapbox/scheduler.py
from gui.impl import backport
from gui.impl.gen import R
from gui import SystemMessages
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IMapboxController

class MapboxScheduler(BaseScheduler):
    __mapboxController = dependency.descriptor(IMapboxController)

    def __init__(self, entity):
        super(MapboxScheduler, self).__init__(entity)
        self.__isPrimeTime = False

    def init(self):
        status, _, _ = self.__mapboxController.getPrimeTimeStatus()
        self.__isPrimeTime = status == PrimeTimeStatus.AVAILABLE
        self.__mapboxController.onPrimeTimeStatusUpdated += self.__update

    def fini(self):
        self.__mapboxController.onPrimeTimeStatusUpdated -= self.__update

    def __update(self, status):
        if not self.__mapboxController.isEnabled():
            return
        else:
            isPrimeTime = status == PrimeTimeStatus.AVAILABLE
            if isPrimeTime != self.__isPrimeTime:
                self.__isPrimeTime = isPrimeTime
                if not isPrimeTime and self.__mapboxController.getCurrentCycleID() is not None:
                    SystemMessages.pushMessage(backport.text(R.strings.system_messages.mapbox.notification.primeTime()), type=SystemMessages.SM_TYPE.PrimeTime, messageData={'title': backport.text(R.strings.system_messages.royale.notification.primeTime.title())})
                g_eventDispatcher.updateUI()
            return
