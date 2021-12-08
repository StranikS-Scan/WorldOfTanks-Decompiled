# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/seniority_awards_controller.py
import Event
from account_helpers.AccountSettings import AccountSettings, SENIORITY_AWARDS_WINDOW_SHOWN
from gui.shared.event_dispatcher import showSeniorityAwardsNotificationWindow
from helpers import dependency, time_utils
from skeletons.gui.game_control import ISeniorityAwardsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_SA_TOKEN = 'SeniorityAwards2021'
_SA_EVENT_POSTFIX = '_psa2021'
SACOIN = 'sacoin'
_NOTIFICATION_REMIND_BEFORE_END = time_utils.ONE_DAY * 30
_NOTIFICATION_REMIND_LAST_CALL_BEFORE_END = time_utils.ONE_DAY * 14

class SeniorityAwardsController(ISeniorityAwardsController):
    __slots__ = ('__isEnabled', '__endTimestamp')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(SeniorityAwardsController, self).__init__()
        self.__isEnabled = False
        self.__endTimestamp = None
        self.onUpdated = Event.Event()
        return

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def endTimestamp(self):
        return self.__endTimestamp

    @property
    def showNotificationLastCallTimestamp(self):
        return self.__endTimestamp - _NOTIFICATION_REMIND_LAST_CALL_BEFORE_END

    @property
    def needShowNotification(self):
        coins = self.getSACoin()
        notificationShown = AccountSettings.getSessionSettings(SENIORITY_AWARDS_WINDOW_SHOWN)
        return 0 < self.__endTimestamp - time_utils.getServerUTCTime() < _NOTIFICATION_REMIND_BEFORE_END and coins > 0 and not notificationShown and self.__isEnabled

    def getSACoin(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(SACOIN, 0)

    def onLobbyInited(self, event):
        super(SeniorityAwardsController, self).onLobbyInited(event)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self.__update()
        if self.needShowNotification:
            showSeniorityAwardsNotificationWindow()

    def fini(self):
        self.onUpdated.clear()
        self.__clear()
        super(SeniorityAwardsController, self).fini()

    def onDisconnected(self):
        self.__clear()
        super(SeniorityAwardsController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__removeListeners()
        super(SeniorityAwardsController, self).onAvatarBecomePlayer()

    def __clear(self):
        self.__removeListeners()
        self.__isEnabled = False
        self.__endTimestamp = None
        return

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        if 'seniority_awards_config' in diff:
            self.__update()

    def __update(self):
        saCfg = self.__lobbyContext.getServerSettings().getSeniorityAwardsConfig()
        self.__isEnabled = saCfg.isEnabled()
        self.__endTimestamp = saCfg.endTimestamp()
        self.onUpdated()

    @staticmethod
    def __eventFilter():
        return lambda q: _SA_EVENT_POSTFIX in q.getID()
