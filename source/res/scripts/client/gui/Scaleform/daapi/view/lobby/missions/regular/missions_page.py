# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/missions_page.py
import weakref
from collections import namedtuple
import typing
import BigWorld
import Windowing
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MISSIONS_PAGE
from adisp import adisp_async as adispasync, adisp_process
from gui.limited_ui.lui_rules_storage import LUI_RULES
from wg_async import wg_async, wg_await
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
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.BATTLE_PASS import BATTLE_PASS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_pass.battle_pass_helpers import isBattlePassDailyQuestsIntroShown
from gui.battle_pass.sounds import HOLIDAY_TASKS_SOUND_SPACE
from gui.impl import backport
from gui.impl.gen import R
from gui.marathon.marathon_event_controller import getMarathons
from gui.server_events import caches, settings
from gui.server_events.events_dispatcher import hideMissionDetails, showMissionDetails
from gui.server_events.events_helpers import isBattleMattersQuestID
from gui.shared import event_bus_handlers, events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import MissionsEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.sounds.ambients import BattlePassSoundEnv, LobbySubViewEnv, MarathonPageSoundEnv, MissionsCategoriesSoundEnv, MissionsEventsSoundEnv, MissionsPremiumSoundEnv, BattleMattersSoundEnv
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import getTypeOfCompactDescr
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IBattlePassController, IHangarSpaceSwitchController, IGameSessionController, IMapboxController, IMarathonEventsController, IRankedBattlesController, ILimitedUIController, IWinbackController, ILiveOpsWebEventsController
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.battle_matters import IBattleMattersController
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
 TabData(QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_MARATHONS, QUESTS.MISSIONS_TAB_MARATHONS, _ms(QUESTS.MISSIONS_TAB_LABEL_MARATHON), None),
 TabData(QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS, QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_LIVE_OPS_WEB_EVENTS, QUESTS.MISSIONS_TAB_LIVE_OPS_WEB_EVENTS, _ms(QUESTS.MISSIONS_TAB_LABEL_MARATHON), None),
 TabData(QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS, QUESTS_ALIASES.BATTLE_MATTERS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_BATTLEMATTERS, QUESTS.MISSIONS_TAB_BATTLEMATTERS, backport.text(R.strings.battle_matters.battleMattersTab()), None),
 TabData(QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS, QUESTS_ALIASES.MAPBOX_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_MAPBOX, QUESTS.MISSIONS_TAB_MAPBOX, backport.text(R.strings.mapbox.mapboxTab()), None),
 TabData(QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS, QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_BATTLE_PASS, QUESTS.MISSIONS_TAB_BATTLE_PASS, _ms(BATTLE_PASS.BATTLEPASSTAB), None),
 TabData(QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_CATEGORIES, QUESTS.MISSIONS_TAB_CATEGORIES, _ms(QUESTS.MISSIONS_TAB_LABEL_CATEGORIES), None),
 TabData(QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_DAILY, QUESTS.MISSIONS_TAB_DAILY, _ms(QUESTS.MISSIONS_TAB_LABEL_DAILY), None)]
MARATHONS_START_TAB_INDEX = 1
NON_FLASH_TABS = (QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS,
 QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS,
 QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS,
 QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS,
 QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS,
 QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS)
TABS_WITHOUT_COMMON_MUSIC = (QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS,)
for marathonIndex, marathon in enumerate(getMarathons(), MARATHONS_START_TAB_INDEX):
    TABS_DATA_ORDERED.insert(marathonIndex, TabData(QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_LINKAGE, marathon.tabTooltip, marathon.tabTooltip, backport.text(marathon.label), marathon.prefix))

def setHideDoneFilter():
    filterData = {'hideDone': True,
     'hideUnavailable': False}
    AccountSettings.setFilter(MISSIONS_PAGE, filterData)


class MissionsPage(LobbySubView, MissionsPageMeta):
    __metaclass__ = event_bus_handlers.EventBusListener
    _COMMON_SOUND_SPACE = TASKS_SOUND_SPACE
    __sound_env__ = LobbySubViewEnv
    __VOICED_TABS = {QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS: (backport.sound(R.sounds.ev_mapbox_enter()), backport.sound(R.sounds.ev_mapbox_exit())),
     QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS: (backport.sound(R.sounds.bm_enter()), backport.sound(R.sounds.bm_exit()))}
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsController = dependency.descriptor(IEventBoardController)
    marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    battlePass = dependency.descriptor(IBattlePassController)
    __liveOpsWebEventsController = dependency.descriptor(ILiveOpsWebEventsController)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __winbackController = dependency.descriptor(IWinbackController)

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
        self.__ctx = ctx or {}
        self.__soundSpace = self._COMMON_SOUND_SPACE
        self.__changeSoundSpace()
        self._initialize(ctx)
        return

    def onTabSelected(self, alias, prefix):
        for tab, soundEvents in self.__VOICED_TABS.iteritems():
            if alias == tab and self.__currentTabAlias != tab:
                self.soundManager.playSound(soundEvents[0])
                break
            if alias != tab and self.__currentTabAlias == tab:
                self.soundManager.playSound(soundEvents[1])
                break

        if self.__currentTabAlias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS and self.currentTab is not None:
            self.currentTab.stop()
        self.__currentTabAlias = alias
        self.__marathonPrefix = prefix
        caches.getNavInfo().setMissionsTab(alias)
        caches.getNavInfo().setMarathonPrefix(prefix)
        if self.currentTab:
            isSupportFilters = self.__currentTabAlias not in NON_FLASH_TABS
            isSupportMarkVisited = isSupportFilters or self.__currentTabAlias in (QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS, QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS)
            if isSupportFilters:
                self.__updateFilterLabel()
                self.currentTab.setFilters(self.__filterData)
            if isSupportMarkVisited:
                self.currentTab.markVisited()
        self.__onPageUpdate()
        self.__fireTabChangedEvent()
        self.__showFilter()
        if alias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS and self.currentTab is not None:
            self.currentTab.start()
        if alias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS:
            self.currentTab.setMarathon(prefix)
        if self.currentTab:
            self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.CHANGE_SOUND_ENVIRONMENT, ctx=self))
            self.currentTab.setActive(True)
        return

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
        if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS:
            return MissionsPremiumSoundEnv
        if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS:
            return MarathonPageSoundEnv
        if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS:
            return MissionsCategoriesSoundEnv
        if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS:
            return MissionsEventsSoundEnv
        return BattleMattersSoundEnv if self.__currentTabAlias == QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS else self.__sound_env__

    def _populate(self):
        super(MissionsPage, self)._populate()
        for builder in self.__builders.itervalues():
            builder.init()

        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdated
        self.addListener(MissionsEvent.ON_GROUPS_DATA_CHANGED, self.__onPageUpdate, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.PAGE_INVALIDATE, self.__pageInvalidate, EVENT_BUS_SCOPE.LOBBY)
        self.eventsCache.onEventsVisited += self.__onEventsVisited
        enterEvent, _ = self.__VOICED_TABS.get(self.__currentTabAlias, (None, None))
        if enterEvent is not None:
            self.soundManager.playSound(enterEvent)
        g_currentVehicle.onChanged += self.__updateHeader
        self.battlePass.onSeasonStateChanged += self.__updateHeader
        self.battlePass.onBattlePassSettingsChange += self.__updateBattlePassTab
        self.__liveOpsWebEventsController.onSettingsChanged += self.__updateLiveOpsWebEventsTab
        self.__liveOpsWebEventsController.onEventStateChanged += self.__updateLiveOpsWebEventsTab
        self.marathonsCtrl.onVehicleReceived += self.__onMarathonVehicleReceived
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        if self.marathonsCtrl.isAnyActive():
            TABS_DATA_ORDERED.insert(MARATHONS_START_TAB_INDEX, TabData(QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_LINKAGE, QUESTS.MISSIONS_TAB_MARATHONS, QUESTS.MISSIONS_TAB_MARATHONS, _ms(QUESTS.MISSIONS_TAB_LABEL_MARATHON), None))
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

        _, exitEvent = self.__VOICED_TABS.get(self.__currentTabAlias, (None, None))
        if exitEvent is not None:
            appLoader = dependency.instance(IAppLoader)
            if appLoader.getSpaceID() != GuiGlobalSpaceID.LOGIN:
                self.soundManager.playSound(exitEvent)
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.marathonsCtrl.onVehicleReceived -= self.__onMarathonVehicleReceived
        self.__liveOpsWebEventsController.onEventStateChanged -= self.__updateLiveOpsWebEventsTab
        self.__liveOpsWebEventsController.onSettingsChanged -= self.__updateLiveOpsWebEventsTab
        g_currentVehicle.onChanged -= self.__updateHeader
        self.battlePass.onSeasonStateChanged -= self.__updateHeader
        self.battlePass.onBattlePassSettingsChange -= self.__updateBattlePassTab
        self.removeListener(MissionsEvent.ON_GROUPS_DATA_CHANGED, self.__onPageUpdate, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.PAGE_INVALIDATE, self.__pageInvalidate, EVENT_BUS_SCOPE.LOBBY)
        self.eventsCache.onEventsVisited -= self.__onEventsVisited
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdated
        caches.getNavInfo().setMissionsTab(self.__currentTabAlias)
        caches.getNavInfo().setMarathonPrefix(self.__marathonPrefix)
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_DEACTIVATE), EVENT_BUS_SCOPE.LOBBY)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in QUESTS_ALIASES.MISSIONS_VIEW_PY_ALIASES:
            viewPy.setBuilder(self.__builders.get(alias), self.__filterData, self._eventID)
        if alias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS:
            viewPy.setProxy(weakref.proxy(self))
            viewPy.setDefaultTab(self.__subTab)
            self.__subTab = None
        if alias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS:
            viewPy.updateState(**self.__ctx)
        if alias == QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS:
            viewPy.updateState(**self.__ctx)
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
            if self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS and not self.__elenHasDisplayableEvents():
                self.__currentTabAlias = None
            if not self.__currentTabAlias:
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
                if self.__elenHasDisplayableEvents():
                    self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS
                elif self.marathonsCtrl.doesShowAnyMissionsTab():
                    enabledMarathon = self.marathonsCtrl.getFirstEnabledMarathon()
                    if enabledMarathon is not None and self.__limitedUIController.isRuleCompleted(LUI_RULES.MissionsMarathonView):
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

    def __onPrimeTimeStatusUpdated(self, *_):
        if self.__mapboxCtrl.getCurrentCycleID() is None:
            self.__eventStatusUpdated(self.__currentTabAlias == QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS)
        elif self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS:
            self.__eventStatusUpdated()
        return

    def __eventStatusUpdated(self, resetCurrentTab=True):
        if resetCurrentTab:
            caches.getNavInfo().setMissionsTab(None)
            self.__currentTabAlias = None
        self._invalidate()
        return

    def __fireTabChangedEvent(self):
        self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_TAB_CHANGED, ctx={'alias': self.__currentTabAlias}), EVENT_BUS_SCOPE.LOBBY)
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

    def __updateBattlePassTab(self, *_):
        self.__updateHeader()
        self.__changeSoundSpace()

    def __updateLiveOpsWebEventsTab(self, *_):
        if not self.__liveOpsWebEventsController.canShowEventsTab():
            self.__eventStatusUpdated(self.__currentTabAlias == QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS)
        elif self.__currentTabAlias == QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS:
            self.__eventStatusUpdated()
        else:
            self.__updateHeader()

    def __changeSoundSpace(self):
        newSoundSpace = HOLIDAY_TASKS_SOUND_SPACE if self.battlePass.isHoliday() and self.battlePass.isActive() else TASKS_SOUND_SPACE
        if self.__soundSpace != newSoundSpace:
            self.__soundSpace = newSoundSpace
            self.initSoundManager(self.__soundSpace)

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
        if alias == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS and not self.__elenHasDisplayableEvents() or alias == QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS and not (marathonEvent and marathonEvent.isEnabled()) or alias == QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS and (self.marathonsCtrl.doesShowAnyMissionsTab() or self.__liveOpsWebEventsController.canShowEventsTab() or self.__mapboxCtrl.isEnabled() and self.__mapboxCtrl.getCurrentCycleID() is not None) or alias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS and self.battlePass.isDisabled() or alias == QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS and (not self.__mapboxCtrl.isEnabled() or self.__mapboxCtrl.getCurrentCycleID() is None) or alias == QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS and not self.__battleMattersTabIsEnabled() or alias == QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS and (not self.__liveOpsWebEventsController.canShowEventsTab() or self.marathonsCtrl.doesShowAnyMissionsTab()):
            if alias == self.__currentTabAlias and marathonEvent and marathonEvent.prefix == self.__marathonPrefix:
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
            elif self.__currentTabAlias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS and self.battlePass.isDisabled():
                if self.currentTab is not None:
                    self.currentTab.finalize()
                self.__currentTabAlias = QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
                showHangar()
            elif self.__currentTabAlias == alias == QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS:
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
            if alias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS and self.__winbackController.isProgressionAvailable():
                tab['label'] = backport.text(R.strings.winback.winbackTab())
                headerTab['tooltip'] = QUESTS.MISSIONS_TAB_WINBACK
            if alias in (QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS,
             QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS,
             QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS,
             QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS,
             QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS,
             QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS):
                newEventsCount = 0
                if alias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS:
                    availableDailyQuests = []
                    availableDailyQuests.extend(self.eventsCache.getDailyQuests(includeEpic=True).values())
                    availableDailyQuests.extend(self.eventsCache.getPremiumQuests(lambda q: q.isAvailable().isValid).values())
                    if availableDailyQuests:
                        newEventsCount = len(settings.getNewCommonEvents(availableDailyQuests))
                        if self.battlePass.isActive() and not isBattlePassDailyQuestsIntroShown():
                            newEventsCount += 1
                elif alias == QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS:
                    newEventsCount = self.__mapboxCtrl.getUnseenItemsCount()
                elif alias == QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS:
                    newEventsCount = self.__liveOpsWebEventsController.getEventTabVisited()
                elif self.currentTab is not None and self.__currentTabAlias == alias:
                    suitableEvents = self.__getSuitableEvents(self.currentTab)
                    newEventsCount = len(settings.getNewCommonEvents(suitableEvents))
                else:
                    if alias == QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS:
                        from gui.Scaleform.daapi.view.lobby.missions.regular.missions_views import MissionsCategoriesView
                        advisableQuests = self.eventsCache.getAdvisableQuests(MissionsCategoriesView.getViewQuestFilter())
                        advisableQuests.update({q.getID():q for q in self.__getSuitableEvents(self.getComponent(alias))})
                    else:
                        advisableQuests = self.eventsCache.getAdvisableQuests()
                    advisableEvents = self.__builders[alias].getBlocksAdvisableEvents(advisableQuests)
                    newEventsCount = len(settings.getNewCommonEvents(advisableEvents))
                tab['value'] = newEventsCount
            return (headerTab, tab)

    def __battleMattersTabIsEnabled(self):
        bm = self.__battleMattersController
        return bm.isEnabled() and (not bm.isFinished() or bm.hasDelayedRewards())

    @staticmethod
    def __getSuitableEvents(tab):
        if not tab:
            return []
        return [ quest for quest in tab.getSuitableEvents() if not isBattleMattersQuestID(quest.getGroupID()) or quest.isAvailable().isValid ]

    def __elenHasDisplayableEvents(self):
        if self.lobbyContext.getServerSettings().isElenEnabled() and self.eventsController.hasEvents():
            for eventData in self.eventsController.getEventsSettingsData().getEvents():
                if not eventData.hasCustomUI():
                    return True

        return False

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
         QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS,
         QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS,
         QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS,
         QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS), self.__currentTabAlias not in NON_FLASH_TABS)


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
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    gameSession = dependency.descriptor(IGameSessionController)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

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
        self.__battleMattersController.onStateChanged += self._onBattleMattersStateChanged
        self.gameSession.onPremiumTypeChanged += self.__onPremiumTypeChanged
        self.__rankedController.onUpdated += self._onEventsUpdate
        self.__rankedController.onGameModeStatusUpdated += self._onEventsUpdate
        self.__spaceSwitchController.onSpaceUpdated += self._onEventsUpdate
        self.addListener(events.MissionsViewEvent.EVENTS_FULL_UPDATE, self._onEventsUpdate, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onEventsUpdate,
         'stats.unlocks': self.__onUnlocksUpdate})

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self._onEventsUpdate
        self.__battleMattersController.onStateChanged -= self._onBattleMattersStateChanged
        self.gameSession.onPremiumTypeChanged -= self.__onPremiumTypeChanged
        self.__rankedController.onUpdated -= self._onEventsUpdate
        self.__rankedController.onGameModeStatusUpdated -= self._onEventsUpdate
        self.__spaceSwitchController.onSpaceUpdated -= self._onEventsUpdate
        self.removeListener(events.MissionsViewEvent.EVENTS_FULL_UPDATE, self._onEventsUpdate, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(MissionView, self)._dispose()

    def _filterMissions(self):
        result = []
        self._totalQuestsCount = 0
        self._filteredQuestsCount = 0
        for data in self._builder.getBlocksData(self.__viewQuests, self.__filter):
            self._appendBlockDataToResult(result, data)
            self._totalQuestsCount += self._getQuestTotalCountFromBlockData(data)
            self._filteredQuestsCount += self._getQuestFilteredCountFromBlockData(data)

        self._questsDP.buildList(result)
        if not self._totalQuestsCount:
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

    @wg_async
    def _onEventsUpdate(self, *args):
        self.as_setWaitingVisibleS(True)
        yield wg_await(self.eventsCache.prefetcher.demand())
        self.as_setWaitingVisibleS(False)
        if self._builder:
            self.__updateEvents()

    def _onBattleMattersStateChanged(self, *args):
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
        return False if self._filterData.get(HIDE_DONE, False) and event.isCompleted() else event.shouldBeShown()

    def _getViewQuestFilter(self):
        return None

    def __onPremiumTypeChanged(self, newAcctType):
        self.markVisited()


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

    @adisp_process
    def _onEventsUpdate(self, *args):
        yield self._onEventsUpdateAsync(*args)

    @adispasync
    @adisp_process
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
