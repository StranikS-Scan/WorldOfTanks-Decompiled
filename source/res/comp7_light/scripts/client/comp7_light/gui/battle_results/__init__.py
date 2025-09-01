# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_results/__init__.py
from constants import ARENA_BONUS_TYPE
from account_helpers.AccountSettings import STATS_COMP7_SORTING
from gui.shared.system_factory import registerBattleResultsStatsSorting
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.COMP7_LIGHT, STATS_COMP7_SORTING)
