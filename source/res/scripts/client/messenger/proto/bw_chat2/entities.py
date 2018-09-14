# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/entities.py
from constants import PREBATTLE_TYPE_NAMES
from messenger.ext import channel_num_gen
from messenger.m_constants import PROTO_TYPE
from messenger.proto.bw_chat2.wrappers import ChannelProtoData, CHAT_TYPE
from messenger.proto.entities import ChannelEntity, MemberEntity

class _BWChannelEntity(ChannelEntity):

    def __init__(self, chatType, settings):
        super(_BWChannelEntity, self).__init__(ChannelProtoData(chatType, settings))
        self._isJoined = True

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2

    def isSystem(self):
        return True


class BWBattleChannelEntity(_BWChannelEntity):
    """Class of channel entity on arena. It's created for the client only."""

    def __init__(self, settings):
        super(BWBattleChannelEntity, self).__init__(CHAT_TYPE.ARENA, settings)

    def getID(self):
        return channel_num_gen.getClientID4BattleChannel(self.getName())

    def getName(self):
        return self.getProtoData().settings.name

    def getFullName(self):
        return self.getName()

    def isBattle(self):
        return True


class BWUnitChannelEntity(_BWChannelEntity):
    """Class of channel entity to unit. It's created for the client only."""

    def __init__(self, settings, prbType):
        super(BWUnitChannelEntity, self).__init__(CHAT_TYPE.UNIT, settings)
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
    """Class of member entity on unit. It's received from prebattle/unit."""

    def __init__(self, jid, nickName, status=None):
        super(BWMemberEntity, self).__init__(jid, nickName, status)

    def getDatabaseID(self):
        return self.getID()

    def getProtoType(self):
        return PROTO_TYPE.BW_CHAT2
