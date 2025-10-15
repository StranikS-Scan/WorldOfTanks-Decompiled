# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/black_market_controller.py
from Event import Event, EventManager, EventsSubscriber
from helpers.events_handler import EventsHandler
from skeletons.gui.game_control import IBlackMarketController
from skeletons.gui.lobby_context import ILobbyContext
from helpers import dependency, time_utils
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers.server_settings import serverSettingsChangeListener
from constants import Configs
_HANGAR_ENTRY_POINTS = 'hangarEntryPoints'
_BLACK_MARKET_ENTRY_POINT = 'BlackMarketEntryPoint'

class BlackMarketController(IBlackMarketController, EventsHandler, EventsSubscriber):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(BlackMarketController, self).__init__()
        self.__eventsManager = EventManager()
        self.__phaseNotifier = PeriodicNotifier(self.__getTimeLeft, self.__onTimerUpdated, (time_utils.ONE_MINUTE,))
        self.onStateChanged = Event(self.__eventsManager)
        self.onBlackMarketUpdated = Event(self.__eventsManager)

    def onLobbyInited(self, event):
        self.subscribeToEvent(self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged)
        self.__phaseNotifier.startNotification()

    def onAccountBecomeNonPlayer(self):
        self.unsubscribeFromAllEvents()
        self.__phaseNotifier.stopNotification()

    def fini(self):
        self.unsubscribeFromAllEvents()
        self.__phaseNotifier.stopNotification()
        self.__phaseNotifier.clear()
        self.__eventsManager.clear()

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def isPaused(self):
        return self.__getConfig().isPaused

    def getStartTime(self):
        return self.__getConfig().startTime

    def getFinishTime(self):
        return self.__getConfig().finishTime

    def isStarted(self):
        return self.getStartTime() <= time_utils.getServerUTCTime()

    def isSpecial(self):
        lootboxSchedule = self.__getConfig().lootboxSchedule
        for startTime, endTime in lootboxSchedule.iteritems():
            if startTime <= time_utils.getServerUTCTime() <= endTime:
                return True

        return False

    def getLastOfferStartDate(self):
        offerLaunchSchedule = self.__getConfig().offerLaunchSchedule
        lastOfferStartDate = None
        for startTime in sorted(offerLaunchSchedule):
            if startTime <= time_utils.getServerUTCTime():
                lastOfferStartDate = startTime

        return lastOfferStartDate

    @serverSettingsChangeListener(Configs.BLACK_MARKET_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.onBlackMarketUpdated()
        self.__phaseNotifier.startNotification()

    def __getTimeLeft(self):
        return max(0, self.getFinishTime() - time_utils.getServerUTCTime() + 1) if self.isEnabled() and not self.isPaused() else 0

    def __onTimerUpdated(self):
        self.onStateChanged()

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().blackMarketConfig
