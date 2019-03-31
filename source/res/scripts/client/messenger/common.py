# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/common.py
# Compiled at: 2011-07-29 13:15:51
from ChatManager import chatManager
from debug_utils import LOG_ERROR

class MessangerSubscriber(object):
    _responseHandlers = {}

    def subscribeAction(self, callback, action, cid=None):
        chatManager.subscribeChatAction(callback, action, cid)

    def unsubscribeAction(self, callback, action, cid=None):
        chatManager.unsubscribeChatAction(callback, action, cid)

    def unsubscribeActionByName(self, object, callbackName, action, cid=None):
        if hasattr(object, callbackName):
            callback = getattr(object, callbackName)
            chatManager.unsubscribeChatAction(callback, action, cid)

    def unsubcribeAllActions(self):
        chatManager.unsubcribeAllChatActions()

    def handleChatActionFailureEvent(self, actionResponse, chatAction):
        handler = self._responseHandlers.get(actionResponse)
        if handler is None:
            return False
        elif hasattr(self, handler):
            return getattr(self, handler)(actionResponse, chatAction)
        else:
            LOG_ERROR('handleChatActionFailureEvent: response handler for response %s(%s) not registered' % (actionResponse, actionResponse.index()))
            return False


class MessengerGlobalStorage(object):
    __slots__ = ('attribute',)
    __storage = {}

    def __init__(self, attribute, defaultValue):
        self.attribute = attribute
        if not self.__storage.has_key(attribute):
            self.__storage[attribute] = defaultValue

    def __set__(self, _, value):
        self.__storage[self.attribute] = value

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        else:
            return self.__storage[self.attribute]

    def value(self):
        return self.__storage[self.attribute]
