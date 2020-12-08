# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/missions_page.py
import weakref
from collections import namedtuple
import typing
from adisp import process, async as adispasync
from async import async, await
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from items import getTypeOfCompactDescr
import BigWorld
import Windowing
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MISSIONS_PAGE, NY_DAILY_QUESTS_VISITED
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import checkEventExist
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import HIDE_DONE, HIDE_UNAVAILABLE
from gui.Scaleform.daapi.view.lobby.missions.regular import group_packers
from gui.Scaleform.daapi.view.lobby.missions.regular.sound_constants import TASKS_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.MissionsListViewBaseMeta import MissionsListViewBaseMeta
from gui.Scaleform.daapi.view.meta.MissionsPageMeta import MissionsPageMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import ListDAAPIDataProvider
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.BATTLE_PASS_2020 import BATTLE_PASS_2020
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.marathon.marathon_event_controller import MARATHON_EVENTS
from gui.server_events import caches, settings
from gui.server_events.events_dispatcher import showMissionDetails, hideMissionDetails
from gui.server_events.events_helpers import isLinkedSet
from gui.shared import events, g_eventBus, event_bus_handlers
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import MissionsEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.sounds.ambients import LobbySubViewEnv, BattlePassSoundEnv
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IBattlePassController, IUISpamController
from skeletons.gui.game_control import IMarathonEventsController, IGameSessionController, IRankedBattlesController
from skeletons.gui.linkedset import ILinkedSetController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import List, Union
    from gui.server_events.event_items import DailyEpicTokenQuest, DailyQuest, PremiumQuest
TabData = namedtuple('TabData', ('alias',
 'linkage',
 'tooltip',
 'tooltipDisabled',
 'label',
 'prefix'))
TABS_DATA_ORDERED = [TabData(QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_EVENTBOARDS, QUESTS.MISSIONS_TAB_EVENTBOARDS_DISABLED, _ms(QUESTS.MISSIONS_TAB_LABEL_EVENTBOARDS), None),
 TabData(QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_MARATHONS, QUESTS.MISSIONS_TAB_MARATHONS, _ms(QUESTS.MISSIONS_TAB_LABEL_MARATHONS), None),
 TabData(QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS, QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_BATTLE_PASS, QUESTS.MISSIONS_TAB_BATTLE_PASS, _ms(BATTLE_PASS_2020.BATTLEPASSTAB), None),
 TabData(QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_CATEGORIES, QUESTS.MISSIONS_TAB_CATEGORIES, _ms(QUESTS.MISSIONS_TAB_LABEL_CATEGORIES), None),
 TabData(QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_DAILY, QUESTS.MISSIONS_TAB_DAILY, _ms(QUESTS.MISSIONS_TAB_LABEL_DAILY), None)]
MARATHONS_START_TAB_INDEX = 1
NON_FLASH_TABS = (QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS, QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS)
for marathonIndex, marathon in enumerate(MARATHON_EVENTS, MARATHONS_START_TAB_INDEX):
    TABS_DATA_ORDERED.insert(marathonIndex, TabData(QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_LINKAGE, marathon.tabTooltip, marathon.tabTooltip, backport.text(marathon.label), marathon.prefix))

def setHideDoneFilter():
    filterData = {'hideDone': True,
     'hideUnavailable': False}
    AccountSettings.setFilter(MISSIONS_PAGE, filterData)


class MissionsPage(LobbySubView, MissionsPageMeta):
    __metaclass__ = event_bus_handlers.EventBusListener
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = TASKS_SOUND_SPACE
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsController = dependency.descriptor(IEventBoardController)
    marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    battlePassCtrl = dependency.descriptor(IBattlePassController)
    uiSpamController = dependency.descriptor(IUISpamController)

    def __init__(self, ctx):
        super(MissionsPage, self).__init__(ctx)
        self.__filterData = AccountSettings.getFilter(MISSIONS_PAGE)
        self._eventID = None
        self._groupID = None
        self.__marathonPrefix = None
        self.__needToScroll = False
        self._showMissionDetails = True
        self.__builders = {QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS: group_packers.MarathonsDumbBuilder(),
         QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS: group_packers.MissionsGroupsBuilder(),
         QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS: group_packers.QuestsGroupsBuilder(),
         QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS: group_packers.VehicleGroupBuilder(),
         QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS: group_packers.ElenGroupsBuilder()}
        self.__currentTabAlias = None
        self.__subTab = None
        self._initialize(ctx)
        return

    def onTabSelected(self, alias, prefix):
        self.__currentTabAlias = alias
        self.__marathonPrefix = prefix
        caches.getNavInfo().setMissionsTab(alias)
        caches.getNavInfo().setMarathonPrefix(prefix)
        if self.currentTab and self.__currentTabAlias not in NON_FLASH_TABS:
            self.__updateFilterLabel()
            self.currentTab.setFilters(self.__filterData)
            self.currentTab.markVisited()
        elif self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS:
            self.currentTab.markVisited()
        self.__onPageUpdate()
        self.__fireTabChangedEvent()
        self.__showFilter()
        if alias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS:
            self.currentTab.setMarathon(prefix)
        if self.currentTab:
            self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.CHANGE_SOUND_ENVIRONMENT, ctx=self))
            self.currentTab.setActive(True)

    def getCurrentTabAlias(self):
        return self.__currentTabAlias

    def getFilterData(self):
        return self.__filterData

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def resetFilters(self):
        self.__filterData = {'hideDone': False,
         'hideUnavailable': False}
        AccountSettings.setFilter(MISSIONS_PAGE, self.__filterData)
        if self.currentTab:
            self.currentTab.setFilters(self.__filterData)

    @property
    def currentTab(self):
        return self.components.get(self.__currentTabAlias)

    def getDynamicSoundEnv(self):
        if self.__currentTabAlias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS:
            return BattlePassSoundEnv
        else:
            return None if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS else self.__sound_env__

    def _populate(self):
        super(MissionsPage, self)._populate()
        for builder in self.__builders.itervalues():
            builder.init()

        self.addListener(MissionsEvent.ON_GROUPS_DATA_CHANGED, self.__onPageUpdate, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.PAGE_INVALIDATE, self.__pageInvalidate, EVENT_BUS_SCOPE.LOBBY)
        self.eventsCache.onEventsVisited += self.__onEventsVisited
        g_currentVehicle.onChanged += self.__updateHeader
        self.battlePassCtrl.onSeasonStateChange += self.__updateHeader
        self.marathonsCtrl.onVehicleReceived += self.__onMarathonVehicleReceived
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        if self.marathonsCtrl.isAnyActive():
            TABS_DATA_ORDERED.insert(MARATHONS_START_TAB_INDEX, TabData(QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_MARATHONS, QUESTS.MISSIONS_TAB_MARATHONS, _ms(QUESTS.MISSIONS_TAB_LABEL_MARATHONS), None))
        self.__updateHeader()
        self.__tryOpenMissionDetails()
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_ACTIVATE), EVENT_BUS_SCOPE.LOBBY)
        return

    def _invalidate(self, ctx=None):
        super(MissionsPage, self)._invalidate(ctx)
        self._initialize(ctx)
        if self.currentTab:
            self.__updateFilterLabel()
        self.__updateHeader()
        self.__tryOpenMissionDetails()

    def _dispose(self):
        super(MissionsPage, self)._dispose()
        for builder in self.__builders.itervalues():
            builder.clear()

        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.marathonsCtrl.onVehicleReceived -= self.__onMarathonVehicleReceived
        g_currentVehicle.onChanged -= self.__updateHeader
        self.battlePassCtrl.onSeasonStateChange -= self.__updateHeader
        self.removeListener(MissionsEvent.ON_GROUPS_DATA_CHANGED, self.__onPageUpdate, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.PAGE_INVALIDATE, self.__pageInvalidate, EVENT_BUS_SCOPE.LOBBY)
        self.eventsCache.onEventsVisited -= self.__onEventsVisited
        caches.getNavInfo().setMissionsTab(self.__currentTabAlias)
        caches.getNavInfo().setMarathonPrefix(self.__marathonPrefix)
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_DEACTIVATE), EVENT_BUS_SCOPE.LOBBY)

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in QUESTS_ALIASES.MISSIONS_VIEW_PY_ALIASES:
            viewPy.setBuilder(self.__builders.get(alias), self.__filterData, self._eventID)
        if alias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS:
            viewPy.setProxy(weakref.proxy(self))
            viewPy.setDefaultTab(self.__subTab)
            self.__subTab = None
        if alias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS:
            viewPy.setSubTab(self.__subTab)
            self.__subTab = None
        self.__fireTabChangedEvent()
        return

    def _initialize(self, ctx=None):
        ctx = ctx or {}
        requestedTab = ctx.get('tab')
        self.__subTab = ctx.get('subTab')
        self.__marathonPrefix = ctx.get('marathonPrefix') or caches.getNavInfo().getMarathonPrefix()
        if requestedTab:
            self.__currentTabAlias = requestedTab
        else:
            self.__currentTabAlias = caches.getNavInfo().getMissionsTab()
            if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS and not self.__elenHasEvents():
                self.__currentTabAlias = None
            if not self.__currentTabAlias:
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
                if self.__elenHasEvents():
                    self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS
                elif self.marathonsCtrl.doesShowAnyMissionsTab():
                    enabledMarathon = self.marathonsCtrl.getFirstEnabledMarathon()
                    if enabledMarathon is not None and not self.uiSpamController.shouldBeHidden(QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS):
                        self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS
                        self.__marathonPrefix = enabledMarathon.prefix
        self._eventID = ctx.get('eventID')
        self._groupID = ctx.get('groupID')
        self._showMissionDetails = ctx.get('showMissionDetails', True)
        self.__needToScroll = self._groupID is not None
        self.__scrollToGroup()
        caches.getNavInfo().setMissionsTab(self.__currentTabAlias)
        caches.getNavInfo().setMarathonPrefix(self.__marathonPrefix)
        self.__fireTabChangedEvent()
        return

    def __fireTabChangedEvent(self):
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_TAB_CHANGED, ctx=self.__currentTabAlias), EVENT_BUS_SCOPE.LOBBY)
        if self.currentTab:
            self.currentTab.markVisited()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_MISSIONS_PAGE_VIEW, EVENT_BUS_SCOPE.DEFAULT)
    def __handleMissionsPageClose(self, _):
        self.destroy()

    def __showMarathonReward(self, isAccessible, prefix):
        isMarathonTab = self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS
        isPrefixCorrect = prefix == self.__marathonPrefix
        canShow = isAccessible and isMarathonTab and isPrefixCorrect
        if canShow:
            self.marathonsCtrl.getMarathon(prefix).showRewardVideo()

    def __onMarathonVehicleReceived(self, prefix):
        self.__showMarathonReward(Windowing.isWindowAccessible(), prefix)

    def __onWindowAccessibilityChanged(self, isAccessible):
        self.__showMarathonReward(isAccessible, self.__marathonPrefix)

    def __pageInvalidate(self, _):
        self._invalidate()

    def __scrollToGroup(self):
        if self._groupID and self.__needToScroll and self.currentTab is not None:
            self.currentTab.as_scrollToItemS('blockId', self._groupID)
            self.__needToScroll = False
        return

    def __onPageUpdate(self, *args):
        if self.currentTab is not None:
            self.__updateFilterLabel()
            self.__updateHeader()
            self.__scrollToGroup()
        return

    def __onEventsVisited(self, counters=None):
        if self.currentTab is not None:
            self.__updateHeader(False)
        return

    def __updateFilterLabel(self):
        filterApplied = False
        if self.__currentTabAlias not in NON_FLASH_TABS:
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

    def __updateHeader(self, updateTabsDataProvider=True):
        data = []
        tabs = []
        for tabData in TABS_DATA_ORDERED:
            headerTab, tab = self.__getHeaderTabData(tabData)
            if not headerTab or not tab:
                continue
            if headerTab in tabs:
                continue
            tabs.append(headerTab)
            data.append(tab)

        if updateTabsDataProvider:
            self.as_setTabsDataProviderS(tabs)
        self.as_setTabsCounterDataS(data)
        self.__showFilter()

    def __getHeaderTabData(self, tabData):
        alias = tabData.alias
        marathonEvent = None
        tab = {'label': tabData.label,
         'linkage': tabData.linkage}
        headerTab = {'alias': alias,
         'linkage': tabData.linkage,
         'tooltip': tabData.tooltip}
        if alias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS:
            marathonEvent = self.marathonsCtrl.getMarathon(tabData.prefix)
            tab['prefix'] = tabData.prefix
            headerTab['prefix'] = tabData.prefix
        if alias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS and not self.__elenHasEvents() or alias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS and not (marathonEvent and marathonEvent.doesShowMissionsTab()) or alias == QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS and self.marathonsCtrl.doesShowAnyMissionsTab() or alias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS and self.battlePassCtrl.isDisabled():
            if alias == self.__currentTabAlias and marathonEvent and marathonEvent.prefix == self.__marathonPrefix:
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
            if self.__currentTabAlias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS and self.battlePassCtrl.isDisabled():
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
            return (None, None)
        else:
            if alias == self.__currentTabAlias:
                if alias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS and self.__marathonPrefix:
                    headerTab['selected'] = self.__marathonPrefix == tabData.prefix
                else:
                    headerTab['selected'] = True
            if alias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS and not self.lobbyContext.getServerSettings().isElenEnabled():
                headerTab['tooltip'] = tabData.tooltipDisabled
                headerTab['enabled'] = False
            if alias == QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS:
                vehicle = g_currentVehicle.item
                vehName = vehicle.shortUserName if vehicle else ''
                tab['label'] = tabData.label % {'vehName': vehName}
            if alias in (QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS,
             QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS,
             QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS,
             QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS):
                newEvents = []
                if alias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS:
                    availableDailyQuests = []
                    availableDailyQuests.extend(self.eventsCache.getDailyQuests(includeEpic=True).values())
                    availableDailyQuests.extend(self.eventsCache.getPremiumQuests(lambda q: q.isAvailable().isValid).values())
                    if availableDailyQuests:
                        newEvents = settings.getNewCommonEvents(availableDailyQuests)
                    if not AccountSettings.getUIFlag(NY_DAILY_QUESTS_VISITED):
                        newEvents.append(NY_DAILY_QUESTS_VISITED)
                elif self.currentTab is not None and self.__currentTabAlias == alias:
                    suitableEvents = [ quest for quest in self.currentTab.getSuitableEvents() if not isLinkedSet(quest.getGroupID()) or quest.isAvailable().isValid ]
                    newEvents = settings.getNewCommonEvents(suitableEvents)
                else:
                    if alias == QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS:
                        from gui.Scaleform.daapi.view.lobby.missions.regular.missions_views import MissionsCategoriesView
                        advisableQuests = self.eventsCache.getAdvisableQuests(MissionsCategoriesView.getViewQuestFilter())
                    else:
                        advisableQuests = self.eventsCache.getAdvisableQuests()
                    advisableEvents = self.__builders[alias].getBlocksAdvisableEvents(advisableQuests)
                    newEvents = settings.getNewCommonEvents(advisableEvents)
                tab['value'] = len(newEvents)
            return (headerTab, tab)

    def __elenHasEvents(self):
        return self.lobbyContext.getServerSettings().isElenEnabled() and self.eventsController.hasEvents()

    def __filterApplied(self):
        for attr in self.__filterData:
            if self.__filterData[attr]:
                return True

        return False

    def __tryOpenMissionDetails(self):
        if self._eventID and self._groupID and self._showMissionDetails:
            showMissionDetails(self._eventID, self._groupID)
        else:
            hideMissionDetails()

    def __showFilter(self):
        self.as_showFilterS(self.__currentTabAlias not in (QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS,
         QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS,
         QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS,
         QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS), self.__currentTabAlias not in NON_FLASH_TABS)


class MissionViewBase(MissionsListViewBaseMeta):

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

    def setActive(self, value):
        pass

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
        if self.__updateDataCallback is None:
            self.__updateDataCallback = BigWorld.callback(0, self.__notifyDataChanged)
        return

    def __notifyDataChanged(self):
        self.__updateDataCallback = None
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_GROUPS_DATA_CHANGED), EVENT_BUS_SCOPE.LOBBY)
        return


class MissionView(MissionViewBase):
    __sound_env__ = LobbySubViewEnv
    eventsCache = dependency.descriptor(IEventsCache)
    linkedSetController = dependency.descriptor(ILinkedSetController)
    gameSession = dependency.descriptor(IGameSessionController)
    __rankedController = dependency.descriptor(IRankedBattlesController)

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
        quests = self.eventsCache.getAdvisableQuests()
        counter = len(settings.getNewCommonEvents(quests.values()))
        self.eventsCache.onEventsVisited({'missions': counter})

    def _populate(self):
        super(MissionView, self)._populate()
        self.eventsCache.onSyncCompleted += self._onEventsUpdate
        self.linkedSetController.onStateChanged += self._onLinkedSetStateChanged
        self.gameSession.onPremiumTypeChanged += self.__onPremiumTypeChanged
        self.__rankedController.onUpdated += self._onEventsUpdate
        self.__rankedController.onGameModeStatusUpdated += self._onEventsUpdate
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onEventsUpdate,
         'stats.unlocks': self.__onUnlocksUpdate})

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self._onEventsUpdate
        self.linkedSetController.onStateChanged -= self._onLinkedSetStateChanged
        self.gameSession.onPremiumTypeChanged -= self.__onPremiumTypeChanged
        self.__rankedController.onUpdated -= self._onEventsUpdate
        self.__rankedController.onGameModeStatusUpdated -= self._onEventsUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(MissionView, self)._dispose()

    def _filterMissions(self):
        result = []
        self._totalQuestsCount = 0
        self._filteredQuestsCount = 0
        nyBannerAdded = self._appendNYBanner(result)
        for data in self._builder.getBlocksData(self.__viewQuests, self.__filter):
            self._appendBlockDataToResult(result, data)
            self._totalQuestsCount += self._getQuestTotalCountFromBlockData(data)
            self._filteredQuestsCount += self._getQuestFilteredCountFromBlockData(data)

        self._questsDP.buildList(result)
        if not self._totalQuestsCount and not nyBannerAdded:
            self.as_showDummyS(self._getDummy())
        else:
            self.as_hideDummyS()

    def _appendBlockDataToResult(self, result, data):
        result.append(data.blockData)

    def _getQuestTotalCountFromBlockData(self, data):
        return data.totalCount

    def _getQuestFilteredCountFromBlockData(self, data):
        return data.filteredCount

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

    def _onLinkedSetStateChanged(self, *args):
        self._onEventsUpdate()

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

    def __onPremiumTypeChanged(self, newAcctType):
        self.markVisited()

    def _appendNYBanner(self, _):
        return False


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
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_EVENT_BOARDS_TABLE), ctx={'eventID': eventID,
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
