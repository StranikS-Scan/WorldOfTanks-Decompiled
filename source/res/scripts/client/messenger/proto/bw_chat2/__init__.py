# Embedded file name: scripts/client/messenger/proto/bw_chat2/__init__.py
from messenger import g_settings
from messenger.m_constants import MESSENGER_SCOPE, PROTO_TYPE
from messenger.proto.bw_chat2 import chat_handlers
from messenger.proto.bw_chat2.ClubListener import ClubListener
from messenger.proto.bw_chat2.VOIPChatProvider import VOIPChatProvider
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.bw_chat2.provider import BWChatProvider
from messenger.proto.bw_chat2.UsersHandler import UsersHandler

class BWProtoPlugin(IProtoPlugin):
    __slots__ = ('__provider', '__adminChat', '__users', '__arenaChat', '__battleCmd', '__unitChat', '__clubChat', '__voipProvider', '__isConnected', '__clubListener')

    def __init__(self):
        super(BWProtoPlugin, self).__init__()
        self.__provider = BWChatProvider()
        self.__adminChat = chat_handlers.AdminChatCommandHandler(self.__provider)
        self.__adminChat.registerHandlers()
        self.__users = UsersHandler(self.__provider)
        self.__users.registerHandlers()
        self.__arenaChat = chat_handlers.ArenaChatHandler(self.__provider, self.__adminChat)
        self.__arenaChat.registerHandlers()
        self.__battleCmd = chat_handlers.BattleChatCommandHandler(self.__provider)
        self.__battleCmd.registerHandlers()
        self.__unitChat = chat_handlers.UnitChatHandler(self.__provider, self.__adminChat)
        self.__unitChat.registerHandlers()
        self.__clubChat = chat_handlers.ClubChatHandler(self.__provider, self.__adminChat)
        self.__clubChat.registerHandlers()
        self.__clubListener = None
        self.__voipProvider = VOIPChatProvider(self.__provider)
        self.__voipProvider.registerHandlers()
        self.__isConnected = False
        return

    @property
    def arenaChat(self):
        return self.__arenaChat

    @property
    def battleCmd(self):
        return self.__battleCmd

    @property
    def unitChat(self):
        return self.__unitChat

    @property
    def clubChat(self):
        return self.__clubChat

    @property
    def adminChat(self):
        return self.__adminChat

    @property
    def provider(self):
        return self.__provider

    @property
    def voipProvider(self):
        return self.__voipProvider

    @property
    def users(self):
        return self.__users

    def isConnected(self):
        return self.__isConnected

    def connect(self, scope):
        if scope != MESSENGER_SCOPE.BATTLE:
            self.__arenaChat.leave()
        if not self.__isConnected:
            self.__isConnected = True
            g_messengerEvents.onPluginConnected(PROTO_TYPE.BW_CHAT2)

    def view(self, scope):
        self.__provider.setEnable(True)
        self.__battleCmd.switch(scope)
        if scope == MESSENGER_SCOPE.LOBBY:
            self.__clubListener = ClubListener()
            self.__clubListener.start()
        elif self.__clubListener:
            self.__clubListener.stop()
            self.__clubListener = None
        return

    def disconnect(self):
        if not self.__isConnected:
            return
        else:
            self.__isConnected = False
            self.__arenaChat.disconnect()
            self.__unitChat.disconnect()
            self.__clubChat.disconnect()
            self.__voipProvider.leave()
            self.__provider.setEnable(False)
            if self.__clubListener:
                self.__clubListener.stop()
                self.__clubListener = None
            g_messengerEvents.onPluginDisconnected(PROTO_TYPE.BW_CHAT2)
            return

    def setFilters(self, msgFilterChain):
        self.__provider.setFilters(msgFilterChain)

    def clear(self):
        if self.__arenaChat:
            self.__arenaChat.unregisterHandlers()
            self.__arenaChat.clear()
            self.__arenaChat = None
        if self.__battleCmd:
            self.__battleCmd.unregisterHandlers()
            self.__battleCmd.clear()
            self.__battleCmd = None
        if self.__unitChat:
            self.__unitChat.unregisterHandlers()
            self.__unitChat.clear()
            self.__unitChat = None
        if self.__clubChat:
            self.__clubChat.unregisterHandlers()
            self.__clubChat.clear()
            self.__clubChat = None
        if self.__adminChat:
            self.__adminChat.unregisterHandlers()
            self.__adminChat.clear()
            self.__adminChat = None
        if self.__voipProvider:
            self.__voipProvider.unregisterHandlers()
            self.__voipProvider.clear()
            self.__voipProvider = None
        if self.__provider:
            self.__provider.clear()
            self.__provider = None
        if self.__users:
            self.__users.clear()
            self.__users = None
        if self.__clubListener:
            self.__clubListener.stop()
            self.__clubListener = None
        return

    def onActionReceived(self, actionID, reqID, args):
        if g_settings.server.BW_CHAT2.isEnabled():
            self.__provider.onActionReceived(actionID, reqID, args)
