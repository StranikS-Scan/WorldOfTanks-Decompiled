# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_model_helpers.py
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.comp7 import comp7_shared
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from season_common import GameSeason
    from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import DivisionInfoModel
    from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel
    from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonModel

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
    seasonState = comp7_shared.getProgressionSeasonState()
    model.setState(seasonState)
    if season is not None:
        model.setStartTimestamp(season.getStartDate())
        model.setEndTimestamp(season.getEndDate())
        model.setServerTimestamp(getServerUTCTime())
    return


def setScheduleInfo(model):
    season = getValidSeason()
    if season is not None:
        model.setTooltipId(TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO)
    setSeasonInfo(model=model.season, season=season)
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


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getCurrentSeason(comp7Controller=None):
    return comp7Controller.getCurrentSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getNextSeason(comp7Controller=None):
    return comp7Controller.getNextSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getPrevSeason(comp7Controller=None):
    return comp7Controller.getPreviousSeason()
