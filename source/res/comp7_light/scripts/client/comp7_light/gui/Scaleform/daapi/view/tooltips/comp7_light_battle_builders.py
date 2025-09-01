# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/tooltips/comp7_light_battle_builders.py
from comp7_core.gui.Scaleform.genConsts.TOOLTIPS_BATTLE_CONSTANTS import TOOLTIPS_BATTLE_CONSTANTS as COMP7_BATTLE_TOOLTIPS
from comp7_light.gui.shared.tooltips.comp7_light_tooltips import Comp7LightRoleSkillBattleTooltipData
from comp7_light.gui.shared.tooltips.contexts import Comp7LightRoleSkillBattleContext
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, vehicle_roles
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(COMP7_BATTLE_TOOLTIPS.COMP7_ROLE_SKILL_BATTLE_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7LightRoleSkillBattleTooltipData(Comp7LightRoleSkillBattleContext())), TooltipWindowBuilder(TOOLTIPS_CONSTANTS.VEHICLE_ROLES, None, vehicle_roles.VehicleRolesTooltipContentWindowData(contexts.ToolTipContext(None))))
