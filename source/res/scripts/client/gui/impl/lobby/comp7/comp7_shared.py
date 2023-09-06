# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_shared.py
import typing
from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import Division
from gui.impl.gen.view_models.views.lobby.comp7.main_widget_model import Rank
from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonState
from gui.impl.gen.view_models.views.lobby.comp7.year_model import YearState
from gui.periodic_battles.models import PeriodType
from helpers import dependency, time_utils
from shared_utils import findFirst
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from helpers.server_settings import Comp7RanksConfig
_SEASON_START_DURATION_DAYS = 7
_SEASON_END_DURATION_DAYS = 7

def getDivisionEnumValue(division):
    return tuple(Division)[division.index - 1]


def getRankEnumValue(division):
    return tuple(Rank)[division.rank - 1]


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRating(comp7Controller=None):
    return comp7Controller.rating


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isElite(comp7Controller=None):
    return comp7Controller.isElite


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isQualification(comp7Controller=None):
    return comp7Controller.isQualificationActive()


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getPlayerDivisionByRating(rating, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    division = findFirst(lambda d: rating in d.range, ranksConfig.divisions if not isElite() else reversed(ranksConfig.divisions))
    return division


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def getPlayerDivisionByRankAndIndex(rank, divisionIdx, lobbyCtx=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    division = findFirst(lambda d: d.index == divisionIdx, ranksConfig.divisionsByRank[rank])
    return division


def getPlayerDivision():
    rating = getRating()
    return getPlayerDivisionByRating(rating)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext, comp7Controller=IComp7Controller)
def hasRankInactivity(rank, lobbyCtx=None, comp7Controller=None):
    if not (comp7Controller.isAvailable() and not comp7Controller.isOffline):
        return False
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    return any((division.hasRankInactivity for division in ranksConfig.divisionsByRank[rank]))


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext, comp7Controller=IComp7Controller)
def hasPlayerRankInactivityWarning(lobbyCtx=None, comp7Controller=None):
    ranksConfig = lobbyCtx.getServerSettings().comp7RanksConfig
    rankInactivityThreshold = ranksConfig.rankInactivityNotificationThreshold
    return getPlayerDivision().hasRankInactivity and comp7Controller.activityPoints <= rankInactivityThreshold


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getProgressionSeasonState(comp7Controller=None):
    currentTime = time_utils.getCurrentLocalServerTimestamp()
    periodInfo = comp7Controller.getPeriodInfo()
    if periodInfo.periodType in (PeriodType.ALL_NOT_AVAILABLE, PeriodType.STANDALONE_NOT_AVAILABLE, PeriodType.UNDEFINED):
        return SeasonState.DISABLED
    if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE):
        return SeasonState.NOTSTARTED
    if periodInfo.periodType in (PeriodType.AFTER_SEASON,
     PeriodType.AFTER_CYCLE,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END):
        return SeasonState.END
    if periodInfo.periodType == PeriodType.BETWEEN_SEASONS:
        return SeasonState.END
    if periodInfo.cycleBorderLeft.delta(currentTime) < time_utils.ONE_DAY * _SEASON_START_DURATION_DAYS:
        return SeasonState.JUSTSTARTED
    return SeasonState.ENDSOON if periodInfo.cycleBorderRight.delta(currentTime) < time_utils.ONE_DAY * _SEASON_END_DURATION_DAYS else SeasonState.ACTIVE


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getProgressionYearState(comp7Controller=None):
    periodInfo = comp7Controller.getPeriodInfo()
    hasNextSeason = comp7Controller.getNextSeason() is not None
    hasPrevSeason = comp7Controller.getPreviousSeason() is not None
    if periodInfo.periodType == PeriodType.BEFORE_SEASON:
        return YearState.NOTSTARTED
    elif periodInfo.periodType in (PeriodType.AFTER_SEASON,
     PeriodType.STANDALONE_NOT_AVAILABLE_END,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.NOT_AVAILABLE_END):
        return YearState.FINISHED
    elif periodInfo.periodType in (PeriodType.AVAILABLE, PeriodType.BETWEEN_CYCLES):
        return YearState.ACTIVE
    else:
        return YearState.OFFSEASON if periodInfo.periodType == PeriodType.BETWEEN_SEASONS or periodInfo.periodType == PeriodType.AFTER_CYCLE and hasNextSeason or periodInfo.periodType == PeriodType.BEFORE_CYCLE and hasPrevSeason else YearState.NOTSTARTED
