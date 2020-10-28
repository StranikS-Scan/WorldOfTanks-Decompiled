# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ranked_battles/__init__.py
from functools import partial
from gui.ranked_battles.constants import RankedDossierKeys, SeasonResultTokenPatterns
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.server_events.events_helpers import isRankedPlatform
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2capi, w2c, W2CSchema, webApiCollection
from web.web_client_api.clans import ClansWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.sound import SoundWebApi, SoundStateWebApi, HangarSoundWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.ui import NotificationWebApi, ContextMenuWebApi, OpenWindowWebApi, CloseWindowWebApi, OpenTabWebApi, UtilWebApi
from web.web_client_api.ui.ranked import OpenRankedPagesMixin

def _packQuest(quest, rankModel):
    return {'isCompleted': quest.isCompleted(),
     'condition': {'rank': rankModel.getUserName() if rankModel is not None else '',
                   'division': rankModel.getDivision().getID() if rankModel is not None else 0,
                   'isLastInDivision': rankModel.isLastInDivision() if rankModel is not None else False},
     'entitlements': {bonus.getValue().id:bonus.getValue().amount for bonus in quest.getBonuses() if bonus.getName() == 'entitlements'}}


@w2capi(name='ranked_battles', key='action')
class RankedBattlesWebApi(OpenRankedPagesMixin):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    @w2c(W2CSchema, name='close_browser')
    def closeBrowser(self, _):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), EVENT_BUS_SCOPE.LOBBY)

    @w2c(W2CSchema, name='get_gamemode_state')
    def getGamemodeState(self, _):
        return {'isEnabled': self.__rankedController.isEnabled(),
         'isShopEnabled': self.__rankedController.isRankedShopEnabled(),
         'isActiveSeason': self.__rankedController.getCurrentSeason() is not None,
         'isSeasonGap': self.__rankedController.getPreviousSeason() is not None,
         'isSeasonRewarding': self.__rankedController.isSeasonRewarding(),
         'isYearGap': self.__rankedController.isYearGap(),
         'expectedSeasons': self.__rankedController.getExpectedSeasons()}

    @w2c(W2CSchema, name='get_platform_quests_info')
    def getPlatformQuestsInfo(self, _):
        rankedQuests = self.__eventsCache.getRankedQuests(lambda q: isRankedPlatform(q.getID())).values()
        leaguesQuests = self.__eventsCache.getActiveQuests(lambda q: isRankedPlatform(q.getID())).values()
        progressQuests = [ _packQuest(qst, self.__rankedController.getRank(qst.getRank())) for qst in sorted(rankedQuests, key=lambda q: q.getRank()) ]
        postProgressQuests = [ _packQuest(quest, None) for quest in leaguesQuests ]
        return {'progressQuests': progressQuests,
         'postProgressQuests': postProgressQuests}

    @w2c(W2CSchema, name='get_seasons_stats')
    def getSeasonsStats(self, _):
        result = {}
        tokens = self.__itemsCache.items.tokens.getTokens()
        for seasonID, _ in self.__rankedController.getSeasonPassed():
            season = self.__rankedController.getSeason(seasonID)
            if season is not None:
                dossier = self.__getRankedSeasonDossier(RankedDossierKeys.SEASON % season.getNumber(), seasonID)
                banToken = tokens.get(SeasonResultTokenPatterns.RANKED_OFF_BANNED.format(seasonID))
                rollToken = tokens.get(SeasonResultTokenPatterns.RANKED_OFF_ROLLED.format(seasonID))
                result[seasonID] = {'maxRank': dossier.getAchievedRank(),
                 'efficiency': dossier.getStepsEfficiency(),
                 'isBanned': banToken is not None and banToken[1] > 0,
                 'isRolled': rollToken is not None and rollToken[1] > 0}

        return result

    def __getRankedSeasonDossier(self, seasonKey, seasonID):
        return self.__itemsCache.items.getAccountDossier().getSeasonRankedStats(seasonKey, seasonID)


class _OpenTabWebApi(OpenTabWebApi):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.RANKED_BATTLE_PAGE

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getRankedShopCallback(cmd)

    def _getVehicleStylePreviewCallback(self, cmd):
        return self.__getRankedShopCallback(cmd)

    def __getRankedShopCallback(self, cmd):
        ctx = {'showedFromWeb': True,
         'webParams': cmd.back_url if cmd.back_url is not None else '',
         'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID}
        return partial(self.__rankedController.showRankedBattlePage, ctx)


class _SoundStateWebApi(SoundStateWebApi):
    _ON_EXIT_STATES = {}


def createRankedBattlesWebHandlers():
    return webApiCollection(RequestWebApi, ContextMenuWebApi, _OpenTabWebApi, OpenWindowWebApi, CloseWindowWebApi, SoundWebApi, _SoundStateWebApi, HangarSoundWebApi, ClansWebApi, NotificationWebApi, RankedBattlesWebApi, QuestsWebApi, ShopWebApi, UtilWebApi)
