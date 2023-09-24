# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_battles_controller.py
import typing
import Event
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from season_provider import SeasonProvider
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
if typing.TYPE_CHECKING:
    from helpers.server_settings import _EventBattlesConfig

class EventBattlesController(IEventBattlesController, Notifiable, SeasonProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(EventBattlesController, self).__init__()
        self.__serverSettings = None
        self.onPrimeTimeStatusUpdated = Event.Event()
        return

    def init(self):
        super(EventBattlesController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))

    def fini(self):
        self.onPrimeTimeStatusUpdated.clear()
        self.clearNotification()
        self.__clear()
        super(EventBattlesController, self).fini()

    def onDisconnected(self):
        super(EventBattlesController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(EventBattlesController, self).onAvatarBecomePlayer()
        self.__clear()

    def onAccountBecomePlayer(self):
        super(EventBattlesController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().eventBattlesConfig

    def getModeSettings(self):
        return self.getConfig()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateEventBattlesSettings
        self.__resetTimer()
        return

    def __updateEventBattlesSettings(self, diff):
        if 'event_battles_config' in diff:
            self.__resetTimer()

    def __clear(self):
        self.stopNotification()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        return

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)
