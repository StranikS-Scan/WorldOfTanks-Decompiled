# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/messenger_common_chat2.py
from collections import namedtuple
from string import Template
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, CHAT_COMMANDS_THAT_IGNORE_COOLDOWNS
from constants import IS_CLIENT, IS_CHINA, ARENA_BONUS_TYPE
_g_id = None

def _makeID(start=None, range=None):
    global _g_id
    id = _g_id = _g_id + 1 if start is None else start
    if range is not None:
        _g_id += range
    return id


_COOLDOWN_OFFSET = 0.0 if IS_CLIENT else -0.1
_INITIAL_DEFAULT_BATTLE_CHAT_COOLDOWN_DURATION = 0.1
_SHORT_BATTLE_CHAT_COOLDOWN_DURATION = 0.0
_TEAM_BATTLE_CHAT_CMD_COOLDOWN_DURATION = 6.0
_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION = 5.0
_SAME_PRIVATE_BATTLE_CHAT_CMD_COOLDOWN_DURATION = 2.0
_OTHER_BATTLE_CHAT_CMD_COOLDOWN_DURATION = 1.0
_ATTENTION_TO_COMMAND_COOLDOWN_DURATION = 0.2
_SAME_TARGET_PERSONAL_BATTLE_CHAT_CMD_COOLDOWN_DURATION = 3.0
_REACTIONAL_CHAT_CMD_COOLDOWN_DURATION = 0.1
_MAX_ATTENTION_TO_CHAT_COMMANDS_WITHIN_TIMEFRAME = 3
_TIMEFRAME_FOR_ATTENTION_TO_STORAGE = 5
_MAX_ATTENTION_TO_PER_TEAM = 3

def messageArgs(int32Arg1=0, int64Arg1=0, floatArg1=0, strArg1='', strArg2=''):
    return {'int32Arg1': int32Arg1,
     'int64Arg1': int64Arg1,
     'floatArg1': floatArg1,
     'strArg1': strArg1,
     'strArg2': strArg2}


EMPTY_ARGS = messageArgs()

class MESSENGER_ERRORS():
    NO_ERROR = _makeID(start=0)
    GENERIC_ERROR = _makeID()
    NOT_READY = _makeID()
    IN_COOLDOWN = _makeID()
    COMMAND_IN_TEAM_COOLDOWN = _makeID()
    IN_CHAT_BAN = _makeID()
    IS_BUSY = _makeID()
    NOT_ALLOWED = _makeID()
    WRONG_ARGS = _makeID()
    USER_NOT_FOUND = _makeID()
    CANNOT_BAN_ONESELF = _makeID()
    CUSTOM_ERROR_ID = _makeID()

    @staticmethod
    def getErrorName(errorCode):
        name = _MESSENGER_ERROR_NAMES.get(errorCode)
        return name if name is not None else 'ERROR_CODE_' + str(errorCode)


class MESSENGER_LIMITS():
    FIND_USERS_BY_NAME_MAX_RESULT_SIZE = 50
    FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC = 5.0 + _COOLDOWN_OFFSET
    BATTLE_CHANNEL_MESSAGE_MAX_SIZE = 140
    UNIT_CHANNEL_MESSAGE_MAX_SIZE = 512
    BATTLE_CHAT_HISTORY_ON_SERVER_MAX_LEN = 10
    UNIT_CHAT_HISTORY_ON_SERVER_MAX_LEN = 20
    BROADCASTS_FROM_CLIENT_COOLDOWN_SEC = (0.5 if not IS_CHINA else 3.0) + _COOLDOWN_OFFSET
    ADMIN_COMMANDS_FROM_CLIENT_COOLDOWN_SEC = 5.0 + _COOLDOWN_OFFSET
    VOIP_CREDENTIALS_REQUEST_COOLDOWN_SEC = 10.0 + _COOLDOWN_OFFSET


class MESSENGER_ACTION_IDS():
    RESPONSE_SUCCESS = _makeID(start=0)
    RESPONSE_FAILURE = _makeID()
    FIND_USERS_BY_NAME = _makeID()
    GET_VOIP_CREDENTIALS = _makeID()
    LOG_VIVOX_LOGIN = _makeID()
    ENTER_VOIP_CHANNEL = _makeID()
    LEAVE_VOIP_CHANNEL = _makeID()
    _ADMIN_COMMAND_START_ID = _makeID(range=10)
    _BATTLE_ACTION_START_ID = _makeID()
    INIT_BATTLE_CHAT = _makeID()
    REINIT_BATTLE_CHAT = _makeID()
    DEINIT_BATTLE_CHAT = _makeID()
    BROADCAST_BATTLE_MESSAGE = _makeID()
    ON_BATTLE_MESSAGE_BROADCAST = _makeID()
    _BATTLE_CHAT_COMMAND_START_ID = _makeID(range=100)
    _BATTLE_ACTION_END_ID = _makeID()
    _UNIT_ACTION_START_ID = _makeID()
    INIT_UNIT_CHAT = _makeID()
    DEINIT_UNIT_CHAT = _makeID()
    BROADCAST_UNIT_MESSAGE = _makeID()
    ON_UNIT_MESSAGE_BROADCAST = _makeID()
    _UNIT_COMMAND_START_ID = _makeID(range=100)
    _UNIT_ACTION_END_ID = _makeID()
    CUSTOM_ACTION_ID = _makeID()

    @staticmethod
    def getActionName(actionID):
        name = _MESSENGER_ACTION_NAMES.get(actionID)
        if name is not None:
            return name
        else:
            actions = MESSENGER_ACTION_IDS
            cmd = actions.adminChatCommandFromActionID(actionID)
            if cmd is not None:
                return 'command:' + cmd.name
            cmd = actions.battleChatCommandFromActionID(actionID)
            if cmd is not None:
                return 'command:' + cmd.name
            offs = actionID - actions.CUSTOM_ACTION_ID
            return 'CUSTOM_ACTION_ID+' + str(offs) if offs >= 0 else str(actionID)

    @staticmethod
    def isBattleChatAction(actionID):
        actions = MESSENGER_ACTION_IDS
        return actions._BATTLE_ACTION_START_ID <= actionID <= actions._BATTLE_ACTION_END_ID

    @staticmethod
    def isUnitChatAction(actionID):
        actions = MESSENGER_ACTION_IDS
        return actions._UNIT_ACTION_START_ID <= actionID <= actions._UNIT_ACTION_END_ID

    @staticmethod
    def isRateLimitedBroadcastFromClient(actionID):
        actions = MESSENGER_ACTION_IDS
        if actionID == actions.BROADCAST_BATTLE_MESSAGE or actionID == actions.BROADCAST_UNIT_MESSAGE:
            return True
        battleChatCmdStartID = actions._BATTLE_CHAT_COMMAND_START_ID
        if battleChatCmdStartID <= actionID < battleChatCmdStartID + len(BATTLE_CHAT_COMMANDS):
            cmdName = actions.battleChatCommandFromActionID(actionID).name
            if cmdName == BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION or cmdName in CHAT_COMMANDS_THAT_IGNORE_COOLDOWNS:
                return False
            return True
        return False

    @staticmethod
    def isChatActionSusceptibleToBan(actionID):
        actions = MESSENGER_ACTION_IDS
        if actions.adminChatCommandFromActionID(actionID) is not None:
            return True
        elif actions.isBattleChatAction(actionID):
            return actions.battleChatCommandFromActionID(actionID) is None
        else:
            return True if actions.isUnitChatAction(actionID) else False

    @staticmethod
    def battleChatCommandFromActionID(actionID):
        startID = MESSENGER_ACTION_IDS._BATTLE_CHAT_COMMAND_START_ID
        return BATTLE_CHAT_COMMANDS[actionID - startID] if startID <= actionID < startID + len(BATTLE_CHAT_COMMANDS) else None

    @staticmethod
    def unitChatCommandFromActionID(actionID):
        startID = MESSENGER_ACTION_IDS._UNIT_COMMAND_START_ID
        return UNIT_CHAT_COMMANDS[actionID - startID] if startID <= actionID < startID + len(UNIT_CHAT_COMMANDS) else None

    @staticmethod
    def adminChatCommandFromActionID(actionID):
        startID = MESSENGER_ACTION_IDS._ADMIN_COMMAND_START_ID
        return ADMIN_CHAT_COMMANDS[actionID - startID] if startID <= actionID < startID + len(ADMIN_CHAT_COMMANDS) else None


class CHAT_COMMAND_COOLDOWN_TYPE_IDS():
    TIMEFRAME_DATA_COOLDOWN = _makeID()
    SAME_COMMAND_COOLDOWN = _makeID()
    OTHER_COMMANDS_COOLDOWN = _makeID()
    PRIVATE_COMMANDS_COOLDOWN = _makeID()
    ATTENTION_TO_BLOCKED_COOLDOWN = _makeID()


_MESSENGER_ACTION_NAMES = {_id:_name for _name, _id in MESSENGER_ACTION_IDS.__dict__.iteritems() if isinstance(_id, int) and not _name.startswith('_')}
_MESSENGER_ERROR_NAMES = {_id:_name for _name, _id in MESSENGER_ERRORS.__dict__.iteritems() if not _name.startswith('_')}
AdminChatCommand = namedtuple('AdminChatCommand', ('id', 'name', 'timeout'))
ADMIN_CHAT_COMMANDS = (AdminChatCommand(id=_makeID(start=MESSENGER_ACTION_IDS._ADMIN_COMMAND_START_ID), name='USERBAN', timeout=30.0), AdminChatCommand(id=_makeID(), name='USERUNBAN', timeout=30.0))
ADMIN_CHAT_COMMANDS_BY_NAMES = {v.name:v for v in ADMIN_CHAT_COMMANDS}
BattleChatCommand = namedtuple('BattleChatCommand', ('id',
 'name',
 'cooldownPeriod',
 'msgText',
 'vehMarker',
 'senderVehMarker',
 'soundNotification',
 'msgOnMarker',
 'soundNotificationReply'))
BattleChatCommand.__new__.__defaults__ = (0,
 None,
 0,
 None,
 None,
 None,
 None)
UnitChatCommand = namedtuple('UnitChatCommand', ('id',
 'name',
 'cooldownPeriod',
 'msgText'))
UNIT_CHAT_COMMANDS = (UnitChatCommand(id=_makeID(start=MESSENGER_ACTION_IDS._UNIT_COMMAND_START_ID), name='ATTENTIONTOCELL', cooldownPeriod=1.0 + _COOLDOWN_OFFSET, msgText='attention_to_cell'),)
UNIT_CHAT_COMMANDS_BY_NAMES = {v.name:v for v in UNIT_CHAT_COMMANDS}
BATTLE_CHAT_COMMANDS = (BattleChatCommand(id=_makeID(start=MESSENGER_ACTION_IDS._BATTLE_CHAT_COMMAND_START_ID), name=BATTLE_CHAT_COMMAND_NAMES.SOS, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='help_me', vehMarker='help_me', senderVehMarker=None, soundNotification='ibc_ping_request', soundNotificationReply='ibc_ping_help_me_ex_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.POSITIVE, cooldownPeriod=_SAME_PRIVATE_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='positive', vehMarker='positive', senderVehMarker=None, soundNotification='ibc_ping_affirmative', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.NEGATIVE, cooldownPeriod=_SAME_PRIVATE_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='negative', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.AFFIRMATIVE, cooldownPeriod=_SAME_PRIVATE_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='affirmative', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name='ATTENTIONTOCELL', cooldownPeriod=_SHORT_BATTLE_CHAT_COOLDOWN_DURATION + _COOLDOWN_OFFSET, msgText='attention_to_cell', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION, cooldownPeriod=_ATTENTION_TO_COMMAND_COOLDOWN_DURATION, msgText='attention_to_position', vehMarker='attention_to', senderVehMarker=None, soundNotification='ibc_ping_attention', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.REPLY, cooldownPeriod=_REACTIONAL_CHAT_CMD_COOLDOWN_DURATION, msgText=None, vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY, cooldownPeriod=_REACTIONAL_CHAT_CMD_COOLDOWN_DURATION, msgText=None, vehMarker=None, senderVehMarker=None, soundNotification='ibc_ping_cancel', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attention_to_objective_atk', vehMarker='attackObjective', senderVehMarker=None, soundNotification='ibc_ping_request', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attention_to_objective_atk_autocommit', vehMarker='attackingObjective', senderVehMarker=None, soundNotification='ibc_ping_action', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attention_to_objective_def', vehMarker='defendObjective', senderVehMarker=None, soundNotification='ibc_ping_request', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attention_to_objective_def_autocommit', vehMarker='defendingObjective', senderVehMarker=None, soundNotification='ibc_ping_request', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attention_to_base_atk', vehMarker='attackBase', senderVehMarker=None, soundNotification='ibc_ping_request', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attention_to_base_def', vehMarker='defendBase', senderVehMarker=None, soundNotification='ibc_ping_request', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='spg_aim_area', vehMarker=None, senderVehMarker=None, soundNotification='ibc_ping_attention', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY_WITH_SPG, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attack_enemy_with_SPG', vehMarker='attack', senderVehMarker='attackSender', soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.TURNBACK, cooldownPeriod=_SAME_PRIVATE_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='turn_back', vehMarker='turn_back', senderVehMarker=None, soundNotification='ibc_ping_retreat', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.HELPME, cooldownPeriod=_SAME_PRIVATE_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='help_me_ex', vehMarker='help_me_ex', senderVehMarker=None, soundNotification='ibc_ping_help_me_ex', soundNotificationReply='ibc_ping_help_me_ex_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attack_enemy', vehMarker='attack', senderVehMarker='attackSender', soundNotification='ibc_ping_request', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='reloading_gun', vehMarker='reloading_gun', senderVehMarker=None, soundNotification='ibc_ping_attention', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.THANKS, cooldownPeriod=_SAME_PRIVATE_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='thanks', vehMarker='thanks', senderVehMarker=None, soundNotification='ibc_ping_thanks', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.RELOADING_CASSETE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='reloading_cassette', vehMarker='reloading_gun', senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='reloading_ready', vehMarker=None, senderVehMarker=None, soundNotification='ibc_ping_attention', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.RELOADING_READY_CASSETE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='reloading_ready_cassette', vehMarker=None, senderVehMarker=None, soundNotification='ibc_ping_attention', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.RELOADING_UNAVAILABLE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='reloading_unavailable', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_SAVE_TANKS_ATK, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/atk/save_tanks', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.GOING_THERE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='going_there', vehMarker='goingTo', senderVehMarker=None, soundNotification='ibc_ping_action', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_SAVE_TANKS_DEF, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/def/save_tanks', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_TIME_ATK, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/atk/time', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_TIME_DEF, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/def/time', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_HQ_ATK, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/atk/focus_hq', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_HQ_DEF, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/def/focus_hq', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_WEST, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/lane/west', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_CENTER, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/lane/center', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.EPIC_GLOBAL_EAST, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='global_msg/lane/east', vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.CLEAR_CHAT_COMMANDS, cooldownPeriod=_REACTIONAL_CHAT_CMD_COOLDOWN_DURATION, msgText=None, vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attacking_enemy', vehMarker='attack', senderVehMarker='attackSender', soundNotification='ibc_ping_action', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='supporting_ally', vehMarker='supportingAlly', senderVehMarker=None, soundNotification='ibc_ping_help_me_ex_reply', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='defending_base', vehMarker='defendingBase', senderVehMarker=None, soundNotification='ibc_ping_action', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='attacking_base', vehMarker='attackingBase', senderVehMarker=None, soundNotification='ibc_ping_action', soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText='going_there', vehMarker='goingTo', senderVehMarker=None, soundNotification=None, soundNotificationReply='ibc_ping_reply'),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.CONFIRM, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText=None, vehMarker='positive', senderVehMarker=None, soundNotification='ibc_ping_attention', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.VEHICLE_SPOTPOINT, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText=None, vehMarker=None, senderVehMarker=None, soundNotification=None, soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText=None, vehMarker=None, senderVehMarker=None, soundNotification='mt_combat_marker', soundNotificationReply=None),
 BattleChatCommand(id=_makeID(), name=BATTLE_CHAT_COMMAND_NAMES.NAVIGATION_POINT, cooldownPeriod=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, msgText=None, vehMarker=None, senderVehMarker=None, soundNotification='mt_navi_marker', soundNotificationReply=None))
BATTLE_CHAT_COMMANDS_BY_NAMES = {v.name:v for v in BATTLE_CHAT_COMMANDS}

class MUC_SERVICE_TYPE(object):
    STANDARD = 1
    USER = 2
    CLAN = 3


MUC_SERVICE_TYPES = frozenset((MUC_SERVICE_TYPE.CLAN, MUC_SERVICE_TYPE.STANDARD, MUC_SERVICE_TYPE.USER))

def resolveMucRoomsOfService(service):
    t = Template(service['format'])
    return t.substitute(service)


def canResolveMucRoomsOfService(service):
    canResolve = False
    try:
        Template(service['format']).substitute(service)
        canResolve = True
    except:
        pass

    return canResolve


ChatCommandBlockedData = namedtuple('ChatCommandBlockedData', ('reqID',
 'cmdID',
 'cooldownType',
 'cooldownEnd',
 'targetID'))
BattleChatCmdGameModeCoolDownData = namedtuple('BattleChatCmdGameModeCoolDownData', ('teamChatCmdCooldown',
 'sameChatCmdCooldown',
 'sameTargetChatCmdCooldown',
 'otherChatCmdCooldown',
 'attentionToTeamLimit',
 'attentionToTimeframeLimit'))
SPAM_PROTECTION_SETTING = BattleChatCmdGameModeCoolDownData(teamChatCmdCooldown=_TEAM_BATTLE_CHAT_CMD_COOLDOWN_DURATION, sameChatCmdCooldown=_SAME_BATTLE_CHAT_CMD_COOLDOWN_DURATION, sameTargetChatCmdCooldown=_SAME_TARGET_PERSONAL_BATTLE_CHAT_CMD_COOLDOWN_DURATION, otherChatCmdCooldown=_OTHER_BATTLE_CHAT_CMD_COOLDOWN_DURATION, attentionToTeamLimit=_MAX_ATTENTION_TO_PER_TEAM, attentionToTimeframeLimit=_MAX_ATTENTION_TO_CHAT_COMMANDS_WITHIN_TIMEFRAME)
BATTLE_CMD_COOLDOWN_ALLOWED_MARGIN = 0.1

def getCooldownGameModeDataForGameMode(gameMode):
    if ARENA_BONUS_TYPE_CAPS.checkAny(gameMode, ARENA_BONUS_TYPE_CAPS.SPAM_PROTECTION):
        return SPAM_PROTECTION_SETTING
    else:
        return None
        return None


def areSenderCooldownsActive(currTime, listOfCoolDownTimeData, cmdIDToSend, targetIDToSend):
    if listOfCoolDownTimeData is None:
        return listOfCoolDownTimeData
    else:
        removeDataList = list()
        blockReasonData = None
        for cmdBlockedData in listOfCoolDownTimeData:
            if round(cmdBlockedData.cooldownEnd - currTime, 2) <= BATTLE_CMD_COOLDOWN_ALLOWED_MARGIN:
                removeDataList.append(cmdBlockedData)
            validBlockData = None
            if cmdBlockedData.cooldownType == CHAT_COMMAND_COOLDOWN_TYPE_IDS.SAME_COMMAND_COOLDOWN and cmdBlockedData.cmdID == cmdIDToSend:
                validBlockData = cmdBlockedData
            elif cmdBlockedData.cooldownType == CHAT_COMMAND_COOLDOWN_TYPE_IDS.OTHER_COMMANDS_COOLDOWN and cmdBlockedData.cmdID != cmdIDToSend:
                validBlockData = cmdBlockedData
            elif cmdBlockedData.cooldownType == CHAT_COMMAND_COOLDOWN_TYPE_IDS.PRIVATE_COMMANDS_COOLDOWN and cmdBlockedData.targetID == targetIDToSend:
                validBlockData = cmdBlockedData
            elif cmdBlockedData.cooldownType == CHAT_COMMAND_COOLDOWN_TYPE_IDS.ATTENTION_TO_BLOCKED_COOLDOWN and cmdBlockedData.cmdID == cmdIDToSend:
                validBlockData = cmdBlockedData
            if cmdBlockedData.cooldownType != CHAT_COMMAND_COOLDOWN_TYPE_IDS.TIMEFRAME_DATA_COOLDOWN and validBlockData is not None:
                blockReasonData = validBlockData

        if removeDataList:
            for cdData in removeDataList:
                if cdData in listOfCoolDownTimeData:
                    listOfCoolDownTimeData.remove(cdData)

        return blockReasonData


def addCoolDowns(currTime, listOfCoolDownTimeData, cmdID, cmdName, cmdCooldownTime, cmdTargetID, reqID, cooldownConf):
    listOfCoolDownTimeData.append(ChatCommandBlockedData(reqID=reqID, cmdID=cmdID, cooldownType=CHAT_COMMAND_COOLDOWN_TYPE_IDS.SAME_COMMAND_COOLDOWN, cooldownEnd=currTime + cmdCooldownTime, targetID=cmdTargetID))
    listOfCoolDownTimeData.append(ChatCommandBlockedData(reqID=reqID, cmdID=cmdID, cooldownType=CHAT_COMMAND_COOLDOWN_TYPE_IDS.OTHER_COMMANDS_COOLDOWN, cooldownEnd=currTime + cooldownConf.otherChatCmdCooldown, targetID=cmdTargetID))
    if cmdName in (BATTLE_CHAT_COMMAND_NAMES.HELPME, BATTLE_CHAT_COMMAND_NAMES.THANKS, BATTLE_CHAT_COMMAND_NAMES.TURNBACK):
        listOfCoolDownTimeData.append(ChatCommandBlockedData(reqID=reqID, cmdID=cmdID, cooldownType=CHAT_COMMAND_COOLDOWN_TYPE_IDS.PRIVATE_COMMANDS_COOLDOWN, cooldownEnd=currTime + cooldownConf.sameTargetChatCmdCooldown, targetID=cmdTargetID))
    if cmdName == BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION:
        activeOldAttComands = [ blockData for blockData in listOfCoolDownTimeData if blockData.cmdID == cmdID and blockData.cooldownType == CHAT_COMMAND_COOLDOWN_TYPE_IDS.TIMEFRAME_DATA_COOLDOWN ]
        if activeOldAttComands and len(activeOldAttComands) >= cooldownConf.attentionToTimeframeLimit - 1:
            data = ChatCommandBlockedData(reqID=reqID, cmdID=cmdID, cooldownType=CHAT_COMMAND_COOLDOWN_TYPE_IDS.ATTENTION_TO_BLOCKED_COOLDOWN, cooldownEnd=currTime + cooldownConf.sameChatCmdCooldown, targetID=cmdTargetID)
        else:
            data = ChatCommandBlockedData(reqID=reqID, cmdID=cmdID, cooldownType=CHAT_COMMAND_COOLDOWN_TYPE_IDS.TIMEFRAME_DATA_COOLDOWN, cooldownEnd=currTime + _TIMEFRAME_FOR_ATTENTION_TO_STORAGE, targetID=cmdTargetID)
        listOfCoolDownTimeData.append(data)
