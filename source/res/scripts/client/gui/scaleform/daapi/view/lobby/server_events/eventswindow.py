# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/EventsWindow.py
import constants
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.server_events import old_events_helpers
from gui.Scaleform.daapi.view.meta.QuestsWindowMeta import QuestsWindowMeta
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES as _QA
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events import settings as quest_settings, caches
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class EventsWindow(QuestsWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(EventsWindow, self).__init__()
        self._navInfo = caches.getNavInfo()
        self._updateNavInfo(ctx.get('eventType'), ctx.get('eventID'), ctx.get('doResetNavInfo', False))

    def onWindowClose(self):
        caches.clearVehiclesData()
        self.destroy()

    def navigate(self, eventType=None, eventID=None):
        if self._updateNavInfo(eventType, eventID):
            tabID = self._selectLastTab()
            self.onTabSelected(tabID)

    def onTabSelected(self, tabID):
        if tabID == _QA.TAB_PERSONAL_QUESTS:
            if quest_settings.isNeedToShowPQIntro(self.eventsCache.fallout):
                return self._showWelcomeView()
            if self._navInfo.selectedPQ.tileID is not None:
                self.showTileChainsView(self._navInfo.selectedPQ.tileID, self._navInfo.selectedPQ.questID)
            else:
                self._showSeasonsView()
        else:
            LOG_WARNING('Unknown personal quests tab id', tabID)
        return

    def showTileChainsView(self, tileID, questID=None):
        self._navInfo.selectPotapovQuest(tileID, questID)
        quest_settings.markPQTileAsVisited(tileID)
        return self._loadView(_QA.TILE_CHAINS_VIEW_LINKAGE, self.__getChainsViewAlias())

    def _populate(self):
        super(EventsWindow, self)._populate()
        self.__initWindow()
        self._selectLastTab()

    def __initWindow(self):
        tabs = []
        if self.lobbyContext.getServerSettings().isPotapovQuestEnabled():
            tabs.append(self.__packTabDataItem(QUESTS.QUESTS_TABS_PERSONAL, _QA.TAB_PERSONAL_QUESTS))
        self.onTabSelected(_QA.TAB_PERSONAL_QUESTS)

    def __packTabDataItem(self, label, id):
        return {'label': label,
         'id': id}

    def _selectLastTab(self):
        tabID = self._navInfo.tabID
        if not tabID:
            if self.lobbyContext.getServerSettings().isPotapovQuestEnabled():
                tabID = _QA.TAB_PERSONAL_QUESTS
        return tabID

    def _updateNavInfo(self, eventType=None, eventID=None, doResetNavInfo=False):
        if eventType is not None:
            if eventID is not None:
                if eventType == constants.EVENT_TYPE.POTAPOV_QUEST:
                    pQuest = self.eventsCache.potapov.getQuests()[int(eventID)]
                    targetQuestTab = old_events_helpers.getTabAliasByQuestBranchID(pQuest.getQuestBranch())
                    if targetQuestTab == _QA.SEASON_VIEW_TAB_RANDOM:
                        self._navInfo.selectRandomQuest(pQuest.getTileID(), pQuest.getID())
                    else:
                        self._navInfo.selectFalloutQuest(pQuest.getTileID(), pQuest.getID())
            elif eventType == constants.EVENT_TYPE.POTAPOV_QUEST:
                self._navInfo.selectTab(_QA.TAB_PERSONAL_QUESTS, doResetNavInfo)
            return True
        else:
            return False

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in (_QA.PERSONAL_WELCOME_VIEW_ALIAS, self.__getChainsViewAlias(), _QA.SEASONS_VIEW_ALIAS):
            viewPy._setMainView(self)
        self.as_hideWaitingS()

    def _showWelcomeView(self):
        self._navInfo.selectTab(_QA.TAB_PERSONAL_QUESTS)
        return self._loadView(_QA.PERSONAL_WELCOME_VIEW_LINKAGE, _QA.PERSONAL_WELCOME_VIEW_ALIAS)

    def _showSeasonsView(self, doResetNavInfo=False):
        self._navInfo.selectTab(_QA.TAB_PERSONAL_QUESTS, doResetNavInfo)
        return self._loadView(_QA.SEASONS_VIEW_LINKAGE, _QA.SEASONS_VIEW_ALIAS)

    def _loadView(self, linkage, alias):
        self.as_showWaitingS('', {})
        self.as_loadViewS(linkage, alias)

    def __getChainsViewAlias(self):
        if self._navInfo.selectedPQType == _QA.SEASON_VIEW_TAB_RANDOM:
            return _QA.RANDOM_TILE_CHAINS_VIEW_ALIAS
        else:
            return _QA.FALLOUT_TILE_CHAINS_VIEW_ALIAS
