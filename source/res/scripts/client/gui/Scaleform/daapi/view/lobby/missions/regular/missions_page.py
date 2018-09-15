# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/missions_page.py
import BigWorld
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MISSIONS_PAGE
from async import async, await
from adisp import process, async as adispasync
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import checkEventExist
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import HIDE_DONE, HIDE_UNAVAILABLE
from gui.Scaleform.daapi.view.lobby.missions.regular import group_packers
from gui.Scaleform.daapi.view.meta.MissionsPageMeta import MissionsPageMeta
from gui.Scaleform.daapi.view.meta.MissionsViewBaseMeta import MissionsViewBaseMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import caches, settings
from gui.server_events.events_dispatcher import showMissionDetails, hideMissionDetails
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import MissionsEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.sounds.ambients import LobbySubViewEnv
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import getTypeOfCompactDescr
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.lobby_context import ILobbyContext
TabData = namedtuple('TabData', ('alias',
 'linkage',
 'tooltip',
 'tooltipDisabled',
 'label'))
TABS_DATA_ORDERED = (TabData(QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_EVENTBOARDS, QUESTS.MISSIONS_TAB_EVENTBOARDS_DISABLED, _ms(QUESTS.MISSIONS_TAB_LABEL_EVENTBOARDS)),
 TabData(QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_MARATHONS, QUESTS.MISSIONS_TAB_MARATHONS, _ms(QUESTS.MISSIONS_TAB_LABEL_MARATHONS)),
 TabData(QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_CATEGORIES, QUESTS.MISSIONS_TAB_CATEGORIES, _ms(QUESTS.MISSIONS_TAB_LABEL_CATEGORIES)),
 TabData(QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS, QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_CURRENTVEHICLE, QUESTS.MISSIONS_TAB_CURRENTVEHICLE, _ms(QUESTS.MISSIONS_TAB_LABEL_CURRENTVEHICLE)))

def setHideDoneFilter():
    filterData = {'hideDone': True,
     'hideUnavailable': False}
    AccountSettings.setFilter(MISSIONS_PAGE, filterData)


class MissionsPage(LobbySubView, MissionsPageMeta):
    __sound_env__ = LobbySubViewEnv
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsController = dependency.descriptor(IEventBoardController)

    def __init__(self, ctx):
        super(MissionsPage, self).__init__(ctx)
        self.__filterData = AccountSettings.getFilter(MISSIONS_PAGE)
        self._eventID = None
        self._groupID = None
        self.__needToScroll = False
        self._showMissionDetails = True
        self.__builders = {QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS: group_packers.MarathonsGroupsFinder(),
         QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS: group_packers.QuestsGroupsFinder(),
         QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS: group_packers.VehicleGroupFinder(),
         QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS: group_packers.ElenGroupsFinder()}
        self._initialize(ctx)
        return

    def onTabSelected(self, alias):
        self.__currentTabAlias = alias
        caches.getNavInfo().setMissionsTab(alias)
        if self.currentTab:
            self.__updateFilterLabel()
            self.currentTab.setFilters(self.__filterData)
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_TAB_CHANGED, ctx=alias), EVENT_BUS_SCOPE.LOBBY)

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def resetFilters(self):
        self.__filterData = {'hideDone': False,
         'hideUnavailable': False}
        AccountSettings.setFilter(MISSIONS_PAGE, self.__filterData)
        if self.currentTab:
            self.currentTab.setFilters(self.__filterData)

    @property
    def currentTab(self):
        return self.components.get(self.__currentTabAlias)

    def _populate(self):
        super(MissionsPage, self)._populate()
        for builder in self.__builders.itervalues():
            builder.init()

        self.addListener(MissionsEvent.ON_GROUPS_DATA_CHANGED, self.__onPageUpdate, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.PAGE_INVALIDATE, self.__pageInvalidate, EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged += self.__updateHeader
        self.__updateHeader()
        self.__tryOpenMissionDetails()
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_ACTIVATE), EVENT_BUS_SCOPE.LOBBY)

    def __pageInvalidate(self, _):
        self._invalidate()

    def _invalidate(self, ctx=None):
        super(MissionsPage, self)._invalidate(ctx)
        self._initialize(ctx)
        if self.currentTab:
            self.__updateFilterLabel()
        self.__updateHeader()
        self.__tryOpenMissionDetails()

    def _dispose(self):
        super(MissionsPage, self)._dispose()
        g_currentVehicle.onChanged -= self.__updateHeader
        self.removeListener(MissionsEvent.ON_GROUPS_DATA_CHANGED, self.__onPageUpdate, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        caches.getNavInfo().setMissionsTab(self.__currentTabAlias)
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_DEACTIVATE), EVENT_BUS_SCOPE.LOBBY)

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in QUESTS_ALIASES.MISSIONS_VIEW_PY_ALIASES:
            viewPy.setBuilder(self.__builders.get(alias), self.__filterData, self._eventID)

    def _initialize(self, ctx=None):
        ctx = ctx or {}
        self.__currentTabAlias = ctx.get('tab') or caches.getNavInfo().getMissionsTab()
        elenEnabled = self.lobbyContext.getServerSettings().isElenEnabled()
        if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS:
            if not elenEnabled or not self.eventsController.hasEvents():
                self.__currentTabAlias = None
        if not self.__currentTabAlias:
            if elenEnabled and self.eventsController.hasEvents():
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS
            elif findFirst(lambda group: group.isMarathon(), self.eventsCache.getGroups().itervalues()):
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS
            else:
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
        self._eventID = ctx.get('eventID')
        self._groupID = ctx.get('groupID')
        self._showMissionDetails = ctx.get('showMissionDetails', True)
        self.__needToScroll = self._groupID is not None
        self.__scrollToGroup()
        caches.getNavInfo().setMissionsTab(self.__currentTabAlias)
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_TAB_CHANGED, ctx=self.__currentTabAlias), EVENT_BUS_SCOPE.LOBBY)
        return

    def __scrollToGroup(self):
        if self._eventID and self._groupID and self.__needToScroll and self.currentTab is not None:
            self.currentTab.as_scrollToItemS('blockId', self._groupID)
            self.__needToScroll = False
        return

    def __onPageUpdate(self, *args):
        if self.currentTab is not None:
            self.currentTab.markVisited()
            self.__updateFilterLabel()
            self.__updateHeader()
            self.__scrollToGroup()
        return

    def __updateFilterLabel(self):
        totalQuests = self.currentTab.getTotalQuestsCount()
        currentQuests = self.currentTab.getCurrentQuestsCount()
        style = text_styles.error if currentQuests == 0 else text_styles.stats
        countText = '{} / {}'.format(style(currentQuests), text_styles.standard(totalQuests))
        filterApplied = self.__filterApplied()
        self.as_showFilterCounterS(countText, filterApplied)
        self.as_showFilterS(self.__currentTabAlias != QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS)
        if filterApplied:
            self.as_blinkFilterCounterS()

    def __onFilterChanged(self, event):
        if event.ctx != self.__filterData:
            self.__filterData = event.ctx
            if self.currentTab is not None:
                self.currentTab.setFilters(self.__filterData)
        return

    def __onFilterClosed(self, event):
        if self.__filterApplied():
            self.as_blinkFilterCounterS()

    def __updateHeader(self):
        data = []
        tabs = []
        isElenEnabled = self.lobbyContext.getServerSettings().isElenEnabled()
        for tabData in TABS_DATA_ORDERED:
            alias = tabData.alias
            tab = {'label': tabData.label,
             'linkage': tabData.linkage}
            header_tab = {'alias': alias,
             'linkage': tabData.linkage,
             'tooltip': tabData.tooltip}
            if alias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS and (not self.eventsController.hasEvents() or not isElenEnabled):
                if alias == self.__currentTabAlias:
                    self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
                continue
            if alias == self.__currentTabAlias:
                header_tab['selected'] = True
            if alias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS:
                if not isElenEnabled:
                    header_tab['tooltip'] = tabData.tooltipDisabled
                    header_tab['enabled'] = False
            if alias == QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS:
                vehicle = g_currentVehicle.item
                if vehicle:
                    vehName = vehicle.shortUserName
                else:
                    vehName = ''
                tab['label'] = tabData.label % {'vehName': vehName}
            if alias in (QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS):
                advisableQuests = self.eventsCache.getAdvisableQuests()
                if self.currentTab is not None and self.__currentTabAlias == alias:
                    newEvents = settings.getNewCommonEvents(self.currentTab.getSuitableEvents())
                else:
                    events = self.__builders[alias].getBlocksAdvisableEvents(advisableQuests)
                    newEvents = settings.getNewCommonEvents(events)
                tab['value'] = len(newEvents)
            tabs.append(header_tab)
            data.append(tab)

        self.as_setTabsDataProviderS(tabs)
        self.as_setTabsCounterDataS(data)
        self.as_showFilterS(self.__currentTabAlias != QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS)
        return

    def __filterApplied(self):
        for attr in self.__filterData:
            if self.__filterData[attr]:
                return True

        return False

    def __tryOpenMissionDetails(self):
        """ Depending on the open context, we may need to open missions details or close them.
        """
        if self._eventID and self._groupID and self._showMissionDetails:
            showMissionDetails(self._eventID, self._groupID)
        else:
            hideMissionDetails()


class MissionViewBase(MissionsViewBaseMeta):

    def __init__(self):
        super(MissionViewBase, self).__init__()
        self._filterData = {}
        self._builder = None
        self._questsDP = None
        self.__updateDataCallback = None
        self._totalQuestsCount = 0
        self._filteredQuestsCount = 0
        self._eventID = None
        return

    def setBuilder(self, builder, filterData, eventID):
        """ Set a builder that propagates view with data.
        """
        self._builder = builder
        self._filterData = filterData
        self._totalQuestsCount = 0
        self._filteredQuestsCount = 0
        self._eventID = eventID
        self._onEventsUpdate()

    def getTotalQuestsCount(self):
        return self._totalQuestsCount

    def getCurrentQuestsCount(self):
        return self._filteredQuestsCount

    def getSuitableEvents(self):
        return self._builder.getSuitableEvents()

    def markVisited(self):
        self._builder.markVisited()

    def _onEventsUpdate(self, *args):
        raise NotImplementedError

    def setFilters(self, filterData):
        pass

    def _populate(self):
        super(MissionViewBase, self)._populate()
        self._questsDP = _GroupedQuestsProvider()
        self._questsDP.setFlashObject(self.as_getDPS())
        self.as_setBackgroundS(self._getBackground())

    def _dispose(self):
        if self._builder is not None:
            self._builder.clear()
        self._questsDP.fini()
        self._builder = None
        self._questsDP = None
        if self.__updateDataCallback is not None:
            BigWorld.cancelCallback(self.__updateDataCallback)
            self.__updateDataCallback = None
        super(MissionViewBase, self)._dispose()
        return

    @staticmethod
    def _getBackground():
        pass

    def _onDataChangedNotify(self):
        """
        Fire event on next frame to prevent freezes
        """
        if self.__updateDataCallback is None:
            self.__updateDataCallback = BigWorld.callback(0, self.__notifyDataChanged)
        return

    def __notifyDataChanged(self):
        self.__updateDataCallback = None
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_GROUPS_DATA_CHANGED), EVENT_BUS_SCOPE.LOBBY)
        return


class MissionView(MissionViewBase):
    """ Missions view represents a single tab in the mission interface.
    """
    __sound_env__ = LobbySubViewEnv
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(MissionView, self).__init__()
        self.__viewQuests = {}

    def openMissionDetailsView(self, eventID, blockID):
        showMissionDetails(eventID, blockID)

    def setFilters(self, filterData):
        if self._filterData != filterData:
            self._filterData = filterData
            self._filterMissions()
        self._onDataChangedNotify()

    def dummyClicked(self, eventType):
        filterData = {'hideDone': False,
         'hideUnavailable': False}
        AccountSettings.setFilter(MISSIONS_PAGE, filterData)
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_FILTER_CHANGED, ctx=filterData), EVENT_BUS_SCOPE.LOBBY)

    def markVisited(self):
        super(MissionView, self).markVisited()
        self.eventsCache.onEventsVisited()

    def _populate(self):
        super(MissionView, self)._populate()
        self.eventsCache.onSyncCompleted += self._onEventsUpdate
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onEventsUpdate,
         'stats.unlocks': self.__onUnlocksUpdate})

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self._onEventsUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(MissionView, self)._dispose()

    def _filterMissions(self):
        result = []
        totalQuestsCount = 0
        filteredQuestsCount = 0
        for data in self._builder.getBlocksData(self.__viewQuests, self.__filter):
            result.append(data.blockData)
            totalQuestsCount += data.totalCount
            filteredQuestsCount += data.filteredCount

        self._totalQuestsCount = totalQuestsCount
        self._filteredQuestsCount = filteredQuestsCount
        self._questsDP.buildList(result)
        if not self._totalQuestsCount:
            self.as_showDummyS(self._getDummy())
        else:
            self.as_hideDummyS()

    @staticmethod
    def _getDummy():
        return {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
         'htmlText': text_styles.main(_ms(QUESTS.MISSIONS_NOTASKS_DUMMY_TEXT)),
         'alignCenter': False,
         'btnVisible': False,
         'btnLabel': '',
         'btnTooltip': '',
         'btnEvent': '',
         'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK}

    @async
    def _onEventsUpdate(self, *args):
        self.as_setWaitingVisibleS(True)
        yield await(self.eventsCache.prefetcher.demand())
        self.as_setWaitingVisibleS(False)
        if self._builder:
            self.__updateEvents()

    def __onUnlocksUpdate(self, unlocks):
        if any((getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE for intCD in unlocks)):
            self._onEventsUpdate()

    def __updateEvents(self):
        self.__viewQuests = self.eventsCache.getActiveQuests(self._getViewQuestFilter())
        self._builder.invalidateBlocks()
        self._filterMissions()
        self._onDataChangedNotify()
        settings.updateCommonEventsSettings(self.__viewQuests)

    def __filter(self, event):
        if self._filterData.get(HIDE_UNAVAILABLE, False) and not event.isAvailable()[0]:
            return False
        return False if self._filterData.get(HIDE_DONE, False) and event.isCompleted() else True

    def _getViewQuestFilter(self):
        return None


class ElenMissionView(MissionViewBase):
    eventsController = dependency.descriptor(IEventBoardController)

    def _populate(self):
        super(ElenMissionView, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ElenMissionView, self)._dispose()

    def onInventoryUpdate(self, _):
        self._onEventsUpdate()

    @checkEventExist
    def openMissionDetailsView(self, eventID, blockID):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_EVENT_BOARDS_TABLE, ctx={'eventID': eventID,
         'leaderboardID': int(blockID)}), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def _onEventsUpdate(self, *args):
        yield self._onEventsUpdateAsync(*args)

    @adispasync
    @process
    def _onEventsUpdateAsync(self, callback, *args):
        self.as_setWaitingVisibleS(True)
        yield self.eventsController.getEvents(isTabVisited=True)
        yield self.eventsController.getHangarFlag()
        self.as_setWaitingVisibleS(False)
        eventsData = self.eventsController.getEventsSettingsData()
        playerData = self.eventsController.getPlayerEventsData()
        myEventsTop = self.eventsController.getMyEventsTopData()
        if self.isDisposed():
            callback(self)
            return
        if eventsData and playerData and playerData.getEventsList() and myEventsTop:
            self._setMaintenance(False)
            self.__updateEvents(eventsData, playerData, myEventsTop)
        else:
            self._setMaintenance(True)
        self._onDataChangedNotify()
        callback(self)

    def _setMaintenance(self, visible):
        pass

    def __updateEvents(self, eventsData, playerData, myEventsTop):
        result = []
        totalQuestsCount = 0
        filteredQuestsCount = 0
        self._builder.setEventsData(eventsData, playerData, myEventsTop, self._eventID)
        for data in self._builder.getBlocksData(None, None):
            result.append(data.blockData)
            totalQuestsCount += data.totalCount
            filteredQuestsCount += data.filteredCount

        self._totalQuestsCount = totalQuestsCount
        self._filteredQuestsCount = filteredQuestsCount
        self._questsDP.buildList(result)
        if not totalQuestsCount:
            self.as_showDummyS({'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
             'htmlText': text_styles.main(_ms(QUESTS.MISSIONS_NOTASKS_DUMMY_TEXT)),
             'alignCenter': False,
             'btnVisible': False,
             'btnLabel': '',
             'btnTooltip': '',
             'btnEvent': ''})
        else:
            self.as_hideDummyS()
        return


class _GroupedQuestsProvider(ListDAAPIDataProvider):

    def __init__(self):
        super(_GroupedQuestsProvider, self).__init__()
        self.__list = []

    @property
    def collection(self):
        return self.__list

    def fini(self):
        self.clear()
        self.destroy()

    def buildList(self, dpList):
        self.__list = dpList
        self.refresh()

    def emptyItem(self):
        return None

    def getItemIndexHandler(self, fieldName, value):
        for index, item in enumerate(self.__list):
            if item[fieldName] == value:
                return index

    def clear(self):
        self.__list = []
