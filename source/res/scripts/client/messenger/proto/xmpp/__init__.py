# Embedded file name: scripts/client/messenger/proto/xmpp/__init__.py
from messenger.proto.xmpp.roster_items import RosterItemStorage
from messenger.storage import addDynStorage, clearDynStorage
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.xmpp.logger import LogHandler
from messenger.proto.xmpp.updaters import UpdatersCollection
from messenger.proto.xmpp.connection import ConnectionHandler, PresenceHandler
from messenger.proto.xmpp.gloox_wrapper import ClientDecorator

class XmppPlugin(IProtoPlugin):

    def __init__(self):
        self.__client = ClientDecorator()
        self.__presence = PresenceHandler()
        self.__connection = ConnectionHandler()
        self.__logger = LogHandler()
        self.__updaters = UpdatersCollection()
        self.__isClientInited = False

    def __repr__(self):
        return 'XmppPlugin(id=0x{0:08X}, ro={1!r:s},'.format(id(self), ['client', 'logger'])

    @property
    def client(self):
        return self.__client

    @property
    def logger(self):
        return self.__logger

    def clear(self):
        self.__isClientInited = False
        self.__finiClientEnv()
        self.__connection.clear()
        self.__presence.clear()
        self.__logger.clear()

    def connect(self, scope):
        self.__presence.update(scope)

    def view(self, scope):
        if self.__client.isConnected():
            return
        if not self.__isClientInited:
            self.__isClientInited = True
            self.__initClientEnv()
        self.__connection.connect()

    def disconnect(self):
        if self.__isClientInited:
            self.clear()
        self.__connection.disconnect()

    def __initClientEnv(self):
        addDynStorage('xmppRoster', RosterItemStorage())
        self.__client.init()
        self.__updaters.init()
        self.__connection.registerHandlers()
        self.__presence.registerHandlers()
        self.__logger.registerHandlers()

    def __finiClientEnv(self):
        clearDynStorage('xmppRoster')
        self.__connection.unregisterHandlers()
        self.__presence.unregisterHandlers()
        self.__logger.unregisterHandlers()
        self.__updaters.fini()
        self.__client.fini()
