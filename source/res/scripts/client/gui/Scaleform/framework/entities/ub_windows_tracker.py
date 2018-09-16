# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/ub_windows_tracker.py
from frameworks.wulf import WindowFlags, Window, WindowStatus

class UnboundWindowsTracker(object):
    __slots__ = ('__window',)

    def __init__(self):
        super(UnboundWindowsTracker, self).__init__()
        self.__window = None
        return

    def getParentWindow(self):
        return self.__window

    def create(self):
        if self.__window is not None:
            return
        else:
            self.__window = Window(wndFlags=WindowFlags.WINDOW, decorator=None, content=None, parent=None)
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
        return
