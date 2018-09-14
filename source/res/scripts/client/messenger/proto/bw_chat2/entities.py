# Embedded file name: scripts/client/messenger/proto/bw_chat2/entities.py
from constants import PREBATTLE_TYPE_NAMES
from messenger.ext import channel_num_gen
from messenger.m_constants import PROTO_TYPE
from messenger.proto.entities import ChannelEntity, MemberEntity

class _BWChannelEntity(ChannelEntity):

    def __init__(self, data):
        super(_BWChannelEntity, self).__init__(data)
        self._isJoined = True

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def isSystem(self):
        return True


class BWBattleChannelEntity(_BWChannelEntity):

    def getID(self):
        return channel_num_gen.getClientID4BattleChannel(self.getName())

    def getName(self):
        return self.getProtoData().name

    def getFullName(self):
        return self.getName()

    def isBattle(self):
        return True


class BWUnitChannelEntity(_BWChannelEntity):

    def __init__(self, data, prbType):
        super(BWUnitChannelEntity, self).__init__(data)
        self._prbType = prbType

    def getID(self):
        return channel_num_gen.getClientID4Prebattle(self._prbType)

    def getName(self):
        return '#chat:channels/{0}'.format(PREBATTLE_TYPE_NAMES[self._prbType].lower())

    def getFullName(self):
        return self.getName()

    def isPrebattle(self):
        return True

    def getPrebattleType(self):
        return self._prbType


class BWMemberEntity(MemberEntity):

    def __init__(self, memberID, nickName, status = None):
        super(BWMemberEntity, self).__init__(memberID, nickName, status)

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2
