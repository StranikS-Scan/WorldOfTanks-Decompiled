# Embedded file name: scripts/client/messenger/proto/xmpp/xmpp_search_processors.py
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.search_processor import SearchProcessor
from messenger.proto.xmpp.gloox_constants import GLOOX_EVENT
from messenger.proto.xmpp.xmpp_constants import CHANNEL_LIMIT
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler
from messenger.proto.xmpp.extensions.search import ChannelSearchQuery, ChannelsListHandler

class SearchChannelsProcessor(SearchProcessor, ClientEventsHandler):

    def __init__(self):
        super(SearchChannelsProcessor, self).__init__()
        self.__sentRequestID = None
        self.__channelSearchAddress = ''
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
            query = ChannelSearchQuery(token, to=self.__channelSearchAddress, count=self.getSearchResultLimit())
            self._lastRequestID = client.sendIQ(query)
        else:
            self._onSearchFailed('XMPP Client is not connected')

    def getSearchResultLimit(self):
        return CHANNEL_LIMIT.MAX_SEARCH_RESULTS

    def __onIQReceived(self, iqID, _, pyGlooxTag):
        result = ChannelsListHandler().handleTag(pyGlooxTag)
        self._onSearchTokenComplete(iqID, list(result))
