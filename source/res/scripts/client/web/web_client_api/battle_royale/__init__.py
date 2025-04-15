# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/battle_royale/__init__.py
from collections import namedtuple
from web.web_client_api import webApiCollection
from web.web_client_api.exchange import PersonalExchangeRatesDiscountsWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.sound import SoundWebApi, SoundStateWebApi, HangarSoundWebApi
from web.web_client_api.ui import NotificationWebApi, OpenWindowWebApi
from web.web_client_api.ui import CloseWindowWebApi, OpenTabWebApi, ContextMenuWebApi, UtilWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.vehicles import VehiclesWebApi
from web.web_client_api import w2capi, W2CSchema, w2c
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
from web.web_client_api.frontline import FrontLineWebApi
BattleRoyaleSeasonAchievements = namedtuple('BattleRoyaleSeasonAchievements', ('season_id', 'episode_id', 'battle_count', 'kill_count', 'top1'))

def createBattleRoyaleWebHanlders():
    return webApiCollection(FrontLineWebApi, BattleRoyaleWebApi, VehiclesWebApi, RequestWebApi, ShopWebApi, OpenWindowWebApi, CloseWindowWebApi, OpenTabWebApi, NotificationWebApi, ContextMenuWebApi, UtilWebApi, SoundWebApi, SoundStateWebApi, HangarSoundWebApi, QuestsWebApi, PersonalExchangeRatesDiscountsWebApi)


@w2capi(name='battle_royale', key='action')
class BattleRoyaleWebApi(W2CSchema):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, name='get_calendar_info')
    def handleGetCalendarInfo(self, _):
        calendarData = dict()
        for season in self.__getSeasons():
            if season is not None:
                calendarData['season'] = {'id': season.getSeasonID(),
                 'start': season.getStartDate(),
                 'end': season.getEndDate()}
                calendarData['cycles'] = [ {'id': cycle.ID,
                 'start': cycle.startDate,
                 'end': cycle.endDate,
                 'announce_only': cycle.announceOnly} for cycle in season.getAllCycles().values() ]

        return calendarData

    @w2c(W2CSchema, name='get_seasons_achievements')
    def getSeasonAchievements(self, _):
        dossierDescr = self.__itemsCache.items.getAccountDossier().getDossierDescr()
        seasonsAchievements = self.__getSeasonAchievements(dossierDescr.expand('battleRoyaleSeasons'), BattleRoyaleSeasonAchievements)
        currentSeason = self.__battleRoyale.getCurrentSeason()
        if currentSeason and currentSeason.getCycleID():
            now = time_utils.getCurrentLocalServerTimestamp()
            stats = self.__battleRoyale.getStats()
            seasonsAchievements[currentSeason.getSeasonID(), currentSeason.getCycleID()] = {'battle_count': stats.battleCount,
             'kill_count': stats.killCount,
             'top1': stats.topCount,
             'season_id': currentSeason.getSeasonID(),
             'episode_id': currentSeason.getCycleID() or currentSeason.getLastActiveCycleID(now)}
        return seasonsAchievements.values()

    def __getSeasonAchievements(self, achievements, template):
        seasonsAchievements = {}
        for seasonID, cycleID in achievements:
            if not self.__validateSeasonData(seasonID, cycleID):
                continue
            key = (seasonID, cycleID)
            seasonsAchievements[key] = template(*(key + achievements[key]))._asdict()

        return seasonsAchievements

    def __validateSeasonData(self, seasonID, cycleID):
        seasons = self.__getSeasons()
        seasonValidationData = {season.getSeasonID():[ cycle.ID for cycle in season.getAllCycles().values() ] for season in seasons if season is not None}
        return seasonID in seasonValidationData and cycleID in seasonValidationData.get(seasonID, [])

    def __getSeasons(self):
        return (self.__battleRoyale.getCurrentSeason(), self.__battleRoyale.getNextSeason(), self.__battleRoyale.getPreviousSeason())
