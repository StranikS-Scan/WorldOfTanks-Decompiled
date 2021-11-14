# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/subsystems.py
import typing
if typing.TYPE_CHECKING:
    from gui.gift_system.constants import GiftMessageType
    from helpers.server_settings import GiftEventConfig

class BaseHubSubsystem(object):
    __slots__ = ('_settings',)

    def __init__(self, eventSettings):
        super(BaseHubSubsystem, self).__init__()
        self._settings = eventSettings

    def destroy(self):
        pass

    def updateSettings(self, eventSettings):
        self._settings = eventSettings


class BaseMessegesDelayer(BaseHubSubsystem):
    __slots__ = ('_msgQueue', '_msgHandlers')

    def __init__(self, eventSettings):
        super(BaseMessegesDelayer, self).__init__(eventSettings)
        self._msgHandlers = {}
        self._msgQueue = []

    def destroy(self):
        self._clearMessagesQueue()
        self._msgHandlers.clear()
        super(BaseMessegesDelayer, self).destroy()

    def isMessagesEnabled(self):
        raise NotImplementedError

    def isMessagesSuspended(self, *args, **kwargs):
        raise NotImplementedError

    def addToQueue(self, msgType, msgData):
        self._msgQueue.append((msgType, msgData))

    def _clearMessagesQueue(self):
        del self._msgQueue[:]

    def _processMessagesQueue(self):
        for msgType, msgData in ((mType, mData) for mType, mData in self._msgQueue if mType in self._msgHandlers):
            self._msgHandlers[msgType](msgData)

        self._clearMessagesQueue()
