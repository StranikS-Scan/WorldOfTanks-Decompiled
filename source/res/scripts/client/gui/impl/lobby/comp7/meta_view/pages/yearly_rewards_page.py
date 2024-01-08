# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/yearly_rewards_page.py
from collections import namedtuple
import typing
from comp7_common import seasonPointsCodeBySeasonNumber
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_rewards_card_model import YearlyRewardsCardModel, RewardsState
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_rewards_model import YearlyRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import ProgressionItemBaseModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.gen.view_models.views.lobby.comp7.season_point_model import SeasonPointState, SeasonName, SeasonPointModel
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.general_rank_tooltip_model import Rank
from gui.impl.lobby.comp7.comp7_bonus_packer import packYearlyRewardsBonuses
from gui.impl.lobby.comp7.comp7_model_helpers import SEASONS_NUMBERS_BY_NAME, getSeasonNameEnum, setElitePercentage
from gui.impl.lobby.comp7.comp7_shared import getPlayerDivisionByRating, getRankEnumValue, getPlayerDivision
from gui.impl.lobby.comp7.meta_view.meta_view_helper import getRankDivisions, setDivisionData, setRankData
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.impl.lobby.comp7.tooltips.fifth_rank_tooltip import FifthRankTooltip
from gui.impl.lobby.comp7.tooltips.general_rank_tooltip import GeneralRankTooltip
from gui.impl.lobby.comp7.tooltips.season_point_tooltip import SeasonPointTooltip
from gui.impl.lobby.comp7.tooltips.sixth_rank_tooltip import SixthRankTooltip
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from helpers.server_settings import Comp7RanksConfig
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))

class YearlyRewardsPage(PageSubModelPresenter):
    __slots__ = ('__tooltips',)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel, parentView):
        super(YearlyRewardsPage, self).__init__(viewModel, parentView)
        self.__tooltips = []

    @property
    def pageId(self):
        return MetaRootViews.YEARLYREWARDS

    @property
    def viewModel(self):
        return super(YearlyRewardsPage, self).getViewModel()

    @property
    def ranksConfig(self):
        return self.__lobbyCtx.getServerSettings().comp7RanksConfig

    def initialize(self):
        super(YearlyRewardsPage, self).initialize()
        self.__updateAllData()
        self.__comp7Controller.setYearlyRewardsAnimationSeen()

    def finalize(self):
        self.__tooltips = []
        super(YearlyRewardsPage, self).finalize()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltips[int(tooltipId)]
            window = backport.BackportTooltipWindow(tooltipData, self.parentView.getParentWindow())
            window.load()
            return window
        else:
            return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.comp7.tooltips.SeasonPointTooltip():
            params = {'state': SeasonPointState(event.getArgument('state')),
             'ignoreState': event.getArgument('ignoreState')}
            return SeasonPointTooltip(params=params)
        elif contentID == R.views.lobby.comp7.tooltips.GeneralRankTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.lobby.comp7.tooltips.FifthRankTooltip():
            return FifthRankTooltip()
        else:
            return SixthRankTooltip() if contentID == R.views.lobby.comp7.tooltips.SixthRankTooltip() else None

    def _getEvents(self):
        return ((self.__comp7Controller.onQualificationStateUpdated, self.__onQualificationStateUpdated),
         (self.__comp7Controller.onSeasonPointsUpdated, self.__onSeasonPointsUpdated),
         (self.__comp7Controller.onRankUpdated, self.__onRankUpdated),
         (self.__comp7Controller.onComp7ConfigChanged, self.__onConfigChanged),
         (self.__comp7Controller.onComp7RanksConfigChanged, self.__onRanksConfigChanged),
         (self.__comp7Controller.onComp7RewardsConfigChanged, self.__onRewardsConfigChanged))

    def __onQualificationStateUpdated(self):
        self.__updateAllData()

    def __onSeasonPointsUpdated(self):
        self.__updateAllData()

    def __onSeasonPointsReloaded(self, isSuccess):
        if isSuccess and self.isLoaded:
            self.__updateAllData()

    def __onRankUpdated(self, *_):
        self.__updateAllData()

    def __onConfigChanged(self):
        self.__updateAllData()

    def __onRanksConfigChanged(self):
        with self.viewModel.transaction() as tx:
            self.__setLegendData(tx)

    def __onRewardsConfigChanged(self):
        with self.viewModel.transaction() as tx:
            self.__setCards(tx)

    def __updateAllData(self):
        with self.viewModel.transaction() as tx:
            self.__setCommonData(tx)
            self.__setCards(tx)

    def __setCommonData(self, model):
        receivedSeasonPoints = self.__comp7Controller.getReceivedSeasonPoints()
        model.setHasDataError(not receivedSeasonPoints)
        model.setHasInitialCardsAnimation(not self.__comp7Controller.isYearlyRewardsAnimationSeen())
        self.__setSeasonData(model)
        self.__setLegendData(model)

    def __areLastSeasonPointsReceived(self):
        lastSeason = self.__comp7Controller.getActualSeasonNumber()
        if lastSeason is None:
            return False
        else:
            lastSeasonPointsEntitlement = seasonPointsCodeBySeasonNumber(lastSeason)
            return self.__comp7Controller.getReceivedSeasonPoints().get(lastSeasonPointsEntitlement, 0) > 0

    def __setSeasonData(self, model):
        actualSeason = self.__comp7Controller.getActualSeasonNumber()
        if actualSeason is None:
            return
        else:
            if self.__comp7Controller.getCurrentSeason() is not None:
                isQualificationActive = self.__comp7Controller.isQualificationActive()
            else:
                isQualificationActive = not self.__comp7Controller.isQualificationPassedInSeason(actualSeason)
            model.setIsQualificationActive(isQualificationActive)
            if not isQualificationActive:
                division = getPlayerDivisionByRating(self.__comp7Controller.getRatingForSeason(actualSeason))
                model.setCurrentRank(getRankEnumValue(division))
            return

    def __setLegendData(self, model):
        ranksArray = model.getRanks()
        ranksArray.clear()
        for rank in self.ranksConfig.ranksOrder:
            rankModel = ProgressionItemBaseModel()
            setRankData(rankModel, rank, self.ranksConfig)
            setDivisionData(rankModel, getRankDivisions(rank, self.ranksConfig))
            ranksArray.addViewModel(rankModel)

        ranksArray.invalidate()
        setElitePercentage(model)

    def __setCards(self, model):
        cards = model.getCards()
        cards.clear()
        self.__tooltips = []
        prevRewardsCost = 0
        seasonPointsGenerator = _SeasonPointsGenerator(self.__areLastSeasonPointsReceived())
        for rewardsData in sorted(self.__comp7Controller.getYearlyRewards().main, key=lambda data: data['cost']):
            cardSeasonPoints = seasonPointsGenerator.getNext(rewardsData['cost'] - prevRewardsCost)
            prevRewardsCost = rewardsData['cost']
            cardModel = YearlyRewardsCardModel()
            cardModel.setRewardsState(self.__getRewardStateForCard(cardSeasonPoints))
            self.__setCardSeasonPoints(cardModel, cardSeasonPoints)
            self.__setRewards(cardModel, rewardsData['bonus'])
            cards.addViewModel(cardModel)

        cards.invalidate()

    def __getRewardStateForCard(self, cardSeasonPoints):
        if all((pointState == SeasonPointState.ACHIEVED for pointState, _ in cardSeasonPoints)):
            if self.__comp7Controller.isYearlyRewardReceived():
                return RewardsState.CLAIMED
            return RewardsState.GUARANTEED
        return RewardsState.POSSIBLE if not any((pointState == SeasonPointState.NOTACHIEVED for pointState, _ in cardSeasonPoints)) else RewardsState.NOTAVAILABLE

    def __setRewards(self, cardModel, bonuses):
        rewards = cardModel.getRewards()
        rewards.clear()
        bonusModels, tooltipsData = packYearlyRewardsBonuses(bonuses)
        for idx, bonusModel in enumerate(bonusModels):
            bonusModel.setTooltipId(str(len(self.__tooltips)))
            rewards.addViewModel(bonusModel)
            self.__tooltips.append(tooltipsData[idx])

        rewards.invalidate()

    @staticmethod
    def __setCardSeasonPoints(cardModel, cardSeasonPoints):
        pointsList = cardModel.getSeasonPoints()
        pointsList.clear()
        for state, season in cardSeasonPoints:
            pointModel = SeasonPointModel()
            pointModel.setState(state)
            if season is not None:
                pointModel.setSeason(season)
            pointsList.addViewModel(pointModel)

        pointsList.invalidate()
        return


class _SeasonPointsGenerator(object):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, areLastSeasonPointsReceived):
        self.__allPointsStates = self.__composePointsStates(areLastSeasonPointsReceived)

    def getNext(self, rewardsCount):
        result, self.__allPointsStates = self.__allPointsStates[:rewardsCount], self.__allPointsStates[rewardsCount:]
        if len(result) < rewardsCount:
            result += [(SeasonPointState.NOTACHIEVED, None)] * (rewardsCount - len(result))
        return result

    def __composePointsStates(self, areLastSeasonPointsReceived):
        result = []
        achievedPoints = self.__getAchievedPoints()
        for seasonName, count in achievedPoints:
            result += [(SeasonPointState.ACHIEVED, seasonName)] * count

        if self.__comp7Controller.getActualSeasonNumber() is None:
            return result
        else:
            if not self.__comp7Controller.isQualificationActive() and not areLastSeasonPointsReceived:
                possiblePointsCount = getPlayerDivision().seasonPoints
                result += [(SeasonPointState.POSSIBLE, getSeasonNameEnum())] * possiblePointsCount
            return result

    def __getAchievedPoints(self):
        achievedPoints = []
        entitlementsCount = self.__comp7Controller.getReceivedSeasonPoints()
        orderedSeasons = sorted(SEASONS_NUMBERS_BY_NAME.items(), key=lambda x: x[1])
        for seasonName, seasonNumber in orderedSeasons:
            count = entitlementsCount.get(seasonPointsCodeBySeasonNumber(seasonNumber), 0)
            achievedPoints.append((SeasonName(seasonName), count))

        return achievedPoints
