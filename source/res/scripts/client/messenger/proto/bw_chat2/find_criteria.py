# Embedded file name: scripts/client/messenger/proto/bw_chat2/find_criteria.py
from constants import PREBATTLE_TYPE
from messenger.ext import channel_num_gen
from messenger.m_constants import BATTLE_CHANNEL, PROTO_TYPE
from messenger.proto.interfaces import IEntityFindCriteria

class BWBattleChannelFindCriteria(IEntityFindCriteria):

    def __init__(self):
        super(BWBattleChannelFindCriteria, self).__init__()
        self.__ids = []
        for item in BATTLE_CHANNEL.ALL:
            clientID = channel_num_gen.getClientID4BattleChannel(item.name)
            if clientID:
                self.__ids.append(clientID)

        clientID = channel_num_gen.getClientID4Prebattle(PREBATTLE_TYPE.SQUAD)
        if clientID:
            self.__ids.append(clientID)

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW_CHAT2 and channel.getClientID() in self.__ids


class BWPrebattleChannelFindCriteria(IEntityFindCriteria):

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW_CHAT2 and channel.getPrebattleType()


class BWChatTypeFindCriteria(IEntityFindCriteria):

    def __init__(self, chatType):
        super(BWChatTypeFindCriteria, self).__init__()
        self.__chatType = chatType

    def filter(self, channel):
        return channel.getProtoType() is PROTO_TYPE.BW_CHAT2 and channel.getProtoData().chatType == self.__chatType
