# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/tooltips/total_efficiency_tooltips.py
from gui.battle_results.presenters.packers.tooltips.efficiency_tooltips import TotalKillsParameter, TotalStunParameter, TotalSpottedParameter, TotalDefencePointsParameter, TotalDamageDealtParameter, TotalDamageAssistedParameter, TotalDamageBlockedByArmorParameter, TotalCapturePointsParameter, EfficiencyTooltipsPacker
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import EfficiencyParameter
_STR_PATH = R.strings.fun_battle_results.efficiencyTooltip.header

class FunTotalKillsParameter(TotalKillsParameter):
    _TITLE = _STR_PATH.kills


class FunTotalDamageDealtParameter(TotalDamageDealtParameter):
    _TITLE = _STR_PATH.damageDealt


class FunTotalStunParameter(TotalStunParameter):
    _TITLE = _STR_PATH.damageAssistedStun


class FunTotalDamageBlockedByArmorParameter(TotalDamageBlockedByArmorParameter):
    _TITLE = _STR_PATH.damageBlockedByArmor


class FunTotalDamageAssistedParameter(TotalDamageAssistedParameter):
    _TITLE = _STR_PATH.damageAssisted


class FunTotalSpottedParameter(TotalSpottedParameter):
    _TITLE = _STR_PATH.spotted


class FunTotalCapturePointsParameter(TotalCapturePointsParameter):
    _TITLE = _STR_PATH.capturePoints


class FunTotalDefencePointsParameter(TotalDefencePointsParameter):
    _TITLE = _STR_PATH.droppedCapturePoints


_FUN_PARAMETERS_TO_TOOLTIP_MAP = {EfficiencyParameter.STUN: FunTotalStunParameter,
 EfficiencyParameter.DAMAGEDEALT: FunTotalDamageDealtParameter,
 EfficiencyParameter.DAMAGEBLOCKEDBYARMOR: FunTotalDamageBlockedByArmorParameter,
 EfficiencyParameter.DAMAGEASSISTED: FunTotalDamageAssistedParameter,
 EfficiencyParameter.SPOTTED: FunTotalSpottedParameter,
 EfficiencyParameter.KILLS: FunTotalKillsParameter,
 EfficiencyParameter.CAPTUREPOINTS: FunTotalCapturePointsParameter,
 EfficiencyParameter.DROPPEDCAPTUREPOINTS: FunTotalDefencePointsParameter}

class FunEfficiencyTooltipsPacker(EfficiencyTooltipsPacker):
    __slots__ = ()
    _TOOLTIPS = _FUN_PARAMETERS_TO_TOOLTIP_MAP
