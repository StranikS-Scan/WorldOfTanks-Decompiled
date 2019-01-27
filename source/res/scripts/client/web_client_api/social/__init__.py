# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/social/__init__.py
from messenger.m_constants import USER_TAG
from messenger.proto.shared_find_criteria import MutualFriendsFindCriteria
from messenger.storage import storage_getter
from web_client_api import w2capi, w2c, W2CSchema

class _OnlineStatus(object):
    OFFLINE = 0
    ONLINE = 1
    BUSY = 2


def getStatuses(users):
    statuses = {}
    for user in users:
        if user.isOnline():
            if USER_TAG.PRESENCE_DND in user.getTags():
                status = _OnlineStatus.BUSY
            else:
                status = _OnlineStatus.ONLINE
        else:
            status = _OnlineStatus.OFFLINE
        statuses[user.getID()] = status

    return statuses


@w2capi(name='social', key='action')
class SocialWebApi(object):

    @storage_getter('users')
    def usersStorage(self):
        return None

    @w2c(W2CSchema, name='friends_status')
    def friendsStatus(self, cmd):
        storage = self.usersStorage
        friends = storage.getList(MutualFriendsFindCriteria())
        return {'action': 'friends_status',
         'friends_status': getStatuses(friends)}
