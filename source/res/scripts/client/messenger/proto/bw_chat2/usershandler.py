# Embedded file name: scripts/client/messenger/proto/bw_chat2/UsersHandler.py
from messenger.m_constants import GAME_ONLINE_STATUS
from messenger.proto.bw_chat2 import provider, limits
from messenger.proto.bw_chat2.wrappers import SearchResultIterator
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS, messageArgs
from debug_utils import LOG_WARNING
from messenger.storage import storage_getter

class UsersHandler(provider.ResponseDictHandler):

    def __init__(self, provider):
        super(UsersHandler, self).__init__(provider)
        self.__limits = limits.FindUserLimits()

    @storage_getter('users')
    def usersStorage(self):
        return None

    def findUsers(self, namePattern, searchOnlineOnly = None):
        provider = self.provider()
        if searchOnlineOnly is None:
            searchOnlineOnly = False
        success, reqID = provider.doAction(_ACTIONS.FIND_USERS_BY_NAME, messageArgs(strArg1=namePattern, int32Arg1=self.__limits.getMaxResultSize(), int64Arg1=searchOnlineOnly), response=True)
        if reqID:
            self.pushRq(reqID, _ACTIONS.FIND_USERS_BY_NAME)
        if success:
            cooldown = self.__limits.getRequestCooldown()
            provider.setActionCoolDown(_ACTIONS.FIND_USERS_BY_NAME, cooldown)
        return (success, reqID)

    def clear(self):
        super(UsersHandler, self).clear()
        self.__limits = None
        return

    def _onResponseSuccess(self, ids, args):
        if not super(UsersHandler, self)._onResponseSuccess(ids, args):
            return
        users = []
        for received in SearchResultIterator(args):
            user = self.usersStorage.getUser(received.getID())
            if user:
                if user.isCurrentPlayer():
                    received = user
                elif user.isOnline():
                    received.update(tags=user.getTags(), gosBit=GAME_ONLINE_STATUS.IN_SEARCH)
                else:
                    received.update(tags=user.getTags())
            users.append(received)

        g_messengerEvents.users.onFindUsersComplete(ids[1], users)

    def _onResponseFailure(self, ids, args):
        actionID = super(UsersHandler, self)._onResponseFailure(ids, args)
        if actionID is None:
            return
        else:
            if actionID == _ACTIONS.FIND_USERS_BY_NAME:
                g_messengerEvents.users.onFindUsersFailed(ids[1], args)
            else:
                LOG_WARNING('Error is not resolved on the client', ids, args)
            return
