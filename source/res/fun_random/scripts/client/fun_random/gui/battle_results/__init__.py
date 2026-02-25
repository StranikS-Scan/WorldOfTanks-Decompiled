# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/__init__.py
from __future__ import absolute_import
from fun_random_common.fun_constants import ARENA_BONUS_TYPE, FunSubModeImpl
from fun_random.gui.battle_results.fun_battle_results_sub_presenter import FunBattleResultsSubPresenter
from fun_random.gui.shared.fun_system_factory import registerBattleResultsSubPresenter
from account_helpers.AccountSettings import STATS_FUN_RANDOM_SORTING
from gui.shared.system_factory import registerBattleResultsStatsSorting
from gui.impl.gen import R
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.FUN_RANDOM, STATS_FUN_RANDOM_SORTING)
registerBattleResultsSubPresenter(FunSubModeImpl.DEFAULT, FunBattleResultsSubPresenter, R.views.fun_random.mono.lobby.battle_results())
