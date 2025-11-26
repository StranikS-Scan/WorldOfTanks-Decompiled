# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/tooltips/total_efficiency_tooltips.py
from __future__ import absolute_import
import typing
from gui.battle_results.presenters.packers.tooltips.efficiency_tooltips import KillsParameter, StunParameter, SpottedParameter, DefencePointsParameter, DamageDealtParameter, DamageAssistedParameter, DamageBlockedByArmorParameter, CapturePointsParameter, EfficiencyTooltipsPacker
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.efficiency_param_constants import EfficiencyParamConstants
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
_STR_PATH = R.strings.fun_battle_results.efficiencyTooltip.header

class FunTotalKillsParameter(KillsParameter):
    _TITLE = _STR_PATH.kills


class FunTotalDamageDealtParameter(DamageDealtParameter):
    _TITLE = _STR_PATH.damageDealt


class FunTotalStunParameter(StunParameter):
    _TITLE = _STR_PATH.damageAssistedStun


class FunTotalDamageBlockedByArmorParameter(DamageBlockedByArmorParameter):
    _TITLE = _STR_PATH.damageBlockedByArmor


class FunTotalDamageAssistedParameter(DamageAssistedParameter):
    _TITLE = _STR_PATH.damageAssisted


class FunTotalSpottedParameter(SpottedParameter):
    _TITLE = _STR_PATH.spotted


class FunTotalCapturePointsParameter(CapturePointsParameter):
    _TITLE = _STR_PATH.capturePoints


class FunTotalDefencePointsParameter(DefencePointsParameter):
    _TITLE = _STR_PATH.droppedCapturePoints


_FUN_PARAMETERS_TO_TOOLTIP_MAP = {EfficiencyParamConstants.STUN: FunTotalStunParameter,
 EfficiencyParamConstants.DAMAGE_DEALT: FunTotalDamageDealtParameter,
 EfficiencyParamConstants.DAMAGE_BLOCKED_BY_ARMOR: FunTotalDamageBlockedByArmorParameter,
 EfficiencyParamConstants.DAMAGE_ASSISTED: FunTotalDamageAssistedParameter,
 EfficiencyParamConstants.SPOTTED: FunTotalSpottedParameter,
 EfficiencyParamConstants.KILLS: FunTotalKillsParameter,
 EfficiencyParamConstants.CAPTURE_POINTS: FunTotalCapturePointsParameter,
 EfficiencyParamConstants.DROPPED_CAPTURE_POINTS: FunTotalDefencePointsParameter}

class FunEfficiencyTooltipsPacker(EfficiencyTooltipsPacker):
    __slots__ = ()
    _TOOLTIPS = _FUN_PARAMETERS_TO_TOOLTIP_MAP

    @classmethod
    def packTooltip(cls, model, battleResults, ctx=None):
        if not ctx['paramType']:
            raise SoftException('Missing parameter type for the FunEfficiencyTooltip')
        ctx['isZeroValuesVisible'] = True
        ctx['isAdditionalValuesVisible'] = False
        super(FunEfficiencyTooltipsPacker, cls).packTooltip(model, battleResults, ctx)
