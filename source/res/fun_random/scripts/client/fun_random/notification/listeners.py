# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/notification/listeners.py
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PeriodType
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from fun_random.notification.decorators import FunRandomButtonDecorator
from notification.listeners import _NotificationListener
from notification.settings import NOTIFICATION_TYPE
from skeletons.gui.game_control import IFunRandomController

class FunRandomEventsListener(_NotificationListener, IGlobalListener):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __STR_PATH = R.strings.fun_random.message

    def __init__(self):
        super(FunRandomEventsListener, self).__init__()
        self.__periodInfo = None
        self.__isAvailable = None
        self.__messageIDs = []
        return

    def start(self, model):
        super(FunRandomEventsListener, self).start(model)
        self.__periodInfo = self.__funRandomCtrl.getPeriodInfo()
        self.__isAvailable = self.__funRandomCtrl.isAvailable()
        self.__funRandomCtrl.onGameModeStatusUpdated += self.__onStatusUpdated
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onItemsUpdated})
        g_clientUpdateManager.addCallbacks({'stats.unlocks': self.__onItemsUpdated})
        self.startGlobalListening()
        return True

    def stop(self):
        self.__messageIDs = []
        self.__periodInfo = None
        self.__funRandomCtrl.onGameModeStatusUpdated -= self.__onStatusUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.stopGlobalListening()
        super(FunRandomEventsListener, self).stop()
        return

    def onPrbEntitySwitched(self):
        self.__updateMessages()

    def __onStatusUpdated(self, _):
        isAvailable = self.__funRandomCtrl.isAvailable()
        currentSeason = self.__funRandomCtrl.getCurrentSeason()
        if isAvailable != self.__isAvailable and currentSeason is not None and not self.__isEventStartedNow(currentSeason):
            self.__pushSwitcherMessage(isAvailable)
        periodInfo = self.__funRandomCtrl.getPeriodInfo()
        if self.__periodInfo.periodType != periodInfo.periodType:
            self.__pushStatusEventMessage(currentSeason)
            self.__periodInfo = periodInfo
        self.__isAvailable = isAvailable
        self.__updateMessages()
        return

    def __onItemsUpdated(self, *_):
        self.__updateMessages()

    def __isEventStartedNow(self, currentSeason):
        return currentSeason is not None and self.__periodInfo.periodType == PeriodType.BEFORE_SEASON

    def __isEventFinished(self, currentSeason):
        return currentSeason is None and self.__funRandomCtrl.getNextSeason() is None

    def __pushStatusEventMessage(self, currentSeason):
        if self.__isEventStartedNow(currentSeason):
            model = self._model()
            if model:
                startTime = currentSeason.getStartDate()
                model.addNotification(FunRandomButtonDecorator(startTime))
                self.__messageIDs.append(startTime)
        elif self.__isEventFinished(currentSeason):
            SystemMessages.pushMessage(text=backport.text(self.__STR_PATH.endEvent.text()), type=SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM)

    def __pushSwitcherMessage(self, isAvailable):
        if isAvailable:
            SystemMessages.pushMessage(text=backport.text(self.__STR_PATH.switch_on.text()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(self.__STR_PATH.switch.title())})
        else:
            SystemMessages.pushMessage(text=backport.text(self.__STR_PATH.switch_off.text()), type=SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(self.__STR_PATH.switch.title())})

    def __updateMessages(self):
        model = self._model()
        if model is None or not self.__messageIDs:
            return
        else:
            for entityID in self.__messageIDs:
                notification = FunRandomButtonDecorator(entityID)
                model.updateNotification(NOTIFICATION_TYPE.MESSAGE, entityID, notification.getEntity(), isStateChanged=False)

            return
