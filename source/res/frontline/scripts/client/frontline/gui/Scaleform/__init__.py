# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/__init__.py
from gui.shared.system_factory import registerBattleTooltipsBuilders, registerLobbyTooltipsBuilders
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS

def registerFLTooltipsBuilders():
    registerBattleTooltipsBuilders([('frontline.gui.Scaleform.daapi.view.tooltips.frontline_battle_builders', _TOOLTIPS.FRONTLINE_BATTLE_SET)])
    registerLobbyTooltipsBuilders([('frontline.gui.Scaleform.daapi.view.tooltips.frontline_battle_builders', _TOOLTIPS.FRONTLINE_BATTLE_SET)])
