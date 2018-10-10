# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/migration/plugin.py
import weakref
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.migration import contacts, messages

class MigrationPlugin(IProtoPlugin):
    __slots__ = ('__bwProto', '__bw2Proto', '__xmppProto', '__contacts', '__messages')

    def __init__(self, plugins):
        super(MigrationPlugin, self).__init__()
        self.__bwProto = weakref.proxy(plugins[PROTO_TYPE.BW])
        self.__bw2Proto = weakref.proxy(plugins[PROTO_TYPE.BW_CHAT2])
        self.__xmppProto = weakref.proxy(plugins[PROTO_TYPE.XMPP])
        self.__contacts = None
        self.__messages = None
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
    def messages(self):
        return self.__messages

    def clear(self):
        if self.__contacts is not None:
            self.__contacts.clear()
            self.__contacts = None
        if self.__messages is not None:
            self.__messages.clear()
            self.__messages = None
        return

    def connect(self, scope):
        if self.__contacts is None:
            if g_settings.server.useToShowContacts(PROTO_TYPE.XMPP):
                self.__contacts = contacts.XMPPContactsManagerProxy(self.__xmppProto)
            else:
                self.__contacts = contacts.BWContactsManagerProxy(self.__bwProto)
        if self.__messages is None:
            if g_settings.server.isUserRoomsEnabled(PROTO_TYPE.XMPP):
                self.__messages = messages.XMPPMessagesManagerProxy(self.__xmppProto)
            else:
                self.__messages = messages.BWMessagesManagerProxy(self.__bwProto)
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
