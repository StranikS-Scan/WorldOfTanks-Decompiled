# Embedded file name: scripts/client/gui/shared/view_helpers/UsersInfoController.py
import BigWorld
from AccountCommands import isCodeValid
from debug_utils import LOG_WARNING
from shared_utils import CONST_CONTAINER
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx
from gui.shared.utils.requesters.RequestsController import RequestsController
from messenger.storage import storage_getter
from messenger.proto import proto_getter, PROTO_TYPE
_GR_MAX_CHUNK_SIZE = 20
_NAMES_MAX_CHUNK_SIZE = 50

class USER_INFO_RQ_TYPE(CONST_CONTAINER):
    GET_GLOBAL_RATINGS = 1
    GET_NICKNAMES = 2


@ReprInjector.withParent(('getDbIDs', 'dbIDs'))

class _GetGlobalRatingCtx(RequestCtx):

    def __init__(self, dbIDs, waitingID = ''):
        super(_GetGlobalRatingCtx, self).__init__(waitingID=waitingID)
        self.__dbIDs = dbIDs

    def getDbIDs(self):
        return self.__dbIDs

    def getRequestType(self):
        return USER_INFO_RQ_TYPE.GET_GLOBAL_RATINGS

    def getCooldown(self):
        return 2.0


@ReprInjector.withParent(('getDbIDs', 'dbIDs'))

class _GetNicknamesCtx(RequestCtx):

    def __init__(self, dbIDs, waitingID = ''):
        super(_GetNicknamesCtx, self).__init__(waitingID=waitingID)
        self.__dbIDs = dbIDs

    def getDbIDs(self):
        return self.__dbIDs

    def getRequestType(self):
        return USER_INFO_RQ_TYPE.GET_NICKNAMES

    def getCooldown(self):
        return 2.0


class UsersInfoController(RequestsController):

    def __init__(self):
        super(UsersInfoController, self).__init__(None)
        self.__handlers = {USER_INFO_RQ_TYPE.GET_GLOBAL_RATINGS: self._getGlobalRatings,
         USER_INFO_RQ_TYPE.GET_NICKNAMES: self._getNicknames}
        return

    def fini(self):
        self.__handlers.clear()
        super(UsersInfoController, self).fini()

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    @storage_getter('users')
    def users(self):
        return None

    def requestNicknames(self, accountDbIDs, callback):
        while len(accountDbIDs):
            self.request(_GetNicknamesCtx(accountDbIDs[:_NAMES_MAX_CHUNK_SIZE]), callback, allowDelay=True)
            del accountDbIDs[:_NAMES_MAX_CHUNK_SIZE]

    def requestGlobalRatings(self, accountDbIDs, callback):
        while len(accountDbIDs):
            self.request(_GetGlobalRatingCtx(accountDbIDs[:_GR_MAX_CHUNK_SIZE]), callback, allowDelay=True)
            del accountDbIDs[:_GR_MAX_CHUNK_SIZE]

    def _getGlobalRatings(self, ctx, callback = None):
        getter = self.users.getUser

        def _ratingsCallback(code, errStr, ratings):
            if isCodeValid(code):
                for userDbID, rating in (ratings or {}).iteritems():
                    user = getter(userDbID)
                    if user:
                        user.update(globalRating=rating)

            else:
                LOG_WARNING('Error occurred while getting global ratings from server', code, errStr, ratings)
            callback(ratings or {})

        BigWorld.player().requestPlayersGlobalRating(ctx.getDbIDs(), _ratingsCallback)
        return True

    def _getNicknames(self, ctx, callback = None):
        return self.proto.nicknames.resolve(ctx.getDbIDs(), callback)

    def _getHandlerByRequestType(self, requestTypeID):
        return self.__handlers.get(requestTypeID)

    def _getRequestTimeOut(self):
        return 30.0
