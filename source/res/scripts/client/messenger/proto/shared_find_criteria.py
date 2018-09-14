# Embedded file name: scripts/client/messenger/proto/shared_find_criteria.py
from debug_utils import LOG_WARNING
from messenger.m_constants import USER_TAG
from messenger.proto.interfaces import IEntityFindCriteria

class ProtoFindCriteria(IEntityFindCriteria):
    __slots__ = ('__protoType',)

    def __init__(self, protoType):
        super(ProtoFindCriteria, self).__init__()
        self.__protoType = protoType

    def filter(self, entity):
        return entity.getProtoType() == self.__protoType


class OnlineFindCriteria(IEntityFindCriteria):

    def __init__(self, onlineMode = None):
        super(OnlineFindCriteria, self).__init__()
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


class UserTagsFindCriteria(OnlineFindCriteria):

    def __init__(self, tags, onlineMode = None):
        super(UserTagsFindCriteria, self).__init__(onlineMode=onlineMode)
        self._tags = tags

    def addTags(self, tags):
        self._tags = self._tags.union(tags)

    def removeTags(self, tags):
        self._tags = self._tags.difference(tags)

    def filter(self, user):
        return user.getTags() & self._tags and self._checkOnlineMode(user)


class FriendsFindCriteria(UserTagsFindCriteria):

    def __init__(self, onlineMode = None):
        super(FriendsFindCriteria, self).__init__({USER_TAG.FRIEND}, onlineMode=onlineMode)


class PendingFriendsCandidatesFindCriteria(UserTagsFindCriteria):

    def __init__(self, onlineMode = None):
        super(PendingFriendsCandidatesFindCriteria, self).__init__({USER_TAG.SUB_PENDING_IN}, onlineMode)


class IgnoredFindCriteria(UserTagsFindCriteria):

    def __init__(self):
        super(IgnoredFindCriteria, self).__init__({USER_TAG.IGNORED}, onlineMode=None)
        return

    def setOnlineMode(self, onlineMode):
        if onlineMode is None:
            return super(IgnoredFindCriteria, self).setOnlineMode(onlineMode)
        else:
            LOG_WARNING('Online mode for ignored list will be skipped')
            return


class MutedFindCriteria(UserTagsFindCriteria):

    def __init__(self, onlineMode = None):
        super(MutedFindCriteria, self).__init__({USER_TAG.MUTED}, onlineMode=onlineMode)
