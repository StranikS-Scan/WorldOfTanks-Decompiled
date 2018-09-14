# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsCurrentTab.py
from collections import defaultdict
import constants
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events.event_items import DEFAULTS_GROUPS
from items import getTypeOfCompactDescr
from shared_utils import CONST_CONTAINER
from gui import SystemMessages, game_control
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters import text_styles
from gui.server_events import g_eventsCache, formatters, settings as quest_settings, caches as quest_caches
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.meta.QuestsCurrentTabMeta import QuestsCurrentTabMeta
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from helpers.i18n import makeString as _ms

class QuestsCurrentTab(QuestsCurrentTabMeta):

    class FILTER_TYPE(CONST_CONTAINER):
        ALL_EVENTS = 0
        QUESTS = 1
        ACTIONS = 2

    def __init__(self):
        super(QuestsCurrentTab, self).__init__()
        self.__collapsedGroups = []
        self.__currentVehicle = None
        return

    def getSortedTableData(self, tableData):
        return events_helpers.getSortedTableData(tableData)

    def _selectQuest(self, questID):
        quests = g_eventsCache.getEvents()
        if questID in quests:
            quest = quests.get(questID)
            if self._isAvailableQuestForTab(quest):
                info = events_helpers.getEventDetails(quest, quests)
                self.as_setSelectedQuestS(questID)
                self.as_updateQuestInfoS(info)
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.QUESTS_NOQUESTSWITHGIVENID)

    def sort(self, filterType, hideCompleted):
        self.__filterType = filterType
        self._hideCompleted = hideCompleted
        self._invalidateEventsData()

    def getQuestInfo(self, eventID):
        self.as_showWaitingS(True)
        svrEvents = self._getEvents()
        event = svrEvents.get(eventID)
        if eventID != self._navInfo.common.questID:
            self._navInfo.selectCommonQuest(eventID)
            quest_settings.visitEventGUI(event)
        info = None
        if event is not None:
            info = events_helpers.getEventDetails(event, svrEvents)
        self.as_updateQuestInfoS(info)
        return

    def collapse(self, groupID):
        """
        Method is used for collapsing quest groups.
        
        :param groupID: group id from xml file describing quest.
        
        Basically it stores an array of groupIDs
        for us to know which quests (based on their
        belonging to the group with groupID) to exclude from
        render list when forming it.
        """
        if groupID in self.__collapsedGroups:
            self.__collapsedGroups.remove(groupID)
        else:
            self.__collapsedGroups.append(groupID)
        self._invalidateEventsData()

    def _populate(self):
        super(QuestsCurrentTab, self)._populate()
        self.__currentVehicle = g_currentVehicle
        self.__currentVehicle.onChanged += self.__onEventsUpdated
        g_eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        game_control.g_instance.igr.onIgrTypeChanged += self.__onEventsUpdated
        g_clientUpdateManager.addCallbacks({'quests': self.__onEventsUpdated,
         'cache.eventsData': self.__onEventsUpdated,
         'inventory.1': self.__onEventsUpdated,
         'stats.unlocks': self.__onItemUnlocked})
        self.__filterType = self.FILTER_TYPE.ALL_EVENTS
        self._hideCompleted = False
        self.addListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onEventsUpdated)
        self._invalidateEventsData()
        if self._navInfo.common.questID:
            self._selectQuest(self._navInfo.common.questID)

    def _invalidateEventsData(self):
        svrEvents = self._getEvents()
        svrGroups = self._getGroups()
        vehicle = self.__currentVehicle.item
        result = []
        groups = defaultdict(list)
        groupedEvents = defaultdict(list)
        for e in self._applyFilters(svrEvents.values()):
            groupID = e.getGroupID()
            eventVO = events_helpers.getEventInfo(e, svrEvents)
            eventVO.update({'description': eventVO['description']})
            isAvailableForCurrentVehicle, _ = e.isAvailableForVehicle(vehicle)
            if isAvailableForCurrentVehicle and self._isQuest(e):
                groups[DEFAULTS_GROUPS.CURRENTLY_AVAILABLE].append(eventVO)
                groupedEvents[DEFAULTS_GROUPS.CURRENTLY_AVAILABLE].append(e)
            groups[groupID].append(eventVO)
            groupedEvents[groupID].append(e)

        currentQuests = groups[DEFAULTS_GROUPS.CURRENTLY_AVAILABLE]
        if len(currentQuests) > 0:
            groupRecord = formatters.packGroupBlock(_ms(QUESTS.QUESTS_TITLE_CURRENTLYAVAILABLE, vehicleName=vehicle.shortUserName))
            groupRecord.update({'showBckgrImage': True,
             'bckgrImage': events_helpers.RENDER_BACKS.get(DEFAULTS_GROUPS.CURRENTLY_AVAILABLE)})
            self.__addGroupRecords(groupRecord, currentQuests, result, DEFAULTS_GROUPS.CURRENTLY_AVAILABLE)
        for groupID, group in self._getSortedEvents(svrGroups):
            groupItems = groups[groupID]
            if len(groupItems) > 0:
                groupEvent = groupedEvents[groupID][0]
                groupStatus = self.__getGroupStatusMessage(groupItems, groupEvent)
                groupRecord = formatters.packGroupBlock(group.getUserName(), events_helpers.RENDER_BACKS.get(group.getIconID(), None))
                groupRecord.update({'groupStatus': groupStatus})
                self.__addGroupRecords(groupRecord, groupItems, result, groupID)

        ungroupedQuests = groups[DEFAULTS_GROUPS.UNGROUPED_QUESTS]
        if len(ungroupedQuests) > 0:
            groupRecord = formatters.packGroupBlock(QUESTS.QUESTS_TITLE_UNGOUPEDQUESTS)
            groupRecord.update({'showBckgrImage': True,
             'bckgrImage': events_helpers.RENDER_BACKS.get(DEFAULTS_GROUPS.UNGROUPED_QUESTS)})
            self.__addGroupRecords(groupRecord, ungroupedQuests, result, DEFAULTS_GROUPS.UNGROUPED_QUESTS)
        ungroupedActions = groups[DEFAULTS_GROUPS.UNGROUPED_ACTIONS]
        if len(ungroupedActions) > 0:
            groupRecord = formatters.packGroupBlock(QUESTS.QUESTS_TITLE_UNGOUPEDACTIONS)
            groupRecord.update({'showBckgrImage': True,
             'bckgrImage': events_helpers.RENDER_BACKS.get(DEFAULTS_GROUPS.UNGROUPED_ACTIONS)})
            self.__addGroupRecords(groupRecord, ungroupedActions, result, DEFAULTS_GROUPS.UNGROUPED_ACTIONS)
        if not result:
            self.as_showNoDataS()
        else:
            self.as_setQuestsDataS({'quests': result,
             'isSortable': True,
             'totalTasks': len(svrEvents),
             'rendererType': QUESTS_ALIASES.QUEST_RENDERER_BZ_ALIAS})
            visibleQuestIDs = map(lambda item: item.get('questID', ''), result)
            if self._navInfo.common.questID not in visibleQuestIDs:
                self._navInfo.selectCommonQuest(None)
                self.as_showNoSelectS()
            self.as_setSelectedQuestS(self._navInfo.common.questID)
        return

    def _dispose(self):
        self.__currentVehicle.onChanged -= self.__onEventsUpdated
        self.__currentVehicle = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onEventsUpdated
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.removeListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onEventsUpdated)
        super(QuestsCurrentTab, self)._dispose()
        return

    @classmethod
    def _getEvents(cls):
        return g_eventsCache.getEvents()

    @classmethod
    def _getGroups(cls):
        return g_eventsCache.getGroups()

    @classmethod
    def _isQuest(cls, svrEvent):
        return svrEvent.getType() in constants.EVENT_TYPE.QUEST_RANGE

    @classmethod
    def _isBattleQuest(cls, svrEvent):
        return svrEvent.getType() == constants.EVENT_TYPE.BATTLE_QUEST

    @classmethod
    def _isAction(cls, svrEvent):
        return svrEvent.getType() == constants.EVENT_TYPE.ACTION

    @classmethod
    def _isAvailableQuestForTab(cls, svrEvent):
        return svrEvent.getType() not in (constants.EVENT_TYPE.MOTIVE_QUEST, constants.EVENT_TYPE.CLUBS_QUEST)

    def _filterFunc(self, event):
        if self.__filterType == self.FILTER_TYPE.ACTIONS and not self._isAction(event):
            return False
        return False if self.__filterType == self.FILTER_TYPE.QUESTS and not self._isQuest(event) else not (self._hideCompleted and event.isCompleted()) and self._isAvailableQuestForTab(event)

    def _applyFilters(self, quests):
        return filter(self._filterFunc, self._applySort(quests))

    def _getSortedEvents(self, events):
        return sorted(events.items(), key=lambda (eID, event): (event.getPriority(), event.getUserName()))

    def _applySort(self, quests):
        return sorted(quests, events_helpers.questsSortFunc)

    def __getGroupStatusMessage(self, groupItems, groupEvent):
        message = _ms(QUESTS.QUESTS_STATUS_ALLDONE)
        for item in groupItems:
            if item['status'] != events_helpers.EVENT_STATUS.COMPLETED:
                message = text_styles.main(events_helpers.getEventActiveDateString(groupEvent))
                break

        return message

    def __addGroupRecords(self, groupRecord, groupItems, result, groupID):
        """
        Method is used to determine whether we need to include quest
        items into render list or not. If groupID is in the list of
        collapsed groups, quests belonging to that group ("groupItems") are not
        appended to the "result".
        
        Method modifies "result" argument for outer scope.
        """
        groupRecord.update({'groupID': groupID})
        groupIsOpen = groupID not in self.__collapsedGroups
        groupRecord.update({'isOpen': groupIsOpen})
        result.append(groupRecord)
        if groupIsOpen:
            result.extend(groupItems)

    def __onEventsCacheSyncCompleted(self):
        self.__onInvalidateCallback()

    def __onInvalidateCallback(self):
        self._invalidateEventsData()

    def __onItemUnlocked(self, unlocks):
        for intCD in unlocks:
            if getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE:
                return self.__onEventsUpdated()

    def __onEventsUpdated(self, *args):
        quest_settings.updateCommonEventsSettings(g_eventsCache.getEvents())
        self._invalidateEventsData()
