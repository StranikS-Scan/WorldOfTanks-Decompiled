# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_shared.py
import typing
from shared_utils import findFirst
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState
from comp7.gui.impl.gen.view_models.views.lobby.year_model import YearState
from gui.periodic_battles.models import PeriodType
from helpers import dependency, time_utils
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
_SEASON_START_DURATION_DAYS = 7
_SEASON_END_DURATION_DAYS = 7

def getDivisionEnumValue(division):
    return tuple(Division)[division.index - 1] if division is not None else None


def getRankEnumValue(division):
    return tuple(Rank)[division.rank - 1]


def getRankById(rankId):
    return Rank(rankId)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRating(comp7Controller=None):
    return comp7Controller.rating


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isElite(seasonNumber=None, comp7Controller=None):
    return comp7Controller.isEliteForSeason(seasonNumber)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isQualification(comp7Controller=None):
    return comp7Controller.isQualificationActive()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getPlayerDivisionByRating(rating, seasonNumber=None, comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
    division = findFirst(lambda d: rating in d.range, ranksConfig.divisions if not isElite(seasonNumber) else reversed(ranksConfig.divisions))
    return division


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getPlayerDivisionByRankAndIndex(rank, divisionIdx, comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
    division = findFirst(lambda d: d.index == divisionIdx, ranksConfig.divisionsByRank[rank])
    return division


def getPlayerDivision():
    rating = getRating()
    return getPlayerDivisionByRating(rating)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def hasRankInactivity(rank, comp7Controller=None):
    if not (comp7Controller.isAvailable() and not comp7Controller.isOffline):
        return False
    ranksConfig = comp7Controller.getRanksConfig()
    return any((division.hasRankInactivity for division in ranksConfig.divisionsByRank[rank]))


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def hasPlayerRankInactivityWarning(comp7Controller=None):
    ranksConfig = comp7Controller.getRanksConfig()
    rankInactivityThreshold = ranksConfig.rankInactivityNotificationThreshold
    return getPlayerDivision().hasRankInactivity and comp7Controller.activityPoints <= rankInactivityThreshold


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getCurrentSeasonState(comp7Controller=None):
    currentTime = time_utils.getCurrentLocalServerTimestamp()
    periodInfo = comp7Controller.getPeriodInfo()
    if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE):
        return SeasonState.NOTSTARTED
    if periodInfo.periodType in (PeriodType.AFTER_SEASON,
     PeriodType.AFTER_CYCLE,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END):
        return SeasonState.END
    if periodInfo.periodType == PeriodType.UNDEFINED:
        return SeasonState.DISABLED
    if periodInfo.periodType == PeriodType.BETWEEN_SEASONS:
        return SeasonState.END
    if periodInfo.cycleBorderLeft.delta(currentTime) < time_utils.ONE_DAY * _SEASON_START_DURATION_DAYS:
        return SeasonState.JUSTSTARTED
    return SeasonState.ENDSOON if periodInfo.cycleBorderRight.delta(currentTime) < time_utils.ONE_DAY * _SEASON_END_DURATION_DAYS else SeasonState.ACTIVE


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getBannerSeasonState(comp7Controller=None):
    startNotificationsPeriodLength = time_utils.ONE_DAY * 14
    endNotificationsPeriodLength = time_utils.ONE_DAY * 14
    currentTime = time_utils.getCurrentLocalServerTimestamp()
    periodInfo = comp7Controller.getPeriodInfo()
    if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE, PeriodType.BETWEEN_SEASONS):
        return SeasonState.NOTSTARTED
    if periodInfo.periodType in (PeriodType.AFTER_SEASON,
     PeriodType.AFTER_CYCLE,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END):
        return SeasonState.END
    if periodInfo.periodType in (PeriodType.ALL_NOT_AVAILABLE, PeriodType.STANDALONE_NOT_AVAILABLE):
        return SeasonState.DISABLED
    if periodInfo.cycleBorderLeft.delta(currentTime) < startNotificationsPeriodLength:
        status = SeasonState.JUSTSTARTED
    elif periodInfo.cycleBorderRight.delta(currentTime) < endNotificationsPeriodLength:
        status = SeasonState.ENDSOON
    else:
        status = SeasonState.ACTIVE
    return status


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
    else:
        return YearState.OFFSEASON if periodInfo.periodType == PeriodType.BETWEEN_SEASONS or periodInfo.periodType == PeriodType.AFTER_CYCLE and hasNextSeason or periodInfo.periodType == PeriodType.BEFORE_CYCLE and hasPrevSeason else YearState.ACTIVE


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRankByName(rankName, comp7Controller=None):
    config = comp7Controller.getRanksConfig()
    rank = findFirst(lambda rankData: rankData['name'].lower() == rankName.lower(), config.ranks.values())
    return Rank(rank['id'])


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def getRankOrder(rank, comp7Controller=None):
    config = comp7Controller.getRanksConfig()
    return config.ranksOrder.index(rank.value) + 1
