# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/__init__.py
from gui.shared.system_factory import registerScaleformBattlePackages, registerBattleTooltipsBuilders, registerLobbyTooltipsBuilders
from constants import ARENA_GUI_TYPE
from gui.Scaleform.daapi.settings import config as sf_config
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS

def registerFLBattlePackages():
    packages = sf_config.BATTLE_PACKAGES + ('gui.Scaleform.daapi.view.battle.epic', 'frontline.gui.Scaleform.daapi.view.battle')
    registerScaleformBattlePackages(ARENA_GUI_TYPE.EPIC_BATTLE, packages)
    registerScaleformBattlePackages(ARENA_GUI_TYPE.EPIC_TRAINING, packages)


def registerFLTooltipsBuilders():
    registerBattleTooltipsBuilders([('frontline.gui.Scaleform.daapi.view.tooltips.frontline_battle_builders', _TOOLTIPS.FRONTLINE_BATTLE_SET)])
    registerLobbyTooltipsBuilders([('frontline.gui.Scaleform.daapi.view.tooltips.frontline_battle_builders', _TOOLTIPS.FRONTLINE_BATTLE_SET)])
