# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/chat_shared.py
from soft_exception import SoftException
import time
import constants
import zlib
import cPickle
from Event import Event
from functools import wraps
from wotdecorators import noexcept
from debug_utils import LOG_DEBUG, LOG_ERROR
from constants import CHAT_LOG, RESTRICTION_TYPE
from enumerations import Enumeration, AttributeEnumItem
__all__ = ['CHAT_ACTIONS']
NOTIFICATION_GROUP = Enumeration('Group of members for notification', ['All',
 'NONE',
 'Originator',
 'ExceptOriginator'])

def __notifyFilterAll(originatorId, entityId):
    return True


def __notifyFilterNone(originatorId, entityId):
    return False


def __notifyFilterOnlyOriginator(originatorId, entityId):
    return originatorId == entityId


def __notifyFilterExceptOriginator(originatorId, entityId):
    return originatorId != entityId


if constants.IS_BASEAPP:
    CHAT_ACTIONS = Enumeration('chatChannelActions', [('enter', {'notifyFilter': __notifyFilterExceptOriginator,
       'notificationGroup': NOTIFICATION_GROUP.ExceptOriginator,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('broadcast', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.MESSAGES}),
     ('leave', {'notifyFilter': __notifyFilterExceptOriginator,
       'notificationGroup': NOTIFICATION_GROUP.ExceptOriginator,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('requestMembers', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('channelDestroyed', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('createChannel', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('requestChannels', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('selfEnter', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('selfLeave', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('requestMessageHistory', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('channelInfoUpdated', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.NONE}),
     ('memberStatusUpdate', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.NONE}),
     ('findUsers', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('requestUsersRoster', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('addIgnored', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('addFriend', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('removeIgnored', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('removeFriend', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('createPrivate', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('friendStatusUpdate', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('userChatCommand', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('sysMessage', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.NONE}),
     ('personalSysMessage', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.NONE}),
     ('chatInitialization', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('userInviteCommand', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('createInvite', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('receiveInvite', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('receiveArchiveInvite', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('receiveMembersCount', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('receiveMembersDelta', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('VOIPSettings', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('VOIPCredentials', {'notifyFilter': __notifyFilterAll,
       'notificationGroup': NOTIFICATION_GROUP.All,
       'logLevel': CHAT_LOG.ACTIONS}),
     ('setMuted', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('unsetMuted', {'notifyFilter': __notifyFilterOnlyOriginator,
       'notificationGroup': NOTIFICATION_GROUP.Originator,
       'logLevel': CHAT_LOG.NONE}),
     ('logVivoxLogin', {'notifyFilter': __notifyFilterNone,
       'notificationGroup': NOTIFICATION_GROUP.NONE,
       'logLevel': CHAT_LOG.NONE})], instance=AttributeEnumItem)
else:
    CHAT_ACTIONS = Enumeration('chatActions', [('enter', {}),
     ('broadcast', {}),
     ('leave', {}),
     ('requestMembers', {}),
     ('channelDestroyed', {}),
     ('createChannel', {}),
     ('requestChannels', {}),
     ('selfEnter', {}),
     ('selfLeave', {}),
     ('requestMessageHistory', {}),
     ('channelInfoUpdated', {}),
     ('memberStatusUpdate', {}),
     ('findUsers', {}),
     ('requestUsersRoster', {}),
     ('addIgnored', {}),
     ('addFriend', {}),
     ('removeIgnored', {}),
     ('removeFriend', {}),
     ('createPrivate', {}),
     ('friendStatusUpdate', {}),
     ('userChatCommand', {}),
     ('sysMessage', {}),
     ('personalSysMessage', {}),
     ('chatInitialization', {}),
     ('userInviteCommand', {}),
     ('createInvite', {}),
     ('receiveInvite', {}),
     ('receiveArchiveInvite', {}),
     ('receiveMembersCount', {}),
     ('receiveMembersDelta', {}),
     ('VOIPSettings', {}),
     ('VOIPCredentials', {}),
     ('setMuted', {}),
     ('unsetMuted', {}),
     ('logVivoxLogin', {})], instance=AttributeEnumItem)
CHAT_RESPONSES = Enumeration('chatActionResponses', ('success', 'internalError', 'channelAlreadyExists', 'channelDestroyed', 'passwordRequired', 'incorrectPassword', 'channelNotExists', 'memberBanned', 'memberDisconnecting', 'notAllowed', 'connectTimeout', 'initializationFailure', 'userNotExists', 'usersRosterLimitReached', 'activeChannelsLimitReached', 'sqlError', 'incorrectCharacter', 'addFriendError', 'addIgnoredError', 'userIgnoredError', 'chatCommandError', 'memberAlreadyBanned', 'memberAlreadyModerator', 'memberNotModerator', 'commandInCooldown', 'createPrivateError', 'actionInCooldown', 'chatBanned', 'inviteCommandError', 'unknownCommand', 'inviteCreateError', 'membersLimitReached', 'notSupported', 'inviteCreationNotAllowed', 'incorrectCommandArgument', 'invalidChannelName', 'setMutedError', 'unsetMutedError'))
__DEFAULT_COOLDOWN = 0.5
__BATTLE_COMMANDS_DEFAULT_COOLDOWN = __DEFAULT_COOLDOWN
__CHINA_USER_MESSAGE_COOLDOWN = 3.0
__COOLDOWN_CHECK_CLIENT = 1
__COOLDOWN_CHECK_BASE = 2
__COOLDOWN_CHECK_ALL = __COOLDOWN_CHECK_CLIENT | __COOLDOWN_CHECK_BASE
CHAT_COMMANDS = Enumeration('chatCommands', [('initAck', {'chnlCmd': 0}),
 ('updateMemeberStatus', {'chnlCmd': 0}),
 ('findUser', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('addFriend', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('addIgnored', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('removeFriend', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('removeIgnored', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('createPrivate', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('joinPrivate', {'chnlCmd': 0}),
 ('requestUsersRoster', {'chnlCmd': 0}),
 ('requestFriendStatus', {'chnlCmd': 0}),
 ('friendStatusChange', {'chnlCmd': 0}),
 ('addAdmirer', {'chnlCmd': 0}),
 ('addAdmirerAck', {'chnlCmd': 0}),
 ('removeAdmirer', {'chnlCmd': 0}),
 ('onAddToIgnored', {'chnlCmd': 0}),
 ('CHGCHNLNAME', {'chnlCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 30.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('GREETING', {'chnlCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 30.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('BAN', {'chnlCmd': 1,
   'argsCnt': 3,
   'cooldown': {'period': 10.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('UNBAN', {'chnlCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 10.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('ADDMODERATOR', {'chnlCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 10.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('DELMODERATOR', {'chnlCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 10.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('HELPME', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/help_me',
   'vehMarker': 'help_me',
   'sound_notification': 'help_me'}),
 ('FOLLOWME', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/follow_me',
   'vehMarker': 'follow_me',
   'sound_notification': 'follow_me'}),
 ('ATTACK', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attack',
   'sound_notification': 'attack'}),
 ('BACKTOBASE', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/back_to_base',
   'sound_notification': 'back_to_base'}),
 ('POSITIVE', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/positive',
   'vehMarker': 'positive',
   'sound_notification': 'positive'}),
 ('NEGATIVE', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/negative',
   'vehMarker': 'negative',
   'sound_notification': 'negative'}),
 ('ATTENTIONTOCELL', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attention_to_cell'}),
 ('ATTACKENEMY', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attack_enemy',
   'vehMarker': 'attack',
   'sound_notification': 'attack_the_enemy'}),
 ('requestLastSysMessages', {'chnlCmd': 0}),
 ('chatAckInitialization', {'chnlCmd': 0}),
 ('createInvite', {'inviteCmd': 1,
   'cooldown': {'period': 0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('inviteReceived', {'inviteCmd': 1}),
 ('acceptInvite', {'inviteCmd': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('rejectInvite', {'inviteCmd': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('getActiveInvites', {'inviteCmd': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('getArchiveInvites', {'inviteCmd': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('getMembersCount', {'chnlCmd': 1,
   'cooldown': {'period': __DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('requestSystemChatChannels', {'chnlCmd': 0,
   'cooldown': {'period': __DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('findChatChannels', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('getChannelInfoById', {'chnlCmd': 0}),
 ('createChatChannel', {'chnlCmd': 0,
   'cooldown': {'period': 10.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('destroyChatChannel', {'chnlCmd': 0}),
 ('requestChatChannelMembers', {'chnlCmd': 1,
   'skipBanCheck': 1,
   'cooldown': {'period': 2.0,
                'side': 0}}),
 ('enterChatChannel', {'chnlCmd': 0,
   'cooldown': {'period': __DEFAULT_COOLDOWN,
                'side': 0}}),
 ('leaveChatChannel', {'chnlCmd': 0,
   'cooldown': {'period': __DEFAULT_COOLDOWN,
                'side': 0}}),
 ('broadcast', {'chnlCmd': 0,
   'cooldown': {'period': __DEFAULT_COOLDOWN if not constants.IS_CHINA else __CHINA_USER_MESSAGE_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('USERBAN', {'userCmd': 1,
   'argsCnt': 4,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('USERUNBAN', {'userCmd': 1,
   'argsCnt': 2,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('requestVOIPSettings', {'chnlCmd': 1,
   'skipBanCheck': 1,
   'cooldown': {'period': __DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('requestVOIPCredentials', {'chnlCmd': 0,
   'skipBanCheck': 1}),
 ('setMuted', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('unsetMuted', {'chnlCmd': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('logVivoxLogin', {'chnlCmd': 0,
   'cooldown': {'period': __DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL}}),
 ('TURNBACK', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/turn_back',
   'vehMarker': 'turn_back',
   'sound_notification': 'turn_back'}),
 ('HELPMEEX', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/help_me_ex',
   'vehMarker': 'help_me_ex',
   'sound_notification': 'help_me_ex'}),
 ('SUPPORTMEWITHFIRE', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/support_me_with_fire',
   'vehMarker': 'attack',
   'sound_notification': 'support_me_with_fire'}),
 ('RELOADINGGUN', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/reloading_gun',
   'vehMarker': 'reloading_gun',
   'sound_notification': 'reloading_gun'}),
 ('STOP', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/stop',
   'vehMarker': 'stop',
   'sound_notification': 'stop'}),
 ('RELOADING_CASSETE', {'battleCmd': 1,
   'argsCnt': 2,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/reloading_cassette',
   'vehMarker': 'reloading_gun',
   'sound_notification': 'reloading_gun'}),
 ('RELOADING_READY', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/reloading_ready'}),
 ('RELOADING_READY_CASSETE', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/reloading_ready_cassette'}),
 ('RELOADING_UNAVAILABLE', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': 5.0,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/reloading_unavailable'}),
 ('ATTENTIONTOPOSITION', {'battleCmd': 1,
   'argsCnt': 2,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attention_to_position'}),
 ('ATTENTIONTOOBJECTIVE_ATK', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attention_to_objective_atk'}),
 ('ATTENTIONTOOBJECTIVE_DEF', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attention_to_objective_def'}),
 ('ATTENTIONTOBASE_ATK', {'battleCmd': 1,
   'argsCnt': 2,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attention_to_base_atk'}),
 ('ATTENTIONTOBASE_DEF', {'battleCmd': 1,
   'argsCnt': 1,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/attention_to_base_def'}),
 ('EPIC_GLOBAL_SAVETANKS_ATK', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/atk/save_tanks'}),
 ('EPIC_GLOBAL_SAVETANKS_DEF', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/def/save_tanks'}),
 ('EPIC_GLOBAL_TIME_ATK', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/atk/time'}),
 ('EPIC_GLOBAL_TIME_DEF', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/def/time'}),
 ('EPIC_GLOBAL_HQ_ATK', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/atk/focus_hq'}),
 ('EPIC_GLOBAL_HQ_DEF', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/def/focus_hq'}),
 ('EPIC_GLOBAL_WEST', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/lane/west'}),
 ('EPIC_GLOBAL_CENTER', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/lane/center'}),
 ('EPIC_GLOBAL_EAST', {'battleCmd': 1,
   'argsCnt': 0,
   'cooldown': {'period': __BATTLE_COMMANDS_DEFAULT_COOLDOWN,
                'side': __COOLDOWN_CHECK_ALL},
   'msgText': '#ingame_gui:chat_shortcuts/global_msg/lane/east'})], instance=AttributeEnumItem)
CHAT_MEMBER_STATUSES = Enumeration('chatMemberStatuses', ['available', 'inBattle'])
CHAT_MEMBER_BAN_TYPE = Enumeration('chatMemberBanType', ['none', 'readonly', 'full'])
CHAT_MEMBER_ROLE = Enumeration('chatMemberRole', ['member', 'visitor', 'moderator'])
CHAT_MEMBER_GROUP = Enumeration('chatMemberRole', ['member',
 'channelOwner',
 'channelModerator',
 'chatAdmin'])
CHAT_CHANNEL_BATTLE_TEAM = 1
CHAT_CHANNEL_BATTLE = 2
CHAT_CHANNEL_PREBATTLE = 4
CHAT_CHANNEL_PRIVATE = 8
CHAT_CHANNEL_DESTROYING = 16
CHAT_CHANNEL_TRAINING = 32
CHAT_CHANNEL_SQUAD = 64
CHAT_CHANNEL_TEAM = 128
CHAT_CHANNEL_VOICE = 256
CHAT_CHANNEL_CLAN = 512
CHAT_CHANNEL_PREBATTLE_CLAN = 1024
CHAT_CHANNEL_TOURNAMENT = 2048
CHAT_CHANNEL_UNIT = 4096
CHAT_CHANNEL_NOTIFY_MEMBERS_MASK = 3
CHAT_CHANNEL_NOTIFY_MEMBERS_IN_OUT = 0
CHAT_CHANNEL_NOT_NOTIFY_MEMBERS_IN_OUT = 1
CHAT_CHANNEL_NOTIFY_MEMBERS_COUNT = 2
CHAT_CHANNEL_NOTIFY_MEMBERS_DELTA = 3

def boundActionResponseFilter(response):

    def wrap(func):

        @wraps(func)
        def wrapper(obj, actionData, *args, **kwArgs):
            if CHAT_RESPONSES[actionData['actionResponse']] == response:
                func(obj, actionData, *args, **kwArgs)

        return wrapper

    return wrap


def buildChatActionData(action, channelId=None, **kwArgs):
    data = {}
    data['requestID'] = kwArgs.get('requestID', -1)
    data['action'] = action.index()
    data['channel'] = channelId if channelId is not None else 0
    data['actionResponse'] = kwArgs.get('actionResponse', CHAT_RESPONSES.success).index()
    data['originator'] = kwArgs.get('originator', -1)
    data['originatorNickName'] = kwArgs.get('originatorNickName', '')
    data['group'] = kwArgs.get('group', CHAT_MEMBER_GROUP.member).index()
    data['data'] = kwArgs.get('data')
    data['time'] = time.time()
    data['sentTime'] = data['time']
    data['flags'] = kwArgs.get('flags', 0)
    return data


ChatChannelKeyPrefix = 'chatChannel_'

def buildChannelsKey(id):
    return '%s%d' % (ChatChannelKeyPrefix, id)


@noexcept
def getChannelsIDFromKey(key):
    if key.startswith(ChatChannelKeyPrefix):
        strID = key.replace(ChatChannelKeyPrefix, '')
        return int(strID)


def isChannelSecured(channelInfo):
    return channelInfo is not None and channelInfo.get('isReadOnly', False)


def _testChannelFlag(channelInfo, testedFlag, resultForNone=True):
    if channelInfo is None:
        return resultForNone
    else:
        flags = channelInfo.get('flags', 0)
        return _testFlags(flags, testedFlag)


def _testFlags(flags, testedFlag):
    return flags & testedFlag == testedFlag


def isChannelDestroying(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_DESTROYING)


def isChannelDestroyingFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_DESTROYING)


def isPrivateChannel(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_PRIVATE)


def isTrainingChannel(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_TRAINING)


def isPrebattleChannel(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_PREBATTLE)


def isPrebattleChannelFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_PREBATTLE)


def isSquadChannel(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_SQUAD)


def isTeamChannel(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_TEAM)


def isBattleTeamFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_BATTLE)


def isArenaBattleTeamFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_BATTLE_TEAM)


def isChannelHasVoice(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_VOICE)


def isChannelHasVoiceFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_VOICE)


def isClanChannel(channelInfo):
    return _testChannelFlag(channelInfo, CHAT_CHANNEL_CLAN, False)


def isClanChannelFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_CLAN)


def isTournamentChannelFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_TOURNAMENT)


def isPrebattleClanChannelFlags(flags):
    return _testFlags(flags, CHAT_CHANNEL_PREBATTLE_CLAN)


def isRegularChannel(channelInfo):
    return False if channelInfo is None else isRegularChannelFlags(channelInfo.get('flags', 0))


def isRegularChannelFlags(flags):
    return flags == 0


class BaseChatCommandProcessor(object):

    def __init__(self, comand):
        self._command = comand

    def parseRawData(self, rawData, verifyData=True):
        if verifyData:
            self.__verifyRawData(rawData)
        parsedData = self._makeTuple(rawData)
        if verifyData:
            self._verifyTupledData(parsedData)
        return self._adjustTupleDataTypes(parsedData)

    def verifyParsedData(self, int64Arg=0, int16arg=0, stringArg1='', stringArg2=''):
        return True

    def _verifyTupledData(self, dataAsTuple):
        return self.verifyParsedData(dataAsTuple[1], dataAsTuple[2], dataAsTuple[3], dataAsTuple[4])

    def __verifyRawData(self, rawData):
        argsCnt = self._command.argsCnt
        if len(rawData) != argsCnt:
            raise ChatCommandError(error='#chat:errors/toosmallargs' if len(rawData) < argsCnt else '#chat:errors/toomanyargs')
        return True

    def _makeTuple(self, rawData):
        return (self._command,
         0,
         0,
         '',
         '')

    def _adjustTupleDataTypes(self, rawTuple):
        return (self._command,
         long(rawTuple[1]),
         int(rawTuple[2]),
         rawTuple[3],
         rawTuple[4])

    def set_command(self, newValue):
        self.__command = newValue

    _command = property(lambda self: self.__command, set_command)


class OneStringArgCommandProcessor(BaseChatCommandProcessor):

    def __init__(self, command):
        BaseChatCommandProcessor.__init__(self, command)

    def _makeTuple(self, rawData):
        return (self._command,
         0,
         0,
         rawData[0],
         '')


class NoArgsCommandProcessor(BaseChatCommandProcessor):

    def __init__(self, command):
        BaseChatCommandProcessor.__init__(self, command)


class BanCommandProcessor(BaseChatCommandProcessor):

    def __init__(self):
        BaseChatCommandProcessor.__init__(self, CHAT_COMMANDS.BAN)

    def _makeTuple(self, rawData):
        return (self._command,
         0,
         -1 if isPermanentBan(rawData[1]) else rawData[1],
         rawData[0],
         rawData[2])

    def verifyParsedData(self, int64Arg=0, int16arg=0, stringArg1='', stringArg2=''):
        errorMessage = '#chat:errors/timeincorrect'
        timeArg = int16arg
        if isinstance(timeArg, basestring) and timeArg.isdigit() or isinstance(timeArg, (int, long)):
            time = int(timeArg)
            if time == -1:
                pass
            elif time < 1 or time > 1440:
                raise ChatCommandError(error=errorMessage)
        else:
            raise ChatCommandError(error=errorMessage)
        return True


class UserCommandProcessor(BaseChatCommandProcessor):
    _USER_BAN_TYPES = Enumeration('UserCommandBanTypes', {RESTRICTION_TYPE.BAN: 'game',
     RESTRICTION_TYPE.CHAT_BAN: 'chat'})

    def __init__(self, command):
        BaseChatCommandProcessor.__init__(self, command)


class UserBanCommandProcessor(UserCommandProcessor):
    import re
    __BAN_TIME_RE = re.compile('([-|+]?)([0-9]*)([hdwmy]?)')

    def __init__(self):
        UserCommandProcessor.__init__(self, CHAT_COMMANDS.USERBAN)

    def _makeTuple(self, rawData):
        if isinstance(rawData[0], basestring):
            banType = rawData[0].lower()
            if banType not in UserCommandProcessor._USER_BAN_TYPES:
                raise IncorrectCommandArgumentError(rawData[0])
        else:
            raise IncorrectCommandArgumentError(rawData[0])
        banTypeIdx = getattr(UserCommandProcessor._USER_BAN_TYPES, banType).index()
        banPeriod = None
        if isinstance(rawData[2], basestring):
            res = self.__BAN_TIME_RE.match(rawData[2])
            multiplier = 1
            if res:
                sign, amount, timeSpec = res.groups()
                if not amount:
                    raise IncorrectCommandArgumentError(rawData[2])
                if 'h' == timeSpec:
                    multiplier = 60
                elif 'd' == timeSpec:
                    multiplier = 1440
                elif 'w' == timeSpec:
                    multiplier = 10080
                elif 'm' == timeSpec:
                    multiplier = 43200
                elif 'y' == timeSpec:
                    multiplier = 43200
                if '-' == sign:
                    multiplier *= -1
                banPeriod = long(amount) * multiplier
        elif isinstance(rawData[2], long):
            banPeriod = rawData[2]
        else:
            raise IncorrectCommandArgumentError(rawData[2])
        words = rawData[3].split()
        if words and 'kick' == words[0].lower():
            banTypeIdx *= -1
            rawData[3] = ' '.join(words[1:])
        return (self._command,
         banPeriod,
         banTypeIdx,
         rawData[1],
         rawData[3])

    def verifyParsedData(self, banPeriod=0, banTypeIdx=0, username='', reason=''):
        if not (isinstance(banPeriod, basestring) and banPeriod.isdigit() or isinstance(banPeriod, (int, long))):
            raise IncorrectCommandArgumentError(banPeriod)
        try:
            _ = UserCommandProcessor._USER_BAN_TYPES[banTypeIdx]
        except:
            raise IncorrectCommandArgumentError(banTypeIdx)

        return True


class UserUnbanCommandProcessor(UserCommandProcessor):

    def __init__(self):
        UserCommandProcessor.__init__(self, CHAT_COMMANDS.USERUNBAN)

    def _makeTuple(self, rawData):
        if isinstance(rawData[0], basestring):
            banType = rawData[0].lower()
            if banType not in UserCommandProcessor._USER_BAN_TYPES:
                raise IncorrectCommandArgumentError(rawData[0])
        else:
            raise IncorrectCommandArgumentError(rawData[0])
        banTypeIdx = getattr(UserCommandProcessor._USER_BAN_TYPES, banType).index()
        return (self._command,
         0,
         banTypeIdx,
         rawData[1],
         '')

    def verifyParsedData(self, banPeriod=0, banTypeIdx=0, username='', reason=''):
        try:
            _ = UserCommandProcessor._USER_BAN_TYPES[banTypeIdx]
        except:
            raise IncorrectCommandArgumentError(banTypeIdx)

        return True


_g_chatCommandProcessors = {CHAT_COMMANDS.BAN: BanCommandProcessor(),
 CHAT_COMMANDS.CHGCHNLNAME: OneStringArgCommandProcessor(CHAT_COMMANDS.CHGCHNLNAME),
 CHAT_COMMANDS.GREETING: OneStringArgCommandProcessor(CHAT_COMMANDS.GREETING),
 CHAT_COMMANDS.UNBAN: OneStringArgCommandProcessor(CHAT_COMMANDS.UNBAN),
 CHAT_COMMANDS.ADDMODERATOR: OneStringArgCommandProcessor(CHAT_COMMANDS.ADDMODERATOR),
 CHAT_COMMANDS.DELMODERATOR: OneStringArgCommandProcessor(CHAT_COMMANDS.DELMODERATOR),
 CHAT_COMMANDS.HELPME: NoArgsCommandProcessor(CHAT_COMMANDS.HELPME),
 CHAT_COMMANDS.ATTACK: NoArgsCommandProcessor(CHAT_COMMANDS.ATTACK),
 CHAT_COMMANDS.BACKTOBASE: NoArgsCommandProcessor(CHAT_COMMANDS.BACKTOBASE),
 CHAT_COMMANDS.FOLLOWME: NoArgsCommandProcessor(CHAT_COMMANDS.FOLLOWME),
 CHAT_COMMANDS.POSITIVE: NoArgsCommandProcessor(CHAT_COMMANDS.POSITIVE),
 CHAT_COMMANDS.NEGATIVE: NoArgsCommandProcessor(CHAT_COMMANDS.NEGATIVE),
 CHAT_COMMANDS.ATTENTIONTOCELL: NoArgsCommandProcessor(CHAT_COMMANDS.ATTENTIONTOCELL),
 CHAT_COMMANDS.ATTACKENEMY: OneStringArgCommandProcessor(CHAT_COMMANDS.ATTACKENEMY),
 CHAT_COMMANDS.USERBAN: UserBanCommandProcessor(),
 CHAT_COMMANDS.USERUNBAN: UserUnbanCommandProcessor(),
 CHAT_COMMANDS.EPIC_GLOBAL_SAVETANKS_ATK: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_SAVETANKS_ATK),
 CHAT_COMMANDS.EPIC_GLOBAL_SAVETANKS_DEF: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_SAVETANKS_DEF),
 CHAT_COMMANDS.EPIC_GLOBAL_TIME_ATK: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_TIME_ATK),
 CHAT_COMMANDS.EPIC_GLOBAL_TIME_DEF: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_TIME_DEF),
 CHAT_COMMANDS.EPIC_GLOBAL_HQ_ATK: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_HQ_ATK),
 CHAT_COMMANDS.EPIC_GLOBAL_HQ_DEF: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_HQ_DEF),
 CHAT_COMMANDS.EPIC_GLOBAL_WEST: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_WEST),
 CHAT_COMMANDS.EPIC_GLOBAL_CENTER: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_CENTER),
 CHAT_COMMANDS.EPIC_GLOBAL_EAST: NoArgsCommandProcessor(CHAT_COMMANDS.EPIC_GLOBAL_EAST)}

def initChatCooldownData():
    cooldDownData = {}
    for command in CHAT_COMMANDS.all():
        coolDownConfig = getattr(command, 'cooldown') if hasattr(command, 'cooldown') else {}
        coolDownPeriod = coolDownConfig.get('period', -1)
        if coolDownPeriod > 0:
            cooldDownData[command.index()] = {'cooldown': coolDownPeriod,
             'side': coolDownConfig.get('side', 0),
             'last': time.time() - coolDownPeriod}

    return cooldDownData


if constants.IS_CLIENT or constants.IS_BOT:
    g_chatCooldownData = initChatCooldownData()

def __isOperationInCooldown(cooldownDataInfo, operation, update=True):
    cooldDownData = cooldownDataInfo.get(operation.index(), None)
    if cooldDownData:
        checkSide = __COOLDOWN_CHECK_CLIENT if constants.IS_CLIENT else __COOLDOWN_CHECK_BASE
        commandTime = time.time()
        lastCommandTime = cooldDownData.get('last', commandTime)
        coolDownPeriod = cooldDownData.get('cooldown', -1)
        cooldownCheckSide = cooldDownData.get('side', 0)
        if cooldownCheckSide & checkSide == checkSide:
            if lastCommandTime + coolDownPeriod >= commandTime:
                return True
            if update:
                cooldDownData['last'] = commandTime
                cooldownDataInfo[operation.index()] = cooldDownData
    return False


def isOperationInCooldown(cooldownData, operation, update=True):
    return __isOperationInCooldown(cooldownData, operation, update=update)


def getOperationCooldownPeriod(operation):
    coolDownConfig = getattr(operation, 'cooldown') if hasattr(operation, 'cooldown') else {}
    return coolDownConfig.get('period', -1)


_g_chatadmins = ['redfox', 'ars', 'snake']

def isChatAdmin(username):
    return username in _g_chatadmins


def __isCommandFromCategory(category, cmdName=None, cmdIdx=None):
    try:
        if cmdIdx is None:
            cmdItem = CHAT_COMMANDS.lookup(cmdName)
        else:
            cmdItem = CHAT_COMMANDS[cmdIdx]
    except:
        cmdItem = None

    return cmdItem is not None and hasattr(cmdItem, category) and getattr(cmdItem, category) == 1


def isInviteCommand(cmdName):
    return __isCommandFromCategory('inviteCmd', cmdName=cmdName)


def isInviteCommandIdx(cmdIdx):
    return __isCommandFromCategory('inviteCmd', cmdIdx=cmdIdx)


def isChannelChatCommand(cmdName):
    return __isCommandFromCategory('chnlCmd', cmdName=cmdName)


def isChannelChatCommandIdx(cmdIdx):
    return __isCommandFromCategory('chnlCmd', cmdIdx=cmdIdx)


def isUserCommand(cmdName):
    return __isCommandFromCategory('userCmd', cmdName=cmdName)


def isUserCommandIdx(cmdIdx):
    return __isCommandFromCategory('userCmd', cmdIdx=cmdIdx)


def isBattleChatCommand(cmdName):
    return __isCommandFromCategory('battleCmd', cmdName=cmdName)


def isBattleChatCommandIdx(cmdIdx):
    return __isCommandFromCategory('battleCmd', cmdIdx=cmdIdx)


def isSkipBanCheckForChatCommand(cmdName):
    return __isCommandFromCategory('skipBanCheck', cmdName=cmdName)


def isSkipBanCheckForCommandIdx(cmdIdx):
    return __isCommandFromCategory('skipBanCheck', cmdIdx=cmdIdx)


def isCommandMessage(message):
    if message.startswith('/'):
        words = message[1:].split()
        if len(words) > 0:
            return isChannelChatCommand(words[0]) or isBattleChatCommand(words[0]) or isUserCommand(words[0])
    return False


def parseCommandMessage(message, verifyArgs=True):
    if isCommandMessage(message):
        data = message[1:].split(None, 1)
        cmd = CHAT_COMMANDS.lookup(data[0])
        argsCnt = cmd.argsCnt - 1
        rawData = data[1].split(None, argsCnt) if len(data) > 1 else []
        cmdProcessor = _g_chatCommandProcessors.get(cmd, None)
        if cmdProcessor is None:
            LOG_ERROR('Can`t process arguments: command %s hasn`t argument processor. command ignored' % (cmd,))
            return (0, 0, '', '')
        else:
            return cmdProcessor.parseRawData(rawData, verifyArgs)
    return


def verifyCommandData(command, int64Arg=0, int16arg=0, stringArg1='', stringArg2=''):
    cmdProcessor = _g_chatCommandProcessors.get(command, None)
    if cmdProcessor is None:
        LOG_ERROR('Can`t process arguments: command %s hasn`t argument processor. command ignored' % (command,))
        return False
    else:
        return cmdProcessor.verifyParsedData(int64Arg, int16arg, stringArg1, stringArg2)
        return


def isPermanentBan(banTime):
    return 'permanent' == banTime


class ChatActionHandlers(object):

    def __init__(self):
        self.__actionHandlers = None
        self._onEntityInit()
        return

    def _onEntityInit(self):
        if hasattr(self, '__actionHandlers'):
            self._clear()
        self.__actionHandlers = {}

    def _onEntityRestore(self):
        self._onEntityInit()

    def _onEntityDestroy(self):
        self._clear()

    def _clear(self):
        for handlers in self.__actionHandlers.values():
            handlers.clear()

        self.__actionHandlers.clear()
        self.__actionHandlers = None
        return

    def _getActionHandlers(self, actionId):
        if actionId not in self.__actionHandlers:
            handlers = self.__actionHandlers[actionId] = Event()
        else:
            handlers = self.__actionHandlers[actionId]
        return handlers

    def _subscribeActionHandler(self, actionId, handler):
        handlers = self._getActionHandlers(actionId)
        handlers += handler

    def _unsubscribeActionHandler(self, actionId, handler):
        handlers = self._getActionHandlers(actionId)
        handlers -= handler


class ChatError(SoftException):

    def __init__(self, response=None, auxMessage=None, messageArgs=None):
        SoftException.__init__(self)
        self.__response = CHAT_RESPONSES.internalError if response is None else response
        self.__auxMessage = auxMessage
        self._messageArgs = messageArgs
        return

    response = property(lambda self: self.__response)

    def _getMessage(self):
        return 'Internal error occurred' + (':' + self.__auxMessage if self.__auxMessage is not None else '')

    def __get_message(self):
        return self._getMessage()

    message = property(__get_message)
    messageArgs = property(lambda self: self._messageArgs)


class UserBannedError(ChatError):

    def __init__(self, banOwnerNick, banReason, banEndTime):
        ChatError.__init__(self, CHAT_RESPONSES.memberBanned)
        self.__banOwnerNick = banOwnerNick
        self.__banReason = banReason
        self.__banEndTime = banEndTime
        self._messageArgs = {'banOwnerNick': self.__banOwnerNick,
         'banReason': self.__banReason,
         'banEndTime': self.__banEndTime}

    def _getMessage(self):
        if self.__banEndTime is not None:
            return 'You are banned by user %s till %s. Reason: %s.' % (self.__banOwnerNick, self.__banEndTime, self.__banReason)
        else:
            return 'You are banned by user %s till %s. Reason: %s.' % (self.__banOwnerNick, self.__banEndTime, self.__banReason)
            return


class ChatBannedError(ChatError):

    def __init__(self, banReason, banEndTime):
        ChatError.__init__(self, CHAT_RESPONSES.chatBanned)
        self.__banReason = banReason
        self.__banEndTime = banEndTime
        self._messageArgs = {'banReason': self.__banReason,
         'banEndTime': self.__banEndTime}

    def _getMessage(self):
        if self.__banEndTime is not None:
            return 'You are banned till %s. Reason: %s.' % (self.__banEndTime, self.__banReason)
        else:
            return 'You are banned. Reason: %s.' % self.__banReason
            return


class ChatSQLError(ChatError):

    def __init__(self, error=None):
        ChatError.__init__(self, CHAT_RESPONSES.sqlError)
        self.__error = error
        self._messageArgs = {'error': error}

    def _getMessage(self):
        return 'SQL error occurred: %s' % (self.__error,)


class IncorrectCharacter(ChatError):

    def __init__(self):
        ChatError.__init__(self, CHAT_RESPONSES.incorrectCharacter)

    def _getMessage(self):
        pass


class AddFriendError(ChatError):

    def __init__(self, reason):
        ChatError.__init__(self, CHAT_RESPONSES.addFriendError)
        self.__reason = reason
        self._messageArgs = {'reason': reason}

    def _getMessage(self):
        return 'Can`t add user to friends: %s' % self.__reason


class AddIgnoredError(ChatError):

    def __init__(self, reason):
        ChatError.__init__(self, CHAT_RESPONSES.addIgnoredError)
        self.__reason = reason
        self._messageArgs = {'reason': reason}

    def _getMessage(self):
        return 'Can`t add user to ignored users list: %s' % self.__reason


class SetMutedError(ChatError):

    def __init__(self, reason):
        ChatError.__init__(self, CHAT_RESPONSES.setMutedError)
        self.__reason = reason
        self._messageArgs = {'reason': reason}

    def _getMessage(self):
        return 'Can`t add user to muted users list: %s' % self.__reason


class UnsetMutedError(ChatError):

    def __init__(self, reason):
        ChatError.__init__(self, CHAT_RESPONSES.unsetMutedError)
        self.__reason = reason
        self._messageArgs = {'reason': reason}

    def _getMessage(self):
        return 'Can`t remove user from muted users list: %s' % self.__reason


class UserIgnoredError(ChatError):

    def __init__(self, ignorerName):
        ChatError.__init__(self, CHAT_RESPONSES.userIgnoredError)
        self.__ignorerName = ignorerName
        self._messageArgs = {'ignorer': ignorerName}

    def _getMessage(self):
        return 'You are in the ignored users list of user %s' % self.__ignorerName


class CreatePrivateError(ChatError):

    def __init__(self, reason):
        ChatError.__init__(self, CHAT_RESPONSES.createPrivateError)
        self.__reason = reason
        self._messageArgs = {'reason': reason}

    def _getMessage(self):
        return 'Can`t create private channel: %s' % self.__reason


class ActiveChannelsLimitReached(ChatError):

    def __init__(self, limit):
        ChatError.__init__(self, CHAT_RESPONSES.activeChannelsLimitReached)
        self.__limit = limit
        self._messageArgs = {'limit': limit}

    def _getMessage(self):
        return 'You have reached limit in %d opened channels' % self.__limit


class UsersRosterLimitReached(ChatError):

    def __init__(self, limit):
        ChatError.__init__(self, CHAT_RESPONSES.usersRosterLimitReached)
        self.__limit = limit
        self._messageArgs = {'limit': limit}

    def _getMessage(self):
        return 'You already have maximum number of users (friends and ignored) allowed: %d' % self.__limit


class ChatCommandError(ChatError):

    def __init__(self, response=None, error=None):
        ChatError.__init__(self, CHAT_RESPONSES.chatCommandError if response is None else response)
        self.__error = error
        if error is not None:
            self._messageArgs = {'error': error}
        return

    def _getMessage(self):
        return 'Chat command error occurred: %s' % (self.__error,)


class InviteCommandError(ChatError):

    def __init__(self, inviteID, response=None, error=None):
        ChatError.__init__(self, CHAT_RESPONSES.inviteCommandError if response is None else response)
        self.__error = error
        self.__inviteID = inviteID
        self._messageArgs = {'inviteID': inviteID}
        if error is not None:
            self._messageArgs['error'] = error
        return

    def _getMessage(self):
        return 'Invite command error occurred: %s during processing invite wit ID: %s' % (self.__error, self.__inviteID)


class InviteCreateError(InviteCommandError):

    def __init__(self, response=None, error=None):
        InviteCommandError.__init__(self, None, response=CHAT_RESPONSES.inviteCreateError if response is None else response, error=error)
        return


class InviteCreationNotAllowed(InviteCreateError):

    def __init__(self, response=None, error=None):
        InviteCreateError.__init__(self, response=CHAT_RESPONSES.inviteCreationNotAllowed if response is None else response, error=error)
        return


class ChatCommandInCooldown(ChatCommandError):

    def __init__(self, command):
        ChatCommandError.__init__(self, CHAT_RESPONSES.commandInCooldown)
        coolDownConfig = getattr(command, 'cooldown') if hasattr(command, 'cooldown') else {}
        coolDownPeriod = coolDownConfig.get('period', None)
        self._messageArgs = {'command': command.name(),
         'cooldownPeriod': coolDownPeriod}
        return


class ChatCommandNotAllowedError(ChatCommandError):

    def __init__(self):
        ChatCommandError.__init__(self, CHAT_RESPONSES.notAllowed, 'operation not allowed to user')


class MemberAlreadyBanned(ChatCommandError):

    def __init__(self, member):
        ChatCommandError.__init__(self, CHAT_RESPONSES.memberAlreadyBanned)
        self._messageArgs = {'user': member}


class MemberAlreadyModerator(ChatCommandError):

    def __init__(self, member):
        ChatCommandError.__init__(self, CHAT_RESPONSES.memberAlreadyModerator)
        self._messageArgs = {'user': member}


class MemberNotModerator(ChatCommandError):

    def __init__(self, member):
        ChatCommandError.__init__(self, CHAT_RESPONSES.memberNotModerator)
        self._messageArgs = {'user': member}


class IncorrectCommandArgumentError(ChatCommandError):

    def __init__(self, arg):
        ChatCommandError.__init__(self, CHAT_RESPONSES.incorrectCommandArgument)
        self._messageArgs = {'arg': arg}


class ChatException(ChatError, Exception):

    def __init__(self, response=None):
        ChatError.__init__(self, response)


class ChannelNotExists(ChatException):

    def __init__(self, id):
        ChatException.__init__(self, CHAT_RESPONSES.channelNotExists)
        self.__channelId = id

    def _getMessage(self):
        return 'Channel with id: %s not exists' % self.__channelId


class UserNotExists(ChatException):

    def __init__(self, nickname):
        ChatException.__init__(self, CHAT_RESPONSES.userNotExists)
        self.__nickname = nickname
        self._messageArgs = {'user': nickname}

    def _getMessage(self):
        return 'User with nickname: %s not exists' % self.__nickname


SYS_MESSAGE_TYPE = Enumeration('systemMessageType', ['serverReboot',
 'serverRebootCancelled',
 'battleResults',
 'achievements',
 'goldReceived',
 'accountTypeChanged',
 'adminTextMessage',
 'accountNameChanged',
 'invoiceReceived',
 'giftReceived',
 'autoMaintenance',
 'reserved_11',
 'reserved_12',
 'waresSold',
 'waresBought',
 'premiumBought',
 'premiumExtended',
 'premiumExpired',
 'prbArenaFinish',
 'prbKick',
 'prbDestruction',
 'vehicleCamouflageTimedOut',
 'vehTypeLockExpired',
 'accountDeleted',
 'serverDowntimeCompensation',
 'vehiclePlayerEmblemTimedOut',
 'vehiclePlayerInscriptionTimedOut',
 'achievementReceived',
 'converter',
 'tokenQuests',
 'notificationsCenter',
 'clanEvent',
 'fortEvent',
 'fortBattleInvite',
 'fortBattleEnd',
 'fortBattleRoundEnd',
 'refSystemQuests',
 'refSystemReferralBoughtVehicle',
 'refSystemReferralContributedXP',
 'vehicleRented',
 'rentalsExpired',
 'rentCompensation',
 'potapovQuestBonus',
 'premiumPersonalDiscount',
 'goodieRemoved',
 'specBattleInvite',
 'specBattleRoundEnd',
 'specBattleEnd',
 'telecomOrderCreated',
 'telecomOrderUpdated',
 'telecomOrderDeleted',
 'prbVehicleKick',
 'goodieDisabled',
 'vehicleGroupLocked',
 'vehicleGroupUnlocked',
 'rankedQuests',
 'bootcamp',
 'prbVehicleMaxSpgKick',
 'hangarQuests',
 'currencyUpdate'])
SYS_MESSAGE_IMPORTANCE = Enumeration('systemMessageImportance', ['normal', 'high'])
SM_REQUEST_PERSONAL_MESSAGES_FLAG = 1
SM_REQUEST_SYSTEM_MESSAGES_FLAG = 2
SM_REQUEST_INTERNAL_SYS_MESSAGES_FLAG = 4

def isMembersListSupported(channelInfo):
    if channelInfo is None:
        return False
    else:
        return isMembersListSupportedByFlags(channelInfo.get('notifyFlags', 0))
        return


def isMembersListSupportedByFlags(channelNotifyFlags):
    return getMembersListMode(channelNotifyFlags) in (CHAT_CHANNEL_NOTIFY_MEMBERS_DELTA, CHAT_CHANNEL_NOTIFY_MEMBERS_IN_OUT)


def getMembersListMode(channelNotifyFlags):
    return channelNotifyFlags & CHAT_CHANNEL_NOTIFY_MEMBERS_MASK


def setMembersListMode(channelNotifyFlags, newMode):
    oldMode = channelNotifyFlags & CHAT_CHANNEL_NOTIFY_MEMBERS_MASK
    channelNotifyFlags -= oldMode
    channelNotifyFlags += newMode
    return channelNotifyFlags


USERS_ROSTER_FRIEND = 1
USERS_ROSTER_IGNORED = 2
USERS_ROSTER_VOICE_MUTED = 4

def isFromFriendRoster(rosterData):
    return _checkRosterAccessBitmask(rosterData, USERS_ROSTER_FRIEND)


def isFromIgnoreRoster(rosterData):
    return _checkRosterAccessBitmask(rosterData, USERS_ROSTER_IGNORED)


def isVoiceMuted(rosterData):
    return _checkRosterAccessBitmask(rosterData, USERS_ROSTER_VOICE_MUTED)


def _checkRosterAccessBitmask(rosterData, bitmask):
    accessFlags = rosterData.get('accessFlags', 0) if rosterData is not None else 0
    return accessFlags & bitmask == bitmask


class MESSAGE_FILTER_TYPE(object):
    EXCLUDE = 1
    INCLUDE = 2


def compressSysMessage(message):
    if isinstance(message, dict):
        message = zlib.compress(cPickle.dumps(message, -1), 1)
    return message


def decompressSysMessage(message):
    try:
        message = cPickle.loads(zlib.decompress(message))
    except:
        pass

    return message
