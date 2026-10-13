# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_results/__init__.py
from __future__ import absolute_import
from account_helpers.AccountSettings import STATS_REGULAR_SORTING
from fort_rush_common.fort_rush_constants import ARENA_BONUS_TYPE
from gui.shared.system_factory import registerBattleResultsStatsSorting

def registerFortRushBattleResultsStatsSorting():
    registerBattleResultsStatsSorting(ARENA_BONUS_TYPE.FORT_RUSH, STATS_REGULAR_SORTING)
