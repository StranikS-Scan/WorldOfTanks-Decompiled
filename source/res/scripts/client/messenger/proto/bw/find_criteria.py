# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw/find_criteria.py
from __future__ import absolute_import
import chat_shared
from messenger.m_constants import PROTO_TYPE, LAZY_CHANNEL
from messenger.proto.bw.entities import PREBATTLE_TYPE_CHAT_FLAG
from messenger.proto.interfaces import IEntityFindCriteria

class BWAllChannelFindCriteria(IEntityFindCriteria):

    def filter(self, entity):
        return entity.getProtoType() is PROTO_TYPE.BW


class BWPrbChannelFindCriteria(IEntityFindCriteria):

    def __init__(self, prbType):
        super(BWPrbChannelFindCriteria, self).__init__()
        self.__prbFlag = PREBATTLE_TYPE_CHAT_FLAG[prbType]

    def filter(self, entity):
        return entity.getProtoType() is PROTO_TYPE.BW and self.__prbFlag & entity.getProtoData().flags != 0


class BWLazyChannelFindCriteria(IEntityFindCriteria):

    def __init__(self, criteria):
        super(BWLazyChannelFindCriteria, self).__init__()
        if hasattr(criteria, '__iter__'):
            self.__channelsNames = criteria
        else:
            self.__channelsNames = []
            self.__channelsNames.append(criteria)

    def filter(self, entity):
        return entity.getProtoType() is PROTO_TYPE.BW and entity.getName() in self.__channelsNames


class BWActiveChannelFindCriteria(IEntityFindCriteria):

    def filter(self, entity):
        if entity.getProtoType() != PROTO_TYPE.BW:
            return False
        data = entity.getProtoData()
        flags = data.flags
        return entity.isJoined() and flags & chat_shared.CHAT_CHANNEL_BATTLE == 0 and (flags & chat_shared.CHAT_CHANNEL_PREBATTLE == 0 or flags & chat_shared.CHAT_CHANNEL_TRAINING != 0) and entity.getName() not in LAZY_CHANNEL.ALL


class BWClanChannelFindCriteria(IEntityFindCriteria):

    def filter(self, entity):
        return entity.getProtoType() is PROTO_TYPE.BW and entity.getProtoData().flags & chat_shared.CHAT_CHANNEL_CLAN != 0


class BWLobbyChannelFindCriteria(IEntityFindCriteria):

    def filter(self, entity):
        return entity.getProtoType() is PROTO_TYPE.BW and entity.getProtoData().flags & chat_shared.CHAT_CHANNEL_BATTLE == 0


class BWBattleChannelFindCriteria(IEntityFindCriteria):

    def filter(self, entity):
        return entity.getProtoType() is PROTO_TYPE.BW and entity.getProtoData().flags & chat_shared.CHAT_CHANNEL_BATTLE != 0


class BWBattleTeamChannelFindCriteria(IEntityFindCriteria):

    def filter(self, entity):
        result = False
        if entity.getProtoType() is PROTO_TYPE.BW:
            flags = entity.getProtoData().flags
            return flags & chat_shared.CHAT_CHANNEL_BATTLE != 0 and flags & chat_shared.CHAT_CHANNEL_BATTLE_TEAM != 0
        return result
