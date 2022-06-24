# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/epic_battle_builders.py
from gui.Scaleform.daapi.view.lobby.epicBattle.tooltips.instruction import EpicBattleInstructionTooltipData, EpicBattleTokenInstructionContext
from gui.Scaleform.daapi.view.lobby.epicBattle.tooltips.recertification_tooltip import EpicBattleRecertificationFormTooltipAdvanced, EpicBattleBlanksContext, EpicBattleRecertificationFormTooltip
from gui.Scaleform.daapi.view.lobby.epicBattle.tooltips.epic_battle_calendar_tooltip import EpicBattleCalendarTooltip
from gui.Scaleform.daapi.view.lobby.epicBattle.tooltips.epic_battle_selector_tooltip import EpicBattleSelectorTooltip
from gui.Scaleform.daapi.view.lobby.epicBattle.tooltips.epic_battle_widget_tooltip import EpicBattleWidgetTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
from gui.shared.tooltips.epic_battle.epic_skills import EpicSkillBaseTooltipData, EpicSkillSlotTooltip, EpicSkillSlotTooltipAdvanced, EpicSkillSlotSetupInfoTooltip
from gui.shared.tooltips.epic_battle.epic_quests_tooltips import EpicBattleQuestsTooltipData, CompletedQuestsTooltipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicSkillBaseTooltipData(contexts.QuestsBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicSkillSlotTooltip(contexts.ToolTipContext(None)), EpicSkillSlotTooltipAdvanced(contexts.HangarCardContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_SETUP_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicSkillSlotSetupInfoTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicBattleQuestsTooltipData(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_BATTLE_COMPLETED_QUESTS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, CompletedQuestsTooltipData(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_BATTLE_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicBattleSelectorTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_BATTLE_WIDGET_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicBattleWidgetTooltip(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.EPIC_BATTLE_RECERTIFICATION_FORM_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicBattleRecertificationFormTooltip(EpicBattleBlanksContext()), EpicBattleRecertificationFormTooltipAdvanced(EpicBattleBlanksContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_BATTLE_CALENDAR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicBattleCalendarTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_BATTLE_INSTRUCTION_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicBattleInstructionTooltipData(EpicBattleTokenInstructionContext())))
