# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/epic_battle_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import epic_skills
from gui.Scaleform.daapi.view.lobby.hangar.epic_battles_widget import EpicBattlesWidgetTooltip
from gui.shared.tooltips.builders import DataBuilder
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_meta_game_selector_tooltip import EpicMetaGameSelectorTooltip
from gui.game_control.epic_meta_game_ctrl import DISABLE_EPIC_META_GAME
__all__ = ('getTooltipBuilders',)

class SkillPopoverBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(SkillPopoverBuilder, self).__init__(tooltipType, linkage, epic_skills.EpicSkillPopoverTooltip(contexts.ToolTipContext(None)))
        return

    def _buildData(self, advanced, *args):
        skillID, level = args
        return self._provider.buildToolTip(skillID, level)


class SkillSlotBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(SkillSlotBuilder, self).__init__(tooltipType, linkage, epic_skills.EpicSkillSlotTooltip(contexts.ToolTipContext(None)))
        return

    def _buildData(self, _advanced, eqCompDescr, *args, **kwargs):
        return self._provider.buildToolTip(eqCompDescr)


class WidgetPopoverBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(WidgetPopoverBuilder, self).__init__(tooltipType, linkage, EpicBattlesWidgetTooltip(contexts.ToolTipContext(None)))
        return

    def _buildData(self, advanced, *args):
        return self._provider.buildToolTip()


def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, epic_skills.EpicSkillExtendedTooltip(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicMetaGameSelectorTooltip(contexts.ToolTipContext(None))),
     SkillPopoverBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_POPOVER_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     SkillSlotBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     WidgetPopoverBuilder(TOOLTIPS_CONSTANTS.EPIC_META_LEVEL_PROGRESS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI)) if not DISABLE_EPIC_META_GAME else (DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, epic_skills.EpicSkillExtendedTooltip(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EPIC_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicMetaGameSelectorTooltip(contexts.ToolTipContext(None))),
     SkillPopoverBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_POPOVER_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     SkillSlotBuilder(TOOLTIPS_CONSTANTS.EPIC_SKILL_SLOT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))
