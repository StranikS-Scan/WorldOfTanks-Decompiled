# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_event_notifications.py
import logging
from constants import IS_LOOT_BOXES_ENABLED
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.wt_event import IWTEventNotifications
from client_constants import EVENT_STATES
from white_tiger.gui.gui_constants import SCH_CLIENT_MSG_TYPE
_logger = logging.getLogger(__name__)

class WTEventNotifications(IWTEventNotifications):
    _STR_RES = R.strings.white_tiger.notifications
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(WTEventNotifications, self).__init__()
        self.__curStatus = PrimeTimeStatus.NOT_SET
        self.__isEnabled = False

    def init(self):
        pass

    def fini(self):
        pass

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__gameEventCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdate
        self.__gameEventCtrl.onUpdated += self.__onEventUpdated
        status, _, _ = self.__gameEventCtrl.getPrimeTimeStatus()
        if self.__curStatus != PrimeTimeStatus.NOT_SET:
            self.__onPrimeTimeStatusUpdate(status)
        else:
            self.__curStatus = status
        self.__isEnabled = self.__gameEventCtrl.isEnabled()

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def __clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__gameEventCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdate
        self.__gameEventCtrl.onUpdated -= self.__onEventUpdated

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

    def __onEventUpdated(self):
        if self.__isEnabled == self.__gameEventCtrl.isEnabled():
            return
        self.__isEnabled = self.__gameEventCtrl.isEnabled()
        eventState = EVENT_STATES.START if self.__isEnabled else EVENT_STATES.FINISH
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'state': eventState}, SCH_CLIENT_MSG_TYPE.WT_EVENT_STATE)

    def __onPrimeTimeStatusUpdate(self, status):
        if self.__curStatus == status:
            return
        if status == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOff.body()), messageData={'header': backport.text(self._STR_RES.switchOff.header())}, type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH)
        elif self.__curStatus == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOn.body()), messageData={'header': backport.text(self._STR_RES.switchOn.header())}, type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH)
        elif status == PrimeTimeStatus.AVAILABLE:
            if not self.__isFirstPrimeTime():
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.primeTime.available.body()), messageData={'header': backport.text(self._STR_RES.primeTime.available.header())}, type=SystemMessages.SM_TYPE.WarningHeader)
        elif status == PrimeTimeStatus.NOT_AVAILABLE:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.primeTime.notAvailable.body()), messageData={'header': backport.text(self._STR_RES.primeTime.notAvailable.header())}, type=SystemMessages.SM_TYPE.WarningHeader)
        self.__curStatus = status

    def __isFirstPrimeTime(self):
        if not self.__gameEventCtrl.getSeasonPassed():
            curSeason = self.__gameEventCtrl.getCurrentSeason()
            if curSeason is not None and curSeason.getPassedCyclesNumber() == 0 and not self.__gameEventCtrl.hasPrimeTimesPassedForCurrentCycle():
                return True
        return False
