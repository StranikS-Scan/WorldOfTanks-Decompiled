# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/player_satisfaction_rating/logging_constants.py
from enum import Enum
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.shared.denunciator import DENUNCIATIONS
FEATURE = 'battle_rating'
MIN_VIEW_TIME = 2.0
NO_MIN_VIEW_TIME = 0.0

class PlayerSatisfactionRatingLogActions(Enum):
    OPENED = 'opened'
    CLICK = 'click'
    VIEWED = 'viewed'


class PlayerSatisfactionRatingCMActions(Enum):
    NO_ACTION = 'no_action'
    UNTRACKED_ACTION = 'untracked_action'
    FRIEND_ACTION = 'friend_action'
    SEND_MESSAGE = 'send_message'
    CREATE_PLATOON = 'create_platoon'
    CREATE_UNIT = 'create_unit'
    COMPLAIN = 'complain'
    BLACKLIST = 'blacklist'
    VOICE_MESSAGES = 'voice_messages'


class PlayerSatisfactionRatingKeys(Enum):
    CONTEXT_MENU = 'context_menu'
    TEAM_SCORE_TAB = 'team_score_tab'
    TEAM_VIEW = 'team_view'
    BATTLE_GUI = 'battle_gui'
    CREATE_PLATOON = 'create_platoon'
    COMMAND_WHEEL = 'command_wheel'
    HOT_KEY = 'hot_key'
    RESPONSE = 'response'


class PlayerSatisfationRatingInviteSource(object):
    FULL_STATS_VIEW = 'full_stats_view'
    IN_BATTLE_GUI = 'in_battle_gui'


class PlayerSatisfactionRatingInfoKeys(object):
    ARENA_ID_KEY = 'arena_id'
    BATTLE_PHASE_KEY = 'battle_phase'
    PHASE_TIME_KEY = 'phase_time'
    IS_ALIVE_KEY = 'is_alive'
    PREBATTLE_ID_KEY = 'prebattle_id'


ARENA_PERIOD_TO_KEY = {0: 'idle',
 1: 'waiting',
 2: 'prebattle',
 3: 'battle',
 4: 'afterbattle'}

class PlayerSatisfactionRatingRadialMenuActions(Enum):
    NO_ACTION = 'no_action'
    UNTRACKED_ACTION = 'untracked_action'
    HELP_PROVIDE = 'help_provide'
    HELP_ASKED = 'help_asked'
    THANK_YOU = 'thank_you'
    RETREAT = 'retreat'


RADIAL_MENU_ACTIONS_TO_LOGGING_ACTIONS = {BATTLE_CHAT_COMMAND_NAMES.THANKS: PlayerSatisfactionRatingRadialMenuActions.THANK_YOU,
 BATTLE_CHAT_COMMAND_NAMES.HELPME: PlayerSatisfactionRatingRadialMenuActions.HELP_ASKED,
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK: PlayerSatisfactionRatingRadialMenuActions.RETREAT,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY: PlayerSatisfactionRatingRadialMenuActions.HELP_PROVIDE}
POST_BATTLE_CM_ACTION_TO_PLAYER_SATISFACTION_CM_ACTION = {USER.ADD_TO_FRIENDS: PlayerSatisfactionRatingCMActions.FRIEND_ACTION,
 USER.REMOVE_FROM_FRIENDS: PlayerSatisfactionRatingCMActions.FRIEND_ACTION,
 USER.REQUEST_FRIENDSHIP: PlayerSatisfactionRatingCMActions.FRIEND_ACTION,
 USER.CREATE_PRIVATE_CHANNEL: PlayerSatisfactionRatingCMActions.SEND_MESSAGE,
 USER.CREATE_SQUAD: PlayerSatisfactionRatingCMActions.CREATE_PLATOON,
 USER.INVITE: PlayerSatisfactionRatingCMActions.CREATE_UNIT,
 DENUNCIATIONS.INCORRECT_BEHAVIOR: PlayerSatisfactionRatingCMActions.COMPLAIN,
 DENUNCIATIONS.NOT_FAIR_PLAY: PlayerSatisfactionRatingCMActions.COMPLAIN,
 DENUNCIATIONS.FORBIDDEN_NICK: PlayerSatisfactionRatingCMActions.COMPLAIN,
 DENUNCIATIONS.BOT: PlayerSatisfactionRatingCMActions.COMPLAIN,
 USER.ADD_TO_IGNORED: PlayerSatisfactionRatingCMActions.BLACKLIST,
 USER.REMOVE_FROM_IGNORED: PlayerSatisfactionRatingCMActions.BLACKLIST}
