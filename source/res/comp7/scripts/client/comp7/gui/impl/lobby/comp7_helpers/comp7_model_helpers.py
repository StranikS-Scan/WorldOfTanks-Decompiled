# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_model_helpers.py
import logging
from itertools import izip
import typing
from comp7.gui.impl.gen.view_models.views.lobby.enums import Rank
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
if typing.TYPE_CHECKING:
    from typing import Optional
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
    from comp7_ranks_common import Comp7Division
    from comp7.gui.impl.gen.view_models.views.lobby.division_info_model import DivisionInfoModel
_logger = logging.getLogger(__name__)
SEASONS_NUMBERS_BY_NAME = {SeasonName.FIRST.value: 1,
 SeasonName.SECOND.value: 2,
 SeasonName.THIRD.value: 3}

def setDivisionInfo(model, division=None):
    division = division or comp7_shared.getPlayerDivision()
    if division is None:
        return
    else:
        divisionValue = comp7_shared.getDivisionEnumValue(division)
        model.setName(divisionValue)
        model.setFrom(division.range.begin)
        model.setTo(division.range.end + 1)
        return


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setRanksInactivityInfo(model, comp7Controller=None):
    model.setHasRankInactivityWarning(comp7_shared.hasPlayerRankInactivityWarning())
    model.setRankInactivityCount(comp7Controller.activityPoints)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setElitePercentage(model, comp7Controller=None):
    model.setTopPercentage(comp7Controller.leaderboard.getEliteRankPercent())


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setRankInfo(model, comp7Controller=None):
    seasonNumber = comp7Controller.getActualSeasonNumber()
    if not seasonNumber:
        return
    rating = comp7Controller.getRatingForSeason(seasonNumber)
    division = comp7_shared.getPlayerDivisionByRating(rating)
    rankEnum = comp7_shared.getRankEnumValue(division)
    model.setCurrentRank(rankEnum)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getYearlyRewardsRank(comp7Controller=None):
    seasonPointsSum = sum(comp7Controller.getReceivedSeasonPoints().itervalues())
    costs = comp7Controller.getYearlyRewards().getCosts()
    costs.reverse()
    for cost, rank in izip(costs, Rank):
        if cost <= seasonPointsSum:
            return rank


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setMaxRankInfo(model, comp7Controller=None):
    seasonNumber = comp7Controller.getActualSeasonNumber()
    if not seasonNumber:
        return
    maxAchivedRankNumber = comp7Controller.getMaxRankNumberForSeason(seasonNumber)
    config = comp7Controller.getRanksConfig()
    ranksOrder = config.ranksOrder
    rankId = ranksOrder[maxAchivedRankNumber - 1]
    model.setMaxAchievedRank(comp7_shared.getRankById(rankId))
