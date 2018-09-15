# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/missions_page.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MISSIONS_PAGE
from async import async, await
from debug_utils import LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions import group_packers
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import HIDE_DONE, HIDE_UNAVAILABLE
from gui.Scaleform.daapi.view.meta.MissionsPageMeta import MissionsPageMeta
from gui.Scaleform.daapi.view.meta.MissionsViewBaseMeta import MissionsViewBaseMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import caches, settings
from gui.server_events.events_dispatcher import showMissionDetails, hideMissionDetails
from gui.shared import events
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
TABS_ORDER = (QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS)

def setHideDoneFilter():
    filterData = {'hideDone': True,
     'hideUnavailable': False}
    AccountSettings.setFilter(MISSIONS_PAGE, filterData)


class MissionsPage(LobbySubView, MissionsPageMeta):
    __sound_env__ = LobbySubViewEnv
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx):
        super(MissionsPage, self).__init__(ctx)
        self.__filterData = AccountSettings.getFilter(MISSIONS_PAGE)
        self.__eventID = None
        self.__groupID = None
        self.__needToScroll = False
        self.__builders = {QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS: group_packers.MarathonsGroupsFinder(),
         QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS: group_packers.QuestsGroupsFinder(),
         QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS: group_packers.VehicleGroupFinder()}
        self._initialize(ctx)
        return

    def onTabSelected(self, alias):
        self.__currentTabAlias = alias
        caches.getNavInfo().setMissionsTab(alias)
        if self.currentTab:
            self.__updateFilterLabel()
            self.currentTab.setFilters(self.__filterData)

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
        g_currentVehicle.onChanged += self.__updateHeader
        self.as_setTabsDataProviderS(self.__getHeaderTabsData())
        self.__tryOpenMissionDetails()

    def _invalidate(self, ctx=None):
        super(MissionsPage, self)._invalidate(ctx)
        self._initialize(ctx)
        self.as_setTabsDataProviderS(self.__getHeaderTabsData())
        self.__updateHeader()
        self.__tryOpenMissionDetails()

    def _dispose(self):
        super(MissionsPage, self)._dispose()
        g_currentVehicle.onChanged -= self.__updateHeader
        self.removeListener(MissionsEvent.ON_GROUPS_DATA_CHANGED, self.__onPageUpdate, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        caches.getNavInfo().setMissionsTab(self.__currentTabAlias)

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in QUESTS_ALIASES.MISSIONS_VIEW_PY_ALIASES:
            viewPy.setBuilder(self.__builders.get(alias), self.__filterData)

    def _initialize(self, ctx=None):
        ctx = ctx or {}
        self.__currentTabAlias = ctx.get('tab') or caches.getNavInfo().getMissionsTab()
        if not self.__currentTabAlias:
            if findFirst(lambda group: group.isMarathon(), self.eventsCache.getGroups().itervalues()):
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS
            else:
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
        self.__eventID = ctx.get('eventID')
        self.__groupID = ctx.get('groupID')
        self.__needToScroll = self.__groupID is not None
        self.__scrollToGroup()
        return

    def __scrollToGroup(self):
        if self.__eventID and self.__groupID and self.__needToScroll and self.currentTab is not None:
            self.currentTab.as_scrollToItemS('blockId', self.__groupID)
            self.__needToScroll = False
        return

    def __getHeaderTabsData(self):
        tabs = [{'alias': QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS,
          'linkage': QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_LINKAGE,
          'tooltip': QUESTS.MISSIONS_TAB_MARATHONS}, {'alias': QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS,
          'linkage': QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_LINKAGE,
          'tooltip': QUESTS.MISSIONS_TAB_CATEGORIES}, {'alias': QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS,
          'linkage': QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_LINKAGE,
          'tooltip': QUESTS.MISSIONS_TAB_CURRENTVEHICLE}]
        tabs[TABS_ORDER.index(self.__currentTabAlias)].update(selected=True)
        return tabs

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
        vehicle = g_currentVehicle.item
        if vehicle:
            vehName = vehicle.shortUserName
        else:
            vehName = ''
        data = [{'label': _ms(QUESTS.MISSIONS_TAB_LABEL_MARATHONS),
          'linkage': QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_LINKAGE}, {'label': _ms(QUESTS.MISSIONS_TAB_LABEL_CATEGORIES),
          'linkage': QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_LINKAGE}, {'label': _ms(QUESTS.MISSIONS_TAB_LABEL_CURRENTVEHICLE, vehName=vehName),
          'linkage': QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_LINKAGE}]
        advisableQuests = self.eventsCache.getAdvisableQuests()
        for idx, alias in enumerate((QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS)):
            if self.__currentTabAlias == alias and self.currentTab is not None:
                newEvents = settings.getNewCommonEvents(self.currentTab.getSuitableEvents())
            else:
                events = self.__builders[alias].getBlocksAdvisableEvents(advisableQuests)
                newEvents = settings.getNewCommonEvents(events)
            data[idx].update(value=len(newEvents))

        self.as_setTabsCounterDataS(data)
        return

    def __filterApplied(self):
        for attr in self.__filterData:
            if self.__filterData[attr]:
                return True

        return False

    def __tryOpenMissionDetails(self):
        """ Depending on the open context, we may need to open missions details or close them.
        """
        if self.__eventID and self.__groupID:
            showMissionDetails(self.__eventID, self.__groupID)
        else:
            hideMissionDetails()


class MissionView(MissionsViewBaseMeta):
    """ Missions view represents a single tab in the mission interface.
    """
    __sound_env__ = LobbySubViewEnv
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(MissionView, self).__init__()
        self._builder = None
        self._questsDP = None
        self.__filterData = {}
        self.__viewQuests = {}
        self.__totalQuestsCount = 0
        self.__filteredQuestsCount = 0
        self.__updateDataCallback = None
        return

    def getTotalQuestsCount(self):
        return self.__totalQuestsCount

    def getCurrentQuestsCount(self):
        return self.__filteredQuestsCount

    def getSuitableEvents(self):
        return self._builder.getSuitableEvents()

    def openMissionDetailsView(self, eventID, blockID):
        showMissionDetails(eventID, blockID)

    def setBuilder(self, builder, filterData):
        """ Set a builder that propagates view with data.
        """
        self._builder = builder
        self.__filterData = filterData
        self.__onEventsUptate()

    def setFilters(self, filterData):
        if self.__filterData != filterData:
            self.__filterData = filterData
            self._filterMissions()
        self._onDataChangedNotify()

    def dummyClicked(self, eventType):
        filterData = {'hideDone': False,
         'hideUnavailable': False}
        AccountSettings.setFilter(MISSIONS_PAGE, filterData)
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_FILTER_CHANGED, ctx=filterData), EVENT_BUS_SCOPE.LOBBY)

    def markVisited(self):
        self._builder.markVisited()
        self.eventsCache.onEventsVisited()

    def _populate(self):
        super(MissionView, self)._populate()
        self.eventsCache.onSyncCompleted += self.__onEventsUptate
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onEventsUptate,
         'stats.unlocks': self.__onUnlocksUpdate})
        self._questsDP = _GroupedQuestsProvider()
        self._questsDP.setFlashObject(self.as_getDPS())
        self.as_setBackgroundS(self._getBackground())

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self.__onEventsUptate
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._builder.clear()
        self._questsDP.fini()
        self._builder = None
        self._questsDP = None
        if self.__updateDataCallback is not None:
            BigWorld.cancelCallback(self.__updateDataCallback)
            self.__updateDataCallback = None
        super(MissionView, self)._dispose()
        return

    def _filterMissions(self):
        result = []
        totalQuestsCount = 0
        filteredQuestsCount = 0
        resultAppendMethod = result.append
        for data in self._builder.getBlocksData(self.__viewQuests, self.__filter):
            resultAppendMethod(data.blockData)
            totalQuestsCount += data.totalCount
            filteredQuestsCount += data.filteredCount

        self.__totalQuestsCount = totalQuestsCount
        self.__filteredQuestsCount = filteredQuestsCount
        self._questsDP.buildList(result)
        if not self.__totalQuestsCount:
            self.as_showDummyS(self._getDummy())
        else:
            self.as_hideDummyS()

    @staticmethod
    def _getBackground():
        pass

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
    def __onEventsUptate(self, *args):
        self.as_setWaitingVisibleS(True)
        yield await(self.eventsCache.prefetcher.demand())
        self.as_setWaitingVisibleS(False)
        if self._builder:
            self.__updateEvents()

    def __onUnlocksUpdate(self, unlocks):
        if any((getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE for intCD in unlocks)):
            self.__onEventsUptate()

    def __updateEvents(self):
        self.__viewQuests = self.eventsCache.getActiveQuests(self._getViewQuestFilter())
        self._builder.invalidateBlocks()
        self._filterMissions()
        self._onDataChangedNotify()
        settings.updateCommonEventsSettings(self.__viewQuests)

    def __filter(self, event):
        if self.__filterData.get(HIDE_UNAVAILABLE, False) and not event.isAvailable()[0]:
            return False
        elif self.__filterData.get(HIDE_DONE, False) and event.isCompleted():
            return False
        else:
            return True

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

    def _getViewQuestFilter(self):
        return None


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
