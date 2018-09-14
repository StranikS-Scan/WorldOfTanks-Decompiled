# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsCurrentTab.py
from collections import defaultdict
import constants
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events.event_items import DEFAULTS_GROUPS
from items import getTypeOfCompactDescr
from shared_utils import CONST_CONTAINER
from gui import SystemMessages, game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.server_events import g_eventsCache, formatters, settings as quest_settings, caches as quest_caches
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.meta.QuestsCurrentTabMeta import QuestsCurrentTabMeta
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES

class QuestsCurrentTab(QuestsCurrentTabMeta):

    class FILTER_TYPE(CONST_CONTAINER):
        ALL_EVENTS = 0
        ACTIONS = 1
        QUESTS = 2

    def __init__(self):
        super(QuestsCurrentTab, self).__init__()
        self._navInfo = quest_caches.getNavInfo()

    def getSortedTableData(self, tableData):
        return formatters.packVehiclesList(*quest_caches.sortVehTable(tableData.tableID, tableData.buttonID, tableData.sortingDirection, int(tableData.nation), int(tableData.vehType), int(tableData.level), tableData.cbSelected, tableData.isAction))

    def selectQuest(self, questID):
        quests = self._getEvents()
        if questID in quests:
            return self.as_setSelectedQuestS(questID)
        SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.QUESTS_NOQUESTSWITHGIVENID)

    def sort(self, filterType, hideCompleted):
        self.__filterType = filterType
        self.__hideCompleted = hideCompleted
        self.__invalidateEventsData()

    def getQuestInfo(self, eventID):
        svrEvents = self._getEvents()
        event = svrEvents.get(eventID)
        quest_settings.visitEventGUI(event)
        self._navInfo.selectCommonQuest(eventID)
        if event is not None:
            return events_helpers.getEventDetails(event, svrEvents)
        else:
            return

    def _populate(self):
        super(QuestsCurrentTab, self)._populate()
        g_eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        game_control.g_instance.igr.onIgrTypeChanged += self.__onEventsUpdated
        g_clientUpdateManager.addCallbacks({'quests': self.__onEventsUpdated,
         'cache.eventsData': self.__onEventsUpdated,
         'inventory.1': self.__onEventsUpdated,
         'stats.unlocks': self.__onItemUnlocked})
        self.__filterType = self.FILTER_TYPE.ALL_EVENTS
        self.__hideCompleted = False
        self.addListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onEventsUpdated)
        self.__invalidateEventsData()
        if self._navInfo.common.questID:
            self.selectQuest(self._navInfo.common.questID)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onEventsUpdated
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.removeListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onEventsUpdated)
        super(QuestsCurrentTab, self)._dispose()

    @classmethod
    def _getEvents(cls):
        return g_eventsCache.getEvents()

    @classmethod
    def _getGroups(cls):
        return g_eventsCache.getGroups()

    @classmethod
    def _isQuest(cls, svrEvent):
        return svrEvent.getType() in (constants.EVENT_TYPE.BATTLE_QUEST, constants.EVENT_TYPE.TOKEN_QUEST, constants.EVENT_TYPE.FORT_QUEST)

    @classmethod
    def _isFortQuest(cls, svrEvent):
        return svrEvent.getType() in (constants.EVENT_TYPE.FORT_QUEST,)

    @classmethod
    def _isAction(cls, svrEvent):
        return svrEvent.getType() == constants.EVENT_TYPE.ACTION

    def __onItemUnlocked(self, unlocks):
        for intCD in unlocks:
            if getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE:
                return self.__onEventsUpdated()

    def __onEventsUpdated(self, *args):
        quest_settings.updateCommonEventsSettings(g_eventsCache.getEvents())
        self.__invalidateEventsData()

    @classmethod
    def __sortFunc(cls, a, b):
        res = cmp(a.isCompleted(), b.isCompleted())
        if res:
            return res
        res = cmp(cls._isFortQuest(a), cls._isFortQuest(b))
        if res:
            return -res
        res = cmp(a.getPriority(), b.getPriority())
        if res:
            return res
        return cmp(a.getUserName(), b.getUserName())

    def __filterFunc(self, a):
        if self.__filterType == self.FILTER_TYPE.ACTIONS and not self._isAction(a):
            return False
        if self.__filterType == self.FILTER_TYPE.QUESTS and not self._isQuest(a):
            return False
        return not self.__hideCompleted or not a.isCompleted()

    def __applyFilters(self, quests):
        return filter(self.__filterFunc, self.__applySort(quests))

    def __applySort(self, quests):
        return sorted(quests, self.__sortFunc)

    def __onEventsCacheSyncCompleted(self):
        self.__onInvalidateCallback()

    def __invalidateEventsData(self):
        svrEvents = self._getEvents()
        svrGroups = self._getGroups()
        result = []
        groups = defaultdict(list)
        for e in self.__applyFilters(svrEvents.values()):
            groupID = e.getGroupID()
            groups[groupID].append(events_helpers.getEventInfo(e, svrEvents))

        for groupID, group in self.__getSortedEvents(svrGroups):
            groupItems = groups[groupID]
            if len(groupItems) > 0:
                result.append(formatters.packGroupBlock(group.getUserName()))
                result.extend(groupItems)

        ungroupedQuests = groups[DEFAULTS_GROUPS.UNGROUPED_QUESTS]
        if len(ungroupedQuests) > 0:
            result.append(formatters.packGroupBlock(QUESTS.QUESTS_TITLE_UNGOUPEDQUESTS))
            result.extend(ungroupedQuests)
        ungroupedActions = groups[DEFAULTS_GROUPS.UNGROUPED_ACTIONS]
        if len(ungroupedActions) > 0:
            result.append(formatters.packGroupBlock(QUESTS.QUESTS_TITLE_UNGOUPEDACTIONS))
            result.extend(ungroupedActions)
        self.as_setQuestsDataS(result, len(svrEvents))

    def __getSortedEvents(self, events):
        return sorted(events.items(), key=lambda (eID, event): (event.getPriority(), event.getUserName()))

    def __onInvalidateCallback(self):
        self.__invalidateEventsData()
