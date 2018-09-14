# Embedded file name: scripts/client/messenger/proto/bw/ServiceChannelManager.py
from collections import deque
from chat_shared import CHAT_ACTIONS
from constants import IS_DEVELOPMENT
from debug_utils import *
from ids_generators import SequenceIDGenerator
from messenger.formatters import collections_by_type
from messenger.m_constants import MESSENGER_SCOPE, SCH_MSGS_MAX_LENGTH
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from messenger.proto.bw.ChatActionsListener import ChatActionsListener
from messenger.proto.bw.wrappers import ServiceChannelMessage
from messenger.proto.events import g_messengerEvents
from adisp import process

class ServiceChannelManager(ChatActionsListener):

    def __init__(self):
        ChatActionsListener.__init__(self)
        self.__idGenerator = SequenceIDGenerator()
        self.__messages = deque([], SCH_MSGS_MAX_LENGTH)
        self.__unreadMessagesCount = 0

    def addListeners(self):
        self.addListener(self.onReceiveSysMessage, CHAT_ACTIONS.sysMessage)
        self.addListener(self.onReceivePersonalSysMessage, CHAT_ACTIONS.personalSysMessage)

    def clear(self):
        self.__messages.clear()
        self.__unreadMessagesCount = 0

    def switch(self, scope):
        if scope is MESSENGER_SCOPE.LOBBY:
            self.requestLastServiceMessages()

    def requestLastServiceMessages(self):
        BigWorld.player().requestLastSysMessages()

    def onReceiveSysMessage(self, chatAction):
        message = ServiceChannelMessage.fromChatAction(chatAction)
        self.__addServerMessage(message)

    def onReceivePersonalSysMessage(self, chatAction):
        message = ServiceChannelMessage.fromChatAction(chatAction, personal=True)
        self.__addServerMessage(message)

    def pushClientSysMessage(self, message, msgType, isAlert = False, priority = None):
        return self.__addClientMessage(message, SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE, isAlert=isAlert, auxData=[msgType.name(), priority])

    def pushClientMessage(self, message, msgType, isAlert = False, auxData = None):
        return self.__addClientMessage(message, msgType, isAlert=isAlert, auxData=auxData)

    def getReadMessages(self):
        if self.__unreadMessagesCount > 0:
            messages = list(self.__messages)[:-self.__unreadMessagesCount]
        else:
            messages = self.__messages
        for clientID, message in messages:
            yield (clientID, message)

    def getMessage(self, clientID):
        mapping = dict(self.__messages)
        message = (False, None, None)
        if clientID in mapping:
            message = mapping[clientID]
        return message

    def getUnreadCount(self):
        return self.__unreadMessagesCount

    def resetUnreadCount(self):
        self.__unreadMessagesCount = 0

    def handleUnreadMessages(self):
        if not self.__unreadMessagesCount:
            return
        unread = list(self.__messages)[-self.__unreadMessagesCount:]
        serviceChannel = g_messengerEvents.serviceChannel
        for clientID, (isServerMsg, formatted, settings) in unread:
            if isServerMsg:
                serviceChannel.onServerMessageReceived(clientID, formatted, settings)
            else:
                serviceChannel.onClientMessageReceived(clientID, formatted, settings)

    @process
    def __addServerMessage(self, message):
        yield lambda callback: callback(True)
        formatter = collections_by_type.SERVER_FORMATTERS.get(message.type)
        serviceChannel = g_messengerEvents.serviceChannel
        serviceChannel.onChatMessageReceived(self.__idGenerator.next(), message)
        LOG_DEBUG('Server message received', message, formatter)
        if formatter:
            try:
                if formatter.isAsync():
                    formatted, settings = yield formatter.format(message)
                else:
                    formatted, settings = formatter.format(message)
            except:
                LOG_CURRENT_EXCEPTION()
                return

            if formatted:
                clientID = self.__idGenerator.next()
                self.__messages.append((clientID, (True, formatted, settings)))
                self.__unreadMessagesCount += 1
                serviceChannel.onServerMessageReceived(clientID, formatted, settings)
                customEvent = settings.getCustomEvent()
                if customEvent is not None:
                    serviceChannel.onCustomMessageDataReceived(clientID, customEvent)
            elif IS_DEVELOPMENT:
                LOG_WARNING('Not enough data to format. Action data : ', message)
        elif IS_DEVELOPMENT:
            LOG_WARNING('Formatter not found. Action data : ', message)
        return

    def __addClientMessage(self, message, msgType, isAlert = False, auxData = None):
        if auxData is None:
            auxData = []
        clientID = 0
        formatter = collections_by_type.CLIENT_FORMATTERS.get(msgType)
        if formatter:
            try:
                formatted, settings = formatter.format(message, auxData)
            except:
                LOG_CURRENT_EXCEPTION()
                return

            if formatted:
                clientID = self.__idGenerator.next()
                if not settings.isAlert:
                    settings.isAlert = isAlert
                self.__messages.append((clientID, (False, formatted, settings)))
                self.__unreadMessagesCount += 1
                g_messengerEvents.serviceChannel.onClientMessageReceived(clientID, formatted, settings)
            elif IS_DEVELOPMENT:
                LOG_WARNING('Not enough data to format. Action data : ', message)
        elif IS_DEVELOPMENT:
            LOG_WARNING('Formatter not found:', msgType, message)
        return clientID
