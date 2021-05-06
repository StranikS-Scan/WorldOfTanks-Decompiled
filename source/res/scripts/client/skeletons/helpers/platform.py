# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/helpers/platform.py
import typing
if typing.TYPE_CHECKING:
    from Event import Event

class IPublishPlatform(object):
    onPayment = None
    onOverlay = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isInited(self):
        raise NotImplementedError

    def isConnected(self):
        raise NotImplementedError
