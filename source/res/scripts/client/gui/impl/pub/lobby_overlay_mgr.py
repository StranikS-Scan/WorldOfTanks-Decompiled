# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/lobby_overlay_mgr.py
import logging
import weakref
import BigWorld
from frameworks.state_machine import SingleStateObserver
from frameworks.wulf import WindowFlags, WindowStatus
from gui.impl.pub.lobby_window import LobbyOverlay
from helpers import dependency
from shared_utils import findFirst
from skeletons.gameplay import IGameplayLogic, GameplayStateID
from skeletons.gui.impl import IGuiLoader, IOverlaysManager
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class UnmanagedOverlayState(object):
    __slots__ = ('uniqueID', 'isSuspended')

    def __init__(self, uniqueID):
        super(UnmanagedOverlayState, self).__init__()
        self.uniqueID = uniqueID
        self.isSuspended = False

    def __repr__(self):
        return 'UnmanagedOverlayState(uniqueID={})'.format(self.uniqueID)

    @property
    def isExclusive(self):
        return False

    @property
    def isRepeatable(self):
        return False

    def close(self, window):
        pass

    def load(self):
        raise SoftException('UnmanagedOverlayState can not load overlay')

    def restore(self):
        raise SoftException('UnmanagedOverlayState can not restore overlay')


class ManagedOverlayState(UnmanagedOverlayState):
    __slots__ = ('behavior', 'uniqueID', 'isSuspended')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, uniqueID, behavior):
        super(ManagedOverlayState, self).__init__(uniqueID)
        self.behavior = behavior

    def __repr__(self):
        return 'ManagedOverlayState(behavior={})'.format(self.behavior)

    @property
    def isExclusive(self):
        return self.behavior.isExclusive

    @property
    def isRepeatable(self):
        return self.behavior.isRepeatable

    def close(self, window):
        self.behavior.close(window)

    def load(self):
        window = self.__gui.windowsManager.getWindow(self.uniqueID)
        if window is not None:
            window.load()
        return

    def restore(self):
        if self.behavior.isRepeatable:
            clone = self.behavior.repeat()
            if clone is not None:
                self.isSuspended = False
                self.uniqueID = clone.uniqueID
                clone.load()
                return True
        else:
            self.isSuspended = False
            self.load()
            return True
        return False


_CHECK_CONDITION_DELAY = 1.0

class AccountStateObserver(SingleStateObserver):
    __slots__ = ('__overlays',)

    def __init__(self, overlays):
        super(AccountStateObserver, self).__init__(GameplayStateID.ACCOUNT)
        self.__overlays = overlays

    def onExitState(self, event=None):
        self.__overlays.clear()


class LobbyOverlaysManager(IOverlaysManager):
    __slots__ = ('__weakref__', '__gui', '__suspended', '__opened', '__isSuspended', '__callbackID', '__observer', '__condition')
    __gui = dependency.descriptor(IGuiLoader)
    __gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self):
        super(LobbyOverlaysManager, self).__init__()
        self.__suspended = []
        self.__opened = []
        self.__isSuspended = False
        self.__callbackID = None
        self.__condition = None
        self.__observer = AccountStateObserver(weakref.proxy(self))
        return

    def init(self):
        self.__gameplay.addStateObserver(self.__observer)
        self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def fini(self):
        self.clear()
        self.__gameplay.removeStateObserver(self.__observer)
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def clear(self):
        self.__clearCallback()
        del self.__suspended[:]
        del self.__opened[:]

    def isSuspended(self, window):
        return findFirst(lambda item: item.uniqueID == window.uniqueID and item.isSuspended, self.__suspended, False)

    def release(self):
        if not self.__isSuspended:
            return
        else:
            self.__isSuspended = False
            self.__condition = None
            self.__restore()
            return

    def suspend(self, condition=None):
        self.__isSuspended = True
        self.__condition = condition

    def __restore(self):
        if self.__opened:
            return
        else:
            for item in self.__suspended:
                if item.restore():
                    _logger.debug('Overlay is restored: %r', item)
                    if item.isExclusive:
                        break

            self.__suspended = [ item for item in self.__suspended if item.isSuspended ]
            if self.__callbackID is None and not self.__opened and [ item for item in self.__suspended if item.isRepeatable ]:
                self.__callbackID = BigWorld.callback(_CHECK_CONDITION_DELAY, self.__tryRestore)
            return

    def __tryRestore(self):
        self.__callbackID = None
        self.__restore()
        return

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __close(self, sequence, window):
        found = findFirst(lambda suspended: suspended.uniqueID == window.uniqueID, sequence, None)
        if found is not None:
            found.close(window)
            sequence.remove(found)
        return found

    def __onOverlayCreated(self, window):
        if not isinstance(window, LobbyOverlay):
            state = UnmanagedOverlayState(window.uniqueID)
            _logger.debug('Unmanaged overlay state is created for: %r', window)
            self.__opened.append(state)
        else:
            state = ManagedOverlayState(window.uniqueID, window.behavior)
            _logger.debug('Managed overlay state is created for: %r', window)
            if self.__isSuspended:
                if self.__condition is not None:
                    isSuspended = self.__condition(window)
                else:
                    isSuspended = True
            else:
                isSuspended = False
            if isSuspended or self.__opened and self.__opened[-1].isExclusive:
                state.isSuspended = True
                self.__suspended.append(state)
                _logger.debug('Overlay is suspended: %r', window)
            else:
                self.__opened.append(state)
        return

    def __onOverlayDestroying(self, window):
        self.__close(self.__suspended, window)
        found = self.__close(self.__opened, window)
        if not self.__isSuspended:
            self.__restore()
        if found is not None and found.isRepeatable:
            found.isSuspended = True
            self.__suspended.append(found)
            _logger.debug('Overlay will be repeat: %r', found)
        return

    def __onWindowStatusChanged(self, uniqueID, newState):
        window = self.__gui.windowsManager.getWindow(uniqueID)
        if window is None:
            return
        elif window.windowFlags != WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN:
            return
        else:
            if newState == WindowStatus.CREATED:
                self.__onOverlayCreated(window)
            elif newState == WindowStatus.DESTROYING:
                self.__onOverlayDestroying(window)
            return
