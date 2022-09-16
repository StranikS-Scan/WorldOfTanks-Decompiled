# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/comp7_battle_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import vehicle_roles
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder
from gui.shared.tooltips.comp7_tooltips import RoleSkillBattleTooltipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.COMP7_ROLE_SKILL_BATTLE_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RoleSkillBattleTooltipData(contexts.Comp7RoleSkillBattleContext())), TooltipWindowBuilder(TOOLTIPS_CONSTANTS.VEHICLE_ROLES, None, vehicle_roles.VehicleRolesTooltipContentWindowData(contexts.ToolTipContext(None))))
