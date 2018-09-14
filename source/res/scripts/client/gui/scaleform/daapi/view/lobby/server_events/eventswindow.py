# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/EventsWindow.py
import constants
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.server_events import g_eventsCache, settings as quest_settings, caches, isPotapovQuestEnabled
from gui.Scaleform.daapi.view.meta.QuestsWindowMeta import QuestsWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES as _QA

class EventsWindow(View, QuestsWindowMeta, AbstractWindowView):

    def __init__(self, ctx = None):
        super(EventsWindow, self).__init__()
        self._navInfo = caches.getNavInfo()
        if 'eventType' in ctx and 'eventID' in ctx:
            if ctx['eventType'] == constants.EVENT_TYPE.POTAPOV_QUEST:
                pQuest = g_eventsCache.potapov.getQuests()[int(ctx['eventID'])]
                self._navInfo.selectPotapovQuest(pQuest.getTileID(), pQuest.getID())
            else:
                self._navInfo.selectCommonQuest(ctx['eventID'])

    def _populate(self):
        super(EventsWindow, self)._populate()
        if isPotapovQuestEnabled():
            tabID = self._navInfo.tabID or _QA.TAB_PERSONAL_QUESTS
        else:
            tabID = _QA.TAB_COMMON_QUESTS
        self.as_selectTabS(tabID)

    def onWindowClose(self):
        caches.clearVehiclesData()
        self.destroy()

    def onTabSelected(self, tabID):
        if tabID == _QA.TAB_PERSONAL_QUESTS:
            if quest_settings.isNeedToShowPQIntro(g_eventsCache.potapov):
                return self._showWelcomeView()
            if self._navInfo.potapov.tileID is not None:
                self._showTileChainsView(self._navInfo.potapov.tileID, self._navInfo.potapov.questID)
            else:
                self._showSeasonsView()
        elif tabID == _QA.TAB_COMMON_QUESTS:
            self._showCommonQuestsView(self._navInfo.common.questID)
        else:
            LOG_WARNING('Unknown personal quests tab id', tabID)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in (_QA.PERSONAL_WELCOME_VIEW_ALIAS, _QA.TILE_CHAINS_VIEW_ALIAS, _QA.SEASONS_VIEW_ALIAS):
            viewPy._setMainView(self)
        self.as_hideWaitingS()

    def _showWelcomeView(self):
        self._navInfo.selectTab(_QA.TAB_PERSONAL_QUESTS)
        return self._loadView(_QA.PERSONAL_WELCOME_VIEW_LINKAGE, _QA.PERSONAL_WELCOME_VIEW_ALIAS)

    def _showSeasonsView(self, doResetNavInfo = False):
        self._navInfo.selectTab(_QA.TAB_PERSONAL_QUESTS, doResetNavInfo)
        return self._loadView(_QA.SEASONS_VIEW_LINKAGE, _QA.SEASONS_VIEW_ALIAS)

    def _showTileChainsView(self, tileID, questID = None):
        self._navInfo.selectPotapovQuest(tileID, questID)
        quest_settings.markPQTileAsVisited(tileID)
        return self._loadView(_QA.TILE_CHAINS_VIEW_LINKAGE, _QA.TILE_CHAINS_VIEW_ALIAS)

    def _showCommonQuestsView(self, questID = None):
        self._navInfo.selectCommonQuest(questID)
        return self._loadView(_QA.COMMON_QUESTS_VIEW_LINKAGE, _QA.COMMON_QUESTS_VIEW_ALIAS)

    def _loadView(self, linkage, alias):
        self.as_showWaitingS('', {})
        self.as_loadViewS(linkage, alias)
