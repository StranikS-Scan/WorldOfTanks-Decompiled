# Embedded file name: scripts/client/messenger/proto/bw/entities.py
import cgi
import types
import chat_shared
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.shared.utils import getPlayerDatabaseID
from messenger.ext import passCensor
from messenger.proto.entities import ChannelEntity, MemberEntity, ChatEntity
from messenger.proto.entities import UserEntity
from messenger.m_constants import PROTO_TYPE, LAZY_CHANNEL, PRIMARY_CHANNEL_ORDER
from messenger.proto.bw.wrappers import ChannelDataWrapper
PREBATTLE_TYPE_CHAT_FLAG = {PREBATTLE_TYPE.SQUAD: chat_shared.CHAT_CHANNEL_SQUAD,
 PREBATTLE_TYPE.COMPANY: chat_shared.CHAT_CHANNEL_TEAM,
 PREBATTLE_TYPE.TRAINING: chat_shared.CHAT_CHANNEL_TRAINING,
 PREBATTLE_TYPE.CLAN: chat_shared.CHAT_CHANNEL_PREBATTLE_CLAN,
 PREBATTLE_TYPE.TOURNAMENT: chat_shared.CHAT_CHANNEL_TOURNAMENT,
 PREBATTLE_TYPE.UNIT: chat_shared.CHAT_CHANNEL_UNIT,
 PREBATTLE_TYPE.SORTIE: chat_shared.CHAT_CHANNEL_UNIT}
PREBATTLE_CHAT_FLAG_TYPE = dict(((v, k) for k, v in PREBATTLE_TYPE_CHAT_FLAG.iteritems()))

class BWChannelEntity(ChannelEntity):
    __slots__ = ('_nameToInvalidate',)

    def __init__(self, data):
        if type(data) is not types.DictType:
            LOG_ERROR('Invalid data', data)
            data = {}
        super(BWChannelEntity, self).__init__(ChannelDataWrapper(**data))
        self._nameToInvalidate = self.getFullName()

    def getID(self):
        return self._data.id

    def getProtoType(self):
        return PROTO_TYPE.BW

    def getName(self):
        channelName = self._data.channelName
        if getPlayerDatabaseID() != self._data.owner:
            channelName = passCensor(channelName)
        return cgi.escape(channelName)

    def getFullName(self):
        name = self.getName()
        if not self._data.isSystem:
            name = u'{0:>s}({1:>s})'.format(name, self._data.ownerName)
        return name

    def isSystem(self):
        return self._data.isSystem

    def isPrivate(self):
        return self._data.flags & chat_shared.CHAT_CHANNEL_PRIVATE != 0

    def isBattle(self):
        return self._data.flags & chat_shared.CHAT_CHANNEL_BATTLE != 0

    def isPrebattle(self):
        return self._data.flags & chat_shared.CHAT_CHANNEL_PREBATTLE != 0

    def getPrebattleType(self):
        if not self.isPrebattle():
            return 0
        result = 0
        flags = self._data.flags
        for prbType, prbFlag in PREBATTLE_TYPE_CHAT_FLAG.iteritems():
            if flags & prbFlag != 0:
                result = prbType
                break

        return result

    def getPrimaryOrder(self):
        if self.getName() in LAZY_CHANNEL.ALL:
            primary = PRIMARY_CHANNEL_ORDER.LAZY
        elif self._data.flags & chat_shared.CHAT_CHANNEL_CLAN > 0:
            primary = PRIMARY_CHANNEL_ORDER.CLAN
        elif self._data.isSystem:
            primary = PRIMARY_CHANNEL_ORDER.SYSTEM
        else:
            primary = PRIMARY_CHANNEL_ORDER.OTHER
        return primary

    def getHistory(self):
        history = super(BWChannelEntity, self).getHistory()
        if self._data.greeting:
            history.insert(0, self._data.greeting)
        return history

    def haveMembers(self):
        listMode = chat_shared.getMembersListMode(self._data.notifyFlags)
        return listMode in (chat_shared.CHAT_CHANNEL_NOTIFY_MEMBERS_IN_OUT, chat_shared.CHAT_CHANNEL_NOTIFY_MEMBERS_DELTA)

    def update(self, **kwargs):
        if 'other' in kwargs:
            self._data = kwargs['other'].getProtoData()
            self.onChannelInfoUpdated(self)

    def invalidateName(self):
        newValue = self.getFullName()
        result = False
        if self._nameToInvalidate != newValue:
            self._nameToInvalidate = newValue
            self.onChannelInfoUpdated(self)
            result = True
        return result


class BWChannelLightEntity(ChatEntity):
    __slots__ = ('__channelID',)

    def __init__(self, channelID):
        super(BWChannelLightEntity, self).__init__()
        self.__channelID = channelID

    def getID(self):
        return self.__channelID

    def setID(self, channelID):
        self.__channelID = channelID

    def getProtoType(self):
        return PROTO_TYPE.BW


class BWMemberEntity(MemberEntity):

    def __init__(self, memberID, nickName = 'Unknown', status = None):
        if nickName and type(nickName) is not types.UnicodeType:
            nickName = unicode(nickName, 'utf-8', errors='ignore')
        super(BWMemberEntity, self).__init__(memberID, nickName, status)

    def getProtoType(self):
        return PROTO_TYPE.BW


class BWUserEntity(UserEntity):
    __slots__ = ('_isOnline',)

    def __init__(self, databaseID, name = None, tags = None, isOnline = False, clanInfo = None):
        super(BWUserEntity, self).__init__(databaseID, name, tags, clanInfo)
        self._isOnline = isOnline

    def __repr__(self):
        return 'BWUserEntity(dbID={0!r:s}, fullName={1:>s}, tags={2!r:s}, isOnline={3!r:s}, clanInfo={4!r:s})'.format(self._databaseID, self.getFullName(), self.getTags(), self.isOnline(), self._clanInfo)

    def getProtoType(self):
        return PROTO_TYPE.BW

    def isOnline(self):
        if self.isIgnored():
            return False
        return self._isOnline

    def update(self, **kwargs):
        if 'isOnline' in kwargs:
            self._isOnline = kwargs['isOnline']
        super(BWUserEntity, self).update(**kwargs)

    def clear(self):
        self._isOnline = False
        super(BWUserEntity, self).clear()
