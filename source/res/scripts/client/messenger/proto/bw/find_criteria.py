# Embedded file name: scripts/client/messenger/proto/bw/find_criteria.py
import chat_shared
from debug_utils import LOG_WARNING
from messenger.m_constants import PREBATTLE_TYPE_CHAT_FLAG, PROTO_TYPE, LAZY_CHANNEL
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
        data = channel.getProtoData()
        flags = data.flags
        return channel.getProtoType() is PROTO_TYPE.BW and channel.isJoined() and flags & chat_shared.CHAT_CHANNEL_BATTLE == 0 and (flags & chat_shared.CHAT_CHANNEL_PREBATTLE == 0 or flags & chat_shared.CHAT_CHANNEL_TRAINING != 0) and channel.getName() not in LAZY_CHANNEL.ALL


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


class BWOnlineFindCriteria(IEntityFindCriteria):

    def __init__(self, onlineMode = None):
        super(BWOnlineFindCriteria, self).__init__()
        self.__onlineMode = onlineMode

    def getOnlineMode(self):
        return self.__onlineMode

    def setOnlineMode(self, onlineMode):
        result = onlineMode != self.__onlineMode
        if result:
            self.__onlineMode = onlineMode
        return result

    def filter(self, user):
        return self._checkOnlineMode(user)

    def _checkOnlineMode(self, user):
        result = True
        if self.__onlineMode is not None:
            result = self.__onlineMode is user.isOnline()
        return result


class BWRosterFindCriteria(BWOnlineFindCriteria):

    def __init__(self, roster, onlineMode = None):
        super(BWRosterFindCriteria, self).__init__(onlineMode=onlineMode)
        self.__roster = roster

    def filter(self, user):
        return user.getRoster() & self.__roster != 0 and self._checkOnlineMode(user)


class BWFriendFindCriteria(BWRosterFindCriteria):

    def __init__(self, onlineMode = None):
        super(BWFriendFindCriteria, self).__init__(chat_shared.USERS_ROSTER_FRIEND, onlineMode=onlineMode)


class BWIgnoredFindCriteria(BWRosterFindCriteria):

    def __init__(self):
        super(BWIgnoredFindCriteria, self).__init__(chat_shared.USERS_ROSTER_IGNORED, onlineMode=None)
        return

    def setOnlineMode(self, onlineMode):
        if onlineMode is None:
            return super(BWIgnoredFindCriteria, self).setOnlineMode(onlineMode)
        else:
            LOG_WARNING('Online mode for ignored list will be skipped')
            return


class BWMutedFindCriteria(BWRosterFindCriteria):

    def __init__(self, onlineMode = None):
        super(BWMutedFindCriteria, self).__init__(chat_shared.USERS_ROSTER_VOICE_MUTED, onlineMode=onlineMode)
