# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/__init__.py
from gui.shared.system_factory import registerScaleformBattlePackages, registerScaleformLobbyPackages, registerBattleTooltipsBuilders, registerLobbyTooltipsBuilders
from constants import ARENA_GUI_TYPE
from gui.Scaleform.daapi.settings import config as sf_config
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS
from gui.Scaleform.required_libraries_config import addBattleRequiredLibraries

def registerBRBattlePackages():
    registerScaleformBattlePackages(ARENA_GUI_TYPE.BATTLE_ROYALE, ('battle_royale.gui.Scaleform.daapi.view.battle', 'battle_royale.gui.Scaleform.daapi.view.battle.shared', 'messenger.gui.Scaleform.view.battle'))


def registerBRLobbyPackages():
    registerScaleformLobbyPackages(['battle_royale.gui.Scaleform.daapi.view.lobby'])


def registerBRTooltipsBuilders():
    registerBattleTooltipsBuilders([('battle_royale.gui.Scaleform.daapi.view.tooltips.royale_battle_builders', _TOOLTIPS.ROYALE_BATTLE_SET)])
    registerLobbyTooltipsBuilders([('battle_royale.gui.Scaleform.daapi.view.tooltips.royale_lobby_builders', _TOOLTIPS.ROYALE_LOBBY_SET), ('battle_royale.gui.Scaleform.daapi.view.tooltips.royale_battle_builders', _TOOLTIPS.ROYALE_BATTLE_SET)])


def registerCustomSwf():
    addBattleRequiredLibraries(['ub_components.swf'], ARENA_GUI_TYPE.BATTLE_ROYALE, 'BattleRoyalePersonality')
