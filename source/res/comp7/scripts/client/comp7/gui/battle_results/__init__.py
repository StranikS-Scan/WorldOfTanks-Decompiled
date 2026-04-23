# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_results/__init__.py
from constants import ARENA_BONUS_TYPE
from account_helpers.AccountSettings import STATS_COMP7_SORTING, STATS_COMP7_SPECIAL_SORTING
from gui.shared.system_factory import registerBattleResultsStatsSorting
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.COMP7, STATS_COMP7_SORTING)
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.TRAINING_COMP7, STATS_COMP7_SPECIAL_SORTING)
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.TOURNAMENT_COMP7, STATS_COMP7_SPECIAL_SORTING)
