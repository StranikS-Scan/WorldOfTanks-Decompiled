# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/main_window.py
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.impl.pub.window_impl import WindowImpl

class MainWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, entryID, content=None):
        super(MainWindow, self).__init__(WindowFlags.MAIN_WINDOW, entryID=entryID, content=content)

    def _initialize(self):
        super(MainWindow, self)._initialize()
        self.gui.windowsManager.addWindowsArea(R.areas.default())
        self.gui.windowsManager.addWindowsArea(R.areas.specific())
        self.gui.windowsManager.addWindowsArea(R.areas.pop_over())

    def _finalize(self):
        self.gui.windowsManager.removeWindowsArea(R.areas.default())
        self.gui.windowsManager.removeWindowsArea(R.areas.specific())
        self.gui.windowsManager.removeWindowsArea(R.areas.pop_over())
        super(MainWindow, self)._finalize()
