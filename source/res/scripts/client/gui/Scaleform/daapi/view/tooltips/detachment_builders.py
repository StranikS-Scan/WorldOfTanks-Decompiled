# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/detachment_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, advanced
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder, AdvancedDataBuilder
from gui.shared.tooltips import detachment
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.DETACHMENT_SELL_LIMIT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, detachment.DetachmentSellLimitTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.DETACHMENT_RECYCLE_BIN_FULL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, detachment.DetachmentRecycleBinFullData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.CREW_RETRAIN_PENALTY, None, detachment.CrewRetrainPenaltyTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.DETACHMENT_PREVIEW, None, detachment.DetachmentPreviewTooltipContentWindowData(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RECERTIFICATION_FORM, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, detachment.RecertificationFormToolTipData(contexts.ToolTipContext(None)), advanced.RecertificationAdvanced(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.DORMITORY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, detachment.DormitoryInfoToolTipData(contexts.ToolTipContext(None)), advanced.DormitoriesAdvanced(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.INSTRUCTOR_BONUSES, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, detachment.InstructorBonusesToolTipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.GF_DETACHMENT_PERK, None, detachment.DetachmentPerkTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.COMMANDER_PERK_GF, None, detachment.CommanderPerkTooltipData(contexts.ToolTipContext(None))))
