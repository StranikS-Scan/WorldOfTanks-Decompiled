# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/impl.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event

class IGuiLoader(object):
    __slots__ = ()

    @property
    def resourceManager(self):
        raise NotImplementedError

    @property
    def windowsManager(self):
        raise NotImplementedError

    @property
    def systemLocale(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class INotificationWindowController(IGameController):
    __slots__ = ('onPostponedQueueUpdated',)
    if typing.TYPE_CHECKING:
        onPostponedQueueUpdated = None

    def append(self, window):
        raise NotImplementedError

    def hasWindow(self, window):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def postponeActive(self):
        raise NotImplementedError

    def releasePostponed(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @property
    def postponedCount(self):
        raise NotImplementedError


class IFullscreenManager(object):
    __slots__ = ()

    def setEnabled(self, value):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class IWindowLoaderController(IGameController):
    __slots__ = ()
