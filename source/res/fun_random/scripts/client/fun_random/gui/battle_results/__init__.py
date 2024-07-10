# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/__init__.py
from constants import ARENA_BONUS_TYPE
from account_helpers.AccountSettings import STATS_FUN_RANDOM_SORTING
from gui.shared.system_factory import registerBattleResultsStatsSorting
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.FUN_RANDOM, STATS_FUN_RANDOM_SORTING)
