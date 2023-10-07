# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/main_window.py
import typing
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.impl.pub.window_impl import WindowImpl
if typing.TYPE_CHECKING:
    from gui.impl.pub.main_view import MainView

class MainWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, content=None):
        super(MainWindow, self).__init__(WindowFlags.MAIN_WINDOW, content=content)

    def _initialize(self):
        super(MainWindow, self)._initialize()
        self.gui.windowsManager.addWindowsArea(R.areas.default())
        self.gui.windowsManager.addWindowsArea(R.areas.specific())
        self.gui.windowsManager.addWindowsArea(R.areas.pop_over())
        self.gui.windowsManager.addWindowsArea(R.areas.context_menu())

    def _finalize(self):
        self.gui.windowsManager.removeWindowsArea(R.areas.default())
        self.gui.windowsManager.removeWindowsArea(R.areas.specific())
        self.gui.windowsManager.removeWindowsArea(R.areas.pop_over())
        self.gui.windowsManager.removeWindowsArea(R.areas.context_menu())
        super(MainWindow, self)._finalize()
