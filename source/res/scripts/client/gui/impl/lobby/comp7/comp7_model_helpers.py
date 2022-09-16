# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_model_helpers.py
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.comp7 import comp7_shared
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


def setSeasonInfo(model, season=None):
    season = season or _getCurrentSeason() or _getNextSeason() or _getPrevSeason()
    if season is not None:
        model.setStartTimestamp(season.getStartDate())
        model.setEndTimestamp(season.getEndDate())
        model.setServerTimestamp(getServerUTCTime())
    return


def setScheduleInfo(model, season=None):
    season = season or _getCurrentSeason() or _getNextSeason() or _getPrevSeason()
    if season is not None:
        model.setTooltipId(TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO)
        setSeasonInfo(model=model.season, season=season)
    return


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setRanksInfo(model, comp7Controller=None):
    model.setRankInactivityCount(comp7Controller.activityPoints)
    setElitePercentage(model)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def setElitePercentage(model, comp7Controller=None):
    model.setTopPercentage(comp7Controller.leaderboard.getEliteRankPercent())


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getCurrentSeason(comp7Controller=None):
    return comp7Controller.getCurrentSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getNextSeason(comp7Controller=None):
    return comp7Controller.getNextSeason()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getPrevSeason(comp7Controller=None):
    return comp7Controller.getPreviousSeason()
