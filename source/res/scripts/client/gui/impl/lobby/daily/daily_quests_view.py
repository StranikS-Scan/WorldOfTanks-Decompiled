# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_view.py
import logging
import typing
from new_year_account_settings import getNYSetting, setNYSettings
from new_year.ny_constants import NY_IS_CELEB_VOICEOVERS_ENABLED, NY_WEEK_IN_QUESTS_VISITED
from Event import Event, EventManager
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_view_model import DailyQuestsViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.daily import DailyTabs, NYTabs
from gui.impl.lobby.daily.daily_quests_facade import DailyQuestsFacade
from gui.impl.lobby.daily.ny_quests_facade import NYQuestsFacade
from gui.impl.lobby.daily.daily_quests_info_page import showDailyQuestsInfoPage
from gui.impl.lobby.play_streak.play_streak_facade import PlayStreakFacade
from gui.impl.lobby.play_streak.play_streak_info_page import showPlayStreakInfoPage
from gui.impl.pub import ViewImpl
from gui.server_events import settings
from gui.server_events.events_helpers import isPremiumQuestsEnable, isDailyQuestsEnable, isPlayStreakEnable, isDailyRegularQuestsEnabled
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showDailyQuestsIntroWindow, showNyDailyQuestsInfoWindow
from SoundGroups import g_instance as SoundGroupsManager
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from new_year.skeletons.new_year import INewYearController
from new_year.gui.impl.lobby.new_year.quests.ny_quest_helper import getCurrentWeek
from new_year.gui.impl.new_year.sounds import NewYearCelebVoiceOvers
if typing.TYPE_CHECKING:
    from SoundGroups import SoundGroups
_logger = logging.getLogger(__name__)
DEFAULT_DAILY_TAB = DailyTabs.QUESTS
DAILY_VIEW = (DailyTabs.QUESTS, DailyTabs.PREMIUM)
DAILY_LAOUT_ID = R.views.lobby.daily.DailyQuestsRegularView()

class DailyQuestsView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__proxyMissionsPage', '__viewActive', '__tabs', '__tabsToSubview', '__subviews', '__currentTabID', '__dailyQuests', '__em', 'onIsCurrentMissionTab', 'onPlayStreakTab', '__playStreak', '__nyQuests', '__celebSound')

    def __init__(self, layoutID=R.views.lobby.daily.DailyQuestsView()):
        viewSettings = ViewSettings(layoutID, ViewFlags.VIEW, DailyQuestsViewModel())
        super(DailyQuestsView, self).__init__(viewSettings)
        self.__tabs = {}
        self.__tabsToSubview = {}
        self.__subviews = []
        self.__proxyMissionsPage = None
        self.__dailyQuests = DailyQuestsFacade(self)
        self.__tabs.update(self.__dailyQuests.getTabs())
        self.__tabsToSubview.update(self.__dailyQuests.getSubviews())
        self.__playStreak = PlayStreakFacade(self)
        self.__tabs.update(self.__playStreak.getTabs())
        self.__tabsToSubview.update(self.__playStreak.getSubviews())
        self.__nyQuests = NYQuestsFacade(self)
        self.__tabsToSubview.update(self.__nyQuests.getSubviews())
        self.__currentTabID = None
        self.__viewActive = False
        self.__em = EventManager()
        self.onIsCurrentMissionTab = Event(self.__em)
        self.onPlayStreakTab = Event(self.__em)
        self.__celebSound = None
        return

    @property
    def viewModel(self):
        return super(DailyQuestsView, self).getViewModel()

    @property
    def currentSubview(self):
        subview, _ = self.__tabsToSubview.get(self.__currentTabID, (None, None))
        return subview

    def setDefaultTab(self, tabIdx=None):
        dq = settings.getDQSettings()
        if tabIdx is None:
            tabIdx = dq.lastVisitedDQTabIdx if dq.lastVisitedDQTabIdx is not None else DEFAULT_DAILY_TAB
        if tabIdx == DailyTabs.QUESTS and not isDailyRegularQuestsEnabled():
            tabIdx = DailyTabs.PREMIUM
        elif tabIdx == DailyTabs.PREMIUM and not isPremiumQuestsEnable():
            tabIdx = DailyTabs.QUESTS
        _logger.debug('PremiumMissionsView:setDefaultTab: tabIdx=%s', tabIdx)
        self.__setCurrentTab(tabIdx, self.viewModel)
        return

    def getCurrentTabID(self):
        return self.__currentTabID

    def changeTab(self, tabIdx):
        with self.viewModel.transaction() as tx:
            self.__setCurrentTab(tabIdx, tx)

    def setProxy(self, proxy):
        self.__proxyMissionsPage = proxy

    def createToolTipContent(self, event, contentID):
        subViewTooltip = self.currentSubview.createToolTipContent(event, contentID) if self.currentSubview else None
        return subViewTooltip if subViewTooltip else self.__dailyQuests.getToolTipContent(event, event.contentID)

    def createToolTip(self, event):
        tooltip = self.currentSubview.createToolTip(event) if self.currentSubview else None
        return tooltip if tooltip else super(DailyQuestsView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        _logger.info('DailyQuestsView::_onLoading')
        super(DailyQuestsView, self)._onLoading()
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
        for tab, tabLayoutID in self.__tabs.values():
            self.__setChild(tab, tabLayoutID)

        for subview, layoutID in self.__tabsToSubview.values():
            self.__addSubiew(subview, layoutID)

        self.initView()

    def initView(self):
        dq = settings.getDQSettings()
        if not dq.dailyQuestsIntroSeen and (isDailyQuestsEnable() or isPlayStreakEnable()):
            showDailyQuestsIntroWindow()
        else:
            with self.viewModel.transaction() as tx:
                tx.setIntroSeen(True)
        if getNYSetting(NY_WEEK_IN_QUESTS_VISITED) != getCurrentWeek():
            self.__toggleCelebVoiceover()
            setNYSettings(NY_WEEK_IN_QUESTS_VISITED, getCurrentWeek())

    def _finalize(self):
        if self.__celebSound is not None:
            self.__stopVoiceover()
            self.__celebSound = None
        self.__dailyQuests.finalize()
        self.__playStreak.finalize()
        self.__tabs.clear()
        self.__tabsToSubview.clear()
        self.__proxyMissionsPage = None
        del self.__subviews[:]
        self.__em.clear()
        super(DailyQuestsView, self)._finalize()
        return

    def _updateModel(self, model):
        model.setIsDailyRegularEnabled(isDailyRegularQuestsEnabled())
        model.setIsDailyPremEnabled(isPremiumQuestsEnable())
        model.setIsSerialEnterEnabled(isPlayStreakEnable())
        model.setIsPersonVoicesNowPlaying(False)
        model.setIsPersonVoicesEnabled(self.nyController.isCelebVoiceoverEnabled())
        battleTypes = model.getDailyBattleTypes()
        nyBattleTypes = model.getNyBattleTypes()
        self.__dailyQuests.updateBattleModes(battleTypes)
        self.__dailyQuests.updateNyBattleModes(nyBattleTypes)

    def _getEvents(self):
        return ((self.viewModel.onTabClick, self.__onTabClick),
         (self.viewModel.onClose, self.__onCloseView),
         (self.viewModel.onInfoClick, self.__showInfoPage),
         (self.viewModel.onShowInfo, self.__showPlayStreakInfoPage),
         (self.viewModel.onNyInfoClick, self.__showNyDailyInfoPage),
         (self.viewModel.onStartStopPersonVoice, self.__toggleCelebVoiceover),
         (self.viewModel.changePersonVoicesEnabled, self.__updateCelebVoicesEnabled))

    def _getListeners(self):
        return ((events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY),)

    @args2params(int)
    def __onTabClick(self, tabIdx):
        if tabIdx == DailyTabs.SERIAL:
            self.onPlayStreakTab()
        self.changeTab(tabIdx)

    def __onCloseView(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), EVENT_BUS_SCOPE.LOBBY)

    def __setCurrentTab(self, tabIdx, model):
        if tabIdx == self.__currentTabID:
            return
        if tabIdx == NYTabs.DAILY and not self.nyController.isEnabled():
            return
        for subview in self.__subviews:
            subview.deactivate()

        self.__currentTabID = tabIdx
        model.setCurrentTabIdx(tabIdx)
        if self.currentSubview:
            self.currentSubview.activate()
        with settings.dailyQuestSettings() as dq:
            dq.setLastVisitedDQTab(tabIdx)

    def __addSubiew(self, subview, layoutID):
        if subview not in self.__subviews:
            self.__subviews.append(subview)
            self.__setChild(subview, layoutID)

    def __setChild(self, child, layoutID):
        existingChild = self.getChildView(layoutID)
        if existingChild is not None:
            _logger.warning('Child id = %d already exists uid = %d', layoutID, existingChild.uniqueID)
            return
        else:
            self.setChildView(layoutID, child)
            return

    def __onMissionsTabChanged(self, event):
        viewActive = event.ctx.get('alias') == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS
        if self.__viewActive != viewActive:
            self.__viewActive = viewActive
            self.onIsCurrentMissionTab(self.__viewActive)

    def __showInfoPage(self):
        showDailyQuestsInfoPage()

    def __showPlayStreakInfoPage(self):
        showPlayStreakInfoPage()

    def __showNyDailyInfoPage(self):
        showNyDailyQuestsInfoWindow()

    def __toggleCelebVoiceover(self):
        if not self.nyController.isCelebVoiceoverEnabled():
            return
        else:
            with self.viewModel.transaction() as ts:
                soundMessage = NewYearCelebVoiceOvers.NY_QUESTS_CELEB_MESSAGES_PREFIX.format(getCurrentWeek())
                if self.__celebSound is None:
                    self.__celebSound = SoundGroupsManager.WWgetSoundCallback(soundMessage, None, None, self.__setStopPlayback)
                isPLaying = self.__celebSound.isPlaying
                ts.setIsPersonVoicesNowPlaying(not isPLaying)
                if isPLaying:
                    self.__stopVoiceover()
                else:
                    self.__celebSound.play()
            return

    def __setStopPlayback(self, _):
        with self.viewModel.transaction() as ts:
            ts.setIsPersonVoicesNowPlaying(False)

    def __stopVoiceover(self):
        SoundGroupsManager.playSound2D(NewYearCelebVoiceOvers.NY_QUESTS_CELEB_STOP_VOICEOVER)

    def __updateCelebVoicesEnabled(self):
        with self.viewModel.transaction() as ts:
            isEnabled = self.nyController.isCelebVoiceoverEnabled()
            if isEnabled and self.__celebSound and self.__celebSound.isPlaying:
                ts.setIsPersonVoicesNowPlaying(False)
                self.__stopVoiceover()
            ts.setIsPersonVoicesEnabled(not isEnabled)
            setNYSettings(NY_IS_CELEB_VOICEOVERS_ENABLED, not isEnabled)
