# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/__init__.py
from gui.Scaleform.daapi.settings import config as sf_config
from gui.shared.system_factory import registerScaleformBattlePackages, registerLobbyTooltipsBuilders
from fall_tanks_constants import ARENA_GUI_TYPE
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_TOOLTIPS_SET

def registerFallTanksScaleform():
    registerScaleformBattlePackages(ARENA_GUI_TYPE.FALL_TANKS, sf_config.BATTLE_PACKAGES + ('fall_tanks.gui.Scaleform.daapi.view.battle',))
    registerLobbyTooltipsBuilders([('fall_tanks.gui.Scaleform.daapi.view.tooltips.tooltip_builders', FALL_TANKS_TOOLTIPS_SET)])
