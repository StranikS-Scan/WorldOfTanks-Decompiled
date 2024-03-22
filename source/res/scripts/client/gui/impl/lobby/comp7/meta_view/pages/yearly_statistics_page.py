# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/yearly_statistics_page.py
from shared_utils import findFirst
from comp7_common import seasonPointsCodeBySeasonNumber
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.comp7.constants import Constants
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_statistics_model import YearlyStatisticsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_statistics_season_model import YearlyStatisticsSeasonModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.lobby.comp7 import comp7_shared
from gui.impl.lobby.comp7.comp7_model_helpers import setSeasonInfo, SEASONS_NUMBERS_BY_NAME
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.shared.event_dispatcher import showComp7SeasonStatisticsScreen
from helpers import dependency, time_utils
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache

class YearlyStatisticsPage(PageSubModelPresenter):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def pageId(self):
        return MetaRootViews.YEARLYSTATISTICS

    @property
    def viewModel(self):
        return super(YearlyStatisticsPage, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(YearlyStatisticsPage, self).initialize(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            seasonCards = tx.getSeasonCards()
            seasonCards.clear()
            for season in self.__comp7Controller.getAllSeasons():
                seasonStatisticsModel = YearlyStatisticsSeasonModel()
                self.__fillSeasonCard(seasonStatisticsModel, season)
                seasonCards.addViewModel(seasonStatisticsModel)

            seasonCards.invalidate()
        g_clientUpdateManager.addCallback('stats.dossier', self.__onDossierReceived)

    def finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(YearlyStatisticsPage, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onGoToSeasonStatistics, self.__onGoToSeasonStatistics),
         (self.__comp7Controller.onRankUpdated, self.__onRatingUpdated),
         (self.__comp7Controller.onComp7ConfigChanged, self.__updateSeasonModels),
         (self.__comp7Controller.onStatusUpdated, self.__updateSeasonModels),
         (self.__comp7Controller.onEntitlementsUpdated, self.__updateSeasonModels))

    def __onRatingUpdated(self, *_):
        self.__invalidateCurrentSeasonCard()

    def __onDossierReceived(self, *_):
        self.__invalidateCurrentSeasonCard()

    def __updateSeasonModels(self, *_):
        for season, model in zip(self.__comp7Controller.getAllSeasons(), self.viewModel.getSeasonCards()):
            self.__fillSeasonCard(model, season)

    def __invalidateCurrentSeasonCard(self):
        currSeason = self.__comp7Controller.getCurrentSeason()
        if currSeason:
            seasonNumber = currSeason.getNumber()
            seasonCard = findFirst(lambda sm: SEASONS_NUMBERS_BY_NAME[sm.season.getName().value] == seasonNumber, self.viewModel.getSeasonCards())
            self.__fillSeasonCard(seasonCard, currSeason)
            self.viewModel.getSeasonCards().invalidate()

    def __fillSeasonCard(self, seasonCard, season):
        setSeasonInfo(seasonCard.season, season)
        self.__setPlayerStatistics(seasonCard, season)

    def __setPlayerStatistics(self, seasonStatisticsModel, season):
        seasonNumber = season.getNumber()
        hasRankReceived = self.__comp7Controller.isQualificationPassedInSeason(seasonNumber)
        rating = self.__comp7Controller.getRatingForSeason(seasonNumber)
        division = comp7_shared.getPlayerDivisionByRating(rating, seasonNumber)
        dossier = self.__itemsCache.items.getAccountDossier().getComp7Stats(season=seasonNumber)
        superSquadBattlesCount = dossier.getSuperSquadBattlesCount()
        singleBattlesCount = dossier.getBattlesCount() - superSquadBattlesCount
        superSquadWinsCount = dossier.getSuperSquadWins()
        singleWinsCount = dossier.getWinsCount() - superSquadWinsCount
        if singleBattlesCount:
            singleWinRate = float(singleWinsCount) / singleBattlesCount * 100
        else:
            singleWinRate = Constants.NOT_AVAILABLE_STATISTIC_VALUE
        if superSquadBattlesCount:
            superSquadWinRate = float(superSquadWinsCount) / superSquadBattlesCount * 100
        else:
            superSquadWinRate = Constants.NOT_AVAILABLE_STATISTIC_VALUE
        with seasonStatisticsModel.transaction() as tx:
            tx.setHasRankReceived(hasRankReceived)
            tx.setHasStatisticsCalculated(self.__isSeasonPointsReceived(seasonNumber))
            tx.setDivision(comp7_shared.getDivisionEnumValue(division))
            tx.setRank(comp7_shared.getRankEnumValue(division))
            tx.setRating(self.__getRatingValue(hasRankReceived, rating))
            tx.setSingleBattlesCount(self.__getBattlesCountValue(season, singleBattlesCount))
            tx.setSuperPlatoonBattlesCount(self.__getBattlesCountValue(season, superSquadBattlesCount))
            tx.setSingleBattlesWinRate(singleWinRate)
            tx.setSuperPlatoonBattlesWinRate(superSquadWinRate)

    @staticmethod
    def __getRatingValue(hasRankReceived, value):
        return value if hasRankReceived else Constants.NOT_AVAILABLE_STATISTIC_VALUE

    @staticmethod
    def __getBattlesCountValue(season, value):
        isCurrentOrPastSeason = season.getStartDate() <= time_utils.getCurrentLocalServerTimestamp()
        return value if isCurrentOrPastSeason else Constants.NOT_AVAILABLE_STATISTIC_VALUE

    def __isSeasonPointsReceived(self, seasonNumber):
        receivedPoints = self.__comp7Controller.getReceivedSeasonPoints()
        return receivedPoints.get(seasonPointsCodeBySeasonNumber(seasonNumber), 0) > 0

    @staticmethod
    def __onGoToSeasonStatistics(params):
        seasonNumber = SEASONS_NUMBERS_BY_NAME[params['seasonName']]
        showComp7SeasonStatisticsScreen(seasonNumber=seasonNumber, force=True)
