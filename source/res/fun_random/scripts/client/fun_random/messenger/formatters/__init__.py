# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/messenger/formatters/__init__.py
from fun_random_common.fun_constants import ARENA_GUI_TYPE
from fun_random.gui.shared.fun_system_factory import registerBattleResultsMessageSubFormatter
from fun_random.messenger.formatters.battle_results_formatters import FunRandomBattleResultsSubFormatter
registerBattleResultsMessageSubFormatter(ARENA_GUI_TYPE.FUN_RANDOM, FunRandomBattleResultsSubFormatter)
