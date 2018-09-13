# Embedded file name: scripts/client/messenger/proto/bw/entities.py
import types
import chat_shared
from debug_utils import LOG_ERROR
from messenger.ext import passCensor
from messenger.proto.entities import ChannelEntity, MemberEntity, ChatEntity
from messenger.proto.entities import UserEntity
from messenger.m_constants import PROTO_TYPE, PREBATTLE_TYPE_CHAT_FLAG
from messenger.ext.player_helpers import getPlayerDatabaseID
from messenger.proto.bw.wrappers import ChannelDataWrapper

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
        return channelName

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

    def isFriend(self):
        return bool(self._roster & chat_shared.USERS_ROSTER_FRIEND)

    def isIgnored(self):
        return bool(self._roster & chat_shared.USERS_ROSTER_IGNORED)

    def isMuted(self):
        return bool(self._roster & chat_shared.USERS_ROSTER_VOICE_MUTED)
