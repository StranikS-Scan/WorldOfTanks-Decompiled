# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/yearly_rewards_page.py
from collections import namedtuple
import typing
from comp7_common import seasonPointsCodeBySeasonNumber
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_rewards_model import YearlyRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_rewards_card_model import SeasonPointState, YearlyRewardsCardModel, RewardsState
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.lobby.comp7 import comp7_shared
from gui.impl.lobby.comp7.comp7_bonus_packer import packQuestBonuses, getComp7BonusPacker
from gui.impl.lobby.comp7.comp7_shared import getPlayerDivisionByRating
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.impl.lobby.comp7.tooltips.season_point_tooltip import SeasonPointTooltip
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))

class YearlyRewardsPage(PageSubModelPresenter):
    __slots__ = ('__tooltips',)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, viewModel, parentView):
        super(YearlyRewardsPage, self).__init__(viewModel, parentView)
        self.__tooltips = []

    @property
    def pageId(self):
        return MetaRootViews.YEARLYREWARDS

    @property
    def viewModel(self):
        return super(YearlyRewardsPage, self).getViewModel()

    def initialize(self):
        super(YearlyRewardsPage, self).initialize()
        self.__updateAllData()

    def finalize(self):
        self.__tooltips = {}
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
            params = {'state': SeasonPointState(event.getArgument('state'))}
            return SeasonPointTooltip(params=params)
        else:
            return None

    def _getEvents(self):
        return ((self.__comp7Controller.onQualificationStateUpdated, self.__onQualificationStateUpdated),
         (self.__comp7Controller.onSeasonPointsUpdated, self.__onSeasonPointsUpdated),
         (self.__comp7Controller.onRankUpdated, self.__onRankUpdated),
         (self.__comp7Controller.onComp7ConfigChanged, self.__onConfigChanged),
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
        model.setSeasonPointsReceived(self.__areLastSeasonPointsReceived())
        if self.__comp7Controller.isAvailable() and not self.__comp7Controller.isQualificationActive():
            model.setCurrentRank(comp7_shared.getRankEnumValue(comp7_shared.getPlayerDivision()))
        else:
            prevSeason = self.__comp7Controller.getPreviousSeason()
            if not prevSeason:
                return
            seasonNumber = prevSeason.getNumber()
            if self.__comp7Controller.isRankAchievedInSeason(seasonNumber):
                prevDivision = getPlayerDivisionByRating(self.__comp7Controller.getRatingForSeason(seasonNumber))
                model.setCurrentRank(comp7_shared.getRankEnumValue(prevDivision))

    def __areLastSeasonPointsReceived(self):
        prevSeason = self.__comp7Controller.getPreviousSeason()
        if prevSeason is None:
            return False
        else:
            lastSeasonPointsEntitlement = seasonPointsCodeBySeasonNumber(prevSeason.getNumber())
            return self.__comp7Controller.getReceivedSeasonPoints().get(lastSeasonPointsEntitlement, 0) > 0

    def __setCards(self, model):
        cards = model.getCards()
        cards.clear()
        prevRewardsCost = 0
        pointStatesGenerator = _PointsStatesGenerator(self.__areLastSeasonPointsReceived())
        for rewardsData in sorted(self.__comp7Controller.getYearlyRewards().main, key=lambda data: data['cost']):
            currentPointsStates = pointStatesGenerator.getNext(rewardsData['cost'] - prevRewardsCost)
            prevRewardsCost = rewardsData['cost']
            cardModel = YearlyRewardsCardModel()
            cardModel.setRewardsState(self.__getRewardStateForCard(currentPointsStates))
            self.__setCardSeasonPoints(cardModel, currentPointsStates)
            self.__setRewards(cardModel, rewardsData['bonus'])
            cards.addViewModel(cardModel)

        cards.invalidate()

    def __getRewardStateForCard(self, cardPointsState):
        if all((pointState == SeasonPointState.ACHIEVED for pointState in cardPointsState)):
            if self.__comp7Controller.isYearlyRewardReceived():
                return RewardsState.CLAIMED
            return RewardsState.GUARANTEED
        return RewardsState.POSSIBLE if not any((pointState == SeasonPointState.NOTACHIEVED for pointState in cardPointsState)) else RewardsState.NOTAVAILABLE

    def __setRewards(self, cardModel, bonuses):
        rewards = cardModel.getRewards()
        rewards.clear()
        self.__tooltips = []
        bonusObjects = []
        for key, value in bonuses.iteritems():
            bonusObjects.extend(getNonQuestBonuses(key, value))

        bonusModels, tooltipsData = packQuestBonuses(bonusObjects, getComp7BonusPacker())
        for idx, bonusModel in enumerate(bonusModels):
            bonusModel.setTooltipId(str(len(self.__tooltips)))
            rewards.addViewModel(bonusModel)
            self.__tooltips.append(tooltipsData[idx])

        rewards.invalidate()

    @staticmethod
    def __setCardSeasonPoints(cardModel, seasonPoints):
        pointsList = cardModel.getSeasonPoints()
        pointsList.clear()
        for state in seasonPoints:
            pointsList.addString(state.value)

        pointsList.invalidate()


class _PointsStatesGenerator(object):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __RANK_ID_TO_SEASON_POINTS_COUNT = {6: 1,
     5: 2,
     4: 3,
     3: 4,
     2: 5,
     1: 6}

    def __init__(self, areLastSeasonPointsReceived):
        self.__allPointsStates = self.__composePointsStates(areLastSeasonPointsReceived)

    def getNext(self, rewardsCount):
        result, self.__allPointsStates = self.__allPointsStates[:rewardsCount], self.__allPointsStates[rewardsCount:]
        if len(result) < rewardsCount:
            result += [SeasonPointState.NOTACHIEVED] * (rewardsCount - len(result))
        return result

    def __composePointsStates(self, areLastSeasonPointsReceived):
        achievedPointsCount = sum(self.__comp7Controller.getReceivedSeasonPoints().values())
        result = [SeasonPointState.ACHIEVED] * achievedPointsCount
        if not self.__comp7Controller.isQualificationActive() and not areLastSeasonPointsReceived:
            possiblePointsCount = self.__RANK_ID_TO_SEASON_POINTS_COUNT.get(comp7_shared.getPlayerDivision().rank, 0)
            result += [SeasonPointState.POSSIBLE] * possiblePointsCount
        return result
