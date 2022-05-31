# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event_entry_points_container.py
import json
import logging
from operator import attrgetter
from itertools import chain
from constants import QUEUE_TYPE
from gui.Scaleform.daapi.view.meta.EventEntryPointsContainerMeta import EventEntryPointsContainerMeta
from gui.impl.lobby.dragon_boat.dragon_boat_entry_point import isDragonBoatEntryPointAvailable
from gui.impl.lobby.mapbox.mapbox_entry_point_view import isMapboxEntryPointAvailable
from gui.impl.lobby.ranked.ranked_entry_point import isRankedEntryPointAvailable
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.game_control.craftmachine_controller import getCraftMachineEntryPointIsActive
from gui.impl.lobby.marathon.marathon_entry_point import isMarathonEntryPointAvailable
from helpers import dependency
from helpers.time_utils import getServerUTCTime, ONE_DAY
from helpers.time_utils import getTimestampByStrDate
from skeletons.gui.game_control import IEventsNotificationsController, IBootcampController, IMapboxController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_HANGAR_ENTRY_POINTS = 'hangarEntryPoints'
_SECONDS_BEFORE_UPDATE = 2
_COUNT_VISIBLE_ENTRY_POINTS = 2
_ADDITIONAL_SWFS_MAP = {}
_ENTRY_POINT_ENABLED_VALIDATOR = {HANGAR_ALIASES.CRAFT_MACHINE_ENTRY_POINT: getCraftMachineEntryPointIsActive,
 RANKEDBATTLES_ALIASES.ENTRY_POINT: isRankedEntryPointAvailable,
 HANGAR_ALIASES.MAPBOX_ENTRY_POINT: isMapboxEntryPointAvailable,
 HANGAR_ALIASES.MARATHON_ENTRY_POINT: isMarathonEntryPointAvailable,
 HANGAR_ALIASES.EVENT_ENTRANCE_POINT: isDragonBoatEntryPointAvailable}
_logger = logging.getLogger(__name__)

class _EntryPointData(object):
    __slots__ = ['id',
     'startDate',
     'endDate',
     'priority',
     'data',
     '__isValidData']

    def __init__(self, enrtyData):
        super(_EntryPointData, self).__init__()
        self.data = enrtyData
        self.id = enrtyData.get('id')
        startDateStr = enrtyData.get('startDate')
        endDateStr = enrtyData.get('endDate')
        self.priority = enrtyData.get('priority')
        priorityIsInt = isinstance(self.priority, int)
        self.__isValidData = priorityIsInt and self.id is not None and startDateStr is not None and endDateStr is not None
        if self.__isValidData:
            self.startDate = getTimestampByStrDate(startDateStr)
            self.endDate = getTimestampByStrDate(endDateStr)
            self.__isValidData = self.startDate < self.endDate
            if not self.__isValidData:
                _logger.error('endDate must be greater than startDate for entryPoint "%s"', self.id)
        else:
            _logger.error('Invalid data %s', str(enrtyData))
            if self.id is None:
                _logger.error('You must set a id')
            if startDateStr is None:
                _logger.error('You must set a startDate')
            if endDateStr is None:
                _logger.error('You must set a endDate')
            if self.priority is None:
                _logger.error('You must set a priority')
            if not priorityIsInt:
                _logger.error('priority must be int')
        return

    def getIsValidData(self):
        return self.__isValidData

    def getIsValidDateForCreation(self):
        return self.startDate < getServerUTCTime() < self.endDate

    def getIsExpiredDate(self):
        return getServerUTCTime() > self.endDate

    def getIsEarlyDate(self):
        return self.startDate > getServerUTCTime()

    def getIsEnabledByValidator(self):
        result = False
        if self.id in _ENTRY_POINT_ENABLED_VALIDATOR:
            configValidator = _ENTRY_POINT_ENABLED_VALIDATOR.get(self.id)
            if configValidator is not None:
                result = configValidator()
            else:
                result = True
        else:
            _logger.error('Entry point "%s" validator error. You should add None object or function for config ' + 'check in _ENTRY_POINT_ENABLED_VALIDATOR.', self.id)
        return result


class EventEntryPointsContainer(EventEntryPointsContainerMeta, Notifiable, IGlobalListener):
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __bootcamp = dependency.descriptor(IBootcampController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __slots__ = ['__entries', '__serverSettings']

    def __init__(self):
        super(EventEntryPointsContainer, self).__init__()
        self.__entries = {}
        self.__serverSettings = None
        return

    def onPrbEntitySwitched(self):
        self.__updateEntries()

    def _dispose(self):
        self.as_updateEntriesS([])
        self.stopGlobalListening()
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdated
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__onEventNotification
        self.clearNotification()
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync
        if self.__serverSettings:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateSettings
        super(EventEntryPointsContainer, self)._dispose()

    def _populate(self):
        super(EventEntryPointsContainer, self)._populate()
        self.__notificationsCtrl.onEventNotificationsChanged += self.__onEventNotification
        self.__handleNotifications(self.__notificationsCtrl.getEventsNotifications())
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdated
        self.startGlobalListening()

    def _isRandomBattleSelected(self):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.RANDOMS) if self.prbDispatcher is not None else False

    def __onPrimeTimeStatusUpdated(self, *_):
        self.__updateEntries()

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
                    if entry.getIsValidData() and not entry.getIsExpiredDate():
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
            if entry.getIsEarlyDate():
                nearestDate = min(nearestDate, entry.startDate)
            nearestDate = min(nearestDate, entry.endDate)

        return nearestDate - currentTime + _SECONDS_BEFORE_UPDATE

    def __updateEntries(self):
        data = []
        if not self.__bootcamp.isInBootcamp() and self._isRandomBattleSelected():
            count = 0
            priorities = [ item.priority for item in self.__entries.itervalues() ]
            if len(priorities) > len(set(priorities)):
                _logger.warning('You have entryPoints with same priorities. EntryPoints have been sorted by startDate')
            sortedEnties = sorted(self.__entries.itervalues(), key=attrgetter('priority', 'startDate'), reverse=True)
            for entry in sortedEnties:
                isValidCount = count < _COUNT_VISIBLE_ENTRY_POINTS
                if isValidCount and entry.getIsValidDateForCreation() and entry.getIsEnabledByValidator():
                    count += 1
                    data.append({'entryLinkage': entry.id,
                     'swfPath': _ADDITIONAL_SWFS_MAP.get(entry.id, '')})

        self.as_updateEntriesS(data)
