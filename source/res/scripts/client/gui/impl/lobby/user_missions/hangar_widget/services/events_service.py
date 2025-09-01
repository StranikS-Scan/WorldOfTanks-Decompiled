# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/events_service.py
import json
import logging
from itertools import chain
from typing import List
from PlayerEvents import g_playerEvents
from battle_royale.gui.impl.lobby.views.battle_royale_entry_point import isBattleRoyaleEntryPointAvailable
from config_schemas.umg import umgEventsConfigSchema
from constants import QUEUE_TYPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.game_control.craftmachine_controller import getCraftMachineEntryPointIsActive
from gui.impl.lobby.mapbox.mapbox_entry_point_view import isMapboxEntryPointAvailable
from gui.impl.lobby.marathon.marathon_entry_point import isMarathonEntryPointAvailable
from gui.impl.lobby.ranked.ranked_entry_point import isRankedEntryPointAvailable
from gui.impl.lobby.stronghold.stronghold_entry_point_view import isStrongholdEntryPointAvailable
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.shared import g_eventBus, events
from gui.shared.system_factory import registerBannerEntryPointValidator, collectBannerEntryPointValidator
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency
from helpers.time_utils import getServerUTCTime, ONE_DAY
from helpers.time_utils import getTimestampByStrDate
from skeletons.gui.game_control import IEventsNotificationsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_HANGAR_ENTRY_POINTS = 'hangarEntryPoints'
_SECONDS_BEFORE_UPDATE = 2
registerBannerEntryPointValidator(HANGAR_ALIASES.CRAFT_MACHINE_ENTRY_POINT, getCraftMachineEntryPointIsActive)
registerBannerEntryPointValidator(RANKEDBATTLES_ALIASES.ENTRY_POINT, isRankedEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.MAPBOX_ENTRY_POINT, isMapboxEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.MARATHON_ENTRY_POINT, isMarathonEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.STRONGHOLD_ENTRY_POINT, isStrongholdEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.BR_ENTRY_POINT, isBattleRoyaleEntryPointAvailable)
_logger = logging.getLogger(__name__)

class _EntryPointData(object):
    __slots__ = ['id',
     'startDate',
     'endDate',
     'weight',
     'data',
     '__isValidData']

    def __init__(self, entryData):
        super(_EntryPointData, self).__init__()
        self.data = entryData
        self.id = entryData.get('id')
        self.updateValidData()

    def updateValidData(self):
        weightConfigName = self.data.get('weightConfig')
        weightModel = getWeightByEventName(weightConfigName)
        self.weight = weightModel.weight if weightModel is not None else -1
        startDateStr = self.data.get('startDate')
        endDateStr = self.data.get('endDate')
        self.__isValidData = weightConfigName and weightModel and self.id is not None and startDateStr is not None and endDateStr is not None
        if self.__isValidData:
            self.startDate = getTimestampByStrDate(startDateStr)
            self.endDate = getTimestampByStrDate(endDateStr)
            self.__isValidData = self.startDate < self.endDate
            if not self.__isValidData:
                _logger.error('endDate must be greater than startDate for entryPoint "%s"', self.id)
        else:
            _logger.error('Invalid data %s', str(self.data))
            if self.id is None:
                _logger.error('You must set a id')
            if startDateStr is None:
                _logger.error('You must set a startDate')
            if endDateStr is None:
                _logger.error('You must set a endDate')
            if weightConfigName is None:
                _logger.error('You must set a weightConfig')
            if weightModel is None:
                _logger.error('Invalid weightConfig %s', weightConfigName)
        return

    def isValidData(self):
        return self.__isValidData

    def isValidDateForCreation(self):
        return self.startDate < getServerUTCTime() < self.endDate

    def isExpiredDate(self):
        return getServerUTCTime() > self.endDate

    def isEarlyDate(self):
        return self.startDate > getServerUTCTime()

    def isEnabledByValidator(self):
        configValidator = collectBannerEntryPointValidator(self.id)
        return configValidator() if configValidator is not None else True


class EventsService(IEventsService, Notifiable):
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ['__entries', '__serverSettings']

    def __init__(self):
        super(EventsService, self).__init__()
        self.__entries = {}
        self.__visibleEntries = []
        self.__serverSettings = None
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        return

    @property
    def isAvailable(self):
        return len(self.getEntries()) > 0

    def onPrbEntitySwitched(self):
        self.__updateEntries()

    def getEntries(self):
        return self.__visibleEntries

    def updateEntries(self):
        self.__updateEntries()

    def startListening(self):
        self.__notificationsCtrl.onEventNotificationsChanged += self.__onEventNotification
        self.__handleNotifications(self.__notificationsCtrl.getEventsNotifications())
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        g_playerEvents.onConfigModelUpdated += self.__onConfigModelUpdated
        self.startGlobalListening()

    def stopListening(self):
        self.__visibleEntries = []
        self.stopGlobalListening()
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__onEventNotification
        self.clearNotification()
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync
        g_playerEvents.onConfigModelUpdated -= self.__onConfigModelUpdated
        if self.__serverSettings:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateSettings

    def finalize(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.stopListening()

    def _isQueueEnabled(self):
        enabledQueues = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.WINBACK)
        return any((self.__isQueueSelected(queueType) for queueType in enabledQueues))

    def __onLobbyInited(self, *_):
        self.startListening()

    def __onAccountBecomeNonPlayer(self):
        self.stopListening()

    def __isQueueSelected(self, queueType):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(queueType) if self.prbDispatcher is not None else False

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onUpdateSettings
        self.__updateEntries()
        return

    def __onUpdateSettings(self, diff):
        self.__updateEntries()

    def __onEventNotification(self, added, removed):
        for item in chain(added, removed):
            if item.eventType == _HANGAR_ENTRY_POINTS:
                self.__handleNotifications(self.__notificationsCtrl.getEventsNotifications())
                break

    def __onCacheResync(self, _, __):
        self.__updateEntries()

    def __handleNotifications(self, notifications):
        newEntries = {}
        for item in notifications:
            if item.eventType == _HANGAR_ENTRY_POINTS:
                notificationEntries = json.loads(item.data)
                for entryData in notificationEntries:
                    entryId = entryData.get('id')
                    entry = self.__entries.get(entryId)
                    if not (entry and entry.data == entryData):
                        entry = _EntryPointData(entryData)
                    if entry.isValidData() and not entry.isExpiredDate():
                        newEntries[entryId] = entry

        if not newEntries == self.__entries:
            self.__entries = newEntries
            self.clearNotification()
            self.addNotificator(SimpleNotifier(self.__getCooldownForUpdate, self.__onUpdateNotify))
            self.startNotification()
        self.__updateEntries()

    def __onUpdateNotify(self):
        self.__handleNotifications(self.__notificationsCtrl.getEventsNotifications())

    def __getCooldownForUpdate(self):
        currentTime = getServerUTCTime()
        nearestDate = currentTime + ONE_DAY
        for entry in self.__entries.itervalues():
            if entry.isEarlyDate():
                nearestDate = min(nearestDate, entry.startDate)
            nearestDate = min(nearestDate, entry.endDate)

        return nearestDate - currentTime + _SECONDS_BEFORE_UPDATE

    def __updateEntries(self):
        data = []
        if self._isQueueEnabled():
            weights = [ item.weight for item in self.__entries.itervalues() ]
            if len(weights) > len(set(weights)):
                _logger.warning('You have entryPoints with same priorities. EntryPoints have been sorted by startDate')
            sortKeyFunc = lambda x: (-x.weight, x.startDate, x.id.lower())
            sortedEntries = sorted(self.__entries.itervalues(), key=sortKeyFunc)
            for entry in sortedEntries:
                if entry.isValidDateForCreation() and entry.isEnabledByValidator() and entry.isValidData():
                    data.append(entry)

        if self.__visibleEntries != data:
            self.__visibleEntries = data
            self.onEventsListChanged()

    def __onConfigModelUpdated(self, gpKey):
        if umgEventsConfigSchema.gpKey == gpKey:
            for entry in self.__entries.values():
                entry.updateValidData()

            self.__handleNotifications(self.__notificationsCtrl.getEventsNotifications())


def getWeightByEventName(eventName):
    return umgEventsConfigSchema.getModel().getWeightByName(eventName)
