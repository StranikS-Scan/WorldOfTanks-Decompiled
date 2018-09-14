# Embedded file name: scripts/client/messenger/proto/xmpp/__init__.py
from messenger.proto.xmpp.messages import MessagesManager
from messenger.proto.xmpp.contacts import ContactsManager
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.xmpp.logger import LogHandler
from messenger.proto.xmpp.connection import ConnectionHandler
from messenger.proto.xmpp.gloox_wrapper import ClientDecorator
from messenger.proto.xmpp.spa_requesters import NicknameResolver

class XmppPlugin(IProtoPlugin):
    __slots__ = ('__client', '__contacts', '__connection', '__logger', '__messages', '__isClientInited', '__nicknameResolver')

    def __init__(self):
        self.__client = ClientDecorator()
        self.__contacts = ContactsManager()
        self.__connection = ConnectionHandler()
        self.__messages = MessagesManager()
        self.__logger = LogHandler()
        self.__nicknameResolver = NicknameResolver()
        self.__isClientInited = False

    def __repr__(self):
        return 'XmppPlugin(id=0x{0:08X}, ro={1!r:s},'.format(id(self), ['client',
         'contacts',
         'messages',
         'logger'])

    @property
    def client(self):
        return self.__client

    @property
    def logger(self):
        return self.__logger

    @property
    def contacts(self):
        return self.__contacts

    @property
    def messages(self):
        return self.__messages

    @property
    def nicknames(self):
        return self.__nicknameResolver

    def isConnected(self):
        return self.__client.isConnected()

    def clear(self):
        if self.__isClientInited:
            self.__finiClientEnv()
        self.__isClientInited = False
        self.__connection.clear()
        self.__contacts.clear()
        self.__messages.clear()
        self.__logger.clear()
        self.__nicknameResolver.clear()

    def connect(self, scope):
        self.__contacts.switch(scope)

    def view(self, scope):
        if self.__client.isConnected():
            return
        if not self.__isClientInited:
            self.__initClientEnv()
            self.__isClientInited = True
        self.__connection.connect()

    def disconnect(self):
        self.__connection.disconnect()
        if self.__isClientInited:
            self.__isClientInited = False
            self.__finiClientEnv()
            self.__connection.clear()
            self.__logger.clear()
            self.__nicknameResolver.clear()

    def setFilters(self, msgFilterChain):
        if self.__messages:
            self.__messages.setFilters(msgFilterChain)

    def __initClientEnv(self):
        self.__client.init()
        self.__connection.registerHandlers()
        self.__contacts.registerHandlers()
        self.__messages.registerHandlers()
        self.__logger.registerHandlers()
        self.__nicknameResolver.registerHandlers()

    def __finiClientEnv(self):
        self.__connection.unregisterHandlers()
        self.__contacts.unregisterHandlers()
        self.__messages.unregisterHandlers()
        self.__logger.unregisterHandlers()
        self.__nicknameResolver.unregisterHandlers()
        self.__client.fini()
