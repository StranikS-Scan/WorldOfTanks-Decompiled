# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/shared_messages.py
from messenger.proto.interfaces import IChatMessage

class ACTION_MESSAGE_TYPE(object):
    PLAYER = 0
    WARNING = 1
    ERROR = 2
    FAIRPLAY_WARNING = 3


class ClientActionMessage(IChatMessage):

    def __init__(self, msg=None, type_=ACTION_MESSAGE_TYPE.PLAYER):
        super(ClientActionMessage, self).__init__()
        self.__message = msg
        self.__type = type_

    def setMessage(self, msg):
        self.__message = msg

    def getMessage(self):
        return self.__message

    def getType(self):
        return self.__type


class ClientActionTemplateMessage(ClientActionMessage):

    def __init__(self, tempalteKey, type_=ACTION_MESSAGE_TYPE.PLAYER):
        super(ClientActionTemplateMessage, self).__init__(type_=type_)
        self._tempalteKey = tempalteKey

    def getTemplateKey(self):
        return self._tempalteKey
