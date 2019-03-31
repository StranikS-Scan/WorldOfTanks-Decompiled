# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scalefrom/ServiceChannelInterface.py
# Compiled at: 2011-07-29 15:44:51
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from messenger.gui.interfaces import DispatcherProxyHolder
from messenger.gui.Scalefrom import SCH_COMMANDS

class ServiceChannelInterface(DispatcherProxyHolder):

    def __init__(self):
        self.__movieViewHandler = None
        return

    @property
    def serviceChannelManager(self):
        return self._dispatcherProxy.serviceChannel

    def populateUI(self, movieViewHandler):
        self.__movieViewHandler = movieViewHandler
        self.serviceChannelManager.onReceiveServerMessage += self.__onReceiveServerMessage
        self.serviceChannelManager.onReceiveClientMessage += self.__onReceiveClientMessage
        self.__movieViewHandler.addExternalCallbacks({SCH_COMMANDS.RequestMessageHistory(): self.onRequestMessageHistory,
         SCH_COMMANDS.RequestUnreadMessages(): self.onRequestUnreadMessages,
         SCH_COMMANDS.ClearUnreadMessagesCount(): self.onClearUnreadMessagesCount})

    def dispossessUI(self):
        self.clear()
        self.serviceChannelManager.onReceiveServerMessage -= self.__onReceiveServerMessage
        self.serviceChannelManager.onReceiveClientMessage -= self.__onReceiveClientMessage
        self.__movieViewHandler.removeExternalCallbacks(SCH_COMMANDS.RequestMessageHistory(), SCH_COMMANDS.RequestUnreadMessages(), SCH_COMMANDS.ClearUnreadMessagesCount())
        self.__movieViewHandler = None
        return

    def clear(self):
        if self.__movieViewHandler:
            self.__movieViewHandler.call(SCH_COMMANDS.ClearData())
        self.serviceChannelManager.resetUnreadCount()

    def onRequestMessageHistory(self, *args):
        parser = CommandArgsParser(self.onRequestMessageHistory.__name__)
        parser.parse(*args)
        parser.addArgs(self.serviceChannelManager.getServiceMessages())
        self.__movieViewHandler.respond(parser.args())

    def onRequestUnreadMessages(self, *args):
        self.serviceChannelManager.fireReceiveMessageEvents()

    def onClearUnreadMessagesCount(self, *args):
        self.serviceChannelManager.resetUnreadCount()

    def __onReceiveServerMessage(self, message, isPriority, notify, auxData):
        if self.__movieViewHandler:
            args = [message, isPriority, notify]
            args.extend(auxData)
            self.__movieViewHandler.call(SCH_COMMANDS.ReceiveServerMessage(), args)

    def __onReceiveClientMessage(self, message, isPriority, notify, auxData):
        if self.__movieViewHandler:
            args = [message, isPriority, notify]
            args.extend(auxData)
            self.__movieViewHandler.call(SCH_COMMANDS.ReceiveClientMessage(), args)
