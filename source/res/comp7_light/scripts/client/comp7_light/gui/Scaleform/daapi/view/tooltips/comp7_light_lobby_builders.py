# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/tooltips/comp7_light_lobby_builders.py
from comp7_light.gui.Scaleform.daapi.view.lobby.tooltips.comp7_light_calendar_day_extended_tooltip import Comp7LightCalendarDayExtendedTooltip
from comp7_light.gui.Scaleform.daapi.view.lobby.tooltips.comp7_light_calendar_day_tooltip import Comp7LightCalendarDayTooltip
from comp7_light.gui.Scaleform.daapi.view.lobby.tooltips.comp7_light_selector_tooltip import Comp7LightSelectorTooltip
from comp7_light.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_LIGHT_TOOLTIPS
from comp7_light.gui.shared.tooltips.comp7_light_tooltips import Comp7LightRoleSkillLobbyTooltipData
from comp7_light.gui.shared.tooltips.contexts import Comp7LightRoleSkillLobbyContext
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7LightSelectorTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_CALENDAR_DAY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7LightCalendarDayTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_CALENDAR_DAY_EXTENDED_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7LightCalendarDayExtendedTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_ROLE_SKILL_LOBBY_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7LightRoleSkillLobbyTooltipData(Comp7LightRoleSkillLobbyContext())))
