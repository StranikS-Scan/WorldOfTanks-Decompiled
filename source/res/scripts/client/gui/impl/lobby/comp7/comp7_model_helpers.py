# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_model_helpers.py
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.comp7.comp7_helpers import getComp7SkillParamsOrder
from gui.impl.gen.view_models.views.lobby.comp7.dynamic_param_model import DynamicParamModel
from gui.impl.gen.view_models.views.lobby.comp7.static_param_model import StaticParamModel
from gui.impl.lobby.comp7 import comp7_shared
from gui.impl.lobby.comp7.meta_view import meta_view_helper
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import DivisionInfoModel
    from gui.impl.gen.view_models.views.lobby.comp7.schedule_info_model import ScheduleInfoModel
    from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonModel
    from gui.impl.gen.view_models.views.lobby.comp7.skill_stats_model import SkillStatsModel
    from gui.impl.wrappers.user_list_model import UserListModel
    from items.artefacts import Equipment
    from season_common import GameSeason

def setDivisionInfo(model, division=None):
    if division is None:
        division = comp7_shared.getPlayerDivision()
    divisionValue = comp7_shared.getDivisionEnumValue(division)
    model.setName(divisionValue)
    model.setFrom(division.range.begin)
    model.setTo(division.range.end + 1)
    model.setState(meta_view_helper.getDivisionState(division))
    model.setType(division.type)
    if division.elitePercent:
        model.setElitePercent(division.elitePercent)
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


def fillEquipmentStats(skillStats, equipment):
    skillStats.setName(equipment.name)
    paramsOrder = getComp7SkillParamsOrder()
    tooltipParams = [ (param, value, paramsOrder.index(param)) for param, value in equipment.tooltipParams.iteritems() ]
    tooltipParams = sorted(tooltipParams, key=lambda x: x[2])
    dynamicParams = skillStats.dynamicParams
    fillDynamicParams(dynamicParams, tooltipParams)
    staticParams = skillStats.staticParams
    fillStaticParams(staticParams, tooltipParams)


def fillDynamicParams(dynamicParams, tooltipParams):
    dynamicParams.clearItems()
    for param, value, _ in tooltipParams:
        if not isinstance(value, tuple):
            continue
        dynamicParam = DynamicParamModel()
        dynamicParam.setName(param)
        dynamicParam.setValue1(str(value[0]))
        dynamicParam.setValue2(str(value[1]))
        dynamicParam.setValue3(str(value[2]))
        dynamicParams.addViewModel(dynamicParam)

    dynamicParams.invalidate()


def fillStaticParams(staticParams, tooltipParams):
    staticParams.clearItems()
    for param, value, _ in tooltipParams:
        if isinstance(value, tuple):
            continue
        staticParam = StaticParamModel()
        staticParam.setName(param)
        staticParam.setValue(str(value))
        staticParams.addViewModel(staticParam)

    staticParams.invalidate()
