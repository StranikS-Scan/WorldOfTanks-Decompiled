# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/EventsWindow.py
import constants
from items import getTypeOfCompactDescr
from gui import SystemMessages, game_control
from gui.shared import g_eventsCache, events
from gui.shared.utils import flashObject2Dict
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.server_events import formatters
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.meta.QuestsWindowMeta import QuestsWindowMeta
from gui.Scaleform.daapi.view.meta.QuestsCurrentTabMeta import QuestsCurrentTabMeta
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View

class EventsWindow(View, QuestsWindowMeta, AbstractWindowView):

    def __init__(self, ctx):
        super(EventsWindow, self).__init__()
        self.__startEventID = ctx.get('eventID')

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.EVENTS_CURRENT_TAB:
            self.selectCurrentEvent(self.__startEventID)
            self.__startEventID = None
        return

    def onWindowClose(self):
        formatters.clearVehiclesData()
        self.destroy()

    def getCurrentTab(self):
        return self.components.get(VIEW_ALIAS.EVENTS_CURRENT_TAB)

    def getFutureTab(self):
        return self.components.get(VIEW_ALIAS.EVENTS_FUTURE_TAB)

    def selectCurrentEvent(self, questID):
        currentTab = self.getCurrentTab()
        if questID is not None and currentTab is not None:
            currentTab.selectQuest(questID)
        return


class _QuestsTabAbstract(QuestsCurrentTabMeta):

    class FILTER_TYPE:
        ALL_EVENTS = 0
        ACTIONS = 1
        QUESTS = 2

    def getSortedTableData(self, tableData):
        td = flashObject2Dict(tableData)
        return formatters.sortingVehTable(td['tableID'], td['buttonID'], td['sortingDirection'], int(td['nation']), int(td['vehType']), int(td['level']), td['cbSelected'], td['isAction'])

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
        events_helpers.visitEventGUI(event)
        if event is not None:
            return events_helpers.getEventDetails(event, svrEvents)
        else:
            return

    def _populate(self):
        super(_QuestsTabAbstract, self)._populate()
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

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onEventsUpdated
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.removeListener(events.LobbySimpleEvent.EVENTS_UPDATED, self.__onEventsUpdated)
        super(_QuestsTabAbstract, self)._dispose()

    def _getEvents(self):
        return g_eventsCache.getCurrentEvents()

    @classmethod
    def _isQuest(cls, svrEvent):
        return svrEvent.getType() in (constants.EVENT_TYPE.BATTLE_QUEST, constants.EVENT_TYPE.TOKEN_QUEST)

    @classmethod
    def _isAction(cls, svrEvent):
        return svrEvent.getType() == constants.EVENT_TYPE.ACTION

    def __onItemUnlocked(self, unlocks):
        for intCD in unlocks:
            if getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE:
                return self.__onEventsUpdated()

    def __onEventsUpdated(self, *args):
        events_helpers.updateEventsSettings(g_eventsCache.getEvents())
        self.__invalidateEventsData()

    def __sortFunc(self, a, b):
        if a.isCompleted():
            return 1
        if b.isCompleted():
            return -1
        return cmp(a.getID(), b.getID())

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
        result = []
        for e in self.__applyFilters(svrEvents.values()):
            result.append(events_helpers.getEventInfo(e, svrEvents))

        self.as_setQuestsDataS(result, len(svrEvents))

    def __onInvalidateCallback(self):
        self.__invalidateEventsData()


class QuestsCurrentTab(_QuestsTabAbstract):

    def _getEvents(self):
        return g_eventsCache.getCurrentEvents()


class QuestsFutureTab(_QuestsTabAbstract):

    def _getEvents(self):
        return g_eventsCache.getFutureEvents()
