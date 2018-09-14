# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsCurrentTab.py
from collections import defaultdict
import time
import constants
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events.event_items import DEFAULTS_GROUPS
from items import getTypeOfCompactDescr
from shared_utils import CONST_CONTAINER
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.formatters import text_styles
from gui.server_events import formatters, settings as quest_settings
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.meta.QuestsCurrentTabMeta import QuestsCurrentTabMeta
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IIGRController, IQuestsController

class QuestsCurrentTab(QuestsCurrentTabMeta):

    class FILTER_TYPE(CONST_CONTAINER):
        ALL_QUESTS = 0
        ACTIONS = 1
        CURRENT_VEHICLE = 2

    igrCtrl = dependency.descriptor(IIGRController)
    eventsCache = dependency.descriptor(IEventsCache)
    _questController = dependency.descriptor(IQuestsController)

    def __init__(self):
        super(QuestsCurrentTab, self).__init__()
        self.__collapsedGroups = []
        self.__currentVehicle = None
        self.__selectedQuestID = None
        return

    def getSortedTableData(self, tableData):
        return events_helpers.getSortedTableData(tableData)

    def _selectQuest(self, questID):
        quests = {e.getID():e for e in self._getEvents()}
        if questID in quests:
            quest = quests.get(questID)
            if self._isAvailableQuestForTab(quest):
                info = events_helpers.getEventDetails(quest, quests)
                self.__selectedQuestID = questID
                self.as_setSelectedQuestS(questID)
                self.as_updateQuestInfoS(info)
                quest_settings.visitEventGUI(quest)
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.QUESTS_NOQUESTSWITHGIVENID)

    def sort(self, filterType, hideCompleted):
        self.__filterType = filterType
        self._hideCompleted = hideCompleted
        self._invalidateEventsData()

    def getQuestInfo(self, eventID):
        self.as_showWaitingS(True)
        if self.__filterType == self.FILTER_TYPE.ACTIONS:
            source = self._getActions()
        else:
            source = self._getEvents()
        svrEvents = {e.getID():e for e in source}
        event = svrEvents.get(eventID)
        if not event:
            return
        else:
            self._navInfo.selectCommonQuest(eventID)
            self.__selectedQuestID = eventID
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
        self.as_setSelectedQuestS(self._navInfo.common.questID)

    def _populate(self):
        super(QuestsCurrentTab, self)._populate()
        self.__currentVehicle = g_currentVehicle
        self.__currentVehicle.onChanged += self.__onEventsUpdated
        self.eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        self.igrCtrl.onIgrTypeChanged += self.__onEventsUpdated
        g_clientUpdateManager.addCallbacks({'quests': self.__onEventsUpdated,
         'cache.eventsData': self.__onEventsUpdated,
         'inventory.1': self.__onEventsUpdated,
         'stats.unlocks': self.__onItemUnlocked})
        self.__filterType = self.FILTER_TYPE.ALL_QUESTS
        self._hideCompleted = False
        self.addListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onEventsUpdated)
        self._invalidateEventsData()
        defaultQuestID = self._getDefaultQuestID()
        if defaultQuestID:
            self._selectQuest(defaultQuestID)
        self._updateFilterView()

    def _updateFilterView(self):
        vehicle = self.__currentVehicle.item

        def _filter(event):
            return quest_settings.isNewCommonEvent(event) and not (self._hideCompleted and event.isCompleted())

        tabs = [{'label': QUESTS.QUESTS_CURRENTTAB_HEADER_TAB_ALL,
          'header': text_styles.highTitle(QUESTS.QUESTS_CURRENTTAB_HEADER_TAB_ALL),
          'cbDoneVisible': True}, {'label': QUESTS.QUESTS_CURRENTTAB_HEADER_TAB_ACTION,
          'header': text_styles.highTitle(QUESTS.QUESTS_CURRENTTAB_HEADER_TAB_ACTION)}, {'label': _ms(QUESTS.QUESTS_CURRENTTAB_HEADER_TAB_VEHICLE, vehicle=vehicle.shortUserName),
          'header': text_styles.highTitle(_ms(QUESTS.QUESTS_CURRENTTAB_HEADER_TAB_VEHICLE, vehicle=vehicle.shortUserName)),
          'cbDoneVisible': True}]
        eventsForVehicle = len([ e for e in self._questController.getQuestForVehicle(vehicle) if _filter(e) ])
        actions = len([ e for e in self._getActions() if quest_settings.isNewCommonEvent(e) ])
        allEvents = len([ e for e in self._getEvents() if quest_settings.isNewCommonEvent(e) ])
        self.as_setTabBarCountersS([allEvents, actions, eventsForVehicle])
        self.as_setTabBarDataS(tabs)

    def _getDefaultQuestID(self):
        return self._navInfo.common.questID

    def _invalidateEventsData(self):
        if self.__filterType == self.FILTER_TYPE.CURRENT_VEHICLE:
            svrEvents = self._questController.getQuestForVehicle(self.__currentVehicle.item)
        elif self.__filterType == self.FILTER_TYPE.ACTIONS:
            svrEvents = self._getActions()
        else:
            svrEvents = self._getEvents()
        svrGroups = self._getGroups()
        result = []
        groups = defaultdict(list)
        groupedEvents = defaultdict(list)
        for e in self._applyFilters(svrEvents):
            groupID = e.getGroupID()
            eventVO = events_helpers.getEventInfo(e, svrEvents)
            eventVO.update({'description': eventVO['description']})
            groups[groupID].append(eventVO)
            groupedEvents[groupID].append(e)

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
            statusText = ''
            if self.__filterType == self.FILTER_TYPE.ACTIONS:
                statusText = '{0}\n{1}'.format(text_styles.middleTitle(QUESTS.QUESTS_EMPTY_ACTIONS_HEADER), text_styles.main(QUESTS.QUESTS_EMPTY_ACTIONS_BODY))
            elif self.__filterType == self.FILTER_TYPE.ALL_QUESTS:
                statusText = '{0}\n{1}'.format(text_styles.middleTitle(QUESTS.QUESTS_EMPTY_QUESTS_HEADER), text_styles.main(QUESTS.QUESTS_EMPTY_QUESTS_BODY))
            elif self.__filterType == self.FILTER_TYPE.CURRENT_VEHICLE:
                statusText = '{0}\n{1}'.format(text_styles.middleTitle(_ms(QUESTS.QUESTS_EMPTY_VEHICLE_HEADER, vehicle=self.__currentVehicle.item.shortUserName)), text_styles.main(QUESTS.QUESTS_EMPTY_VEHICLE_BODY))
            self.as_showNoDataS(statusText)
            self.__selectedQuestID = None
            self._navInfo.selectCommonQuest(None)
        else:
            self.as_setQuestsDataS({'quests': result,
             'totalTasks': len(svrEvents),
             'rendererType': QUESTS_ALIASES.QUEST_RENDERER_BZ_ALIAS})
            visibleQuestIDs = map(lambda item: item.get('questID', ''), result)
            if self._navInfo.common.questID not in visibleQuestIDs:
                self._navInfo.selectCommonQuest(None)
                self.as_showNoSelectS()
                self.__selectedQuestID = None
                self.as_setSelectedQuestS(self._navInfo.common.questID)
            elif self._navInfo.common.questID != self.__selectedQuestID:
                self.__selectedQuestID = self._navInfo.common.questID
                self.as_setSelectedQuestS(self._navInfo.common.questID)
        return

    def _dispose(self):
        self.__currentVehicle.onChanged -= self.__onEventsUpdated
        self.__currentVehicle = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.igrCtrl.onIgrTypeChanged -= self.__onEventsUpdated
        self.eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.removeListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onEventsUpdated)
        super(QuestsCurrentTab, self)._dispose()
        return

    @classmethod
    def _getEvents(cls):
        return cls._questController.getAllAvailableQuests()

    @classmethod
    def _getGroups(cls):
        return cls._questController.getQuestGroups()

    @classmethod
    def _getActions(cls):
        return cls.eventsCache.getActions().values()

    @classmethod
    def _isQuest(cls, svrEvent):
        return svrEvent.getType() in constants.EVENT_TYPE.QUEST_RANGE

    @classmethod
    def _isAction(cls, svrEvent):
        return svrEvent.getType() == constants.EVENT_TYPE.ACTION

    @classmethod
    def _isAvailableQuestForTab(cls, svrEvent):
        return svrEvent.getType() == constants.EVENT_TYPE.MOTIVE_QUEST

    def _filterFunc(self, event):
        if self.__filterType == self.FILTER_TYPE.ACTIONS:
            return self._isAction(event)
        return not (self._hideCompleted and event.isCompleted() and event.getFinishTimeLeft()) if self._isQuest(event) else False

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
                event_date = events_helpers.getEventActiveDateString(groupEvent)
                message = text_styles.main(event_date) if event_date else ''
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
        newTasksCount = 0
        for item in groupItems:
            if item.get('isNew'):
                newTasksCount += 1

        groupRecord.update({'newSubtasksCount': newTasksCount})
        groupRecord.update({'groupID': groupID})
        groupIsOpen = groupID not in self.__collapsedGroups
        groupRecord.update({'isOpen': groupIsOpen})
        if self.__filterType == self.FILTER_TYPE.ALL_QUESTS:
            result.append(groupRecord)
        if groupIsOpen or self.__filterType != self.FILTER_TYPE.ALL_QUESTS:
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
        quest_settings.updateCommonEventsSettings({e.getID():e for e in self._getEvents()})
        self._invalidateEventsData()
        self._updateFilterView()
