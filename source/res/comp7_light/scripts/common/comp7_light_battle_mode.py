# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/common/comp7_light_battle_mode.py
import comp7_light_constants
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from constants_utils import AbstractBattleMode
from comp7_light_common.battle_results import comp7_light

class Comp7LightBattleMode(AbstractBattleMode):
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.COMP7_LIGHT
    _QUEUE_TYPE = QUEUE_TYPE.COMP7_LIGHT
    _ARENA_GUI_TYPE = comp7_light_constants.ARENA_GUI_TYPE.COMP7_LIGHT
    _PREBATTLE_TYPE = comp7_light_constants.PREBATTLE_TYPE.COMP7_LIGHT
    _INVITATION_TYPE = comp7_light_constants.INVITATION_TYPE.COMP7_LIGHT
    _UNIT_MGR_NAME = 'Comp7LightUnitMgr'
    _UNIT_MGR_FLAGS = comp7_light_constants.UNIT_MGR_FLAGS.COMP7_LIGHT
    _ROSTER_TYPE = comp7_light_constants.ROSTER_TYPE.COMP7_LIGHT_ROSTER
    _BATTLE_RESULTS_CONFIG = comp7_light
    _SEASON_TYPE_BY_NAME = 'comp7_light'
    _SEASON_TYPE = comp7_light_constants.GameSeasonType.COMP7_LIGHT
    _SEASON_MANAGER_TYPE = (comp7_light_constants.GameSeasonType.COMP7_LIGHT, 'comp7_light_config')
    _SM_TYPE_BATTLE_RESULT = 'comp7LightBattleResults'
    _SM_TYPE_PROGRESSION = 'comp7LightProgressionNotification'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT, _SM_TYPE_PROGRESSION]

    @property
    def _rosterClass(self):
        from unit_roster_config import Comp7LightRoster
        return Comp7LightRoster
