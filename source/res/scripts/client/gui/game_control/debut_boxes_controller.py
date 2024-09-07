# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/debut_boxes_controller.py
import logging
import typing
import Event
from Event import EventManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CAROUSEL_FILTER_2, RANKED_CAROUSEL_FILTER_2, COMP7_CAROUSEL_FILTER_2
from constants import Configs
from shared_utils import findFirst
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import checkForTags
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from helpers.server_settings import serverSettingsChangeListener
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IDebutBoxesController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Dict
    from helpers.server_settings import DebutBoxesConfig
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)
UNSUPPORTED_TAGS = (VEHICLE_TAGS.EVENT,
 VEHICLE_TAGS.EPIC_BATTLES,
 VEHICLE_TAGS.BATTLE_ROYALE,
 VEHICLE_TAGS.MAPS_TRAINING)
_SETTINGS_SECTIONS = (CAROUSEL_FILTER_2, RANKED_CAROUSEL_FILTER_2, COMP7_CAROUSEL_FILTER_2)

class DebutBoxesController(IDebutBoxesController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __bootcamp = dependency.descriptor(IBootcampController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__eventsManager = EventManager()
        self.__eventsSubscriber = Event.EventsSubscriber()
        self.__notifier = SimpleNotifier(self.__getTimer, self.__onTimerUpdated)
        self.__quests = {}
        self.__enabled = None
        self.onConfigChanged = Event.Event(self.__eventsManager)
        self.onStateChanged = Event.Event(self.__eventsManager)
        self.onQuestsChanged = Event.Event(self.__eventsManager)
        return

    def onLobbyInited(self, event):
        self.__eventsSubscriber.subscribeToEvent(self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged)
        self.__eventsSubscriber.subscribeToEvent(self.__eventsCache.onSyncCompleted, self.__onEventsCache)
        self.__quests = self.__getAllQuests()
        self.__notifier.startNotification()
        if self.__enabled is not None:
            self.__tryNotifyStateChanged()
        self.__enabled = self.__getConfig().isEnabled
        if not self.isEnabled():
            self.__clearCarouselFilters()
        return

    def onAccountBecomeNonPlayer(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__notifier.stopNotification()
        self.__quests = {}

    def fini(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__eventsManager.clear()

    def isEnabled(self):
        serverTime = time_utils.getServerUTCTime()
        config = self.__getConfig()
        return config.isEnabled and config.startDate <= serverTime <= config.endDate and not self.__bootcamp.isInBootcamp()

    def isQuestsCompletedOnVehicle(self, vehicle):
        return any((quest.bonusCond.isGroupProgressCompleted(groupByKey=vehicle.intCD) for quest in self.__quests.values()))

    def isQuestsAvailableOnVehicle(self, vehicle):
        quest = self.getQuestForVehicle(vehicle)
        return quest is not None and not quest.bonusCond.isGroupProgressCompleted(groupByKey=vehicle.intCD)

    def getQuestsIDs(self):
        return self.__getConfig().questIDs

    def getQuestForVehicle(self, vehicle):
        return findFirst(lambda quest: quest.vehicleReqs.isAvailable(vehicle), self.__quests.values(), None) if not vehicle.isRented and not checkForTags(vehicle.tags, UNSUPPORTED_TAGS) or VEHICLE_TAGS.DEBUT_BOXES in vehicle.tags else None

    def getGroupID(self):
        quest = next(self.__quests.itervalues(), None)
        return quest.getGroupID() if quest else None

    def getInfoPageUrl(self):
        return self.__getConfig().infoPageUrl

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().debutBoxesConfig

    def __getTimer(self):
        serverTime = time_utils.getServerUTCTime()
        config = self.__getConfig()
        if not config.isEnabled:
            return 0
        if serverTime < config.startDate:
            return config.startDate - serverTime
        return config.endDate - serverTime if serverTime < config.endDate else 0

    def __onTimerUpdated(self):
        if not self.isEnabled():
            self.__clearCarouselFilters()
        self.onStateChanged()

    def __tryNotifyStateChanged(self):
        serverTime = time_utils.getServerUTCTime()
        config = self.__getConfig()
        if not config.startDate < serverTime < config.endDate:
            return
        if self.__enabled == config.isEnabled or self.__bootcamp.isInBootcamp():
            return
        if config.isEnabled:
            textID = R.strings.system_messages.debutBoxes.enabled.body()
            notificationType = SM_TYPE.InformationHeader
            priority = NotificationPriorityLevel.MEDIUM
            messageData = {'header': backport.text(R.strings.system_messages.debutBoxes.enabled.header())}
        else:
            textID = R.strings.system_messages.debutBoxes.disabled.body()
            notificationType = SM_TYPE.ErrorHeader
            priority = NotificationPriorityLevel.HIGH
            messageData = {'header': backport.text(R.strings.system_messages.debutBoxes.disabled.header())}
        SystemMessages.pushMessage(text=backport.text(textID), type=notificationType, priority=priority, messageData=messageData)

    @serverSettingsChangeListener(Configs.DEBUT_BOXES_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        debutBoxesDiff = diff[Configs.DEBUT_BOXES_CONFIG.value]
        if {'isEnabled', 'startDate', 'endDate'}.intersection(debutBoxesDiff):
            self.__notifier.startNotification()
            self.__tryNotifyStateChanged()
            if not self.isEnabled():
                self.__clearCarouselFilters()
            self.onStateChanged()
        self.__enabled = self.__getConfig().isEnabled
        self.onConfigChanged()

    def __clearCarouselFilters(self):
        for section in _SETTINGS_SECTIONS:
            defaults = AccountSettings.getFilterDefault(section)
            settings = self.__settingsCore.serverSettings.getSection(section, defaults)
            settings['debut_boxes'] = False
            self.__settingsCore.serverSettings.setSectionSettings(section, settings)

    def __getAllQuests(self):
        questIDs = set(self.__getConfig().questIDs)
        return self.__eventsCache.getQuests(lambda q: q.getID() in questIDs)

    def __onEventsCache(self):
        self.__quests = self.__getAllQuests()
        self.onQuestsChanged()
