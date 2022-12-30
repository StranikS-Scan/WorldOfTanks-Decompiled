# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/collective_goal_marathons_controller.py
import logging
from collections import namedtuple
import typing
import Event
from Event import EventsSubscriber
from constants import Configs
from gui.marathon.collective_goal_marathon import COLLECTIVE_GOAL_MARATHON_PREFIX
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import ICollectiveGoalMarathonsController, IMarathonEventsController
from skeletons.gui.lobby_context import ILobbyContext
from helpers.server_settings import serverSettingsChangeListener
if typing.TYPE_CHECKING:
    from helpers.server_settings import _CollectiveGoalMarathonsConfig
_logger = logging.getLogger(__name__)
Marathon = namedtuple('Marathon', ['isEnabled',
 'startTime',
 'finishTime',
 'url',
 'prefix'])

class CollectiveGoalMarathonsController(ICollectiveGoalMarathonsController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __marathonEventsController = dependency.descriptor(IMarathonEventsController)

    def __init__(self):
        self.__em = Event.EventManager()
        self.__eventsSubscriber = EventsSubscriber()
        self.__notifier = SimpleNotifier(self.__getClosestMarathonUpdate, self.__updateMarathonEvent)
        self.onMarathonUpdated = Event.Event(self.__em)

    def onLobbyInited(self, event):
        self.__eventsSubscriber.subscribeToEvent(self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged)
        self.__updateMarathonEvent()
        self.__notifier.startNotification()

    def onAccountBecomeNonPlayer(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__notifier.stopNotification()

    def fini(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__em.clear()
        self.__notifier.stopNotification()
        self.__notifier.clear()

    def __getClosestMarathonUpdate(self):
        config = self.__getConfig()
        if not config.isEnabled:
            return 0
        currentTime = time_utils.getServerUTCTime()
        if currentTime < config.startTime:
            return config.startTime - currentTime
        return config.finishTime - currentTime if currentTime < config.finishTime else 0

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().collectiveGoalMarathonsConfig

    def __updateMarathonEvent(self):
        marathon = self.__marathonEventsController.getMarathon(COLLECTIVE_GOAL_MARATHON_PREFIX)
        marathon.setState()
        self.onMarathonUpdated()

    @serverSettingsChangeListener(Configs.COLLECTIVE_GOAL_MARATHONS_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.__updateMarathonEvent()
        self.__notifier.startNotification()
