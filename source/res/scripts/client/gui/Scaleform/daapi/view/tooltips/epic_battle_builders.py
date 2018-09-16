# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/epic_battle_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import epic_skills
from gui.Scaleform.daapi.view.lobby.hangar.epic_battles_widget import EpicBattlesWidgetTooltip
from gui.shared.tooltips.builders import DataBuilder
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_game_selector_tooltip import EpicMetaGameSelectorTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, epic_skills.EpicSkillExtendedTooltip(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicMetaGameSelectorTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, epic_skills.EpicSkillSlotTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_META_LEVEL_PROGRESS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicBattlesWidgetTooltip(contexts.ToolTipContext(None))))
