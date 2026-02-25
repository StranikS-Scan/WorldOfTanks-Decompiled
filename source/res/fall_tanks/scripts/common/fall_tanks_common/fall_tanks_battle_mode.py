# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/common/fall_tanks_common/fall_tanks_battle_mode.py
from __future__ import absolute_import
from fall_tanks_constants import ARENA_GUI_TYPE
from fall_tanks_common.battle_results import fall_tanks
from fun_random_common.fun_battle_mode import FunRandomBattleMode

class FallTanksBattleMode(FunRandomBattleMode):
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.FALL_TANKS
    _BATTLE_RESULTS_CONFIG = fall_tanks
