# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/meta_view_helper.py
import logging
import typing
from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import DivisionInfoModel, Division, State
from gui.impl.gen.view_models.views.lobby.comp7.leaderboard_navigation_division_info import LeaderboardNavigationDivisionInfo
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import Rank
from helpers import dependency
from intervals import Interval
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.lobby.comp7 import comp7_shared
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_base_model import ProgressionBaseModel
    from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import ProgressionItemBaseModel
    from helpers.server_settings import Comp7RanksConfig
_logger = logging.getLogger(__name__)

def setProgressionItemData(itemModel, parentModel, rankIdx, ranksConfig):
    setRankData(itemModel, parentModel, rankIdx, ranksConfig)
    setDivisionsData(itemModel, getRankDivisions(rankIdx, ranksConfig))


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setRankData(itemModel, parentModel, rank, ranksConfig, comp7Controller=None):
    sortedDivisions = getRankDivisions(rank, ranksConfig)
    rankLimits = Interval(sortedDivisions[0].range.begin, sortedDivisions[-1].range.end)
    isRankElite = rank == _getEliteRank()
    if not isRankElite or comp7Controller.isElite:
        if comp7Controller.rating in rankLimits:
            rankIdx = ranksConfig.ranksOrder.index(rank)
            parentModel.setCurrentItemIndex(rankIdx)
    itemModel.setRank(comp7_shared.getRankEnumValue(sortedDivisions[0]))
    itemModel.setFrom(rankLimits.begin)
    itemModel.setTo(rankLimits.end + 1)


def getRankDivisions(rank, ranksConfig):
    if len(ranksConfig.ranksOrder) != len(Rank):
        _logger.error('Config/ enum ranks length mismatch')
    sortedDivisions = ranksConfig.divisionsByRank[rank]
    if len(sortedDivisions) > len(Division):
        _logger.error('Config/ enum divisions length mismatch')
    return sortedDivisions


def setDivisionsData(itemModel, divisions):
    divisionsArray = itemModel.getDivisions()
    divisionsArray.clear()
    for division in divisions:
        divisionModel = DivisionInfoModel()
        setDivisionData(divisionModel, division)
        divisionsArray.addViewModel(divisionModel)

    divisionsArray.invalidate()


def setDivisionData(divisionModel, division):
    divisionModel.setName(comp7_shared.getDivisionEnumValue(division))
    divisionModel.setState(getDivisionState(division))
    divisionModel.setFrom(division.range.begin)
    divisionModel.setTo(division.range.end)
    divisionModel.setType(division.type)
    divisionModel.setElitePercent(division.elitePercent)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getDivisionState(division, comp7Controller=None):
    eliteRank = _getEliteRank()
    if division.rank == eliteRank and not comp7Controller.isElite:
        return State.INACTIVE
    if comp7Controller.isElite:
        if division.rank != eliteRank:
            return State.ACHIEVED
        eliteDivisionIdx = comp7Controller.getEliteDivisionIdx()
        if division.index > eliteDivisionIdx:
            return State.INACTIVE
        if division.index < eliteDivisionIdx:
            return State.ACHIEVED
        return State.CURRENT
    currentRating = comp7Controller.rating
    if currentRating < division.range.begin:
        return State.INACTIVE
    return State.CURRENT if currentRating <= division.range.end else State.ACHIEVED


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def _getEliteRank(lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    eliteRank = ranksConfig.ranksOrder[-1]
    return eliteRank
