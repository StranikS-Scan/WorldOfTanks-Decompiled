# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/tooltips_packers.py
import inspect
from gui.battle_results.presenters.packers.tooltips.efficiency_tooltips import DamageAssistedParameter, SpottedParameter, DamageBlockedByArmorParameter, DamageDealtParameter, KillsParameter, StunParameter, CapturePointsParameter, DefencePointsParameter, EfficiencyTooltipsPacker
from gui.impl.gen.view_models.views.lobby.battle_results.base_capture_info_model import BaseCaptureInfoModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_item_model import DetailedPersonalEfficiencyItemModel
DETAILED_PARAMETERS_TO_TOOLTIP_MAP = {DetailedPersonalEfficiencyItemModel.SPOTTED: SpottedParameter,
 DetailedPersonalEfficiencyItemModel.DAMAGE_ASSISTED: DamageAssistedParameter,
 DetailedPersonalEfficiencyItemModel.DAMAGE_BLOCKED_BY_ARMOR: DamageBlockedByArmorParameter,
 DetailedPersonalEfficiencyItemModel.DAMAGE_DEALT: DamageDealtParameter,
 DetailedPersonalEfficiencyItemModel.KILLED: KillsParameter,
 DetailedPersonalEfficiencyItemModel.STUN: StunParameter,
 BaseCaptureInfoModel.CAPTURE_POINTS: CapturePointsParameter,
 BaseCaptureInfoModel.DROPPED_CAPTURE_POINTS: DefencePointsParameter}

class BattleEfficiencyTooltipsPacker(EfficiencyTooltipsPacker):
    __slots__ = ()
    _TOOLTIPS = DETAILED_PARAMETERS_TO_TOOLTIP_MAP

    @staticmethod
    def _getEfficiencyParameter(paramType):
        efficiencyItems = inspect.getmembers(DetailedPersonalEfficiencyItemModel, lambda a: not inspect.ismethod(a))
        for _, attrValue in efficiencyItems:
            if attrValue == paramType:
                return attrValue

        baseCaptureItems = inspect.getmembers(BaseCaptureInfoModel, lambda a: not inspect.ismethod(a))
        for _, attrValue in baseCaptureItems:
            if attrValue == paramType:
                return attrValue

        return None
