# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/wgcg/requests.py
import types
from shared_utils import CONST_CONTAINER
from gui.shared.utils.requesters.abstract import Response, ClientRequestsByIDProcessor
from gui.shared.utils.requesters.RequestsController import RequestsController
from client_request_lib.exceptions import ResponseCodes

class SERVER_SIDE_REPLAY_REQUEST_TYPE(CONST_CONTAINER):
    GET_BEST_REPLAYS = 1
    GET_TOP_REPLAYS = 2
    GET_REPLAY_LINK = 3
    POST_FIND_REPLAY = 4


class ServerSideReplayRequestResponse(Response):

    def isSuccess(self):
        return self.getCode() == ResponseCodes.NO_ERRORS

    def getCode(self):
        return self.code

    def clone(self, data=None):
        return ServerSideReplayRequestResponse(self.code, self.txtStr, data or self.data)

    def mergeData(self, data):
        self.data.update(data)


class ServerSideReplayRequester(ClientRequestsByIDProcessor):

    def __init__(self, sender):
        super(ServerSideReplayRequester, self).__init__(sender, ServerSideReplayRequestResponse)

    def _getSenderMethod(self, sender, methodName):
        if isinstance(methodName, types.TupleType):
            storageName, methodName = methodName
            sender = getattr(sender, storageName, None)
        return super(ServerSideReplayRequester, self)._getSenderMethod(sender, methodName)

    def _doCall(self, method, *args, **kwargs):
        requestID = self._idsGenerator.next()

        def _callback(data, statusCode, responseCode, headers):
            ctx = self._requests[requestID]
            response = self._makeResponse(responseCode, '', data, ctx, extraCode=statusCode, headers=headers)
            self._onResponseReceived(requestID, response)

        method(_callback, *args, **kwargs)
        return requestID


class ServerSideReplayRequestsController(RequestsController):

    def __init__(self, requester):
        super(ServerSideReplayRequestsController, self).__init__(requester)
        self.__handlers = {SERVER_SIDE_REPLAY_REQUEST_TYPE.GET_BEST_REPLAYS: self.__getBestReplays,
         SERVER_SIDE_REPLAY_REQUEST_TYPE.GET_TOP_REPLAYS: self.__getTopReplays,
         SERVER_SIDE_REPLAY_REQUEST_TYPE.GET_REPLAY_LINK: self.__getReplayLink,
         SERVER_SIDE_REPLAY_REQUEST_TYPE.POST_FIND_REPLAY: self.__postFindReplay}

    def fini(self):
        self.__handlers.clear()
        super(ServerSideReplayRequestsController, self).fini()

    def _getHandlerByRequestType(self, requestTypeID):
        return self.__handlers.get(requestTypeID) if self.__handlers else None

    def __getBestReplays(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('server_replays', 'get_best_replays'), jwt_token=ctx.jwtToken, **ctx.getRequestKwargs())

    def __getTopReplays(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('server_replays', 'get_top_replays'), jwt_token=ctx.jwtToken)

    def __getReplayLink(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('server_replays', 'get_replay_link'), jwt_token=ctx.jwtToken, replay_id=ctx.getReplayID())

    def __postFindReplay(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('server_replays', 'post_find_replay'), jwt_token=ctx.jwtToken, replay_name=ctx.getReplayName())
