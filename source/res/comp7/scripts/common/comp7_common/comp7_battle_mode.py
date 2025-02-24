# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/common/comp7_common/comp7_battle_mode.py
from comp7_common import comp7_constants
from comp7_common.comp7_battle_results import comp7
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from constants_utils import AbstractBattleMode, addBattleResultsConfig

class Comp7BattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = comp7_constants.PREBATTLE_TYPE.COMP7
    _QUEUE_TYPE = QUEUE_TYPE.COMP7
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.COMP7
    _ARENA_GUI_TYPE = comp7_constants.ARENA_GUI_TYPE.COMP7
    _INVITATION_TYPE = comp7_constants.INVITATION_TYPE.COMP7
    _UNIT_MGR_NAME = 'Comp7UnitMgr'
    _UNIT_MGR_FLAGS = comp7_constants.UNIT_MGR_FLAGS.COMP7
    _ROSTER_TYPE = comp7_constants.ROSTER_TYPE.COMP7_ROSTER
    _BATTLE_RESULTS_CONFIG = comp7
    _SEASON_TYPE_BY_NAME = 'comp7'
    _SEASON_TYPE = comp7_constants.GameSeasonType.COMP7
    _SEASON_MANAGER_TYPE = (comp7_constants.GameSeasonType.COMP7, 'comp7_config')

    def registerAdditionalBattleResultsConfig(self):
        if self._BATTLE_RESULTS_CONFIG is not None:
            for arenaBonusType in (ARENA_BONUS_TYPE.TOURNAMENT_COMP7, ARENA_BONUS_TYPE.TRAINING_COMP7):
                addBattleResultsConfig(arenaBonusType, self._BATTLE_RESULTS_CONFIG)

        return

    @property
    def _rosterClass(self):
        from unit_roster_config import Comp7Roster
        return Comp7Roster
