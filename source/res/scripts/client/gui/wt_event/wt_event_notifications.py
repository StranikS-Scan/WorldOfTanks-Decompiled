# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_notifications.py
import logging
from constants import IS_LOOT_BOXES_ENABLED
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.wt_event import IWTEventNotifications
_logger = logging.getLogger(__name__)

class WTEventNotifications(IWTEventNotifications):
    _STR_RES = R.strings.event.notifications
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(WTEventNotifications, self).__init__()
        self.__curStatus = PrimeTimeStatus.NOT_SET

    def init(self):
        pass

    def fini(self):
        pass

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__gameEventCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdate
        status, _, _ = self.__gameEventCtrl.getPrimeTimeStatus()
        self.__curStatus = status

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def __clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__gameEventCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdate

    def __onTokensUpdate(self, diff):
        config = self.__gameEventCtrl.getConfig()
        if config.ticketToken in diff:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.ticketToken.received.body(), ticketsCount=str(self.__gameEventCtrl.getTicketCount())), messageData={'header': backport.text(self._STR_RES.ticketToken.received.header())}, type=SystemMessages.SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH)

    def __onServerSettingsChange(self, diff):
        if not self.__gameEventCtrl.isAvailable():
            return
        if IS_LOOT_BOXES_ENABLED in diff:
            if self.__lobbyContext.getServerSettings().isLootBoxesEnabled():
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.lootboxes.switchOn.body()), type=SystemMessages.SM_TYPE.WTEventSwitchOnLootboxes)
            else:
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.lootboxes.switchOff.body()), type=SystemMessages.SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(self._STR_RES.lootboxes.header())})

    def __onPrimeTimeStatusUpdate(self, status):
        if self.__curStatus == status:
            return
        if status == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOff.body()), messageData={'header': backport.text(self._STR_RES.switchOff.header())}, type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH)
        elif self.__curStatus == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOn.body()), messageData={'header': backport.text(self._STR_RES.switchOn.header())}, type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH)
        elif status == PrimeTimeStatus.AVAILABLE:
            if self.__isFirstPrimeTime():
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.eventStart.body()), type=SystemMessages.SM_TYPE.WTEventStart)
            else:
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.primeTime.available.body()), messageData={'header': backport.text(self._STR_RES.primeTime.available.header())}, type=SystemMessages.SM_TYPE.WarningHeader)
        elif status == PrimeTimeStatus.NOT_AVAILABLE and not self.__gameEventCtrl.getNextSeason() and not self.__gameEventCtrl.getCurrentSeason():
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.eventEnd.body()), type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM)
        self.__curStatus = status

    def __isFirstPrimeTime(self):
        if not self.__gameEventCtrl.getSeasonPassed():
            curSeason = self.__gameEventCtrl.getCurrentSeason()
            if curSeason is not None and curSeason.getPassedCyclesNumber() == 0 and not self.__gameEventCtrl.hasPrimeTimesPassedForCurrentCycle():
                return True
        return False
