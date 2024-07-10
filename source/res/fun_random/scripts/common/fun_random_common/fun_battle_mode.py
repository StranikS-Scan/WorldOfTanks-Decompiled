# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/common/fun_random_common/fun_battle_mode.py
from battle_results import fun_random
from constants import PREBATTLE_TYPE, ARENA_BONUS_TYPE, QUEUE_TYPE
from constants_utils import AbstractBattleMode
from fun_random_common.fun_constants import ARENA_GUI_TYPE, UNIT_MGR_FLAGS, ROSTER_TYPE, INVITATION_TYPE

class FunRandomBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.FUN_RANDOM
    _QUEUE_TYPE = QUEUE_TYPE.FUN_RANDOM
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.FUN_RANDOM
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.FUN_RANDOM
    _INVITATION_TYPE = INVITATION_TYPE.FUN_RANDOM
    _UNIT_MGR_NAME = 'FunRandomUnitMgr'
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.FUN_RANDOM
    _ROSTER_TYPE = ROSTER_TYPE.FUN_RANDOM_ROSTER
    _BATTLE_RESULTS_CONFIG = fun_random

    @property
    def _rosterClass(self):
        from fun_random_common.fun_roster_config import FunRandomRoster
        return FunRandomRoster
