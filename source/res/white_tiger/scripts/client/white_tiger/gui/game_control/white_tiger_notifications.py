# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/white_tiger_notifications.py
import logging
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages
from gui.shared.lock_overlays import lockNotificationManager
from skeletons.gui.shared.utils import IHangarSpace
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_notifications import IWhiteTigerNotifications
from white_tiger.gui.white_tiger_account_settings import AccountSettingsKeys, getSettings, setSettings
_logger = logging.getLogger(__name__)

class WhiteTigerNotifications(IWhiteTigerNotifications):
    _STR_RES = R.strings.white_tiger_lobby.notifications
    __wtCtrl = dependency.descriptor(IWhiteTigerController)
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(WhiteTigerNotifications, self).__init__()
        self.__curStatus = PrimeTimeStatus.NOT_SET

    def init(self):
        self.__hangarSpace.onSpaceCreate += self.__onSpaceCreate

    def fini(self):
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreate

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__wtCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdate
        self.__wtCtrl.onEventEnded += self.__onEventEnd
        status, _, _ = self.__wtCtrl.getPrimeTimeStatus()
        self.__curStatus = status

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def onLobbyStarted(self, ctx):
        lockNotificationManager(lock=True)

    def __clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__wtCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdate
        self.__wtCtrl.onEventEnded -= self.__onEventEnd

    def __onTokensUpdate(self, diff):
        if self.__economicsCtrl.getTicketTokenName() in diff:
            self.__checkNewTicketsObtained()

    def __onPrimeTimeStatusUpdate(self, status):
        if self.__curStatus == status:
            return
        if status == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOff.body()), messageData={'header': backport.text(self._STR_RES.switchOff.header())}, type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH)
        elif self.__curStatus == PrimeTimeStatus.FROZEN and status == PrimeTimeStatus.AVAILABLE:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOn.body()), messageData={'header': backport.text(self._STR_RES.switchOn.header())}, type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH)
        elif status == PrimeTimeStatus.AVAILABLE:
            if self.__isFirstPrimeTime():
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.eventStart.body()), type=SystemMessages.SM_TYPE.WTEventStart, priority=NotificationPriorityLevel.MEDIUM)
            else:
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.primeTime.available.body()), messageData={'header': backport.text(self._STR_RES.primeTime.available.header())}, type=SystemMessages.SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH)
        self.__curStatus = status

    def __onEventEnd(self):
        SystemMessages.pushMessage(text=backport.text(self._STR_RES.eventEnd.body()), type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM)

    def __onSpaceCreate(self, *args, **kwargs):
        lockNotificationManager(lock=False, releasePostponed=True)
        self.__checkNewTicketsObtained()

    def __checkNewTicketsObtained(self):
        currentTicketCount = self.__economicsCtrl.getTicketCount()
        lastTicketCount = getSettings(AccountSettingsKeys.WT_LAST_SEEN_TICKETS)
        if currentTicketCount > 0 and lastTicketCount < currentTicketCount:
            self.__pushTicketsEarnedMessage(currentTicketCount)
        setSettings(AccountSettingsKeys.WT_LAST_SEEN_TICKETS, currentTicketCount)

    def __isFirstPrimeTime(self):
        if not self.__wtCtrl.getSeasonsPassed():
            curSeason = self.__wtCtrl.getCurrentSeason()
            if curSeason is not None and curSeason.getPassedCyclesNumber() == 0 and not self.__wtCtrl.hasPrimeTimesPassedForCurrentCycle():
                return True
        return False

    def __pushTicketsEarnedMessage(self, ticketCount):
        SystemMessages.pushMessage(text=backport.text(self._STR_RES.ticketToken.received.body(), ticketsCount=str(ticketCount)), messageData={'header': backport.text(self._STR_RES.ticketToken.received.header())}, type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.MEDIUM)
