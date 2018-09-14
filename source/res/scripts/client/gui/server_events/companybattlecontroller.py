# Embedded file name: scripts/client/gui/server_events/CompanyBattleController.py
import weakref
from Event import Event
from gui.shared.utils.scheduled_notifications import Notifiable, AcyclicNotifier
from gui.shared import g_eventBus
from gui.shared.events import GUICommonEvent
from PlayerEvents import g_playerEvents
from ConnectionManager import connectionManager as g_connectionManager

class CompanyBattleController(Notifiable):

    def __init__(self, eventsCache):
        self.__eventsCache = weakref.proxy(eventsCache)
        self.onCompanyStateChanged = Event()
        super(CompanyBattleController, self).__init__()
        self.__isLobbyLoaded = False
        self.__delayedCompanyState = []

    def start(self):
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        g_connectionManager.onDisconnected += self.__onDisconnected
        self.setNotificators()

    def stop(self):
        self.onCompanyStateChanged.clear()
        self.clearNotification()
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        g_connectionManager.onDisconnected -= self.__onDisconnected

    def setNotificators(self):
        battle = self.__eventsCache.getCompanyBattles()
        self.clearNotification()
        if battle.isValid():
            destroyingTimeLeft = battle.getDestroyingTimeLeft()
            if destroyingTimeLeft is not None:
                if destroyingTimeLeft <= 0:
                    self.__onCompanyFinished()
                else:
                    self.addNotificators(AcyclicNotifier(battle.getDestroyingTimeLeft, self.__onCompanyFinished))
            if battle.isCreationTimeCorrect():
                self.__onCompanyStarted()
            else:
                self.addNotificators(AcyclicNotifier(battle.getCreationTimeLeft, self.__onCompanyStarted))
            self.startNotification()
        else:
            self.__onCompanyFinished()
        return

    def __onLobbyInited(self, *args):
        self.__isLobbyLoaded = True
        self.__handlePostponed()

    def __onAvatarBecomePlayer(self):
        self.__isLobbyLoaded = False

    def __onDisconnected(self):
        self.__isLobbyLoaded = False

    def __onCompanyStarted(self):
        if self.__isLobbyLoaded:
            self.onCompanyStateChanged(True)
        else:
            self.__delayedCompanyState.append(True)

    def __onCompanyFinished(self):
        if self.__isLobbyLoaded:
            self.onCompanyStateChanged(False)
        else:
            self.__delayedCompanyState.append(False)

    def __handlePostponed(self):
        for companyState in self.__delayedCompanyState:
            self.onCompanyStateChanged(companyState)

        self.__delayedCompanyState = []
