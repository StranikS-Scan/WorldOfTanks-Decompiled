# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/migration/messages.py
from messenger.m_constants import LAZY_CHANNEL
from messenger.proto.bw import bw_chat_string_utils
from messenger.proto.events import g_messengerEvents
from messenger.proto.migration.proxy import MigrationProxy
from messenger.proto.xmpp import xmpp_string_utils
from messenger.proto.xmpp.jid import JID

class MessagesManagerProxy(MigrationProxy):
    __slots__ = ()

    def getSearchUserRoomsProcessor(self):
        raise NotImplementedError

    def getUserRoomValidator(self):
        raise NotImplementedError

    def createUserRoom(self, name, password=''):
        raise NotImplementedError

    def joinToUserRoom(self, roomID, name, password=''):
        raise NotImplementedError

    def getCompanyRoomName(self):
        raise NotImplementedError


class BWMessagesManagerProxy(MessagesManagerProxy):
    __slots__ = ()

    def __init__(self, proto):
        super(BWMessagesManagerProxy, self).__init__(proto)

    def getSearchUserRoomsProcessor(self):
        from messenger.proto.bw import search_processors
        return search_processors.SearchChannelsProcessor()

    def getUserRoomValidator(self):
        return bw_chat_string_utils

    def createUserRoom(self, name, password=''):
        self._proto.channels.createChannel(name, password)
        return True

    def joinToUserRoom(self, roomID, name, password=''):
        self._proto.channels.joinToChannel(roomID, password)
        return True

    def getCompanyRoomName(self):
        return LAZY_CHANNEL.COMPANIES


class XMPPMessagesManagerProxy(MessagesManagerProxy):
    __slots__ = ()

    def __init__(self, proto):
        super(XMPPMessagesManagerProxy, self).__init__(proto)

    def getSearchUserRoomsProcessor(self):
        from messenger.proto.xmpp import xmpp_search_processors
        return xmpp_search_processors.SearchUserRoomsProcessor()

    def getUserRoomValidator(self):
        return xmpp_string_utils

    def createUserRoom(self, name, password=''):
        result, error = self._proto.messages.createUserRoom(name, password)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def joinToUserRoom(self, roomID, name, password=''):
        result, error = self._proto.messages.joinToMUC(JID(roomID), password=password, name=name)
        if not result:
            g_messengerEvents.onErrorReceived(error)
        return result

    def getCompanyRoomName(self):
        return LAZY_CHANNEL.XMPP_COMPANIES
