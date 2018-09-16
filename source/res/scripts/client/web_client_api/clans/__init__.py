# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/clans/__init__.py
from gui.shared.ClanCache import g_clanCache
from messenger.m_constants import USER_TAG
from messenger.proto.shared_find_criteria import MutualFriendsFindCriteria
from web_client_api import w2capi, w2c, W2CSchema

class _OnlineStatus(object):
    OFFLINE = 0
    ONLINE = 1
    BUSY = 2


@w2capi(name='clan_management', key='action')
class ClansWebApi(object):

    @w2c(W2CSchema, name='members_online')
    def membersOnline(self, cmd):
        members = g_clanCache.clanMembers
        onlineCount = 0
        for member in members:
            if member.isOnline():
                onlineCount += 1

        return {'action': 'members_online',
         'all_members': len(members),
         'online_members': onlineCount}

    @w2c(W2CSchema, name='members_status')
    def membersStatus(self, cmd):
        members = g_clanCache.clanMembers
        return {'action': 'members_status',
         'members_status': self._getStatuses(members)}

    @w2c(W2CSchema, name='friends_status')
    def friendsStatus(self, cmd):
        storage = g_clanCache.usersStorage
        friends = storage.getList(MutualFriendsFindCriteria(), iterator=storage.getClanMembersIterator(False))
        return {'action': 'friends_status',
         'friends_status': self._getStatuses(friends)}

    def _getStatuses(self, users):
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
