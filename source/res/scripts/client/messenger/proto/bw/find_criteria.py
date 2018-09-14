# Embedded file name: scripts/client/messenger/proto/bw/find_criteria.py
import chat_shared
from messenger.m_constants import PROTO_TYPE, LAZY_CHANNEL
from messenger.proto.bw.entities import PREBATTLE_TYPE_CHAT_FLAG
from messenger.proto.interfaces import IEntityFindCriteria

class BWAllChannelFindCriteria(IEntityFindCriteria):

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW


class BWPrbChannelFindCriteria(IEntityFindCriteria):

    def __init__(self, prbType):
        super(BWPrbChannelFindCriteria, self).__init__()
        self.__prbFlag = PREBATTLE_TYPE_CHAT_FLAG[prbType]

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW and self.__prbFlag & channel.getProtoData().flags != 0


class BWLazyChannelFindCriteria(IEntityFindCriteria):

    def __init__(self, criteria):
        super(BWLazyChannelFindCriteria, self).__init__()
        if hasattr(criteria, '__iter__'):
            self.__channelsNames = criteria
        else:
            self.__channelsNames = []
            self.__channelsNames.append(criteria)

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW and channel.getName() in self.__channelsNames


class BWActiveChannelFindCriteria(IEntityFindCriteria):

    def filter(self, channel):
        if channel.getProtoType() != PROTO_TYPE.BW:
            return False
        data = channel.getProtoData()
        flags = data.flags
        return channel.isJoined() and flags & chat_shared.CHAT_CHANNEL_BATTLE == 0 and (flags & chat_shared.CHAT_CHANNEL_PREBATTLE == 0 or flags & chat_shared.CHAT_CHANNEL_TRAINING != 0) and channel.getName() not in LAZY_CHANNEL.ALL


class BWClanChannelFindCriteria(IEntityFindCriteria):

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW and channel.getProtoData().flags & chat_shared.CHAT_CHANNEL_CLAN != 0


class BWLobbyChannelFindCriteria(IEntityFindCriteria):

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW and channel.getProtoData().flags & chat_shared.CHAT_CHANNEL_BATTLE == 0


class BWBattleChannelFindCriteria(IEntityFindCriteria):

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW and channel.getProtoData().flags & chat_shared.CHAT_CHANNEL_BATTLE != 0


class BWBattleTeamChannelFindCriteria(IEntityFindCriteria):

    def filter(self, channel):
        result = False
        if channel.getProtoType() is PROTO_TYPE.BW:
            flags = channel.getProtoData().flags
            return flags & chat_shared.CHAT_CHANNEL_BATTLE != 0 and flags & chat_shared.CHAT_CHANNEL_BATTLE_TEAM != 0
        return result
