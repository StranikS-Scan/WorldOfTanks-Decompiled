# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_constants.py
import UnitBase
import constants
from constants_utils import ConstInjector, AbstractBattleMode
from battle_results import white_tiger

class ARENA_GUI_TYPE(constants.ARENA_GUI_TYPE, ConstInjector):
    WHITE_TIGER = 301


class ARENA_BONUS_TYPE(constants.ARENA_BONUS_TYPE, ConstInjector):
    WHITE_TIGER = 52
    WHITE_TIGER_2 = 53
    WT_BATTLES_RANGE = (WHITE_TIGER, WHITE_TIGER_2)


class PREBATTLE_TYPE(constants.PREBATTLE_TYPE, ConstInjector):
    WHITE_TIGER = 301


class QUEUE_TYPE(constants.QUEUE_TYPE, ConstInjector):
    WHITE_TIGER = 301


class GameSeasonType(constants.GameSeasonType, ConstInjector):
    WHITE_TIGER = 9


class UNIT_MGR_FLAGS(UnitBase.UNIT_MGR_FLAGS, ConstInjector):
    WHITE_TIGER = 2097152


class ROSTER_TYPE(UnitBase.ROSTER_TYPE, ConstInjector):
    WHITE_TIGER = UNIT_MGR_FLAGS.SQUAD | UNIT_MGR_FLAGS.WHITE_TIGER


class INVITATION_TYPE(UnitBase.INVITATION_TYPE, ConstInjector):
    WHITE_TIGER = PREBATTLE_TYPE.WHITE_TIGER


class WT_COMPONENT_NAMES(object):
    SHIELD_DEBUFF_ARENA_TIMER = 'wtShieldDebuffDuration'
    ACTIVATION_ARENA_TIMER = 'activationTimer'
    GENERATORS_COUNTER = 'wtCapturesTillEndgame'
    HYPERION_COUNTER = 'wtHyperionCharge'


class WT_TAGS(object):
    WT_BOSS = 'event_boss'
    WT_BOT = 'wt_bot'
    WT_HUNTER = 'event_hunter'
    WT_SPECIAL_BOSS = 'special_event_boss'


class WT_BATTLE_STAGE(object):
    INVINCIBLE = 0
    DEBUFF = 1
    END_GAME = 2

    @staticmethod
    def getCurrent(arenaInfo):
        if WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER in arenaInfo.dynamicComponents:
            return WT_BATTLE_STAGE.DEBUFF
        else:
            generatorsCounterComponent = arenaInfo.dynamicComponents.get(WT_COMPONENT_NAMES.GENERATORS_COUNTER)
            return WT_BATTLE_STAGE.END_GAME if generatorsCounterComponent is not None and generatorsCounterComponent.counter == 0 else WT_BATTLE_STAGE.INVINCIBLE


class WT_TEAMS(object):
    BOSS_TEAM = 1
    HUNTERS_TEAM = 2


WHITE_TIGER_GAME_PARAMS_KEY = 'white_tiger_config'

class WhiteTigerBattleMode(AbstractBattleMode):
    _PREBATTLE_TYPE = PREBATTLE_TYPE.WHITE_TIGER
    _QUEUE_TYPE = QUEUE_TYPE.WHITE_TIGER
    _ARENA_BONUS_TYPE = ARENA_BONUS_TYPE.WHITE_TIGER
    _ARENA_GUI_TYPE = ARENA_GUI_TYPE.WHITE_TIGER
    _UNIT_MGR_FLAGS = UNIT_MGR_FLAGS.WHITE_TIGER
    _ROSTER_TYPE = ROSTER_TYPE.WHITE_TIGER
    _INVITATION_TYPE = INVITATION_TYPE.WHITE_TIGER
    _BATTLE_MGR_NAME = 'WhiteTigerBattlesMgr'
    _GAME_PARAMS_KEY = WHITE_TIGER_GAME_PARAMS_KEY
    _SEASON_TYPE_BY_NAME = 'white_tiger_battle'
    _SEASON_TYPE = GameSeasonType.WHITE_TIGER
    _SEASON_MANAGER_TYPE = (GameSeasonType.WHITE_TIGER, WHITE_TIGER_GAME_PARAMS_KEY)
    _BATTLE_RESULTS_CONFIG = white_tiger
    _SM_TYPE_BATTLE_RESULT = 'whiteTigerBattleResults'
    _SM_TYPES = [_SM_TYPE_BATTLE_RESULT, 'wtEventTicketTokenWithdrawn']

    @property
    def _ROSTER_CLASS(self):
        from white_tiger_common.wt_roster_config import WhiteTigerRoster
        return WhiteTigerRoster


WHITE_TIGER_ACC_SETTINGS_KEY = 'white_tiger_key'
WHITE_TIGER_INTRO_VIEWED = 'white_tiger_intro_viewed'
WHITE_TIGER_OUTRO_VIDEO_VIEWED = 'white_tiger_outro_video_viewed'
ACCOUNT_DEFAULT_SETTINGS = {WHITE_TIGER_ACC_SETTINGS_KEY: {WHITE_TIGER_INTRO_VIEWED: False,
                                WHITE_TIGER_OUTRO_VIDEO_VIEWED: False}}
