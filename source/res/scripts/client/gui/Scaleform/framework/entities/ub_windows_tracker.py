# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/ub_windows_tracker.py
import typing
import weakref
from frameworks.wulf import WindowFlags, Window, WindowStatus

class UnboundWindowsTracker(object):
    __slots__ = ('__window', '__view')

    def __init__(self, view):
        super(UnboundWindowsTracker, self).__init__()
        self.__view = weakref.proxy(view)
        self.__window = None
        return

    def getParentWindow(self):
        return self.__window

    def create(self, parent=None):
        if self.__window is not None:
            return
        else:
            self.__window = Window(wndFlags=WindowFlags.WINDOW, decorator=None, content=None, parent=parent)
            self.__window.onStatusChanged += self.__onStatusChanged
            self.__window.load()
            return

    def destroy(self):
        if self.__window is not None:
            self.__window.onStatusChanged -= self.__onStatusChanged
            self.__window.destroy()
            self.__window = None
        return

    def __onStatusChanged(self, state):
        if state == WindowStatus.DESTROYED:
            self.__window = None
            if not self.__view.isDisposed():
                self.__view.destroy()
        return
