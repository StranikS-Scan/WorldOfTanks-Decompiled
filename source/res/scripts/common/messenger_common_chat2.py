# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/messenger_common_chat2.py
from collections import namedtuple
from constants import IS_CLIENT, IS_CHINA
from string import Template
_g_id = None

def _makeID(start=None, range=None):
    global _g_id
    id = _g_id = _g_id + 1 if start is None else start
    if range is not None:
        _g_id += range
    return id


_COOLDOWN_OFFSET = 0.0 if IS_CLIENT else -0.1

def messageArgs(int32Arg1=0, int64Arg1=0, floatArg1=0, strArg1='', strArg2=''):
    return {'int32Arg1': int32Arg1,
     'int64Arg1': int64Arg1,
     'floatArg1': floatArg1,
     'strArg1': strArg1,
     'strArg2': strArg2}


EMPTY_ARGS = messageArgs()

class MESSENGER_ERRORS:
    NO_ERROR = _makeID(start=0)
    GENERIC_ERROR = _makeID()
    NOT_READY = _makeID()
    IN_COOLDOWN = _makeID()
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


class MESSENGER_LIMITS:
    FIND_USERS_BY_NAME_MAX_RESULT_SIZE = 50
    FIND_USERS_BY_NAME_REQUEST_COOLDOWN_SEC = 5.0 + _COOLDOWN_OFFSET
    BATTLE_CHANNEL_MESSAGE_MAX_SIZE = 140
    UNIT_CHANNEL_MESSAGE_MAX_SIZE = 512
    BATTLE_CHAT_HISTORY_ON_SERVER_MAX_LEN = 10
    UNIT_CHAT_HISTORY_ON_SERVER_MAX_LEN = 20
    BROADCASTS_FROM_CLIENT_COOLDOWN_SEC = (0.5 if not IS_CHINA else 3.0) + _COOLDOWN_OFFSET
    ADMIN_COMMANDS_FROM_CLIENT_COOLDOWN_SEC = 5.0 + _COOLDOWN_OFFSET
    VOIP_CREDENTIALS_REQUEST_COOLDOWN_SEC = 10.0 + _COOLDOWN_OFFSET


class MESSENGER_ACTION_IDS:
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
        return True if battleChatCmdStartID <= actionID < battleChatCmdStartID + len(BATTLE_CHAT_COMMANDS) else False

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


_MESSENGER_ACTION_NAMES = {_id:_name for _name, _id in MESSENGER_ACTION_IDS.__dict__.iteritems() if isinstance(_id, int) and not _name.startswith('_')}
_MESSENGER_ERROR_NAMES = {_id:_name for _name, _id in MESSENGER_ERRORS.__dict__.iteritems() if not _name.startswith('_')}
AdminChatCommand = namedtuple('AdminChatCommand', ('id', 'name', 'timeout'))
ADMIN_CHAT_COMMANDS = (AdminChatCommand(id=_makeID(start=MESSENGER_ACTION_IDS._ADMIN_COMMAND_START_ID), name='USERBAN', timeout=30.0), AdminChatCommand(id=_makeID(), name='USERUNBAN', timeout=30.0))
ADMIN_CHAT_COMMANDS_BY_NAMES = {v.name:v for v in ADMIN_CHAT_COMMANDS}
BattleChatCommand = namedtuple('BattleChatCommand', ('id', 'name', 'cooldownPeriod', 'msgText', 'vehMarker', 'soundNotification'))
UnitChatCommand = namedtuple('UnitChatCommand', ('id', 'name', 'cooldownPeriod', 'msgText'))
UNIT_CHAT_COMMANDS = (UnitChatCommand(id=_makeID(start=MESSENGER_ACTION_IDS._UNIT_COMMAND_START_ID), name='ATTENTIONTOCELL', cooldownPeriod=1.0 + _COOLDOWN_OFFSET, msgText='attention_to_cell'),)
UNIT_CHAT_COMMANDS_BY_NAMES = {v.name:v for v in UNIT_CHAT_COMMANDS}
BATTLE_CHAT_COMMANDS = (BattleChatCommand(id=_makeID(start=MESSENGER_ACTION_IDS._BATTLE_CHAT_COMMAND_START_ID), name='HELPME', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='help_me', vehMarker='help_me', soundNotification='help_me'),
 BattleChatCommand(id=_makeID(), name='FOLLOWME', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='follow_me', vehMarker='follow_me', soundNotification='follow_me'),
 BattleChatCommand(id=_makeID(), name='ATTACK', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='attack', vehMarker=None, soundNotification='attack'),
 BattleChatCommand(id=_makeID(), name='BACKTOBASE', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='back_to_base', vehMarker=None, soundNotification='back_to_base'),
 BattleChatCommand(id=_makeID(), name='POSITIVE', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='positive', vehMarker='positive', soundNotification='positive'),
 BattleChatCommand(id=_makeID(), name='NEGATIVE', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='negative', vehMarker='negative', soundNotification='negative'),
 BattleChatCommand(id=_makeID(), name='ATTENTIONTOCELL', cooldownPeriod=0.5 + _COOLDOWN_OFFSET, msgText='attention_to_cell', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='ATTENTIONTOPOSITION', cooldownPeriod=0.5 + _COOLDOWN_OFFSET, msgText='attention_to_position', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='ATTENTIONTOOBJECTIVE_ATK', cooldownPeriod=0.5 + _COOLDOWN_OFFSET, msgText='attention_to_objective_atk', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='ATTENTIONTOOBJECTIVE_DEF', cooldownPeriod=0.5 + _COOLDOWN_OFFSET, msgText='attention_to_objective_def', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='ATTENTIONTOBASE_ATK', cooldownPeriod=0.5 + _COOLDOWN_OFFSET, msgText='attention_to_base_atk', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='ATTENTIONTOBASE_DEF', cooldownPeriod=0.5 + _COOLDOWN_OFFSET, msgText='attention_to_base_def', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='SPG_AIM_AREA', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='spg_aim_area', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='ATTACKENEMY', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='attack_enemy', vehMarker='attack', soundNotification='attack_the_enemy'),
 BattleChatCommand(id=_makeID(), name='TURNBACK', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='turn_back', vehMarker='turn_back', soundNotification='turn_back'),
 BattleChatCommand(id=_makeID(), name='HELPMEEX', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='help_me_ex', vehMarker='help_me_ex', soundNotification='help_me_ex'),
 BattleChatCommand(id=_makeID(), name='SUPPORTMEWITHFIRE', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='support_me_with_fire', vehMarker='attack', soundNotification='support_me_with_fire'),
 BattleChatCommand(id=_makeID(), name='RELOADINGGUN', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='reloading_gun', vehMarker='reloading_gun', soundNotification='reloading_gun'),
 BattleChatCommand(id=_makeID(), name='STOP', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='stop', vehMarker='stop', soundNotification='stop'),
 BattleChatCommand(id=_makeID(), name='RELOADING_CASSETE', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='reloading_cassette', vehMarker='reloading_gun', soundNotification='reloading_gun'),
 BattleChatCommand(id=_makeID(), name='RELOADING_READY', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='reloading_ready', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='RELOADING_READY_CASSETE', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='reloading_ready_cassette', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='RELOADING_UNAVAILABLE', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='reloading_unavailable', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_SAVETANKS_ATK', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/atk/save_tanks', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_SAVETANKS_DEF', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/def/save_tanks', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_TIME_ATK', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/atk/time', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_TIME_DEF', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/def/time', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_HQ_ATK', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/atk/focus_hq', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_HQ_DEF', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/def/focus_hq', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_WEST', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/lane/west', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_CENTER', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/lane/center', vehMarker=None, soundNotification=None),
 BattleChatCommand(id=_makeID(), name='EPIC_GLOBAL_EAST', cooldownPeriod=5.0 + _COOLDOWN_OFFSET, msgText='global_msg/lane/east', vehMarker=None, soundNotification=None))
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
