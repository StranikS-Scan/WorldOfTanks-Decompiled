# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/search_processor.py
from debug_utils import LOG_WARNING
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.search_processor import SearchProcessor
from messenger.proto.bw_chat2 import limits
from messenger.ext import checkAccountName
from messenger.proto.bw_chat2 import errors

class SearchUsersProcessor(SearchProcessor):

    def __init__(self):
        super(SearchUsersProcessor, self).__init__()
        self.__limits = limits.FindUserLimits()

    def init(self):
        super(SearchUsersProcessor, self).init()
        g_messengerEvents.users.onFindUsersComplete += self.__um_onSearchTokenComplete
        g_messengerEvents.users.onFindUsersFailed += self.__um_onSearchTokenFailed

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto(self):
        return None

    def getSearchResultLimit(self):
        return self.__limits.getMaxResultSize()

    def getSearchCoolDown(self):
        return self.__limits.getRequestCooldown()

    def find(self, token, onlineMode=None):
        token = token.strip()
        isCorrect, reason = checkAccountName(token)
        if not isCorrect:
            self._onSearchFailed(reason)
            return False
        success, reqID = self.proto.users.findUsers(token, onlineMode)
        self._lastRequestID = reqID
        return success

    def fini(self):
        super(SearchUsersProcessor, self).fini()
        g_messengerEvents.users.onFindUsersComplete -= self.__um_onSearchTokenComplete
        g_messengerEvents.users.onFindUsersFailed -= self.__um_onSearchTokenFailed

    def __um_onSearchTokenComplete(self, requestID, result):
        self._onSearchTokenComplete(requestID, result)

    def __um_onSearchTokenFailed(self, requestID, args):
        if self._lastRequestID == requestID:
            error = errors.createSearchUserError(args)
            if error:
                reason = error.getMessage()
            else:
                reason = ''
                LOG_WARNING('Search error is not resolved on the client', args)
            self._onSearchFailed(reason)
