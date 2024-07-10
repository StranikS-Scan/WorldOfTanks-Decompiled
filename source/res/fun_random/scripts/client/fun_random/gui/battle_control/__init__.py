# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_control/__init__.py
from fun_random_common.fun_constants import ARENA_GUI_TYPE
from fun_random.gui.ingame_help.fun_random_pages import FunRandomHelpPagesBuilder
from fun_random.helpers.tips import FunRandomTipsCriteria
from gui.shared.system_factory import registerBattleTipCriteria, registerIngameHelpPagesBuilder

def registerFunRandomBattle():
    registerBattleTipCriteria(ARENA_GUI_TYPE.FUN_RANDOM, FunRandomTipsCriteria)
    registerIngameHelpPagesBuilder(FunRandomHelpPagesBuilder)
