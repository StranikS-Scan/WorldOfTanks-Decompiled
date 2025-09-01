# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/__init__.py
from comp7_core.gui.Scaleform.genConsts.TOOLTIPS_BATTLE_CONSTANTS import TOOLTIPS_BATTLE_CONSTANTS as COMP7_BATTLE_TOOLTIPS
from comp7_light.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_LIGHT_TOOLTIPS
from comp7_light_constants import ARENA_GUI_TYPE
from gui.Scaleform.daapi.settings.config import BATTLE_PACKAGES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.system_factory import registerScaleformLobbyPackages, registerLobbyTooltipsBuilders, registerScaleformBattlePackages, registerBattleTooltipsBuilders

def registerComp7LightScaleform():
    registerScaleformLobbyPackages(('comp7_light.gui.Scaleform.daapi.view.lobby',))
    registerLobbyTooltipsBuilders([('comp7_light.gui.Scaleform.daapi.view.tooltips.comp7_light_lobby_builders', COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_LOBBY_SET)])
    registerScaleformBattlePackages(ARENA_GUI_TYPE.COMP7_LIGHT, BATTLE_PACKAGES + ('comp7_light.gui.Scaleform.daapi.view.battle',))
    COMP7_BATTLE_TOOLTIPS.COMP7_BATTLE_SET.append(TOOLTIPS_CONSTANTS.VEHICLE_ROLES)
    registerBattleTooltipsBuilders([('comp7_light.gui.Scaleform.daapi.view.tooltips.comp7_light_battle_builders', COMP7_BATTLE_TOOLTIPS.COMP7_BATTLE_SET)])
