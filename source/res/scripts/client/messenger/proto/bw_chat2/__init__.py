# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/__init__.py
from messenger import g_settings
from messenger.m_constants import MESSENGER_SCOPE, PROTO_TYPE
from messenger.proto.bw_chat2 import chat_handlers
from messenger.proto.bw_chat2.VOIPChatProvider import VOIPChatProvider
from messenger.proto.bw_chat2.VOIPChatController import VOIPChatController
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IProtoPlugin
from messenger.proto.bw_chat2.provider import BWChatProvider
from messenger.proto.bw_chat2.UsersHandler import UsersHandler

class BWProtoPlugin(IProtoPlugin):
    __slots__ = ('__provider', '__adminChat', '__users', '__arenaChat', '__battleCmd', '__unitChat', '__voipProvider', '__voipCtrl', '__isConnected')

    def __init__(self):
        super(BWProtoPlugin, self).__init__()
        self.__provider = None
        self.__adminChat = None
        self.__users = None
        self.__arenaChat = None
        self.__battleCmd = None
        self.__unitChat = None
        self.__voipProvider = None
        self.__voipCtrl = None
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
    def adminChat(self):
        return self.__adminChat

    @property
    def provider(self):
        return self.__provider

    @property
    def voipProvider(self):
        return self.__voipProvider

    @property
    def voipController(self):
        return self.__voipCtrl

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
            self.__voipCtrl.start()
            g_messengerEvents.onPluginConnected(PROTO_TYPE.BW_CHAT2)

    def view(self, scope):
        self.__provider.setEnable(True)
        self.__battleCmd.switch(scope)

    def disconnect(self):
        if not self.__isConnected:
            return
        self.__isConnected = False
        self.__arenaChat.disconnect()
        self.__unitChat.disconnect()
        self.__voipProvider.leave()
        self.__voipCtrl.stop()
        self.__provider.setEnable(False)
        g_messengerEvents.onPluginDisconnected(PROTO_TYPE.BW_CHAT2)

    def setFilters(self, msgFilterChain):
        self.__provider.setFilters(msgFilterChain)

    def init(self):
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
        self.__voipCtrl = VOIPChatController()

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
        if self.__voipCtrl:
            self.__voipCtrl.stop()
            self.__voipCtrl = None
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
