# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_shared.py
import typing
from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import Division
from gui.impl.gen.view_models.views.lobby.comp7.views.main_widget_model import Rank
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from helpers.server_settings import Comp7PrestigeRanksConfig

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getDivisionEnumValue(division, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7PrestigeRanksConfig
    rankDivisions = ranksConfig.divisionsByRank[division.rank]
    divisionIdx = len(rankDivisions) - division.index - 1
    return tuple(Division)[divisionIdx]


def getRankEnumValue(division):
    rankIdx = division.rank
    return tuple(Rank)[rankIdx]


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRating(comp7Controller=None):
    return comp7Controller.rating


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isElite(comp7Controller=None):
    return comp7Controller.isElite


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getPlayerDivisionByRating(rating, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7PrestigeRanksConfig
    division = findFirst(lambda d: rating in d.range, ranksConfig.divisions if not isElite() else reversed(ranksConfig.divisions))
    return division


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getPlayerDivisionByRankAndIndex(rank, divisionIdx, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7PrestigeRanksConfig
    division = findFirst(lambda d: d.rank == rank and d.index == divisionIdx, ranksConfig.divisions)
    return division


def getPlayerDivision():
    rating = getRating()
    return getPlayerDivisionByRating(rating)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext, comp7Controller=IComp7Controller)
def hasRankInactivity(rankIdx, lobbyCtx=None, comp7Controller=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7PrestigeRanksConfig
    division = findFirst(lambda d: rankIdx == d.rank, ranksConfig.divisions)
    if not (comp7Controller.isAvailable() and not comp7Controller.isOffline):
        return False
    else:
        return division.hasRankInactivity if division is not None else False


def hasPlayerRankInactivity():
    return getPlayerDivision().hasRankInactivity
