# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/battle_results/__init__.py
from __future__ import absolute_import
from account_helpers.AccountSettings import STATS_REGULAR_SORTING
from constants import ARENA_BONUS_TYPE
from gui.shared.system_factory import registerBattleResultsStatsSorting
registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.EPIC_BATTLE, STATS_REGULAR_SORTING)
