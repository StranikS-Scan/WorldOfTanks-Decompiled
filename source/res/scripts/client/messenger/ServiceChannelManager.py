# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/ServiceChannelManager.py
# Compiled at: 2011-07-29 15:44:51
import BigWorld
from chat_shared import CHAT_ACTIONS
from collections import deque
from constants import IS_DEVELOPMENT
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from messenger import SCH_MSGS_MAX_LENGTH, SCH_CLIENT_FORMATTERS_DICT, SCH_SERVER_FORMATTERS_DICT, SCH_CLIENT_MSG_TYPE
from messenger.common import MessangerSubscriber
from messenger.wrappers import ServiceChannelMessage
import Event

class ServiceChannelManager(MessangerSubscriber):
    __messages = deque([], SCH_MSGS_MAX_LENGTH)

    def __init__(self):
        MessangerSubscriber.__init__(self)
        self.__unreadMessageCount = 0
        self.onReceiveServerMessage = Event.Event()
        self.onReceiveClientMessage = Event.Event()
        self.__expirationShown = False

    def subscribeToActions(self):
        self.subscribeAction(self.onReceiveSysMessage, CHAT_ACTIONS.sysMessage)
        self.subscribeAction(self.onReceivePersonalSysMessage, CHAT_ACTIONS.personalSysMessage)

    def clear(self):
        self.__messages.clear()
        self.onReceiveServerMessage.clear()
        self.onReceiveClientMessage.clear()

    def __addServerMessage(self, message):
        formatter = SCH_SERVER_FORMATTERS_DICT.get(message.type)
        if formatter:
            try:
                formatted = formatter.format(message)
                notify = formatter.notify()
            except:
                LOG_CURRENT_EXCEPTION()
                return

            if formatted:
                priority = message.isHighImportance and message.active
                self.__messages.append((formatted,
                 True,
                 priority,
                 notify,
                 []))
                self.__unreadMessageCount += 1
                self.onReceiveServerMessage(formatted, message.isHighImportance and message.active, notify, [])
            elif IS_DEVELOPMENT:
                LOG_WARNING('Not enough data to format. Action data : ', message)
        elif IS_DEVELOPMENT:
            LOG_WARNING('Formatter not found. Action data : ', message)

    def __addClientMessage(self, message, type, isPriority=False, auxData=None):
        if auxData is None:
            auxData = []
        formatter = SCH_CLIENT_FORMATTERS_DICT.get(type)
        if formatter:
            try:
                formatted = formatter.format(message, auxData)
                notify = formatter.notify()
            except:
                LOG_CURRENT_EXCEPTION()
                return

            self.__messages.append((formatted,
             False,
             isPriority,
             notify,
             auxData))
            self.__unreadMessageCount += 1
            self.onReceiveClientMessage(formatted, isPriority, notify, auxData)
        elif IS_DEVELOPMENT:
            LOG_WARNING('Formatter not found:', type, message)
        return

    def requestLastServiceMessages(self):
        BigWorld.player().requestLastSysMessages()

    def onReceiveSysMessage(self, chatAction):
        message = ServiceChannelMessage.fromChatAction(chatAction)
        self.__addServerMessage(message)

    def onReceivePersonalSysMessage(self, chatAction):
        message = ServiceChannelMessage.fromChatAction(chatAction, personal=True)
        self.__addServerMessage(message)

    def pushClientSysMessage(self, message, type, isPriority=False):
        self.__addClientMessage(message, SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE, isPriority=isPriority, auxData=[type.name()])

    def pushClientMessage(self, message, type, isPriority=False, auxData=None):
        self.__addClientMessage(message, type, isPriority=isPriority, auxData=auxData)

    def getServiceMessagesCount(self):
        return len(self.__messages)

    def getServiceMessages(self):
        return map(lambda item: item[0], self.__messages)

    def fireReceiveMessageEvents(self):
        if not self.__unreadMessageCount:
            return
        unreadMessages = list(self.__messages)[-self.__unreadMessageCount:]
        for message, isServerMsg, flag, notify, auxData in unreadMessages:
            dispatchEvent = self.onReceiveServerMessage if isServerMsg else self.onReceiveClientMessage
            dispatchEvent(message, flag, notify, auxData)

    def resetUnreadCount(self):
        self.__unreadMessageCount = 0
