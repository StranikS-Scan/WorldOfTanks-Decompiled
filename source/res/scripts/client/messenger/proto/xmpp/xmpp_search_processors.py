# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_search_processors.py
from debug_utils import LOG_WARNING
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE, CLIENT_ACTION_ID, CLIENT_ERROR_ID
from messenger.proto import proto_getter
from messenger.proto.search_processor import SearchProcessor
from messenger.proto.shared_errors import ClientActionError
from messenger.proto.xmpp.errors import createServerActionIQError
from messenger.proto.xmpp.gloox_constants import GLOOX_EVENT, IQ_TYPE
from messenger.proto.xmpp.xmpp_constants import CHANNEL_LIMIT
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler
from messenger.proto.xmpp.extensions.search import ChannelSearchQuery, ChannelsListHandler

class SearchChannelsProcessor(SearchProcessor, ClientEventsHandler):

    def __init__(self, service):
        super(SearchChannelsProcessor, self).__init__()
        self.__sentRequestID = None
        self.__service = service
        self.proto.client.registerHandler(GLOOX_EVENT.IQ, self.__onIQReceived)
        return

    def __del__(self):
        super(SearchChannelsProcessor, self).__init__()
        self.proto.client.unregisterHandler(GLOOX_EVENT.IQ, self.__onIQReceived)

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    def find(self, token, **kwargs):
        client = self.proto.client
        if client.isConnected():
            query = ChannelSearchQuery(token, to=self.__service, count=self.getSearchResultLimit())
            self._lastRequestID = client.sendIQ(query)
        else:
            error = ClientActionError(CLIENT_ACTION_ID.SEARCH_USER_ROOM, CLIENT_ERROR_ID.NOT_CONNECTED)
            self._onSearchFailed(error.getMessage())

    def getSearchResultLimit(self):
        return CHANNEL_LIMIT.MAX_SEARCH_RESULTS

    def __onIQReceived(self, iqID, iqType, pyGlooxTag):
        if self._lastRequestID != iqID:
            return
        if iqType == IQ_TYPE.ERROR:
            error = createServerActionIQError(CLIENT_ACTION_ID.SEARCH_USER_ROOM, pyGlooxTag)
            if error:
                reason = error.getMessage()
            else:
                reason = ''
                LOG_WARNING('Search error is not resolved on the client', pyGlooxTag.getXml())
            self._onSearchFailed(reason)
        else:
            result = ChannelsListHandler().handleTag(pyGlooxTag)
            self._onSearchTokenComplete(iqID, list(result))


class SearchUserRoomsProcessor(SearchChannelsProcessor):

    def __init__(self):
        super(SearchUserRoomsProcessor, self).__init__(g_settings.server.XMPP.userRoomsService)
