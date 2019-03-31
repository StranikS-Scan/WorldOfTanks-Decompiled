# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/wrappers.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld
import constants
from collections import namedtuple
from chat_shared import CHAT_CHANNEL_BATTLE, CHAT_CHANNEL_BATTLE_TEAM, CHAT_CHANNEL_PREBATTLE, CHAT_CHANNEL_PRIVATE, CHAT_CHANNEL_SQUAD, CHAT_CHANNEL_TEAM, CHAT_CHANNEL_PREBATTLE_CLAN, CHAT_CHANNEL_TOURNAMENT, CHAT_CHANNEL_CLAN
from chat_shared import USERS_ROSTER_FRIEND, USERS_ROSTER_IGNORED, SYS_MESSAGE_IMPORTANCE, USERS_ROSTER_VOICE_MUTED
import invites
from items import vehicles
from helpers import time_utils
from messenger import LAZY_CHANNELS, passCensor
import time as _time, datetime
import types
from helpers import int2roman
_ChannelData = namedtuple('_ChannelData', ' '.join(['cid',
 'channelName',
 'ownerName',
 'isReadOnly',
 'isSystem',
 'isSecured',
 'greeting',
 'flags',
 'notifyFlags',
 'lazy']))

class ChannelWrapper(_ChannelData):

    def __new__(cls, id=0, channelName='Unknown', owner=-1L, ownerName='', isReadOnly=False, isSystem=False, isSecured=False, greeting='', flags=0, notifyFlags=0, **kwargs):
        lazy = 0
        if isSystem and channelName in LAZY_CHANNELS.INDICES:
            indiceIdx = LAZY_CHANNELS.INDICES.index(channelName)
            lazy = LAZY_CHANNELS.CLIENT_IDXS[indiceIdx]
        result = _ChannelData.__new__(cls, id, channelName, ownerName, isReadOnly, isSystem, isSecured, greeting, flags, notifyFlags, lazy)
        result.password = None
        result.joined = False
        result.joinedTime = None
        result.selected = False
        result.owner = owner
        result.hidden = False
        result.waitingDestroyedEvent = False
        return result

    @property
    def isPrebattle(self):
        return self.flags & CHAT_CHANNEL_PREBATTLE != 0

    @property
    def isBattleSession(self):
        return self.flags & CHAT_CHANNEL_PREBATTLE_CLAN != 0 or self.flags & CHAT_CHANNEL_TOURNAMENT != 0

    @property
    def isBattle(self):
        return self.flags & CHAT_CHANNEL_BATTLE != 0

    @property
    def isBattleTeam(self):
        return self.flags & CHAT_CHANNEL_BATTLE_TEAM != 0

    @property
    def isPrivate(self):
        return self.flags & CHAT_CHANNEL_PRIVATE != 0

    @property
    def isSquad(self):
        return self.flags & CHAT_CHANNEL_SQUAD != 0

    @property
    def isCompany(self):
        return self.flags & CHAT_CHANNEL_TEAM != 0

    @property
    def isClan(self):
        return self.flags & CHAT_CHANNEL_CLAN != 0

    def update(self, other):
        other.password = self.password
        other.selected = self.selected
        other.joined = self.joined
        other.joinedTime = other.joinedTime
        return other

    def __eq__(self, other):
        return self.cid == other.cid

    def __hash__(self):
        return self.cid

    def __repr__(self):
        return 'ChannelWrapper(cid={0[0]!r:s}, channelName={0[1]!r:s}, owner={1!r:s}, ownerName={0[2]!r:s}, isReadOnly={0[3]!r:s}, isSystem={0[4]!r:s}, isSecured={0[5]!r:s}, greeting={0[6]!r:s}, flags={0[7]!r:s}, notifyFlags={0[8]!r:s}, lazy={0[9]!r:s}, joined={2!r:s}, joinedTime={3!r:s}, hidden={4!r:s})'.format(self, self.owner, self.joined, self.joinedTime, self.hidden)


_MemberData = namedtuple('_MemberData', 'uid nickName')

class MemberWrapper(_MemberData):

    def __new__(cls, id=-1L, nickName='Unknown', status=0):
        result = _MemberData.__new__(cls, long(id), unicode(nickName, 'utf-8', errors='ignore'))
        result.status = int(status)
        return result

    def tuple(self):
        return (self.uid, self.nickName, self.status)

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return self.uid

    def __repr__(self):
        return 'MemberWrapper(uid=%r, nickName=%s, status=%d)' % (self.uid, self.nickName, self.status)


_SquadPlayerData = namedtuple('_SquadPlayerData', ' '.join(['accId',
 'name',
 'dbID',
 'time',
 'clanAbbrev']))

class SquadPlayerWrapper(_SquadPlayerData):

    def __new__(cls, id=-1L, name='Unknown', dbID=-1L, state=0, time=0, vehCompDescr='', clanAbbrev='', **kwargs):
        result = _SquadPlayerData.__new__(cls, id, name, dbID, time, clanAbbrev)
        result.state = state
        result.roles = 0
        result.vehCompDescr = vehCompDescr
        return result

    @property
    def vUserString(self):
        if self.vehCompDescr and len(self.vehCompDescr) > 0:
            return vehicles.VehicleDescr(compactDescr=self.vehCompDescr).type.shortUserString

    @property
    def isCommander(self):
        if self.roles is not None:
            return self.roles & constants.PREBATTLE_ROLE.SQUAD_CREATOR != 0
        else:
            return False

    @property
    def displayName(self):
        if self.clanAbbrev:
            return '%s[%s]' % (self.name, self.clanAbbrev)
        return self.name

    def __repr__(self):
        return 'SquadPlayerWrapper(accId=%r, name=%s, dbID= %d, state=%d, roles=%d, time=%f, vehCompDescr=%s, displayName=%s)' % (self.accId,
         self.name,
         self.dbID,
         self.state,
         self.roles,
         self.time,
         self.vehCompDescr,
         self.displayName)


_TeamPlayerData = namedtuple('_TeamPlayerData', ' '.join(['accId',
 'name',
 'dbID',
 'time',
 'clanAbbrev',
 'clanDBID']))

class TeamPlayerWrapper(_TeamPlayerData):

    def __new__(cls, id=-1L, name='Unknown', dbID=-1L, state=0, time=0, vehCompDescr='', clanAbbrev='', clanDBID=0, **kwargs):
        result = _TeamPlayerData.__new__(cls, id, name, dbID, time, clanAbbrev, clanDBID)
        result.state = state
        result.roles = 0
        result.vehCompDescr = vehCompDescr
        return result

    @property
    def vUserString(self):
        if self.vehCompDescr and len(self.vehCompDescr) > 0:
            return vehicles.VehicleDescr(compactDescr=self.vehCompDescr).type.shortUserString

    def __checkVehicleType(self, typeStrID):
        if self.vehCompDescr and len(self.vehCompDescr) > 0:
            return typeStrID in vehicles.VEHICLE_CLASS_TAGS.intersection(vehicles.VehicleDescr(compactDescr=self.vehCompDescr).type.tags)
        return False

    @property
    def isVehicleLightTank(self):
        return self.__checkVehicleType('lightTank')

    @property
    def isVehicleMediumTank(self):
        return self.__checkVehicleType('mediumTank')

    @property
    def isVehicleHeavyTank(self):
        return self.__checkVehicleType('heavyTank')

    @property
    def isVehicleSPG(self):
        return self.__checkVehicleType('SPG')

    @property
    def isVehicleATSPG(self):
        return self.__checkVehicleType('AT-SPG')

    @property
    def vLevel(self):
        if self.vehCompDescr and len(self.vehCompDescr) > 0:
            return vehicles.VehicleDescr(compactDescr=self.vehCompDescr).level

    @property
    def displayName(self):
        if self.clanAbbrev:
            return '%s[%s]' % (self.name, self.clanAbbrev)
        return self.name

    @property
    def vRomanLevel(self):
        return int2roman(self.vLevel)

    @property
    def isCommander(self):
        if self.roles is not None:
            return self.roles & constants.PREBATTLE_ROLE.COMPANY_CREATOR != 0
        else:
            return False

    def __repr__(self):
        return 'TeamPlayerWrapper(accId=%r, name=%s, dbID= %d, state=%d, roles=%d, time=%f, vehCompDescr=%s, displayName=%s)' % (self.accId,
         self.name,
         self.dbID,
         self.state,
         self.roles,
         self.time,
         self.vehCompDescr,
         self.displayName)


class UserWrapper(object):

    def __init__(self, *args):
        length = len(args)
        self.uid = long(args[0]) if length > 0 else -1L
        self.userName = args[1] if length > 1 else 'Unknown'
        self.roster = int(args[2]) if length > 2 else 0
        self.online = None
        self.clanName = None
        self.breaker = False
        self.himself = False
        return

    @staticmethod
    def fromSearchAction(*args):
        wrapper = UserWrapper()
        wrapper.uid = long(args[1])
        wrapper.userName = args[0]
        wrapper.roster = 0
        wrapper.online = bool(args[2])
        wrapper.clanName = args[3]
        return wrapper

    @property
    def displayName(self):
        if self.clanName:
            return '%s[%s]' % (self.userName, self.clanName)
        return self.userName

    def update(self, other):
        self.uid = other.uid
        self.userName = other.userName
        self.roster = other.roster

    def isFriend(self):
        return bool(self.roster & USERS_ROSTER_FRIEND)

    def isIgnored(self):
        return bool(self.roster & USERS_ROSTER_IGNORED)

    def isMuted(self):
        return bool(self.roster & USERS_ROSTER_VOICE_MUTED)

    def tuple(self):
        return (self.uid,
         self.userName,
         self.roster,
         self.online,
         self.himself,
         self.displayName)

    def list(self):
        return [self.uid,
         self.userName,
         self.roster,
         self.online,
         self.himself,
         self.displayName]

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return self.uid

    def __repr__(self):
        return 'UserWrapper(uid=%r, userName=%s, roster=%d, online=%s, himself=%s, displayName=%s)' % (self.uid,
         self.userName,
         self.roster,
         self.online,
         self.himself,
         self.displayName)


_ChatActionData = namedtuple('_ChatActionData', ' '.join(['action',
 'channel',
 'actionResponse',
 'group',
 'originator',
 'originatorNickName',
 'requestID',
 'time',
 'sentTime',
 'flags']))

class ChatActionWrapper(_ChatActionData):

    def __new__(cls, action=-1, channel=0, actionResponse=-1, group=0, originator=-1, originatorNickName='Unknown', requestID=-1, data=None, time=_time.time(), sentTime=_time.time(), flags=0, **kwargs):
        result = _ChatActionData.__new__(cls, action, channel, actionResponse, group, originator, unicode(originatorNickName, 'utf-8', errors='ignore'), requestID, time, sentTime, flags)
        result.data = unicode(data, 'utf-8', errors='ignore') if type(data) in types.StringTypes else data
        return result


_ServiceChannelData = namedtuple('_ServiceChannelData', ' '.join(['messageId',
 'userId',
 'type',
 'importance',
 'active',
 'personal',
 'sentTime',
 'startedAt',
 'finishedAt',
 'createdAt',
 'data']))

class ServiceChannelMessage(_ServiceChannelData):
    """
    Hold sysMessage and personalSysMessage actions data in chat system
    """

    @staticmethod
    def __new__(cls, messageID=-1L, user_id=-1L, type=-1, importance=SYS_MESSAGE_IMPORTANCE.normal.index(), active=True, personal=False, sentTime=_time.time(), started_at=None, finished_at=None, created_at=None, data=None, **kwargs):
        return _ServiceChannelData.__new__(cls, messageID, user_id, type, importance, active, personal, sentTime, started_at, finished_at, created_at, data)

    @property
    def isHighImportance(self):
        return self.importance == SYS_MESSAGE_IMPORTANCE.high.index()

    @classmethod
    def fromChatAction(cls, chatAction, personal=False):
        kwargs = dict(chatAction['data']) if chatAction.has_key('data') else {}
        kwargs['personal'] = personal
        kwargs['sentTime'] = chatAction['sentTime']
        return ServiceChannelMessage.__new__(cls, **kwargs)


_PrbInviteData = namedtuple('_PrbInviteData', ' '.join(['id',
 'createTime',
 'type',
 'comment',
 'creator',
 'creatorDBID',
 'receiver',
 'receiverDBID',
 'state',
 'count',
 'peripheryID',
 'anotherPeriphery']))

class PrbInviteWrapper(_PrbInviteData):

    @staticmethod
    def __new__(cls, id=-1L, createTime=None, type=0, comment=str(), creator=str(), creatorDBID=-1L, receiver=str(), receiverDBID=-1L, state=None, count=0, peripheryID=0, anotherPeriphery=False, **kwargs):
        if createTime is not None:
            createTime = time_utils.makeLocalServerTime(createTime)
        result = _PrbInviteData.__new__(cls, id, createTime, type, comment, creator, creatorDBID, receiver, receiverDBID, state, count, peripheryID, anotherPeriphery)
        return result

    def _merge(self, other):
        data = {}
        if other.createTime is not None:
            data['createTime'] = time_utils.makeLocalServerTime(other.createTime)
        if other.state > 0:
            data['state'] = other.state
        if other.count > 0:
            data['count'] = other.count
        if len(other.comment):
            data['comment'] = other.comment
        return self._replace(**data)

    def isPlayerSender(self):
        return False

    def isActive(self):
        return self.state == constants.PREBATTLE_INVITE_STATE.ACTIVE

    def opFlags(self):
        result = 0
        if self.isActive():
            if self.id > 0:
                result |= 1
            if not self.anotherPeriphery:
                result |= 2
        return result
