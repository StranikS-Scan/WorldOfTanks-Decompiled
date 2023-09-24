# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_model_helpers.py
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.comp7 import comp7_shared
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IComp7Controller
from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonName, SeasonState
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from season_common import GameSeason
    from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import DivisionInfoModel
    from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel
    from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonModel
_SEASONS_NAMES_BY_NUMBER = {1: SeasonName.FIRST,
 2: SeasonName.SECOND,
 3: SeasonName.THIRD}
SEASONS_NUMBERS_BY_NAME = {v.value:k for k, v in _SEASONS_NAMES_BY_NUMBER.iteritems()}

def setDivisionInfo(model, division=None):
    if division is None:
        division = comp7_shared.getPlayerDivision()
    divisionValue = comp7_shared.getDivisionEnumValue(division)
    model.setName(divisionValue)
    model.setFrom(division.range.begin)
    model.setTo(division.range.end + 1)
    return


def getValidSeason(season=None):
    return season or _getCurrentSeason() or _getPrevSeason() or _getNextSeason()


def setSeasonInfo(model, season=None):
    season = getValidSeason(season)
    _SeasonPresenter.setSeasonInfo(model, season)


def setScheduleInfo(model):
    season = getValidSeason()
    if season is not None:
        model.setTooltipId(TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO)
    _SeasonPresenter.setSeasonInfo(model.season, season)
    yearState = comp7_shared.getProgressionYearState()
    model.year.setState(yearState)
    return


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setRanksInactivityInfo(model, comp7Controller=None):
    model.setHasRankInactivityWarning(comp7_shared.hasPlayerRankInactivityWarning())
    model.setRankInactivityCount(comp7Controller.activityPoints)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setElitePercentage(model, comp7Controller=None):
    model.setTopPercentage(comp7Controller.leaderboard.getEliteRankPercent())


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isModeForcedDisabled(status, comp7Controller=None):
    return not comp7Controller.isAvailable() and status == PrimeTimeStatus.AVAILABLE


def getSeasonNameEnum(season=None):
    season = getValidSeason(season)
    return _SEASONS_NAMES_BY_NUMBER.get(season.getNumber()) if season else None


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getCurrentSeason(comp7Controller=None):
    return comp7Controller.getCurrentSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getNextSeason(comp7Controller=None):
    return comp7Controller.getNextSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getPrevSeason(comp7Controller=None):
    return comp7Controller.getPreviousSeason()


class _SeasonPresenter(object):

    @classmethod
    def setSeasonInfo(cls, model, season):
        if season is not None:
            model.setName(getSeasonNameEnum(season))
            model.setStartTimestamp(season.getStartDate())
            model.setEndTimestamp(season.getEndDate())
            model.setServerTimestamp(getServerUTCTime())
            model.setHasTentativeDates(season.hasTentativeDates())
        model.setState(cls.__getSeasonState(season))
        return

    @staticmethod
    def __getSeasonState(season):
        if season is not None:
            currentTime = getServerUTCTime()
            if currentTime < season.getStartDate():
                return SeasonState.NOTSTARTED
            if currentTime > season.getEndDate():
                return SeasonState.END
        return comp7_shared.getCurrentSeasonState()
