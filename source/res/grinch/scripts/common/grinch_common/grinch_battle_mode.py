# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/grinch_battle_mode.py
from battle_results import grinch
from constants_utils import AbstractBattleMode
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT
from grinch_common.grinch_constants import PREBATTLE_TYPE, ARENA_GUI_TYPE, UNIT_MGR_FLAGS, ROSTER_TYPE, INVITATION_TYPE, QUEUE_TYPE, ARENA_BONUS_TYPE, GameSeasonType, Configs

class GrinchBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.GRINCH
    _QUEUE_TYPE = QUEUE_TYPE.GRINCH
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.GRINCH
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.GRINCH
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.GRINCH
    _ROSTER_TYPE = ROSTER_TYPE.GRINCH
    _INVITATION_TYPE = INVITATION_TYPE.GRINCH
    _SEASON_TYPE_BY_NAME = 'grinch'
    _SEASON_TYPE = GameSeasonType.GRINCH
    _SEASON_MANAGER_TYPE = (GameSeasonType.GRINCH, Configs.GRINCH_CONFIG.value)
    _REQUIRED_VEHICLE_TAGS = ('event_battles',)
    _FORBIDDEN_VEHICLE_TAGS = BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT
    _BATTLE_RESULTS_CONFIG = grinch
    _SM_TYPE_BATTLE_RESULT = 'grinchBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT]

    @property
    def _rosterClass(self):
        from grinch_common.grinch_roster_config import GrinchRoster
        return GrinchRoster
