# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/social/__init__.py
from gui.shared.view_helpers import UsersInfoHelper
from messenger.m_constants import USER_TAG
from messenger.proto.shared_find_criteria import MutualFriendsFindCriteria
from messenger.storage import storage_getter
from web_client_api import w2capi, w2c, W2CSchema, Field
from web_client_api.common import SPA_ID_TYPES

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


class _PlayerStatusSchema(W2CSchema):
    player_id = Field(required=True, type=SPA_ID_TYPES)


@w2capi(name='social', key='action')
class SocialWebApi(object):

    def __init__(self):
        super(SocialWebApi, self).__init__()
        self.__usersInfoHelper = UsersInfoHelper()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @w2c(W2CSchema, name='friends_status')
    def friendsStatus(self, cmd):
        storage = self.usersStorage
        friends = storage.getList(MutualFriendsFindCriteria())
        return {'action': 'friends_status',
         'friends_status': getStatuses(friends)}

    @w2c(_PlayerStatusSchema, name='player_status')
    def isPlayerOnline(self, cmd, ctx):
        callback = ctx.get('callback')
        playerId = cmd.player_id

        def isAvailable():
            player = self.__usersInfoHelper.getContact(playerId)
            return {'is_online': player.isOnline() if player is not None else False}

        def onNamesReceivedCallback():
            callback(isAvailable())
            self.__usersInfoHelper.onNamesReceived -= onNamesReceivedCallback

        if not bool(self.__usersInfoHelper.getUserName(playerId)):
            self.__usersInfoHelper.onNamesReceived += onNamesReceivedCallback
            self.__usersInfoHelper.syncUsersInfo()
        else:
            return isAvailable()
