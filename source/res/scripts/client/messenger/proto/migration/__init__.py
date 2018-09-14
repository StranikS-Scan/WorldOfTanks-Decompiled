# Embedded file name: scripts/client/messenger/proto/migration/__init__.py
import weakref
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.migration import contacts

class MigrationPlugin(IProtoPlugin):
    __slots__ = ('__bwProto', '__bw2Proto', '__xmppProto', '__contacts')

    def __init__(self, plugins):
        super(MigrationPlugin, self).__init__()
        self.__bwProto = weakref.proxy(plugins[PROTO_TYPE.BW])
        self.__bw2Proto = weakref.proxy(plugins[PROTO_TYPE.BW_CHAT2])
        self.__xmppProto = weakref.proxy(plugins[PROTO_TYPE.XMPP])
        self.__contacts = None
        return

    def isConnected(self):
        if g_settings.server.useToShowContacts(PROTO_TYPE.XMPP):
            proto = self.__xmppProto
        else:
            proto = self.__bwProto
        return proto.isConnected()

    @property
    def contacts(self):
        return self.__contacts

    @property
    def voipProvider(self):
        if g_settings.server.BW_CHAT2.isEnabled():
            proto = self.__bw2Proto
        else:
            proto = self.__bwProto
        return proto.voipProvider

    def clear(self):
        if self.__contacts:
            self.__contacts.clear()
            self.__contacts = None
        return

    def connect(self, scope):
        if self.__contacts is None:
            if g_settings.server.useToShowContacts(PROTO_TYPE.XMPP):
                self.__contacts = contacts.XMPPContactsManagerProxy(self.__bwProto, self.__xmppProto)
            else:
                self.__contacts = contacts.BWContactsManagerProxy(self.__bwProto)
        g_messengerEvents.onPluginConnected += self.__onPluginConnected
        g_messengerEvents.onPluginDisconnected += self.__onPluginDisconnected
        return

    def disconnect(self):
        g_messengerEvents.onPluginConnected -= self.__onPluginConnected
        g_messengerEvents.onPluginDisconnected -= self.__onPluginDisconnected
        self.clear()

    def __onPluginConnected(self, protoType):
        if protoType == PROTO_TYPE.MIGRATION:
            return
        if g_settings.server.useToShowContacts(protoType):
            g_messengerEvents.onPluginConnected(PROTO_TYPE.MIGRATION)

    def __onPluginDisconnected(self, protoType):
        if protoType == PROTO_TYPE.MIGRATION:
            return
        if g_settings.server.useToShowContacts(protoType):
            g_messengerEvents.onPluginDisconnected(PROTO_TYPE.MIGRATION)


def getSearchUserProcessor():
    if g_settings.server.BW_CHAT2.isEnabled():
        from messenger.proto.bw_chat2.search_processor import SearchUsersProcessor
        return SearchUsersProcessor()
    else:
        from messenger.proto.bw.search_processors import SearchUsersProcessor
        return SearchUsersProcessor()


def getBattleCommandFactory():
    if g_settings.server.BW_CHAT2.isEnabled():
        from messenger.proto import proto_getter
        factory = proto_getter(PROTO_TYPE.BW_CHAT2).get().battleCmd.factory
    else:
        from messenger.proto.bw.battle_chat_cmd import BattleCommandFactory
        factory = BattleCommandFactory()
    return factory
