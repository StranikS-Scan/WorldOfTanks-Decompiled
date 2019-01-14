# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_battles_offline_view.py
from helpers.i18n import makeString as localize
from helpers.dependency import descriptor
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.formatters import text_styles
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.daapi.view.meta.EpicBattlesOfflineViewMeta import EpicBattlesOfflineViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_prestige_progress import getPrestigeProgressVO
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_cycle_helpers import getActiveCycleTimeFrameStrings
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from constants import IS_DEVELOPMENT
from debug_utils import LOG_ERROR, LOG_CODEPOINT_WARNING

class EpicBattlesOfflineView(LobbySubView, EpicBattlesOfflineViewMeta):
    epicMetaGameCtrl = descriptor(IEpicBattleMetaGameController)
    eventsCache = descriptor(IEventsCache)
    lobbyCtx = descriptor(ILobbyContext)

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def onAboutButtonClick(self):
        self.fireEvent(events.LoadViewEvent(EPICBATTLES_ALIASES.EPIC_BATTLES_BROWSER_ALIAS, ctx={'urlID': 'gameRules',
         'showBackBtn': False,
         'previousPage': EPICBATTLES_ALIASES.EPIC_BATTLES_OFFLINE_ALIAS}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(EpicBattlesOfflineView, self)._populate()
        self.as_setDataS(self._packInfoViewVO())

    def _packInfoViewVO(self):
        pPrestigeLevel, pMetaLevel, _ = self.epicMetaGameCtrl.getPlayerLevelInfo()
        maxMetaLevel = self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxLevel', 0)
        prestigeProgressVO = getPrestigeProgressVO(self.eventsCache.getAllQuests(), self.lobbyCtx.getServerSettings().epicMetaGame.metaLevel, pPrestigeLevel, maxMetaLevel == pMetaLevel)
        nextSeason = self.epicMetaGameCtrl.getCurrentSeason()
        if not nextSeason:
            nextSeason = self.epicMetaGameCtrl.getNextSeason()
        if not IS_DEVELOPMENT and self.epicMetaGameCtrl.getCurrentSeason() is not None:
            LOG_ERROR('EpicBattlesOfflineView displayed although inside of a season!')
        cycleTimes = getActiveCycleTimeFrameStrings(nextSeason)
        if cycleTimes.startDay is not None:
            calendarSubTitle = text_styles.promoSubTitle(localize(EPIC_BATTLE.EPICBATTLESOFFLINEVIEW_CALENDARSUBTITLE, month=cycleTimes.startMonth, dateStart=cycleTimes.startDay, dateEnd=cycleTimes.endDay))
            startDay = cycleTimes.startDay
        else:
            LOG_ERROR('EpicBattlesOfflineView displayed although there are no planned seasons!')
            LOG_CODEPOINT_WARNING()
            startDay = ''
            calendarSubTitle = ''
        titleTextBig = text_styles.epicTitle(EPIC_BATTLE.EPICBATTLESOFFLINEVIEW_TITLE)
        titleTextSmall = text_styles.heroTitle(EPIC_BATTLE.EPICBATTLESOFFLINEVIEW_TITLE)
        return {'backgroundImageSrc': RES_ICONS.MAPS_ICONS_EPICBATTLES_BACKGROUNDS_META_BG,
         'headlineTitleHtmlTextBig': titleTextBig,
         'headlineTitleHtmlTextSmall': titleTextSmall,
         'calendarText': startDay,
         'calendarSubTitleHtmlText': calendarSubTitle,
         'prestigeProgressVO': prestigeProgressVO}

    def __close(self):
        self.fireEvent(events.DirectLoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)
