# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/tooltips/fall_tanks_total_efficiency_tooltips.py
from __future__ import absolute_import
from gui.battle_results.presenters.packers.tooltips.efficiency_tooltips import BaseParameter
from gui.impl.gen import R
from fun_random.gui.battle_results.tooltips.total_efficiency_tooltips import FunEfficiencyTooltipsPacker
from fall_tanks.gui.battle_results.fall_tanks_pbs_constants import FallTanksEfficiencyParam
_STR_HEADER_PATH = R.strings.fun_battle_results.sub_modes.fall_tanks.efficiencyTooltip.header
_STR_DESCRIPTION_PATH = R.strings.fun_battle_results.sub_modes.fall_tanks.efficiencyTooltip.description
_ICON_PATH = R.images.fun_random.gui.maps.icons.feature.asset_packs.sub_modes.fall_tanks.battle_results.stat_list.small

class TotalFinishTimeParameter(BaseParameter):
    _TITLE = _STR_HEADER_PATH.finishTime
    _DESCRIPTION = _STR_DESCRIPTION_PATH.finishTime
    _ICON = _ICON_PATH.finishTime


class TotalFinishPositionParameter(BaseParameter):
    _TITLE = _STR_HEADER_PATH.finishPosition
    _DESCRIPTION = _STR_DESCRIPTION_PATH.finishPosition
    _ICON = _ICON_PATH.finishPosition


class TotalDeathCountsParameter(BaseParameter):
    _TITLE = _STR_HEADER_PATH.deathCount
    _DESCRIPTION = _STR_DESCRIPTION_PATH.deathCount
    _ICON = _ICON_PATH.deathCount


class TotalPassedCheckpointsParameter(BaseParameter):
    _TITLE = _STR_HEADER_PATH.checkpointsPassed
    _DESCRIPTION = _STR_DESCRIPTION_PATH.checkpointsPassed
    _ICON = _ICON_PATH.checkpointsPassed


class TotalDestroyedCountParameter(BaseParameter):
    _TITLE = _STR_HEADER_PATH.destroyed
    _DESCRIPTION = _STR_DESCRIPTION_PATH.destroyed
    _ICON = _ICON_PATH.destroyed


class FallTanksEfficiencyTooltipsPacker(FunEfficiencyTooltipsPacker):
    _TOOLTIPS = {FallTanksEfficiencyParam.FINISH_POSITION: TotalFinishPositionParameter,
     FallTanksEfficiencyParam.FINISH_TIME: TotalFinishTimeParameter,
     FallTanksEfficiencyParam.CHECKPOINTS_PASSED: TotalPassedCheckpointsParameter,
     FallTanksEfficiencyParam.DESTROYED: TotalDestroyedCountParameter,
     FallTanksEfficiencyParam.DEATH_COUNT: TotalDeathCountsParameter}
