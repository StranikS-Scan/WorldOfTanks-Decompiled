# Embedded file name: scripts/client/messenger/proto/bw_chat2/__init__.py
from messenger import g_settings
from messenger.m_constants import MESSENGER_SCOPE
from messenger.proto.bw_chat2 import chat_handlers
from messenger.proto.bw_chat2.VOIPChatProvider import VOIPChatProvider
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.bw_chat2.provider import BWChatProvider
from messenger.proto.bw_chat2.UsersHandler import UsersHandler

class BWProtoPlugin(IProtoPlugin):

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
        self.__voipProvider = VOIPChatProvider(self.__provider)
        self.__voipProvider.registerHandlers()

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

    def connect(self, scope):
        if scope != MESSENGER_SCOPE.BATTLE:
            self.__arenaChat.leave()

    def view(self, scope):
        self.__battleCmd.switch(scope)
        self.__voipProvider.switch(scope)

    def disconnect(self):
        self.__arenaChat.disconnect()
        self.__unitChat.disconnect()
        self.__voipProvider.leave()

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
        return

    def onActionReceived(self, actionID, reqID, args):
        if g_settings.server.BW_CHAT2.isEnabled():
            self.__provider.onActionReceived(actionID, reqID, args)
