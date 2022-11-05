# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_control/__init__.py
from constants import ARENA_GUI_TYPE
from fun_random.gui.battle_control.arena_info.arena_descrs import FunRandomArenaDescription
from fun_random.gui.battle_control.controllers.repository import FunRandomControllerRepository
from fun_random.gui.ingame_help.fun_random_pages import FunRandomHelpPagesBuilder
from fun_random.helpers.tips import FunRandomTipsCriteria
from gui.battle_control.arena_info.squad_finder import TeamScopeNumberingFinder
from gui.shared.system_factory import registerBattleControllerRepo, registerArenaDescription, registerArenaSquadFinder, registerBattleTipCriteria, registerIngameHelpPagesBuilder

def registerFunRandomBattle():
    registerBattleControllerRepo(ARENA_GUI_TYPE.FUN_RANDOM, FunRandomControllerRepository)
    registerBattleTipCriteria(ARENA_GUI_TYPE.FUN_RANDOM, FunRandomTipsCriteria)
    registerArenaDescription(ARENA_GUI_TYPE.FUN_RANDOM, FunRandomArenaDescription)
    registerArenaSquadFinder(ARENA_GUI_TYPE.FUN_RANDOM, TeamScopeNumberingFinder)
    registerIngameHelpPagesBuilder(FunRandomHelpPagesBuilder)
