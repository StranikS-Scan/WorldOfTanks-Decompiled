# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/platform/base.py
from Event import EventManager, Event
from skeletons.helpers.platform import IPublishPlatform

class BasePublishPlatform(IPublishPlatform):
    __slots__ = ('__eventMgr', 'onPayment', 'onOverlay')

    def __init__(self):
        super(BasePublishPlatform, self).__init__()
        self.__eventMgr = EventManager()
        self.onPayment = Event(self.__eventMgr)
        self.onOverlay = Event(self.__eventMgr)

    def init(self):
        pass

    def fini(self):
        self.__eventMgr.clear()

    def isInited(self):
        return False

    def isConnected(self):
        return False
