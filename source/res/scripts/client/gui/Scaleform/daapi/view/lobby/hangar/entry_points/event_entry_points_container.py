# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/entry_points/event_entry_points_container.py
import json
import logging
from operator import attrgetter
from itertools import chain
from battle_royale.gui.impl.lobby.views.battle_royale_entry_point import isBattleRoyaleEntryPointAvailable
from constants import QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.comp7.comp7_entry_point import isComp7EntryPointAvailable
from gui.Scaleform.daapi.view.meta.EventEntryPointsContainerMeta import EventEntryPointsContainerMeta
from gui.impl.lobby.mapbox.mapbox_entry_point_view import isMapboxEntryPointAvailable
from gui.impl.lobby.ranked.ranked_entry_point import isRankedEntryPointAvailable
from gui.impl.lobby.marathon.marathon_entry_point import isMarathonEntryPointAvailable
from gui.Scaleform.daapi.view.lobby.collection.collection_entry_point import isCollectionEntryPointAvailable
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.impl.lobby.stronghold.stronghold_entry_point_view import isStrongholdEntryPointAvailable
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.system_factory import registerBannerEntryPointValidator, collectBannerEntryPointValidator, registerBannerEntryPointLUIRule, collectBannerEntryPointLUIRule
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.game_control.craftmachine_controller import getCraftMachineEntryPointIsActive
from gui.game_control.shop_sales_event_controller import getShopSalesEntryPointIsActive
from helpers import dependency
from helpers.time_utils import getServerUTCTime, ONE_DAY
from helpers.time_utils import getTimestampByStrDate
from skeletons.gui.game_control import IEventsNotificationsController, IBootcampController, ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_HANGAR_ENTRY_POINTS = 'hangarEntryPoints'
_SECONDS_BEFORE_UPDATE = 2
_COUNT_VISIBLE_ENTRY_POINTS = 2
_ADDITIONAL_SWFS_MAP = {}
registerBannerEntryPointValidator(HANGAR_ALIASES.CRAFT_MACHINE_ENTRY_POINT, getCraftMachineEntryPointIsActive)
registerBannerEntryPointValidator(HANGAR_ALIASES.SHOP_SALES_ENTRY_POINT, getShopSalesEntryPointIsActive)
registerBannerEntryPointValidator(RANKEDBATTLES_ALIASES.ENTRY_POINT, isRankedEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.MAPBOX_ENTRY_POINT, isMapboxEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.MARATHON_ENTRY_POINT, isMarathonEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.COMP7_ENTRY_POINT, isComp7EntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.STRONGHOLD_ENTRY_POINT, isStrongholdEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.BR_ENTRY_POINT, isBattleRoyaleEntryPointAvailable)
registerBannerEntryPointValidator(HANGAR_ALIASES.COLLECTION_ENTRY_POINT, isCollectionEntryPointAvailable)
registerBannerEntryPointLUIRule(HANGAR_ALIASES.COMP7_ENTRY_POINT, LuiRules.COMP7_ENTRY_POINT)
registerBannerEntryPointLUIRule(HANGAR_ALIASES.CRAFT_MACHINE_ENTRY_POINT, LuiRules.CRAFT_MACHINE_ENTRY_POINT)
registerBannerEntryPointLUIRule(HANGAR_ALIASES.SHOP_SALES_ENTRY_POINT, LuiRules.SHOP_SALES_ENTRY_POINT)
registerBannerEntryPointLUIRule(HANGAR_ALIASES.MAPBOX_ENTRY_POINT, LuiRules.MAPBOX_ENTRY_POINT)
registerBannerEntryPointLUIRule(HANGAR_ALIASES.STRONGHOLD_ENTRY_POINT, LuiRules.STRONGHOLD_ENTRY_POINT)
registerBannerEntryPointLUIRule(HANGAR_ALIASES.BR_ENTRY_POINT, LuiRules.BR_ENTRY_POINT)
ENTRY_POINTS_REQUIRING_DATA = [HANGAR_ALIASES.COLLECTION_ENTRY_POINT]
_logger = logging.getLogger(__name__)

class _EntryPointData(object):
    __slots__ = ['id',
     'startDate',
     'endDate',
     'priority',
     'data',
     '__isValidData']

    def __init__(self, entryData):
        super(_EntryPointData, self).__init__()
        self.data = entryData
        self.id = entryData.get('id')
        startDateStr = entryData.get('startDate')
        endDateStr = entryData.get('endDate')
        self.priority = entryData.get('priority')
        priorityIsInt = isinstance(self.priority, int)
        self.__isValidData = priorityIsInt and self.id is not None and startDateStr is not None and endDateStr is not None
        if self.__isValidData:
            self.startDate = getTimestampByStrDate(startDateStr)
            self.endDate = getTimestampByStrDate(endDateStr)
            self.__isValidData = self.startDate < self.endDate
            if not self.__isValidData:
                _logger.error('endDate must be greater than startDate for entryPoint "%s"', self.id)
        else:
            _logger.error('Invalid data %s', str(entryData))
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
        configValidator = collectBannerEntryPointValidator(self.id)
        if configValidator is not None:
            if self.id in ENTRY_POINTS_REQUIRING_DATA:
                return configValidator(self.data)
            return configValidator()
        else:
            return True

    def getLUIRule(self):
        return collectBannerEntryPointLUIRule(self.id)


class EventEntryPointsContainer(EventEntryPointsContainerMeta, Notifiable, IGlobalListener):
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __bootcamp = dependency.descriptor(IBootcampController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __luiController = dependency.descriptor(ILimitedUIController)
    __slots__ = ['__entries', '__serverSettings']

    def __init__(self):
        super(EventEntryPointsContainer, self).__init__()
        self.__entries = {}
        self.__serverSettings = None
        return

    def onPrbEntitySwitched(self):
        self.__updateEntries()

    def _dispose(self):
        self.__unsubscribeLUI()
        self.as_updateEntriesS([])
        self.stopGlobalListening()
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
        self.startGlobalListening()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EventEntryPointsContainer, self)._onRegisterFlashComponent(viewPy, alias)
        if alias in ENTRY_POINTS_REQUIRING_DATA:
            entry = self.__entries.get(alias, None)
            if entry is not None:
                viewPy.setData(entry.data)
        return

    def _isQueueEnabled(self):
        return self.__isQueueSelected(QUEUE_TYPE.RANDOMS)

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
                    if entry.getIsValidData() and not entry.getIsExpiredDate():
                        newEntries[entryId] = entry

        if not newEntries == self.__entries:
            self.__unsubscribeLUI()
            self.__entries = newEntries
            self.__subscribeLUI()
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
        if not self.__bootcamp.isInBootcamp() and self._isQueueEnabled():
            count = 0
            priorities = [ item.priority for item in self.__entries.itervalues() ]
            if len(priorities) > len(set(priorities)):
                _logger.warning('You have entryPoints with same priorities. EntryPoints have been sorted by startDate')
            sortedEntries = sorted(self.__entries.itervalues(), key=attrgetter('priority', 'startDate'))
            for entry in sortedEntries:
                isValidCount = count < _COUNT_VISIBLE_ENTRY_POINTS
                if isValidCount and entry.getIsValidDateForCreation() and entry.getIsEnabledByValidator() and self.__luiController.isRuleCompleted(entry.getLUIRule()):
                    count += 1
                    data.append({'entryLinkage': entry.id,
                     'swfPath': _ADDITIONAL_SWFS_MAP.get(entry.id, '')})

        self.as_updateEntriesS(data)

    def __unsubscribeLUI(self):
        for entry in self.__entries.values():
            self.__luiController.stopObserve(entry.getLUIRule(), self.__updateEntryPointVisibility)

    def __subscribeLUI(self):
        for entry in self.__entries.values():
            self.__luiController.startObserve(entry.getLUIRule(), self.__updateEntryPointVisibility)

    def __updateEntryPointVisibility(self, *_):
        self.__updateEntries()
