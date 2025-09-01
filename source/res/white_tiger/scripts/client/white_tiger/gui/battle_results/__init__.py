# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_results/__init__.py
from white_tiger_common.wt_constants import ARENA_BONUS_TYPE
from account_helpers.AccountSettings import STATS_REGULAR_SORTING
from gui.shared.system_factory import registerBattleResultsStatsSorting
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.WHITE_TIGER, STATS_REGULAR_SORTING)
