# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_results/pbs_helpers.py
from __future__ import absolute_import
from typing import Dict, TYPE_CHECKING
from fort_rush_common.configs.fort_rush_battles_config import fortRushBattlesConfigGameParamsSchema
from fort_rush_common.fort_rush_constants import FINISH_REASON
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.simple_stats_parameter_model import ValueType, RegularParamType
from gui.battle_results.pbs_helpers.team_stats_helpers import getStatsParamValue
from gui.battle_results.presenters.packers.team.stats_params_settings import _Parameter
if TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
FORT_RUSH_PARAMETERS_UPDATE = {RegularParamType.CAPTUREPOINTSVAL: _Parameter(path=R.strings.battle_results.team.stats.labels_fortRushScore, stringId='fortRushScore', fields=('fortRushScore',), valueType=ValueType.INTEGER, conditions=None, extractor=getStatsParamValue, details=())}

def getProgressionPointsCountToShow(reusable):
    progressionToken = fortRushBattlesConfigGameParamsSchema.getModel().baseProgressionToken
    questTokensCount = reusable.personal.getQuestTokensCount()
    tokenData = questTokensCount.get(progressionToken)
    return tokenData['diff'] if tokenData else 0


def isProgressionPointsShown(value, hasFines, rewardValues, reusable):
    if hasFines:
        return True
    else:
        progressionToken = fortRushBattlesConfigGameParamsSchema.getModel().baseProgressionToken
        questTokensCount = reusable.personal.getQuestTokensCount()
        tokenData = questTokensCount.get(progressionToken)
        if tokenData is None:
            return False
        controller = dependency.instance(IFortRushBattleController)
        lastStageThreshold = controller.getLastStageThreshold()
        return False if 0 < lastStageThreshold <= tokenData['total'] - tokenData['diff'] else value >= 0


def makeFortRushFinishResultLabel(finishReason, teamResult):
    reasonResource = R.strings.fort_rush.endGame.reason.num(finishReason).dyn(teamResult)() if finishReason == FINISH_REASON.WIN_POINTS_CAP else R.strings.fort_rush.endGame.reason.num(finishReason)()
    return backport.text(reasonResource)
