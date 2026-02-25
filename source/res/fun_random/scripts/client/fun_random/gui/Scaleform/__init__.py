# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/__init__.py
from __future__ import absolute_import
from fun_random_common.fun_constants import ARENA_GUI_TYPE
from fun_random.gui.fun_gui_constants import FunRandomTooltipConstants
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.Scaleform.daapi.settings import config as sf_config
from gui.shared.system_factory import registerScaleformLobbyPackages, registerLobbyTooltipsBuilders, registerScaleformBattlePackages, registerLifecycleHandledSubViews

def registerFunRandomScaleform():
    registerScaleformLobbyPackages(('fun_random.gui.Scaleform.daapi.view.lobby',))
    registerScaleformBattlePackages(ARENA_GUI_TYPE.FUN_RANDOM, sf_config.BATTLE_PACKAGES + ('fun_random.gui.Scaleform.daapi.view.battle',))
    registerLobbyTooltipsBuilders([('fun_random.gui.Scaleform.daapi.view.tooltips.lobby_builders', FunRandomTooltipConstants.LOBBY_TOOLTIPS_SET)])
    registerLifecycleHandledSubViews([FUNRANDOM_ALIASES.FUN_RANDOM_HANGAR, FUNRANDOM_ALIASES.FUN_PROGRESSION])
